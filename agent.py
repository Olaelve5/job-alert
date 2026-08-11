import os
import json
import sqlite3
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.genai.errors import ClientError
import time

from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
model = os.environ.get("MODEL", "gemini-3.5-flash-lite")


# 1. Definer datastrukturen vi vil ha ut fra LLM-en
class JobAnalysis(BaseModel):
    is_junior_or_graduate: int = Field(
        description="True dersom stillingen passer for nyutdannede eller juniorer"
    )
    relevance_score: int = Field(
        description="Relevansscore fra 1 til 10 basert på hvor relevant den er for en juniorutvikler"
    )
    company: str = Field(description="Selskapsnavn")
    role_title: str = Field(description="Stillingstittel")
    tech_stack: List[str] = Field(
        description="Teknologier og rammeverk nevnt i utlysningen"
    )
    summary: str = Field(description="Kort sammendrag på 2-3 setninger om rollen")
    deadline: Optional[str] = Field(
        default=None,
        description="Søknadsfrist konvertert til formatet YYYY-MM-DD. Hvis fristen er 'Snarest', 'Løpende' eller ikke oppgitt, returner null.",
    )


def init_db(db_path: str = "db/ola_jobs.db"):
    dir_name = os.path.dirname(db_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            score INTEGER,
            is_junior INTEGER DEFAULT 0,
            summary TEXT,
            tech_stack TEXT,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_notified INTEGER DEFAULT 0,
            deadline DATE DEFAULT NULL
        )
    """)
    conn.commit()
    conn.close()


def is_already_seen(job_id: str, db_path: str = "jobs.db") -> bool:
    if not os.path.exists(db_path):
        init_db()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def save_job(
    job_id: str,
    title: str,
    company: str,
    score: int,
    url: str,
    is_junior: int,
    tech_stack: List[str],
    summary: str,
    deadline: str = None,
    db_path: str = "jobs.db",
):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO jobs (job_id, title, company, is_junior, url, score, tech_stack, summary, deadline) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            job_id,
            title,
            company,
            is_junior,
            url,
            score,
            json.dumps(tech_stack, ensure_ascii=False),
            summary,
            deadline,
        ),
    )
    conn.commit()
    conn.close()


# 3. Analyser utlysning med Gemini Flash
def analyze_job_posting(
    job_text: str, max_retries: int = 3, prompt_override: str = None
) -> JobAnalysis:
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    if prompt_override:
        prompt = prompt_override
    else:
        prompt = f"""
        Analyser følgende stillingsutlysning og vurder om dette er en junior- eller graduate-stilling innen softwareutvikling.
        
        Utlysningstekst:
        {job_text}
        """

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=JobAnalysis,
                    temperature=0.1,
                ),
            )

            # Respect rate limits by adding a delay before returning the response
            time.sleep(0.5)

            return JobAnalysis.model_validate_json(response.text)

        except ClientError as e:
            if e.code == 429:
                wait_time = 10
                print(
                    f"⚠️ Rate limit hit (429). Pausing for {wait_time}s before retrying (Attempt {attempt + 1}/{max_retries})..."
                )
                print(f"\nError details: {e}")
                time.sleep(wait_time)
            else:
                raise e

    raise RuntimeError(
        "Failed to analyze job posting after max retries due to rate limits."
    )


def process_job(
    job_id: str,
    job_url: str,
    job_text: str,
    db_path: str = "jobs.db",
    prompt_override: str = None,
):
    if is_already_seen(job_id, db_path):
        print(f"Job {job_id} has already been processed. Skipping.")
        return

    analysis = analyze_job_posting(job_text, prompt_override=prompt_override)

    print(f"Analysis for {job_id}:")
    print(f"  Is Junior/Graduate: {analysis.is_junior_or_graduate}")
    print(f"  Relevance Score: {analysis.relevance_score}")
    print(f"  Company: {analysis.company}")
    print(f"  Role Title: {analysis.role_title}")
    print(f"  Tech Stack: {', '.join(analysis.tech_stack)}")
    print(f"  Summary: {analysis.summary}")
    print(f"  Deadline: {analysis.deadline}")

    save_job(
        job_id,
        analysis.role_title,
        analysis.company,
        analysis.relevance_score,
        job_url,
        analysis.is_junior_or_graduate,
        analysis.tech_stack,
        analysis.summary,
        db_path=db_path,
        deadline=analysis.deadline,
    )
