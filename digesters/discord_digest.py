import os
import requests
from typing import Optional
from digesters.digest import BaseDigest


class DiscordDigest(BaseDigest):
    """Sends formatted job alerts to a specific Discord webhook."""

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        webhook_env_var: str = "DISCORD_WEBHOOK_URL",
        db_path: str = "jobs.db",
        min_score: int = 6,
        header_title: str = "🌅 **Morning Job Digest**",
        max_jobs: int = 10,
    ):
        super().__init__(db_path=db_path, min_score=min_score, max_jobs=max_jobs)

        # Resolve webhook URL either directly or from an environment variable
        self.webhook_url = webhook_url or os.environ.get(webhook_env_var)
        self.header_title = header_title

        if not self.webhook_url:
            raise ValueError(
                f"Discord Webhook URL not found. Provide `webhook_url` or set `{webhook_env_var}` in your .env file."
            )

    def send(self) -> None:
        jobs = self.get_unnotified_jobs(max_jobs=self.max_jobs)

        if not jobs:
            print(
                f"[{self.__class__.__name__}] No new jobs found (min_score >= {self.min_score})."
            )
            return

        print(
            f"[{self.__class__.__name__}] Sending {len(jobs)} job alerts to Discord..."
        )

        embeds = []
        for job in jobs:
            if len(embeds) >= self.max_jobs:
                print(
                    f"Reached max_jobs limit ({self.max_jobs}). Stopping further job embeds."
                )
                break

            # Green border for score >= 8, Orange for 6-7
            color = 3066993 if job["score"] >= 8 else 15105570

            # helper to read field from sqlite3.Row or dict-like
            def _read_field(j, field, fallback=None):
                if hasattr(j, "get"):
                    val = j.get(field)
                    return val if val else fallback
                if hasattr(j, "keys") and field in j.keys():
                    val = j[field]
                    return val if val else fallback
                return fallback

            deadline = _read_field(job, "deadline", "Snarest")
            start_date_val = _read_field(job, "start_date", "Not specified")
            location_val = _read_field(job, "location", "Not specified")

            tech_stack_val = _read_field(job, "tech_stack", "Not specified")

            embeds.append(
                {
                    "title": f"🎯 [{job['score']}/10] {job['title']} @ {job['company']}",
                    "url": job["url"],
                    "color": color,
                    "fields": [
                        {"name": "⏰ Frist", "value": deadline, "inline": False},
                        {
                            "name": "🚀 Oppstart",
                            "value": start_date_val,
                            "inline": False,
                        },
                        {
                            "name": "💻 Tech Stack",
                            "value": tech_stack_val,
                            "inline": False,
                        },
                        {
                            "name": "📝 Summary",
                            "value": job["summary"],
                            "inline": False,
                        },
                        {
                            "name": "📍 Location",
                            "value": location_val,
                            "inline": False,
                        },
                    ],
                }
            )

        # Discord accepts up to 10 embeds per POST request
        for chunk in [embeds[i : i + 10] for i in range(0, len(embeds), 10)]:
            payload = {
                "content": f"{self.header_title} ({len(jobs)} new match{'es' if len(jobs) > 1 else ''}):",
                "embeds": chunk,
            }
            res = requests.post(self.webhook_url, json=payload)

            if res.status_code not in [200, 204]:
                print(f"Failed to post to Discord: {res.status_code} - {res.text}")
                return

        sent_ids = [job["job_id"] for job in jobs]
        self.mark_as_notified(sent_ids)
        print("Done! All jobs sent and updated in database.")
