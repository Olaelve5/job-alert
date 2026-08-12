import os
from scrapers.finn_scraper import FinnScraper
from digesters.discord_digest import DiscordDigest
from agent import init_db

from dotenv import load_dotenv

load_dotenv()

init_db(db_path="db/ola_jobs.db")
#init_db(db_path="db/peter_jobs.db")

# Profiles
from profiles.ola import OlaProfile
from profiles.peter import PeterProfile

ola_profile = OlaProfile()
peter_profile = PeterProfile()

ola_finn_junior = ola_profile.create_scraper()
peter_finn_junior = peter_profile.create_scraper()


def main():
    #ola_finn_junior.run()
    # peter_finn_junior.run()

    #ola_finn_junior.send_digest()
    # peter_finn_junior.send_digest()


main()
