import csv
from pathlib import Path
from datetime import datetime

from app.dtc_library import is_known_dtc

UNKNOWN_FILE = Path("unknown_dtcs.csv")


def track_unknown_dtcs(data):
    vehicle_info = data.get("vehicle_info", {})
    intake = data.get("intake", {})
    dtcs = data.get("dtcs", [])

    rows_to_add = []

    for d in dtcs:
        code = d.get("code", "").upper()
        module = d.get("module", "Unknown Module")
        description = d.get("description", "")

        if not code:
            continue

        if is_known_dtc(code):
            continue

        rows_to_add.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "vehicle": vehicle_info.get("vehicle", "Not detected"),
            "vin": vehicle_info.get("vin", "Not detected"),
            "make_model": vehicle_info.get("vehicle", "Not detected"),
            "ro_number": intake.get("ro_number", "Not provided"),
            "impact_area": intake.get("impact_area", "Not specified"),
            "module": module,
            "code": code,
            "description": description,
            "reviewed": "no",
            "meaning": "",
            "possible_causes": "",
            "recommended_fixes": "",
            "adas_impact": ""
        })

    if not rows_to_add:
        return 0

    file_exists = UNKNOWN_FILE.exists()

    fieldnames = [
        "timestamp",
        "vehicle",
        "vin",
        "make_model",
        "ro_number",
        "impact_area",
        "module",
        "code",
        "description",
        "reviewed",
        "meaning",
        "possible_causes",
        "recommended_fixes",
        "adas_impact"
    ]

    existing_keys = set()

    if file_exists:
        with open(UNKNOWN_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_keys.add(
                    (
                        row.get("vin", ""),
                        row.get("module", ""),
                        row.get("code", "")
                    )
                )

    new_rows = []

    for row in rows_to_add:
        key = (row["vin"], row["module"], row["code"])
        if key not in existing_keys:
            new_rows.append(row)

    if not new_rows:
        return 0

    with open(UNKNOWN_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerows(new_rows)

    return len(new_rows)