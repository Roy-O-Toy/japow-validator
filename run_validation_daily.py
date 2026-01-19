print("✅ The script started running")
"""
run_validation_daily.py
Runs resort data validation once using validator module.
"""

from datetime import datetime
import os

# Simple inline validator for now
class ResortValidator:
    def run_validation(self, data_path, source_type="official"):
        print("Validating resort data...")
        # Dummy sample log data
        log = [
            {"resort_name": "Niseko United", "validation_status": "valid", "reliability_score": 0.9},
            {"resort_name": "Hakuba Valley", "validation_status": "valid", "reliability_score": 0.85},
            {"resort_name": "Zao Onsen", "validation_status": "valid", "reliability_score": 0.8},
        ]
        return log

DATA_PATH = "sample_resorts.json"

# Ensure logs folder exists
if not os.path.exists("logs"):
    os.makedirs("logs")

def job():
    validator = ResortValidator()
    log = validator.run_validation(DATA_PATH, source_type="official")
    valid_count = sum(1 for entry in log if entry['validation_status'] == 'valid')
    warn_count = sum(1 for entry in log if entry['reliability_score'] < 0.75)
    print(f"Validation completed: [{len(log)} resorts checked], [{valid_count} valid], [{warn_count} warnings]")

if __name__ == "__main__":
    print(f"[{datetime.now()}] Resort validation started.")
    job()
    print("✅ The script finished running")
