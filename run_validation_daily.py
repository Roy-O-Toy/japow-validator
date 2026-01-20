"""
run_validation_daily.py
Runs Japow-validator against the real resorts dataset.
This script is intended to be executed by GitHub Actions.
"""

from datetime import datetime
import os

from validator import ResortValidator

# 🔧 IMPORTANT: This must point to your real dataset
DATA_PATH = "resorts_master.json"

# Ensure logs folder exists
if not os.path.exists("logs"):
    os.makedirs("logs")

def job():
    print("🧭 Starting Japow resort validation run...")

    # Run the REAL validator
    log = ResortValidator.run_validation(
        file_path=DATA_PATH,
        source_type="official"
    )

    print(f"✅ Validation completed for {len(log)} resorts")

    # Summary output (used by GitHub Actions logs)
    valid_count = sum(
        1 for entry in log if entry["validation_status"] == "valid"
    )
    warning_count = sum(
        1 for entry in log if entry["reliability_score"] < 0.75
    )

    print(
        f"📊 Summary: "
        f"{len(log)} checked | "
        f"{valid_count} valid | "
        f"{warning_count} warnings"
    )

    return log

if __name__ == "__main__":
    print(f"[{datetime.utcnow().isoformat()}Z] Validator run started")
    job()
    print("🏁 Validator run finished")
