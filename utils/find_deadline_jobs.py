#!/usr/bin/env python3
import argparse
import sqlite3
import json
from datetime import date, timedelta


def find_deadline_jobs(db_path: str, days: int = 3):
    today = date.today()
    end_date = today + timedelta(days=days)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT job_id, title, company, deadline, url
        FROM jobs
        WHERE deadline IS NOT NULL
          AND deadline != ''
          AND date(deadline) BETWEEN ? AND ?
          AND is_junior = 1
        ORDER BY date(deadline) ASC
        """,
        (today.isoformat(), end_date.isoformat()),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def main():
    p = argparse.ArgumentParser(
        description="Find jobs with deadlines within the next N days."
    )
    p.add_argument(
        "db", nargs="?", default="db/peter_jobs.db", help="Path to SQLite DB"
    )
    p.add_argument("--days", "-n", type=int, default=3, help="Lookahead in days")
    p.add_argument("--json", action="store_true", help="Emit JSON output")
    args = p.parse_args()

    results = find_deadline_jobs(args.db, args.days)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print("No jobs found with deadlines in the next", args.days, "days.")
            return
        for r in results:
            print(
                f"{r.get('deadline')}  {r.get('job_id')}  {r.get('title') or '-'}  {r.get('company') or '-'}  {r.get('url') or '-'}"
            )


if __name__ == "__main__":
    main()
