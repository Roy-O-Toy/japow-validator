"""
validator.py
Core validation engine for Japow Insider Guide.
Validates resort data and produces reliability-scored output.
"""

import json
import os
from datetime import datetime, timedelta

VALID_REGIONS = {"Hokkaido", "Nagano", "Niigata", "Tohoku"}

class ResortValidator:

    @staticmethod
    def _parse_iso(ts: str):
        try:
            return datetime.fromisoformat(ts.replace("Z", ""))
        except Exception:
            return None

    @staticmethod
    def _recency_weight(verified_at: datetime) -> float:
        if not verified_at:
            return 0.0
        age = datetime.utcnow() - verified_at
        if age <= timedelta(hours=24):
            return 1.0
        elif age <= timedelta(hours=72):
            return 0.8
        else:
            return 0.6

    @staticmethod
    def _completeness_weight(entry: dict) -> float:
        required = [
            "resort_name",
            "region",
            "elevation_m",
            "terrain_mix",
            "avg_snowfall_cm",
            "english_support",
            "last_verified",
        ]
        present = sum(1 for f in required if entry.get(f) not in (None, ""))
        return present / len(required)

    @staticmethod
    def _validate_entry(entry: dict):
        issues = []

        if not entry.get("resort_name"):
            issues.append("Missing resort_name")

        if entry.get("region") not in VALID_REGIONS:
            issues.append("Invalid or missing region")

        try:
            elev = float(entry.get("elevation_m", 0))
            if not (100 <= elev <= 2500):
                issues.append("elevation_m out of range")
        except Exception:
            issues.append("Invalid elevation_m")

        try:
            snow = float(entry.get("avg_snowfall_cm", 0))
            if not (100 <= snow <= 2000):
                issues.append("avg_snowfall_cm out of range")
        except Exception:
            issues.append("Invalid avg_snowfall_cm")

        try:
            eng = int(entry.get("english_support", 0))
            if not (1 <= eng <= 5):
                issues.append("english_support out of range")
        except Exception:
            issues.append("Invalid english_support")

        verified_at = ResortValidator._parse_iso(entry.get("last_verified", ""))

        return issues, verified_at

    @staticmethod
    def run_validation(file_path: str, source_type: str = "official"):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")

        with open(file_path, "r") as f:
            data = json.load(f)

        results = []

        source_weight = 1.0 if source_type == "official" else 0.7

        for entry in data:
            issues, verified_at = ResortValidator._validate_entry(entry)

            recency_weight = ResortValidator._recency_weight(verified_at)
            completeness_weight = ResortValidator._completeness_weight(entry)

            reliability = round(
                0.4 * source_weight
                + 0.4 * recency_weight
                + 0.2 * completeness_weight,
                2,
            )

            status = "valid" if not issues else "invalid"

            results.append({
                "resort_name": entry.get("resort_name", "UNKNOWN"),
                "validation_status": status,
                "reliability_score": reliability,
                "validator_verified_at": (
                    verified_at.isoformat() + "Z" if verified_at else None
                ),
            })

        # Hard guardrail: prevent publishing demo-sized output
        if len(results) < 5:
            raise RuntimeError(
                "Validator returned too few resorts — refusing to publish."
            )

        return results
