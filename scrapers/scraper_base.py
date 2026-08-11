from typing import Any, Dict, List, Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
import requests
from agent import process_job, is_already_seen
from digesters.digest import BaseDigest


class ScraperBase:
    """Single base class for job scrapers.

    Define defaults on the class, or override them when instantiating.
    Subclasses only need to implement `parse_list()` and `parse_detail()`.
    """

    # --- Core Configuration ---
    name: str = "base"
    start_url: Optional[str] = None
    db_path: str = "jobs.db"
    max_pages: int = 10

    # Quick title filtering before wasting HTTP/LLM calls
    skip_words: List[str] = [
        "senior",
        "lead",
        "principal",
        "head of",
        "director",
        "arkitekt",
        "manager",
    ]

    # Prompt template and custom agent rules
    demands: Dict[str, Any] = {
        "max_experience_years": 2,
        "target_roles": "Junior / Graduate / Trainee",
    }

    prompt_template: str = """
    Analyser følgende stillingsutlysning og vurder om dette er en junior- eller graduate-stilling.

    Vurderingene skal baseres på følgende kriterier:
    - Maksimal erfaring: {max_experience_years} år
    - Target roller: {target_roles}

    Utlysningstekst:
    {text}
    """

    # HTTP settings
    headers: Dict[str, str] = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/127.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "nb-NO,nb;q=0.9,no;q=0.8,nn;q=0.7,en-US;q=0.6,en;q=0.5",
        "Cache-Control": "max-age=0",
    }
    timeout: int = 10

    def __init__(
        self,
        name: Optional[str] = None,
        start_url: Optional[str] = None,
        db_path: Optional[str] = None,
        skip_words: Optional[List[str]] = None,
        demands: Optional[Dict[str, Any]] = None,
        prompt_template: Optional[str] = None,
        digest: Optional[BaseDigest] = None,
    ) -> None:
        if name:
            self.name = name
        if start_url:
            self.start_url = start_url
        if db_path:
            self.db_path = db_path
        if skip_words is not None:
            self.skip_words = skip_words
        if demands is not None:
            self.demands = demands
        if prompt_template:
            self.prompt_template = prompt_template
        if digest:
            self.digest = digest

    # --- Helper Methods ---

    def is_obviously_irrelevant(self, title: str) -> bool:
        """Returns True if the title contains any of the skip_words."""
        title_lower = title.lower()
        return any(word.lower() in title_lower for word in self.skip_words)

    def build_prompt(self, text: str) -> str:
        """Formats the prompt using demands and the job text."""
        context = dict(self.demands or {})
        context["text"] = text
        try:
            return self.prompt_template.format(**context)
        except KeyError:
            return self.prompt_template.replace("{text}", text)

    def fetch(self, url: str) -> str:
        """Fetches raw HTML from a URL."""
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text

    def get_page_url(self, page: int) -> str:
        """Appends or updates the page parameter in the search URL."""
        if page == 1:
            return self.start_url

        url_parts = list(urlparse(self.start_url))
        # parse_qsl maintains duplicate keys (e.g. multiple location= params)
        query_pairs = parse_qsl(url_parts[4], keep_blank_values=True)

        # Remove existing page param if present, then add current page
        query_pairs = [(k, v) for k, v in query_pairs if k != "page"]
        query_pairs.append(("page", str(page)))

        url_parts[4] = urlencode(query_pairs)
        return urlunparse(url_parts)

    # --- Methods to Override in Subclasses ---

    def parse_list(self, html: str) -> List[Dict[str, str]]:
        """Extract job listings from search page HTML.
        Must return a list of dicts: [{'id': '123', 'url': 'https://...', 'title': '...'}, ...]
        """
        raise NotImplementedError("Subclasses must implement `parse_list()`")

    def parse_detail(self, html: str) -> str:
        """Extract main posting body text from individual job page HTML."""
        raise NotImplementedError("Subclasses must implement `parse_detail()`")

    # --- Execution Loop ---

    def find_candidates(self) -> List[Dict[str, str]]:
        """Fetches search pages and returns a list of candidate job postings."""
        if not self.start_url:
            raise ValueError(f"[{self.name}] start_url is not configured!")

        candidates: List[Dict[str, str]] = []

        for page in range(1, self.max_pages + 1):
            url = self.get_page_url(page)
            print(f"\n📄 Fetching search page {page}: {url}")

            search_html = self.fetch(url)
            page_candidates = self.parse_list(search_html)
            if not page_candidates:
                print(
                    f"No listings found on search page {page}. Stopping further pages."
                )
                break

            print(f"Found {len(page_candidates)} listings on search page.")

            candidates.extend(page_candidates)

        return candidates

    def run(self) -> None:
        """Runs the entire pipeline for this scraper instance."""
        if not self.start_url:
            raise ValueError(f"[{self.name}] start_url is not configured!")

        candidates = self.find_candidates()

        for job in candidates:
            job_id = f"{self.name}_{job['id']}"
            job_url = job["url"]
            title = job.get("title", "")

            # 2. Check DB if already processed
            if is_already_seen(job_id, db_path=self.db_path):
                continue

            # 3. Check skipwords
            if title and self.is_obviously_irrelevant(title):
                print(f"Skipping (matches skip_words): {title}")
                continue

            # 4. Fetch detail page & parse text
            print(f"Fetching detail text for: {job_id}")
            detail_html = self.fetch(job_url)
            job_text = self.parse_detail(detail_html)

            if not job_text:
                continue

            # 5. Build prompt with custom demands & send to Gemini/DB
            prompt = self.build_prompt(job_text)
            process_job(
                job_id=job_id,
                job_url=job_url,
                job_text=job_text,
                prompt_override=prompt,
                db_path=self.db_path,
            )

    def send_digest(self) -> None:
        """Sends a digest of unnotified jobs via the configured digest mechanism."""
        if not hasattr(self, "digest") or not self.digest:
            print(f"[{self.name}] No digest mechanism configured. Skipping digest.")
            return

        print(f"[{self.name}] Sending job digest...")
        self.digest.send()
