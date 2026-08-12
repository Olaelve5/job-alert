from agent import init_db
from dotenv import load_dotenv
from profiles.ola import OlaProfile
from profiles.peter import PeterProfile
from send_deadlines import send_for_profile

load_dotenv()

init_db(db_path="db/ola_jobs.db")
init_db(db_path="db/peter_jobs.db")

ola_profile = OlaProfile()
peter_profile = PeterProfile()

ola_finn_junior = ola_profile.create_scraper()
peter_finn_junior = peter_profile.create_scraper()


# Sends deadline alerts for both profiles (Ola and Peter) via Discord.
def send_deadline_alerts():
    send_for_profile(ola_profile, days=3, dry_run=False)
    send_for_profile(peter_profile, days=3, dry_run=False)

# Scans for new jobs for both profiles (Ola and Peter) and saves them to their respective databases.
def scan_for_jobs():
    ola_finn_junior.run()
    peter_finn_junior.run()

# Sends job digests for both profiles (Ola and Peter) via Discord.
def send_digests():
    ola_finn_junior.send_digest()
    peter_finn_junior.send_digest()
