def is_honda_acura(vehicle_info):
    text = " ".join([
        str(vehicle_info.get("vehicle", "")),
        str(vehicle_info.get("decoded_make", "")),
        str(vehicle_info.get("decoded_model", "")),
    ]).lower()

    return "honda" in text or "acura" in text


def honda_oem_rules(vehicle_info, estimate_analysis, adas_equipment, impact_area=""):
    recommendations = []

    def add(system, confidence, reason):
        recommendations.append({
            "system": system,
            "confidence": confidence,
            "reason": reason
        })

    if not is_honda_acura(vehicle_info):
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

    collision_detected = (
        impact_area not in ["", "Not specified", None]
        or "collision_indicated" in trigger_text
        or "left_rear_impact" in trigger_text
        or "point of impact" in trigger_text
    )

    has_camera = any(x in equipment_text for x in [
        "camera",
        "lkas",
        "honda sensing",
        "multipurpose",
        "lane"
    ])

    has_radar = any(x in equipment_text for x in [
        "radar",
        "adaptive cruise",
        "acc",
        "cmbs"
    ])

    has_bsi = any(x in equipment_text for x in [
        "blind spot",
        "bsi",
        "lane change"
    ])

    has_parking = any(x in equipment_text for x in [
        "parking",
        "park sensor",
        "parking aid"
    ])

    has_multiview = any(x in equipment_text for x in [
        "multi view",
        "surround",
        "aerial",
        "ground view"
    ])

    rear_body_trigger = any(x in trigger_text for x in [
        "rear_bumper",
        "rear_park_sensor",
        "quarter_panel_blindspot",
        "left_rear_impact",
        "rear body",
        "quarter panel",
        "rear structural",
        "body pull",
        "rear body panel",
        "structural"
    ])

    front_body_trigger = any(x in trigger_text for x in [
        "front_bumper",
        "front radar",
        "grille",
        "front structural",
        "radiator support",
        "bumper reinforcement"
    ])

    glass_trigger = any(x in trigger_text for x in [
        "windshield",
        "glass",
        "camera bracket"
    ])

    door_or_mirror_trigger = any(x in trigger_text for x in [
        "rear_door",
        "front_door",
        "side_repair",
        "mirror",
        "door"
    ])

    geometry_source_text = f"{trigger_text} {repair_text}"

    geometry_affecting_repair_detected = any(x in geometry_source_text for x in [
       "rear structural",
       "front structural",
       "body pull",
       "structural",
       "rear body panel",
       "quarter panel",
       "rear_bumper",
       "front_bumper",
       "rear door",
       "front door",
       "door side repair",
       "fender",
       "frame rail",
       "radiator support",
       "bumper reinforcement",
       "reinforcement",
       "apron",
       "unibody",
       "weld",
       "section",
       "replace panel",
       "repair panel",
       "geometry_affecting",
       "sensor_adjacent",
       "HIGH"
])

    # Honda collision safety logic
    if collision_detected:

        add(
            "Seat weight sensor initialization / passenger weight sensor check",
            "HIGH",
            "Honda collision logic: passenger seat weight sensor initialization or verification should be reviewed after collision repairs."
        )

        add(
            "SRS deployment history check",
            "HIGH",
            "Honda collision logic: SRS deployment history should be checked when the vehicle has been involved in a collision."
        )

    # Honda alignment before aiming logic
    if collision_detected and (has_camera or has_radar):

        add(
            "Four-wheel alignment check before camera/radar aiming",
            "HIGH",
            "Honda driving support system logic: if camera or radar aiming is necessary due to collision repairs, a four-wheel alignment check should be reviewed before aiming."
        )

        add(
            "VSA sensor neutral position memorization",
            "HIGH",
            "Honda logic: VSA sensor neutral position memorization should be reviewed when wheel alignment, steering, or camera/radar aiming operations are involved."
        )

    # Honda collision geometry logic
    if geometry_affecting_repair_detected and (has_camera or has_radar):

        add(
            "Multipurpose camera aiming review",
            "HIGH",
            "Honda collision geometry logic: non-minor exterior, structural, or bolt-on panel repairs may affect vehicle geometry, ride height, thrust angle, centerline, or camera aiming relationships."
        )

        add(
            "Millimeter wave radar aiming review",
            "HIGH",
            "Honda collision geometry logic: non-minor exterior, structural, or bumper reinforcement repairs may affect radar aiming relationships and vehicle centerline geometry."
        )

        add(
            "Four-wheel alignment verification",
            "HIGH",
            "Honda collision geometry logic: panel, structural, suspension, or collision repairs should include alignment/thrust-angle verification before final ADAS aiming when camera or radar systems are involved."
        )

    # Honda front radar / front structure
    if front_body_trigger and has_radar:

        add(
            "Millimeter wave radar aiming",
            "HIGH",
            "Honda logic: front bumper, grille, front structure, or radar-area repairs may require millimeter wave radar aiming."
        )

    # Honda camera / windshield
    if glass_trigger and has_camera:

        add(
            "Multipurpose camera aiming",
            "HIGH",
            "Honda logic: windshield replacement, camera removal, or camera bracket disturbance may require multipurpose camera aiming."
        )

    # Honda rear body / BSI
    if rear_body_trigger and has_bsi:

        add(
            "BSI radar unit aiming inspection",
            "HIGH",
            "Honda logic: rear body, rear bumper, quarter panel, or rear structural repairs may affect BSI radar mounting areas."
        )

        add(
            "BSI radar unit mounting area check",
            "HIGH",
            "Honda logic: BSI radar mounting area should be checked when rear quarter/rear structural areas are repaired."
        )

    # Honda rear park sensors
    if rear_body_trigger and has_parking:

        add(
            "Rear park sensor reset / parking and back-up sensor control unit verification",
            "HIGH",
            "Honda logic: rear bumper cover or rear park sensor operations may require parking sensor reset/calibration verification."
        )

    # Honda multi-view camera
    if has_multiview and (
        front_body_trigger
        or rear_body_trigger
        or door_or_mirror_trigger
    ):

        add(
            "Multi-view camera system aiming / verification",
            "HIGH",
            "Honda logic: front grille, front bumper, mirrors, doors, tailgate, or rear camera-related repairs may affect multi-view camera calibration."
        )

    return recommendations