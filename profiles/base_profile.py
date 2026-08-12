import os
from typing import List, Optional, Dict, Any

from scrapers.finn_scraper import FinnScraper
from digesters.discord_digest import DiscordDigest


class BaseProfile:
    """Capture profile-specific settings and provide factory helpers.

    Subclass or instantiate with values for `name`, `db_path`, `start_url`,
    `skip_words`, and `prompt_template`. Use `create_scraper()` to get a
    configured `FinnScraper` instance.
    """

    name: str = "base"
    db_path: str = "db/jobs.db"
    start_url: Optional[str] = None
    skip_words: Optional[List[str]] = None
    prompt_template: Optional[str] = None
    min_score: int = 6
    max_jobs: int = 10

    def __init__(
        self,
        name: Optional[str] = None,
        db_path: Optional[str] = None,
        start_url: Optional[str] = None,
        skip_words: Optional[List[str]] = None,
        prompt_template: Optional[str] = None,
        min_score: Optional[int] = None,
        max_jobs: Optional[int] = None,
    ) -> None:
        if name:
            self.name = name
        if db_path:
            self.db_path = db_path
        if start_url:
            self.start_url = start_url
        if skip_words is not None:
            self.skip_words = skip_words
        if prompt_template is not None:
            self.prompt_template = prompt_template
        if min_score is not None:
            self.min_score = min_score
        if max_jobs is not None:
            self.max_jobs = max_jobs

    def create_digest(self) -> DiscordDigest:
        webhook_env = f"{self.name.upper()}_DISCORD_WEBHOOK_URL"
        webhook_url = os.getenv(webhook_env)
        return DiscordDigest(
            webhook_url=webhook_url,
            db_path=self.db_path,
            min_score=self.min_score,
            max_jobs=self.max_jobs,
        )

    def create_scraper(self) -> FinnScraper:
        digest = self.create_digest()
        scraper = FinnScraper(
            db_path=self.db_path,
            start_url=self.start_url,
            skip_words=self.skip_words,
            prompt_template=self.prompt_template,
            digest=digest,
            name=self.name,
        )
        return scraper
