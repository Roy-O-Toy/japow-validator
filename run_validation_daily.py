"""
run_validation_daily.py
Schedules and runs resort data validation daily using validator module.
"""

import schedule
import time
from datetime import datetime
import os

# from validator import ResortValidator
# Simple inline validator for now
class ResortValidator:
    def validate(self):
        print("Validating resort data...")
        # Add minimal schema checks here later
        return True

DATA_PATH = "sample_resorts.json"

# Ensure logs folder exists
if not os.path.exists("logs"):
    os.makedirs("logs")

def job():
    log = ResortValidator.run_validation(DATA_PATH, source_type="official")
    valid_count = sum(1 for entry in log if entry['validation_status'] == 'valid')
    warn_count = sum(1 for entry in log if entry['reliability_score'] < 0.75)
    print(f"Validation completed: [{len(log)} resorts checked], [{valid_count} valid], [{warn_count} warnings]")

schedule.every().day.at("00:00").do(job)

if __name__ == "__main__":
    print(f"[{datetime.now()}] Resort validation scheduler started.")
    while True:
        schedule.run_pending()
        time.sleep(60)
