# Job Agent 🔎🤖

> A tiny, profile-driven job scraping and digesting tool that analyzes job postings with Google Gemini and posts curated alerts to Discord.

---

## ✨ What it does

- Scrapes job listings (currently FINN) using profile-specific search URLs.
- Sends each posting to an LLM (Google Gemini) for structured analysis (junior-match, score, tech-stack, summary, deadline, start date).
- Persists results per-profile into SQLite (db/ola_jobs.db, db/peter_jobs.db).
- Posts digest messages and deadline alerts to Discord webhooks.

---

## 🧭 Quick start

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

3. Provide secrets (example `.env`):

```
GEMINI_API_KEY=your_gemini_api_key
OLA_DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
PETER_DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

4. Run the scraper once:

```bash
python main.py
```

5. Send deadline alerts (dry-run first):

```bash
python send_deadlines.py --days 3 --dry-run
python send_deadlines.py --days 3
```

---

## 🛠️ Files & Structure

- `main.py` — orchestrates profiles, scrapers and digests.
- `profiles/` — profile classes (`OlaProfile`, `PeterProfile`) with per-user settings.
- `scrapers/` — scraper implementations (FINN-specific parser + base class).
- `agent.py` — LLM client, schema, DB helpers.
- `digesters/discord_digest.py` — formats and posts Discord embeds, includes `send_deadlines`.
- `utils/find_deadline_jobs.py` — helper to query upcoming deadlines.
- `send_deadlines.py` — CLI to send deadline alerts for Ola and Peter.

---

## ✅ Notes & Troubleshooting

- The LLM integration uses `google.genai` and expects `GEMINI_API_KEY` in the environment.
- SQLite `deadline` values should be ISO dates (`YYYY-MM-DD`) for deadline queries to work.
- If pip installs fail with macOS SSL errors in the sandbox, run the `pip install` commands locally outside the sandbox or fix system certs.
- If you see `no such table: jobs`, run `main.py` or call `init_db()` to create the schema for the configured DB path.
