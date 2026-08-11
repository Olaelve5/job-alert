import os
from scrapers.finn_scraper import FinnScraper
from digesters.discord_digest import DiscordDigest
from agent import init_db

from dotenv import load_dotenv

load_dotenv()

init_db(db_path="db/ola_jobs.db")
init_db(db_path="db/peter_jobs.db")

# Configure the scraper and digest mechanism - OLA
ola_discord_digest = DiscordDigest(
    webhook_url=os.getenv("OLA_DISCORD_WEBHOOK_URL"),
    db_path="db/ola_jobs.db",
    min_score=5,
    max_jobs=10,
)

ola_prompt_template = """
    Analyser følgende stillingsutlysning og vurder om dette er en junior- eller graduate-stilling.

    Vurderingene skal baseres på følgende kriterier:
    - Maksimal erfaring: {max_experience_years} år
    - Target roller: {target_roles}
    
    Kandidatens ferdighetsprofil:
    - Programmeringsspråk: Python, TypeScript, JavaScript, Rust, Java
    - AI / ML & Data Science: JAX/Flax, PyTorch, Computer Vision (objektdeteksjon/sporing), LLM-integrasjoner, Azure Foundry
    - Web & Frontend: React, Next.js, Node.js, REST, GraphQL, HTML/CSS
    - Databaser & Verktøy: SQLite, MongoDB, Git, Vercel, macOS/Linux
    - Annet: Web scraping, undervisning/mentoring (læringsassistent), algoritmer og problemløsning, skybaserte løsninger (Azure)

    Evaluering:
    1. Er stillingen en junior/graduate-rolle? (0 = nei, 1 = ja)
    2. Hvor godt matcher utlysningen kandidatens ferdigheter? Gi en score fra 1 til 10.
       - High score (8-10): Krever Python, AI/ML, React/TypeScript, eller generell fullstack for nyutdannede.
       - Mid score (5-7): Relevant IT/utvikler-rolle, men krever teknologier kandidaten må lære seg på jobben (f.eks. C#, Java/Spring, Docker/Kubernetes).
       - Low score (1-4): Krever mange års erfaring, feil fagfelt (f.eks. ren embedded C, data warehouse), eller ledelsesansvar.

    Utlysningstekst:
    {job_text}
"""

ola_finn_junior = FinnScraper(db_path="db/ola_jobs.db", digest=ola_discord_digest)


# Configure the scraper and digest mechanism - PETER
peter_discord_digest = DiscordDigest(
    webhook_url=os.getenv("PETER_DISCORD_WEBHOOK_URL"),
    db_path="db/peter_jobs.db",
    min_score=5,
    max_jobs=10,
)

peter_skip_words = skip_words = [
    "senior",
    "lead",
    "principal",
    "head of",
    "director",
    "arkitekt",
    "manager",
    "summer",
    "sommer",
    "sommerjobb",
    "revisor",
    "sjef",
    "leder",
    "regnskapssjef",
    "økonomisjef",
    "jurist",
    "advokat",
]

peter_start_url = "https://www.finn.no/job/search?job_duration=3951&location=1.20001.20061&occupation=0.12&occupation=0.25&occupation=0.48&occupation=0.51&occupation=0.68&sort=PUBLISHED_DESC"

peter_prompt_template = """
    Analyser følgende stillingsutlysning og vurder om dette er en junior- eller graduate-stilling.

    Vurderingene skal baseres på følgende kriterier:
    - Maksimal erfaring: {max_experience_years} år
    - Target roller: {target_roles} (f.eks. Junior prosjektleder, Prosjektkoordinator, IT-konsulent, Trainee innen ledelse/teknologi)

    Kandidatens profil:
    - Bakgrunn: Utdanning innen Ledelse og Teknologi (prosjektledelse, prosessoptimalisering, IT-strategi, teknologiforståelse).
    - Hovedinteresse: Romfart (space), satelitteknologi, aerospace, forsvar og dyp-teknologi (deep tech).
    - Ønskede oppgaver: Prosjektledelse, prosjektkoordinering, organisering og skjæringspunktet mellom teknologi og ledelse.

    Evaluering og poenggiving (score 1-10):
    - Score 9-10 (Drømmematch): Utlysningen gjelder romfart/space/aerospace ELLER avansert dyp-teknologi, OG er en junior/entry-level prosjektleder- eller koordinatorrolle.
    - Score 7-8 (Sterk match): Junior prosjektleder, prosjektkoordinator, trainee eller junior management/IT-konsulent i andre teknologiselskaper (selv utenfor romfart).
    - Score 4-6 (Middels match): Generell teknologi- eller forretningsrolle med innslag av koordinering, men uten tydelig fokus på prosjektledelse.
    - Score 1-3 (Dårlig match): Krever mer enn {max_experience_years} års erfaring, eller er en ren tung spesialiststilling (f.eks. ren programmering/hardware uten ledelseselementer).

    VIKTIG ERFARINGSREGEL:
    Dersom stillingen krever mer enn {max_experience_years} års erfaring, skal den IKKE regnes som junior, og scoren skal være lav selv om selskapet driver med romfart.

    Utlysningstekst:
    {text}
"""

peter_finn_junior = FinnScraper(
    db_path="db/peter_jobs.db",
    start_url=peter_start_url,
    digest=peter_discord_digest,
    skip_words=peter_skip_words,
    prompt_template=peter_prompt_template,
)


def main():
    ola_finn_junior.run()
    ola_finn_junior.send_digest()

    # peter_finn_junior.run()
    # peter_finn_junior.send_digest()


main()
