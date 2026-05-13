import re


SECTION_HEADERS = [
    "FRONT BUMPER",
    "REAR BUMPER",
    "FENDER",
    "HOOD",
    "ROOF",
    "REAR DOOR",
    "FRONT DOOR",
    "QUARTER PANEL",
    "REAR LAMPS",
    "VEHICLE DIAGNOSTICS",
    "SAFETY",
    "SEATS",
    "WHEELS",
    "SUSPENSION",
]


def clean_estimate_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def detect_vehicle_collision(text_lower: str) -> bool:
    return any(x in text_lower for x in [
        "point of impact",
        "collision",
        "supplement",
        "repair facility",
        "preliminary supplement",
        "estimate",
        "rear structural",
        "front structural",
        "vehicle is involved"
    ])


def add_trigger(triggers, recommendations, trigger, label, matched_keywords, recs):
    triggers.append({
        "trigger": trigger,
        "label": label,
        "matched_keywords": matched_keywords
    })

    for rec in recs:
        if rec not in recommendations:
            recommendations.append(rec)


def parse_estimate_text(text: str):
    clean = clean_estimate_text(text)
    lower = clean.lower()

    triggers = []
    recommendations = []

    current_section = ""
    section_lines = []

    def flush_section(section_name, lines):
        if not section_name:
            return

        section_text = "\n".join(lines)
        section_lower = section_text.lower()

        # Rear bumper must be handled before generic bumper logic
        if section_name == "REAR BUMPER":
            matched = []

            if any(x in section_lower for x in ["bumper cover", "rear cover", "lower cover", "park sensor", "parking sensor"]):
                matched.append("rear bumper / bumper cover / park sensor")

            if matched:
                add_trigger(
                    triggers,
                    recommendations,
                    "rear_bumper",
                    "Rear Bumper / Rear Body Repair",
                    matched,
                    [
                        "Rear bumper/rear body repair detected: parking aid and rear camera verification recommended.",
                        "Inspect rear body harness, parking sensors, rear camera, and blind spot radar areas.",
                        "Rear park sensor reset/calibration review recommended when rear bumper cover or park sensor operations are present."
                    ]
                )

            if any(x in section_lower for x in ["park sensor", "parking sensor", "park assist"]):
                add_trigger(
                    triggers,
                    recommendations,
                    "rear_park_sensor",
                    "Rear Park Sensor Operation",
                    ["park sensor / parking sensor / park assist"],
                    [
                        "Rear park sensor operation detected: reset/calibration/verification of parking and back-up sensor control unit should be reviewed.",
                        "Confirm rear parking sensor orientation, mounting depth, paint thickness, and sensor operation."
                    ]
                )

        if section_name == "FRONT BUMPER":
            matched = []

            if any(x in section_lower for x in ["bumper cover", "front cover", "front fascia", "grille", "radar", "sensor"]):
                matched.append("front bumper / grille / radar / sensor")

            if matched:
                add_trigger(
                    triggers,
                    recommendations,
                    "front_bumper",
                    "Front Bumper / Front Radar Area Repair",
                    matched,
                    [
                        "Front bumper/grille repair detected: inspect radar mounting, camera view path, sensor brackets, and aiming surfaces.",
                        "Forward radar aiming/calibration review recommended if bumper, grille, radar bracket, or front structure was affected."
                    ]
                )

        if section_name == "QUARTER PANEL":
            matched = []

            if any(x in section_lower for x in ["quarter panel", "lt quarter", "rt quarter", "body pull", "rear body panel"]):
                matched.append("quarter panel / rear structural area")

            if matched:
                add_trigger(
                    triggers,
                    recommendations,
                    "quarter_panel_blindspot",
                    "Quarter Panel / Blind Spot Radar Area",
                    matched,
                    [
                        "Quarter panel/side radar area detected: blind spot monitoring verification recommended.",
                        "Inspect side radar mounting points, brackets, and rear side harness routing.",
                        "Blind spot radar aiming inspection should be reviewed when quarter panel or rear structural repairs are present."
                    ]
                )

        if section_name in ["REAR DOOR", "FENDER"]:
            if any(x in section_lower for x in ["outer panel", "seal", "molding", "flare", "trim panel"]):
                add_trigger(
                    triggers,
                    recommendations,
                    f"{section_name.lower().replace(' ', '_')}_side_repair",
                    f"{section_name.title()} Side Repair",
                    [section_name.lower()],
                    [
                        "Side body repair detected: inspect adjacent wiring, sensor mounting areas, and blind spot radar zones where equipped."
                    ]
                )

        if section_name == "VEHICLE DIAGNOSTICS":
            if any(x in section_lower for x in ["pre-repair scan", "post-repair scan", "pre scan", "post scan"]):
                add_trigger(
                    triggers,
                    recommendations,
                    "vehicle_diagnostics",
                    "Pre/Post Scan Operation",
                    ["pre-repair scan / post-repair scan"],
                    [
                        "Vehicle diagnostics operation detected: pre-scan and post-scan documentation should be included."
                    ]
                )

    for raw_line in clean.splitlines():
        line = raw_line.strip()
        upper = line.upper().strip()

        if upper in SECTION_HEADERS:
            flush_section(current_section, section_lines)
            current_section = upper
            section_lines = []
        else:
            section_lines.append(line)

    flush_section(current_section, section_lines)

    # Global estimate-level logic
    collision_detected = detect_vehicle_collision(lower)

    if collision_detected:
        add_trigger(
            triggers,
            recommendations,
            "collision_indicated",
            "Collision / Repair Event",
            ["collision / estimate / point of impact / supplement"],
            [
                "Collision/repair event detected from estimate: safety system post-repair verification should be reviewed."
            ]
        )

    # Point of impact
    if "point of impact" in lower and "left rear" in lower:
        add_trigger(
            triggers,
            recommendations,
            "left_rear_impact",
            "Left Rear Point of Impact",
            ["Point of Impact: Left Rear"],
            [
                "Left rear impact detected: blind spot monitoring, rear park sensors, rear camera, and rear body harness areas should be reviewed."
            ]
        )

    if "alignment" in lower or "wheel alignment" in lower:
        add_trigger(
            triggers,
            recommendations,
            "wheel_alignment",
            "Wheel Alignment",
            ["alignment / wheel alignment"],
            [
                "Wheel alignment operation detected: steering angle sensor/VSA neutral position memorization review recommended where applicable.",
                "If camera or radar aiming is required due to collision repairs, four-wheel alignment check should be reviewed."
            ]
        )

    if "disconnect & reconnect battery" in lower or "disconnect and reconnect battery" in lower:
        add_trigger(
            triggers,
            recommendations,
            "battery_disconnect",
            "Battery Disconnect / Reconnect",
            ["disconnect & reconnect battery"],
            [
                "Battery disconnect/reconnect detected: review initialization, learned values, and post-repair module readiness procedures."
            ]
        )

    return {
        "estimate_triggers": triggers,
        "estimate_recommendations": recommendations
    }