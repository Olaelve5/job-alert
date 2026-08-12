#!/usr/bin/env python3
"""Send imminent-deadline job alerts for Ola and Peter via Discord.

This script uses the profile classes to build `DiscordDigest` instances
and calls their `send_deadlines` helper which posts deadline alerts.
"""

import argparse
import os
from profiles.ola import OlaProfile
from profiles.peter import PeterProfile


def send_for_profile(profile, days: int = 3, dry_run: bool = False):
    digest = profile.create_digest()
    if dry_run:
        # Show which DB and days would be used
        from utils.find_deadline_jobs import find_deadline_jobs

        jobs = find_deadline_jobs(db_path=profile.db_path, days=days)
        if not jobs:
            print(f"[{profile.name}] No deadline jobs in next {days} days.")
            return
        print(f"[{profile.name}] Would send {len(jobs)} deadline alerts:")
        for j in jobs:
            print(
                f"  {j['deadline']}  {j['job_id']}  {j.get('title') or '-'}  {j.get('company') or '-'}"
            )
        return

    print(
        f"[{profile.name}] Sending deadline alerts (db={profile.db_path}, days={days})"
    )
    digest.send_deadlines(db_path=profile.db_path, days=days)


def main():
    p = argparse.ArgumentParser(
        description="Send job deadline alerts to Ola and Peter."
    )
    p.add_argument("--days", "-n", type=int, default=3, help="Lookahead in days")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't post to Discord; just show matches",
    )
    args = p.parse_args()

    # Ensure env is loaded by user (GEMINI_API_KEY and webhook URLs expected in .env)
    ola = OlaProfile()
    peter = PeterProfile()

    send_for_profile(ola, days=args.days, dry_run=args.dry_run)
    send_for_profile(peter, days=args.days, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
