from .base_profile import BaseProfile


class OlaProfile(BaseProfile):
    def __init__(self):
        super().__init__(
            name="ola",
            db_path="db/ola_jobs.db",
            start_url="https://www.finn.no/job/search?job_duration=3951&location=2.20001.20016.20318&location=2.20001.20012.20203&location=2.20001.20012.20196&location=1.20001.20061&occupation=0.23&sort=PUBLISHED_DESC",
            skip_words=[
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
            ],
            prompt_template="""
                    Analyser følgende stillingsutlysning og vurder om dette er en junior- eller graduate-stilling.

                    Vurderingene skal baseres på følgende kriterier:
                    - Maksimal erfaring: {max_experience_years} år
                    - Target roller: {target_roles}
                    - MERK: Norske stillingsutlysninger oppgir nesten alltid 'Tiltredelse: Etter avtale' eller 'Snarest'. Dersom det ikke står en konkret, eksplisitt dato for oppstart, SKAL start_date settes til null.
                    
                    Kandidatens ferdighetsprofil:
                    - Programmeringsspråk: Python, TypeScript, JavaScript, Rust, Java
                    - AI / ML & Data Science: JAX/Flax, PyTorch, Computer Vision (objektdeteksjon/sporing), LLM-integrasjoner, Azure Foundry
                    - Web & Frontend: React, Next.js, Node.js, REST, GraphQL, HTML/CSS
                    - Databaser & Verktøy: SQLite, MongoDB, Git, Vercel, macOS/Linux
                    - Annet: Web scraping, undervisning/mentoring (læringsassistent), algoritmer og problemløsning, skybaserte løsninger (Azure), Bygging av agenter og automatisering

                    Evaluering:
                    1. Er stillingen en junior/graduate-rolle? (0 = nei, 1 = ja)
                    2. Hvor godt matcher utlysningen kandidatens ferdigheter? Gi en score fra 1 til 10.
                    - High score (8-10): Krever Python, AI/ML, React/TypeScript, eller generell fullstack for nyutdannede.
                    - Mid score (5-7): Relevant IT/utvikler-rolle, men krever teknologier kandidaten må lære seg på jobben (f.eks. C#, Java/Spring, Docker/Kubernetes).
                    - Low score (1-4): Krever mange års erfaring, feil fagfelt (f.eks. ren embedded C, data warehouse), eller ledelsesansvar.

                    Oppstartspreferanse:
                    - Gi høyere score dersom stillingen uttrykkelig oppgir oppstart sommer eller høst 2027.
                    - Gi lavere score dersom oppstart beskrives som "snarest", "umiddelbart", eller i nærmeste framtid.

                    Utlysningstekst:
                    {text}
                """,
            min_score=5,
            max_jobs=10,
        )
