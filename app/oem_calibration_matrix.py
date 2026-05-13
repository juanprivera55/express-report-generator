def build_oem_calibration_matrix(
    vehicle_info,
    dtcs,
    adas_equipment,
    impact_area="",
    estimate_analysis=None
):
    recommendations = []
    estimate_analysis = estimate_analysis or {}
    estimate_triggers = estimate_analysis.get("estimate_triggers", [])
    estimate_recommendations = estimate_analysis.get("estimate_recommendations", [])
    estimate_trigger_text = " ".join([
        f"{x.get('trigger', '')} {x.get('label', '')} {' '.join(x.get('matched_keywords', []))}"
        for x in estimate_triggers
    ]).lower()

    def add(system, confidence, reason):
        recommendations.append({
            "system": system,
            "confidence": confidence,
            "reason": reason
        })

    vehicle_text = " ".join([
        str(vehicle_info.get("vehicle", "")),
        str(vehicle_info.get("decoded_make", "")),
        str(vehicle_info.get("decoded_model", "")),
    ]).lower()

    dtc_text = " ".join([
        f"{d.get('code', '')} {d.get('module', '')} {d.get('description', '')}"
        for d in dtcs
    ]).lower()

    equipment_names = " ".join([
        item.get("name", "")
        for item in adas_equipment
    ]).lower()

    combined = f"{vehicle_text} {dtc_text} {equipment_names}"

    has_camera = any(x in combined for x in [
        "camera",
        "lane",
        "ipma",
        "ipmb",
        "kafas",
        "eyesight",
        "multifunction"
    ])

    has_radar = any(x in combined for x in [
        "radar",
        "adaptive cruise",
        "distronic",
        "acc"
    ])

    has_blindspot = any(x in combined for x in [
        "blind spot",
        "bsd",
        "lane change"
    ])

    has_parking = any(x in combined for x in [
        "parking",
        "park assist",
        "parktronic",
        "parking aid"
    ])

    has_steering = any(x in combined for x in [
        "steering",
        "lane keep",
        "pscm",
        "sas"
    ])

    # FRONT IMPACT
    if impact_area == "front":

        if has_camera:
            add(
                "Forward camera calibration",
                "HIGH",
                "Front impact combined with probable forward camera-related equipment/modules."
            )

        if has_radar:
            add(
                "Forward radar aiming / calibration",
                "HIGH",
                "Front impact combined with probable radar/adaptive cruise equipment."
            )

        if has_steering:
            add(
                "Steering angle sensor reset / verification",
                "MODERATE",
                "Steering or lane-keeping related systems may require recalibration after repairs."
            )

        add(
            "Post-repair ADAS functional road test",
            "HIGH",
            "Front structural and ADAS-related repairs commonly require validation testing."
        )

    # REAR IMPACT
    elif impact_area == "rear":

        if has_blindspot:
            add(
                "Blind spot radar verification",
                "HIGH",
                "Rear-quarter radar systems may be affected by rear impact repairs."
            )

        if has_parking:
            add(
                "Parking aid sensor verification",
                "HIGH",
                "Rear impact commonly affects parking sensors and rear harness areas."
            )

        add(
            "Rear camera inspection / verification",
            "MODERATE",
            "Rear impact may affect rear camera alignment or operation."
        )

    # SIDE IMPACT
    elif impact_area in ["left_side", "right_side"]:

        if has_blindspot:
            add(
                "Blind spot monitoring calibration / verification",
                "HIGH",
                "Side impacts may affect blind spot radar mounting and alignment."
            )

        add(
            "Side object detection system verification",
            "MODERATE",
            "Side impact repairs may affect side-mounted ADAS components and wiring."
        )

    # GLASS / ROOF
    elif impact_area == "roof_glass":

        if has_camera:
            add(
                "Forward camera calibration",
                "HIGH",
                "Windshield/glass repairs commonly affect camera aiming and calibration."
            )

        add(
            "Lane keeping / pre-collision functional validation",
            "MODERATE",
            "Windshield-mounted systems may require verification after replacement."
        )

    # SUSPENSION / STEERING
    elif impact_area == "suspension_steering":

        add(
            "Steering angle sensor calibration",
            "HIGH",
            "Suspension or steering repairs commonly affect steering angle values."
        )

        add(
            "Wheel alignment verification",
            "HIGH",
            "Alignment verification is recommended after suspension/steering repairs."
        )

        if has_camera:
            add(
                "Forward camera calibration review",
                "MODERATE",
                "Alignment and steering changes may affect camera-based lane systems."
            )

    # UNDERCARRIAGE
    elif impact_area == "undercarriage":

        add(
            "ABS / stability control verification",
            "HIGH",
            "Undercarriage impacts may affect wheel speed, ride height, or chassis sensors."
        )

        add(
            "Chassis sensor inspection",
            "MODERATE",
            "Inspect related wiring and chassis-mounted sensors."
        )

    # MULTIPLE
    elif impact_area == "multiple":

        if has_camera:
            add(
                "Forward camera calibration",
                "HIGH",
                "Multiple impact areas increase likelihood of camera-related repairs."
            )

        if has_radar:
            add(
                "Forward radar calibration",
                "HIGH",
                "Multiple impact areas increase likelihood of radar-related repairs."
            )

        if has_blindspot:
            add(
                "Blind spot radar verification",
                "HIGH",
                "Multiple impact areas may affect side radar systems."
            )

        add(
            "Comprehensive ADAS system validation",
            "HIGH",
            "Multiple repair areas require broader post-repair validation."
        )
        # HONDA / ACURA COLLISION-SPECIFIC SAFETY LOGIC
    is_honda_acura = any(x in vehicle_text for x in ["honda", "acura"])

    collision_indicated = (
        impact_area not in ["", "Not specified", None]
        or "collision" in combined
        or "impact" in combined
        or "supplement" in combined
        or "repair" in combined
    )

    if is_honda_acura and collision_indicated:
        add(
            "Seat weight sensor initialization / passenger weight sensor check",
            "HIGH",
            "Honda/Acura collision-related service logic: passenger seat weight sensor initialization or verification should be reviewed after collision repairs."
        )

        add(
            "SRS deployment history check",
            "HIGH",
            "Honda/Acura collision-related service logic: SRS deployment history should be checked when the vehicle has been involved in a collision."
        )

        add(
            "VSA sensor neutral position memorization review",
            "MODERATE",
            "Honda/Acura collision-related service logic: VSA/steering sensor neutral position memorization may be required when alignment, steering, suspension, or aiming operations are involved."
        )
        # ESTIMATE-BASED HONDA / ACURA LOGIC
    if is_honda_acura and ("collision_indicated" in estimate_trigger_text or collision_indicated):
        add(
            "Seat weight sensor initialization / passenger weight sensor check",
            "HIGH",
            "Honda/Acura collision-related logic: passenger seat weight sensor initialization or verification should be reviewed after collision repairs."
        )

        add(
            "SRS deployment history check",
            "HIGH",
            "Honda/Acura collision-related logic: SRS deployment history should be checked when the vehicle has been involved in a collision."
        )

    if is_honda_acura and (
        "wheel_alignment" in estimate_trigger_text
        or "front radar" in combined
        or "camera" in combined
        or "radar" in combined
    ):
        add(
            "Wheel alignment check before camera/radar aiming",
            "HIGH",
            "Honda/Acura logic: if aiming a radar or camera is necessary due to collision repairs, a four-wheel alignment check should be reviewed."
        )

        add(
            "VSA sensor neutral position memorization",
            "HIGH",
            "Honda/Acura logic: VSA sensor neutral position memorization should be reviewed after wheel alignment or steering-related calibration operations."
        )

    if is_honda_acura and (
        "rear_bumper" in estimate_trigger_text
        or "rear_park_sensor" in estimate_trigger_text
    ):
        add(
            "Rear park sensor reset/calibration",
            "HIGH",
            "Rear bumper or rear park sensor operation detected on Honda/Acura estimate."
        )

    if is_honda_acura and (
        "quarter_panel_blindspot" in estimate_trigger_text
        or "left_rear_impact" in estimate_trigger_text
    ):
        add(
            "Blind spot radar aiming inspection",
            "HIGH",
            "Quarter panel, rear structural, or left rear impact repair detected with likely blind spot system equipment."
        )
    # DTC-BASED INTELLIGENCE
    if any(x in dtc_text for x in ["communication", "gateway", "u0140", "u0146", "u1123"]):
        add(
            "Network communication verification",
            "MODERATE",
            "Communication faults may affect ADAS system operation and module integration."
        )

    if any(x in dtc_text for x in ["camera", "ipma", "ipmb", "kafas", "eyesight"]):
        add(
            "Camera system verification",
            "HIGH",
            "Camera-related faults detected within scan data."
        )

    if any(x in dtc_text for x in ["radar", "adaptive cruise", "distronic"]):
        add(
            "Radar system verification",
            "HIGH",
            "Radar/adaptive cruise related faults detected."
        )

    # Remove duplicates
    unique = []
    seen = set()

    for item in recommendations:
        key = item["system"]

        if key not in seen:
            unique.append(item)
            seen.add(key)

    return unique