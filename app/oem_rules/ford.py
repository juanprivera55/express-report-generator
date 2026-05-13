def is_ford_lincoln(vehicle_info):
    text = " ".join([
        str(vehicle_info.get("vehicle", "")),
        str(vehicle_info.get("decoded_make", "")),
        str(vehicle_info.get("decoded_model", "")),
    ]).lower()

    return "ford" in text or "lincoln" in text


def ford_oem_rules(vehicle_info, estimate_analysis, adas_equipment, impact_area=""):
    recommendations = []

    def add(system, confidence, reason):
        recommendations.append({
            "system": system,
            "confidence": confidence,
            "reason": reason
        })

    if not is_ford_lincoln(vehicle_info):
        return recommendations

    estimate_analysis = estimate_analysis or {}
    triggers = estimate_analysis.get("estimate_triggers", [])
    repair_classifications = estimate_analysis.get("repair_classifications", [])

    trigger_text = " ".join([
        f"{x.get('trigger', '')} {x.get('label', '')} {' '.join(x.get('matched_keywords', []))}"
        for x in triggers
    ]).lower()

    repair_text = " ".join([
        f"{x.get('line', '')} {x.get('severity', '')} {' '.join(x.get('flags', []))}"
        for x in repair_classifications
    ]).lower()

    equipment_text = " ".join([
        f"{x.get('name', '')} {x.get('confidence', '')} {x.get('reason', '')}"
        for x in adas_equipment
    ]).lower()

    combined = f"{trigger_text} {repair_text} {equipment_text}"

    collision_detected = (
        impact_area not in ["", "Not specified", None]
        or "collision_indicated" in combined
        or "impact" in combined
        or "repair" in combined
    )

    has_camera = any(x in combined for x in [
        "camera", "ipma", "ipmb", "lane keeping", "pre-collision"
    ])

    has_radar = any(x in combined for x in [
        "radar", "adaptive cruise", "acc", "c-cm", "ccm"
    ])

    has_blindspot = any(x in combined for x in [
        "blind spot", "sodl", "sodr", "side object"
    ])

    has_parking = any(x in combined for x in [
        "parking", "park sensor", "pam", "parking aid"
    ])

    front_body_trigger = any(x in combined for x in [
        "front_bumper", "front bumper", "grille", "radiator support",
        "front structural", "bumper reinforcement", "radar bracket"
    ])

    glass_trigger = any(x in combined for x in [
        "windshield", "glass", "camera bracket", "mirror bracket"
    ])

    rear_body_trigger = any(x in combined for x in [
        "rear_bumper", "rear bumper", "rear_park_sensor", "quarter panel",
        "rear body panel", "rear structural", "left rear", "right rear"
    ])

    geometry_affecting_repair_detected = any(x in combined for x in [
        "geometry_affecting", "sensor_adjacent", "high", "structural",
        "body pull", "frame rail", "radiator support", "bumper reinforcement",
        "reinforcement", "quarter panel", "rear body panel", "fender",
        "door", "rocker", "pillar", "apron", "unibody", "weld",
        "section", "subframe", "suspension", "control arm", "strut",
        "knuckle", "tie rod", "alignment"
    ])

    if collision_detected:
        add(
            "Ford/Lincoln collision-related ADAS procedure review",
            "HIGH",
            "Ford/Lincoln collision logic: affected camera, radar, parking, blind spot, steering, and stability systems should be reviewed after collision repairs."
        )

    if geometry_affecting_repair_detected:
        add(
            "Four-wheel alignment / steering angle verification",
            "HIGH",
            "Ford/Lincoln logic: structural, suspension, steering, panel, or geometry-affecting repairs may affect steering angle, vehicle centerline, and ADAS aiming relationships."
        )

    if has_camera and (glass_trigger or geometry_affecting_repair_detected):
        add(
            "Forward camera calibration / IPMA verification",
            "HIGH",
            "Ford/Lincoln logic: windshield, camera bracket, alignment, steering, or geometry-affecting repairs may require forward camera/IPMA calibration review."
        )

    if has_radar and (front_body_trigger or geometry_affecting_repair_detected):
        add(
            "Forward radar aiming / C-CM verification",
            "HIGH",
            "Ford/Lincoln logic: front bumper, grille, radar bracket, reinforcement, or geometry-affecting repairs may require forward radar aiming verification."
        )

    if has_blindspot and rear_body_trigger:
        add(
            "Blind spot radar verification / SODL-SODR review",
            "HIGH",
            "Ford/Lincoln logic: rear bumper, quarter panel, rear body, or rear structural repairs may affect blind spot radar mounting and operation."
        )

    if has_parking and (front_body_trigger or rear_body_trigger):
        add(
            "Parking aid sensor verification / PAM review",
            "HIGH",
            "Ford/Lincoln logic: bumper cover, parking sensor, or parking aid wiring repairs may require parking aid sensor verification."
        )

    return recommendations