def is_toyota_lexus(vehicle_info):
    text = " ".join([
        str(vehicle_info.get("vehicle", "")),
        str(vehicle_info.get("decoded_make", "")),
        str(vehicle_info.get("decoded_model", "")),
    ]).lower()

    return "toyota" in text or "lexus" in text


def toyota_oem_rules(vehicle_info, estimate_analysis, adas_equipment, impact_area=""):
    recommendations = []

    def add(system, confidence, reason):
        recommendations.append({
            "system": system,
            "confidence": confidence,
            "reason": reason
        })

    if not is_toyota_lexus(vehicle_info):
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

    combined_repair_text = f"{trigger_text} {repair_text}"

    collision_detected = (
        impact_area not in ["", "Not specified", None]
        or "collision_indicated" in trigger_text
        or "impact" in combined_repair_text
        or "repair" in combined_repair_text
    )

    has_camera = any(x in equipment_text for x in [
        "camera",
        "toyota safety sense",
        "lexus safety system",
        "lane",
        "pre-collision"
    ])

    has_radar = any(x in equipment_text for x in [
        "radar",
        "millimeter",
        "adaptive cruise",
        "dynamic radar",
        "pre-collision"
    ])

    has_bsm = any(x in equipment_text for x in [
        "blind spot",
        "bsm",
        "lane change"
    ])

    has_parking = any(x in equipment_text for x in [
        "parking",
        "clearance sonar",
        "parking assist",
        "park sensor"
    ])

    has_panoramic_view = any(x in equipment_text for x in [
        "panoramic",
        "surround",
        "around view",
        "multi-terrain",
        "camera system"
    ])

    front_body_trigger = any(x in combined_repair_text for x in [
        "front_bumper",
        "front bumper",
        "grille",
        "radiator support",
        "front structural",
        "bumper reinforcement",
        "front reinforcement",
        "radar",
        "front sensor"
    ])

    glass_trigger = any(x in combined_repair_text for x in [
        "windshield",
        "glass",
        "camera bracket",
        "mirror bracket"
    ])

    rear_body_trigger = any(x in combined_repair_text for x in [
        "rear_bumper",
        "rear bumper",
        "rear_park_sensor",
        "quarter panel",
        "rear body panel",
        "rear structural",
        "body pull",
        "left_rear_impact",
        "right rear",
        "left rear"
    ])

    side_body_trigger = any(x in combined_repair_text for x in [
        "door",
        "fender",
        "quarter panel",
        "rocker",
        "pillar",
        "side repair"
    ])

    geometry_affecting_repair_detected = any(x in combined_repair_text for x in [
        "geometry_affecting",
        "sensor_adjacent",
        "high",
        "structural",
        "body pull",
        "frame rail",
        "radiator support",
        "bumper reinforcement",
        "reinforcement",
        "quarter panel",
        "rear body panel",
        "fender",
        "door",
        "rocker",
        "pillar",
        "apron",
        "unibody",
        "weld",
        "section",
        "subframe",
        "suspension",
        "control arm",
        "strut",
        "knuckle",
        "tie rod",
        "alignment"
    ])

    # Toyota/Lexus collision safety and ADAS review
    if collision_detected:
        add(
            "Toyota/Lexus collision-related ADAS procedure review",
            "HIGH",
            "Toyota/Lexus collision logic: after collision repairs, affected driving support, camera, radar, parking, and stability systems should be reviewed against OEM repair procedures."
        )

    # Geometry / alignment / zero point logic
    if geometry_affecting_repair_detected:
        add(
            "Four-wheel alignment / thrust angle verification",
            "HIGH",
            "Toyota/Lexus collision geometry logic: structural, suspension, panel, or bumper reinforcement repairs may affect vehicle centerline, thrust angle, and ADAS aiming relationships."
        )

        add(
            "Steering angle / yaw rate / zero point calibration review",
            "HIGH",
            "Toyota/Lexus logic: steering angle, yaw rate, and zero point calibration should be reviewed after alignment, suspension, steering, or geometry-affecting collision repairs."
        )

    # Forward recognition camera
    if has_camera and (glass_trigger or geometry_affecting_repair_detected):
        add(
            "Forward recognition camera calibration review",
            "HIGH",
            "Toyota/Lexus logic: windshield, camera bracket, alignment, or geometry-affecting repairs may require forward recognition camera calibration/learning."
        )

    # Millimeter wave radar
    if has_radar and (front_body_trigger or geometry_affecting_repair_detected):
        add(
            "Millimeter wave radar sensor alignment / calibration review",
            "HIGH",
            "Toyota/Lexus logic: front bumper, grille, radar bracket, reinforcement, structural, or geometry-affecting repairs may require millimeter wave radar alignment."
        )

    # Blind spot monitor
    if has_bsm and (rear_body_trigger or side_body_trigger):
        add(
            "Blind spot monitor sensor calibration / beam axis inspection",
            "HIGH",
            "Toyota/Lexus logic: rear bumper, quarter panel, side body, or rear structural repairs may affect blind spot monitor sensor mounting or beam axis."
        )

    # Parking / clearance sonar
    if has_parking and (front_body_trigger or rear_body_trigger):
        add(
            "Clearance sonar / parking assist sensor verification",
            "HIGH",
            "Toyota/Lexus logic: bumper cover, parking sensor, or sensor mounting repairs may require clearance sonar or parking assist verification."
        )

    # Panoramic view monitor
    if has_panoramic_view and (
        front_body_trigger
        or rear_body_trigger
        or side_body_trigger
        or glass_trigger
    ):
        add(
            "Panoramic view monitor / camera aiming verification",
            "HIGH",
            "Toyota/Lexus logic: bumper, grille, door, mirror, rear camera, or body panel repairs may affect panoramic view monitor camera aiming."
        )

    # DTC / scan support
    if "communication" in combined_repair_text or "dtc" in combined_repair_text:
        add(
            "Post-repair scan and driving support system health check",
            "MODERATE",
            "Toyota/Lexus logic: scan data and communication concerns should be verified after repair and calibration operations."
        )

    return recommendations