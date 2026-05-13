import re


GEOMETRY_AFFECTING_PARTS = [
    "frame rail", "rail", "radiator support", "core support", "apron",
    "unibody", "rear body panel", "quarter panel", "floor pan",
    "rear panel", "body panel", "rocker panel", "pillar",
    "bumper reinforcement", "reinforcement", "impact bar",
    "suspension", "control arm", "strut", "knuckle",
    "tie rod", "steering rack", "crossmember", "subframe"
]

SENSOR_ADJACENT_PARTS = [
    "bumper", "grille", "windshield", "mirror", "tailgate",
    "liftgate", "quarter panel", "door", "park sensor",
    "parking sensor", "radar", "camera", "blind spot",
    "lane change", "sensor bracket"
]

STRUCTURAL_WORDS = [
    "section", "weld", "pull", "measure", "straighten",
    "replace", "r&r", "r&i", "repair", "frame",
    "structural", "blend", "refinish"
]


def classify_repair_operations(estimate_text: str):
    text = estimate_text.lower()
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    classifications = []

    for line in lines:
        severity = "LOW"
        flags = []

        if any(part in line for part in GEOMETRY_AFFECTING_PARTS):
            severity = "HIGH"
            flags.append("geometry_affecting")

        if any(part in line for part in SENSOR_ADJACENT_PARTS):
            flags.append("sensor_adjacent")

        if any(word in line for word in STRUCTURAL_WORDS):
            flags.append("repair_operation")

        if "refinish" in line and not any(x in flags for x in ["geometry_affecting", "sensor_adjacent"]):
            severity = "LOW"

        if "replace" in line or "r&r" in line or "section" in line or "weld" in line:
            if "geometry_affecting" in flags or "sensor_adjacent" in flags:
                severity = "HIGH"

        if "repair" in line and ("geometry_affecting" in flags or "sensor_adjacent" in flags):
            severity = "MODERATE"

        if flags:
            classifications.append({
                "line": line,
                "severity": severity,
                "flags": flags
            })

    return classifications