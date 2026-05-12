import re


ESTIMATE_TRIGGER_RULES = {
    "front_bumper": {
        "keywords": ["front bumper", "bumper cover", "front cover", "front fascia", "grille", "radiator support"],
        "recommendations": [
            "Front bumper/grille repair detected: inspect radar mounting, camera view path, sensor brackets, and aiming surfaces.",
            "Forward radar aiming/calibration review recommended if bumper, grille, radar bracket, or front structure was affected."
        ]
    },
    "windshield_camera": {
        "keywords": ["windshield", "glass", "camera bracket", "rain sensor", "mirror bracket"],
        "recommendations": [
            "Windshield/glass operation detected: forward camera calibration review recommended.",
            "Verify camera bracket, mounting position, and camera view path."
        ]
    },
    "suspension_alignment": {
        "keywords": ["alignment", "suspension", "control arm", "strut", "knuckle", "tie rod", "steering rack"],
        "recommendations": [
            "Suspension/steering operation detected: steering angle sensor and alignment verification recommended.",
            "Lane keeping and stability control systems may require validation after alignment/steering repairs."
        ]
    },
    "rear_bumper": {
        "keywords": ["rear bumper", "rear cover", "rear fascia", "liftgate", "tailgate"],
        "recommendations": [
            "Rear bumper/rear body repair detected: parking aid and rear camera verification recommended.",
            "Inspect rear body harness, parking sensors, rear camera, and blind spot radar areas."
        ]
    },
    "quarter_panel_blindspot": {
        "keywords": ["quarter panel", "blind spot", "side object", "lane change", "rear body panel"],
        "recommendations": [
            "Quarter panel/side radar area detected: blind spot monitoring verification recommended.",
            "Inspect side radar mounting points, brackets, and rear side harness routing."
        ]
    },
    "parking_sensors": {
        "keywords": ["park sensor", "parking sensor", "park assist", "parking aid", "sensor bracket"],
        "recommendations": [
            "Parking sensor operation detected: parking aid sensor verification recommended.",
            "Confirm sensor orientation, mounting depth, paint thickness, and sensor operation."
        ]
    },
    "radar_specific": {
        "keywords": ["radar", "radar bracket", "acc sensor", "adaptive cruise sensor", "distance sensor"],
        "recommendations": [
            "Radar-related operation detected: radar aiming/calibration review recommended.",
            "Verify radar bracket position, mounting angle, and OEM calibration procedure."
        ]
    },
    "camera_specific": {
        "keywords": ["camera", "front camera", "rear camera", "surround view", "calibration"],
        "recommendations": [
            "Camera-related operation detected: camera calibration/verification review recommended.",
            "Verify camera mounting, field of view, and system operation."
        ]
    },
}


def extract_estimate_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def parse_estimate_text(text: str):
    clean = extract_estimate_text(text)
    lower = clean.lower()

    triggers = []
    recommendations = []

    for trigger_name, rule in ESTIMATE_TRIGGER_RULES.items():
        matched_keywords = []

        for keyword in rule["keywords"]:
            if keyword in lower:
                matched_keywords.append(keyword)

        if matched_keywords:
            triggers.append({
                "trigger": trigger_name,
                "matched_keywords": matched_keywords,
                "label": trigger_name.replace("_", " ").title()
            })

            for rec in rule["recommendations"]:
                recommendations.append(rec)

    # Deduplicate recommendations
    unique_recommendations = []
    seen = set()

    for rec in recommendations:
        if rec not in seen:
            unique_recommendations.append(rec)
            seen.add(rec)

    return {
        "estimate_triggers": triggers,
        "estimate_recommendations": unique_recommendations
    }