from bs4 import BeautifulSoup
from scrapers.scraper_base import ScraperBase


class FinnScraper(ScraperBase):
    name = "finn"
    start_url = (
        "https://www.finn.no/job/search?"
        "job_duration=3951"
        "&location=2.20001.20016.20318"
        "&location=2.20001.20012.20203"
        "&location=2.20001.20012.20196"
        "&location=1.20001.20061"
        "&occupation=0.23"
        "&sort=PUBLISHED_DESC"
    )
    max_pages = 1

    skip_words = [
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
    ]

    def parse_list(self, html: str) -> list[dict[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        candidates = []

        for card in soup.find_all("article"):
            link = card.find("a", href=True)
            if not link:
                continue

            url = link["href"]
            if not url.startswith("http"):
                url = f"https://www.finn.no{url}"

            raw_id = (
                url.split("finnkode=")[-1].split("&")[0]
                if "finnkode=" in url
                else url.rstrip("/").split("/")[-1]
            )
            title = card.get_text(strip=True)

            candidates.append({"id": raw_id, "url": url, "title": title})

        return candidates

    def parse_detail(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        section = soup.find("section", {"class": "import-decoration"}) or soup.find(
            "main"
        )
        return section.get_text(separator="\n", strip=True) if section else ""
