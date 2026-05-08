ADAS_MODULE_RULES = {
    # Ford / general
    "IPMA": "Forward camera calibration / camera system verification",
    "IPMB": "Forward camera calibration / image processing module verification",
    "CCM": "Forward radar calibration / adaptive cruise control verification",
    "C-CM": "Forward radar calibration / adaptive cruise control verification",
    "SODL": "Left blind spot radar verification",
    "SODR": "Right blind spot radar verification",
    "PAM": "Parking aid sensor verification",
    "PSCM": "Steering angle / lane keeping related verification",
    "ABS": "ABS / stability control sensor verification",
    "RCM": "Restraint system verification",
    "BCM": "Body control / lighting / harness verification",
    "BDYCM": "Body control / lighting / harness verification",
    "GWM": "Gateway / network communication verification",

    # GM / Stellantis / general naming
    "SDM": "Restraint / safety module verification",
    "EBCM": "Brake / stability control verification",
    "BCM": "Body control and lighting system verification",
    "RADAR": "Radar calibration / radar aiming verification",
    "CAMERA": "Camera calibration / camera aiming verification",
    "PARK": "Parking aid verification",

    # Toyota / Lexus
    "PCS": "Pre-collision system verification",
    "LDA": "Lane departure / lane trace assist verification",
    "BSM": "Blind spot monitoring verification",
    "ICS": "Parking support / clearance sonar verification",

    # Honda / Acura
    "LKAS": "Lane keeping assist camera verification",
    "CMBS": "Collision mitigation braking system verification",
    "ACC": "Adaptive cruise control verification",

    # VW / Audi
    "A5": "VW/Audi front camera / lane assist calibration verification",
    "13": "VW/Audi adaptive cruise radar verification",
    "3C": "VW/Audi lane change assist / blind spot verification",
    "19": "VW/Audi gateway / network verification",
    "03": "VW/Audi ABS / stability control verification",
    "09": "VW/Audi central electronics / body system verification",

    # BMW / Mini
    "KAFAS": "BMW/Mini forward camera calibration / driver assistance verification",
    "DSC": "BMW/Mini stability control verification",
    "BDC": "BMW body domain controller / body system verification",
    "FEM": "BMW front electronic module / body system verification",
    "REM": "BMW rear electronic module / rear body system verification",

    # Mercedes-Benz
    "DISTRONIC": "Mercedes radar / adaptive cruise verification",
    "ESP": "Mercedes stability control verification",
    "SAM": "Mercedes body electrical / signal acquisition module verification",
    "MULTIFUNCTION CAMERA": "Mercedes multifunction camera calibration verification",
}


DTC_BASED_RULES = {
    "B115E": "Forward camera calibration required / camera system verification",
    "U0140": "Network communication verification required",
    "U0146": "Gateway communication verification required",
    "B1445": "Rear lighting circuit and rear body harness verification",
    "B153E": "Trailer hitch lighting circuit and rear harness verification",
    "U1123": "Manufacturer-specific network/data bus verification required",
}


KEYWORD_RULES = {
    "camera": "Forward camera calibration may be required",
    "image processing": "Camera/image processing module verification required",
    "front assist": "Forward camera/radar driver assistance verification recommended",
    "lane": "Lane keeping / lane assist verification recommended",
    "radar": "Radar calibration or radar aiming verification may be required",
    "cruise": "Adaptive cruise control verification may be required",
    "acc": "Adaptive cruise control verification may be required",
    "blind spot": "Blind spot radar verification may be required",
    "lane change": "Blind spot / lane change assist verification may be required",
    "park": "Parking aid system verification may be required",
    "parking": "Parking aid system verification may be required",
    "steering": "Steering angle / lane keeping verification may be required",
    "gateway": "Network gateway communication verification required",
    "communication": "Network communication verification required",
    "body control": "Body control module communication and harness verification",
    "trailer": "Trailer wiring / rear harness inspection recommended",
    "rear": "Rear body harness and rear sensor area inspection recommended",
    "brake": "Brake / stability control verification recommended",
    "abs": "ABS / stability control verification recommended",
    "restraint": "Restraint system verification recommended",
    "airbag": "Restraint system verification recommended",
}


IMPACT_AREA_RULES = {
    "front": [
        "Front impact review: inspect front camera, radar, bumper-mounted sensors, grille brackets, and aiming surfaces",
        "Forward camera calibration recommended if windshield, camera bracket, suspension, alignment, or front body structure was affected",
        "Forward radar calibration / aiming verification recommended if front bumper, grille, radar bracket, or front structure was affected",
        "Pre-collision assist, adaptive cruise, and lane keeping functional validation"
    ],
    "rear": [
        "Rear impact review: inspect rear body harness, parking sensors, trailer wiring, rear camera, and blind spot radar areas",
        "Parking aid sensor verification recommended",
        "Blind spot monitoring verification recommended if quarter panels, rear bumper, or side radar mounting areas were affected",
        "Rear camera operation and alignment verification"
    ],
    "left_side": [
        "Left side impact review: inspect left blind spot radar area, side sensors, door harnesses, and body wiring",
        "Left blind spot radar verification recommended",
        "Side object detection system functional validation"
    ],
    "right_side": [
        "Right side impact review: inspect right blind spot radar area, side sensors, door harnesses, and body wiring",
        "Right blind spot radar verification recommended",
        "Side object detection system functional validation"
    ],
    "roof_glass": [
        "Windshield/glass impact review: inspect camera bracket, windshield mounting area, and camera view path",
        "Forward camera calibration recommended after windshield replacement or camera bracket disturbance",
        "Lane keeping and pre-collision camera system validation"
    ],
    "suspension_steering": [
        "Suspension/steering repair review: verify alignment, steering angle sensor, stability control data, and lane keeping inputs",
        "Steering angle sensor calibration/initialization may be required",
        "Lane keeping and stability control road test validation"
    ],
    "undercarriage": [
        "Undercarriage impact review: inspect wiring, wheel speed sensors, ride height sensors, and chassis-related harnesses",
        "ABS/stability control sensor verification recommended",
        "Road test and chassis sensor validation"
    ],
    "multiple": [
        "Multiple impact area review: verify all affected ADAS sensors, cameras, radar modules, wiring, and mounting points",
        "OEM procedure review required for all affected repair areas",
        "Complete system calibration and functional validation plan recommended"
    ]
}


def detect_adas_operations(dtcs, impact_area=""):
    operations = set()

    operations.add("Pre-scan and post-scan documentation review")
    operations.add("Confirm OEM repair procedures based on repair area and affected systems")

    for d in dtcs:
        module = d.get("module", "").upper()
        desc = d.get("description", "").lower()
        code = d.get("code", "").upper()
        base_code = code.split(":")[0].split("-")[0]

        for module_key, operation in ADAS_MODULE_RULES.items():
            if module_key.upper() in module or module_key.upper() in desc.upper():
                operations.add(operation)

        if base_code in DTC_BASED_RULES:
            operations.add(DTC_BASED_RULES[base_code])

        if len(base_code) > 5 and base_code[:5] in DTC_BASED_RULES:
            operations.add(DTC_BASED_RULES[base_code[:5]])

        if len(base_code) > 4 and base_code[:4] in DTC_BASED_RULES:
            operations.add(DTC_BASED_RULES[base_code[:4]])

        for keyword, operation in KEYWORD_RULES.items():
            if keyword in desc:
                operations.add(operation)

        if code.startswith("U"):
            operations.add("CAN network health check / module communication verification")

        if code.startswith("C"):
            operations.add("Chassis, steering, ABS, or stability control verification")

        if code.startswith("B"):
            operations.add("Body, safety, camera, parking, lighting, or comfort system verification")

        if code.startswith("P"):
            operations.add("Powertrain fault review and post-repair drivability validation")

    if impact_area in IMPACT_AREA_RULES:
        for item in IMPACT_AREA_RULES[impact_area]:
            operations.add(item)

    operations.add("Clear codes only after repairs are completed")
    operations.add("Perform post-repair road test and functional validation")
    operations.add("Complete final post-scan and confirm no related DTCs return")

    return sorted(operations)


def impact_area_label(value):
    labels = {
        "front": "Front Impact",
        "rear": "Rear Impact",
        "left_side": "Left Side Impact",
        "right_side": "Right Side Impact",
        "roof_glass": "Roof / Windshield / Glass",
        "suspension_steering": "Suspension / Steering",
        "undercarriage": "Undercarriage",
        "multiple": "Multiple Impact Areas",
        "": "Not specified",
        "Not specified": "Not specified"
    }

    return labels.get(value, value or "Not specified")