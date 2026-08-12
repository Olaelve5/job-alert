from .base_profile import BaseProfile


class PeterProfile(BaseProfile):
    def __init__(self):
        peter_skip_words = [
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

        peter_prompt_template = """
                Analyser følgende stillingsutlysning og vurder om dette er en junior- eller graduate-stilling.

                Vurderingene skal baseres på følgende kriterier:
                - Maksimal erfaring: {max_experience_years} år
                - Target roller: {target_roles} (f.eks. Junior prosjektleder, Prosjektkoordinator, IT-konsulent, Trainee innen ledelse/teknologi)
                - MERK: Norske stillingsutlysninger oppgir nesten alltid 'Tiltredelse: Etter avtale' eller 'Snarest'. Dersom det ikke står en konkret, eksplisitt dato for oppstart, SKAL start_date settes til null.

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

                Oppstartspreferanse:
                - Foretrekk stillinger med uttrykt oppstart sommer eller høst 2027 ved å gi dem høyere score.
                - Reduser scoren for stillinger som annonserer oppstart "snarest", "umiddelbart" eller i nærmeste framtid.

                Utlysningstekst:
                {text}
            """

        super().__init__(
            name="peter",
            db_path="db/peter_jobs.db",
            start_url="https://www.finn.no/job/search?job_duration=3951&location=1.20001.20061&occupation=0.12&occupation=0.25&occupation=0.48&occupation=0.51&occupation=0.68&sort=PUBLISHED_DESC",
            skip_words=peter_skip_words,
            prompt_template=peter_prompt_template,
            min_score=5,
            max_jobs=10,
        )
