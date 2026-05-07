DTC_LIBRARY = {
    "U0140": {
        "meaning": "Lost communication with the Body Control Module.",
        "causes": [
            "Low voltage or battery disconnect",
            "CAN network communication issue",
            "Loose, damaged, or corroded connector",
            "Body Control Module power/ground issue"
        ],
        "fixes": [
            "Verify battery voltage and charging system",
            "Inspect BCM connectors and grounds",
            "Check CAN network communication",
            "Clear codes and verify they do not return"
        ],
        "adas_impact": "May affect communication between ADAS, lighting, body, and safety-related modules."
    },
    "U0146": {
        "meaning": "Lost communication with gateway module.",
        "causes": [
            "Network interruption",
            "Gateway module power/ground issue",
            "Damaged CAN wiring",
            "Module unplugged during repair"
        ],
        "fixes": [
            "Perform network health check",
            "Inspect gateway module connectors",
            "Verify module communication after repairs"
        ],
        "adas_impact": "Gateway communication issues can prevent ADAS modules from communicating properly."
    },
    "B115E": {
        "meaning": "Camera module / image processing system fault.",
        "causes": [
            "Camera misalignment",
            "Camera calibration lost",
            "Windshield or camera bracket disturbance",
            "Camera wiring or connector issue",
            "Camera module fault"
        ],
        "fixes": [
            "Inspect camera mounting and windshield area",
            "Verify camera/module communication",
            "Perform OEM forward camera calibration",
            "Complete post-calibration road test"
        ],
        "adas_impact": "Critical ADAS concern. May affect lane keep assist, pre-collision assist, forward collision warning, and related camera-based systems."
    },
    "B1445": {
        "meaning": "Rear park lamp output circuit fault.",
        "causes": [
            "Damaged rear lighting circuit",
            "Open or shorted wiring",
            "Corroded connector",
            "Rear body damage or repair-related harness issue"
        ],
        "fixes": [
            "Inspect rear lamp wiring and connectors",
            "Check for short/open circuit",
            "Repair damaged harness",
            "Verify lighting operation"
        ],
        "adas_impact": "Rear body electrical concerns may require inspection of nearby sensors, harnesses, and parking/side detection systems."
    },
    "B153E": {
        "meaning": "Trailer hitch / trailer lighting output fault.",
        "causes": [
            "Trailer wiring fault",
            "Damaged hitch wiring",
            "Corrosion at trailer connector",
            "Shorted lighting output"
        ],
        "fixes": [
            "Inspect trailer connector",
            "Check hitch wiring harness",
            "Test lighting circuits",
            "Repair or replace damaged wiring"
        ],
        "adas_impact": "Rear wiring issues may overlap with parking aid, blind spot, and rear body harness inspection needs."
    }
}


def lookup_dtc(code: str):
    base = code.split(":")[0].split("-")[0].upper()
    return DTC_LIBRARY.get(base, {
        "meaning": "This code indicates a detected fault in the related vehicle system or module.",
        "causes": [
            "Wiring or connector issue",
            "Low voltage event",
            "Sensor or module fault",
            "Communication concern"
        ],
        "fixes": [
            "Perform pinpoint diagnostics",
            "Inspect wiring and connectors",
            "Repair root cause",
            "Clear codes and complete post-scan verification"
        ],
        "adas_impact": "ADAS impact should be verified based on the affected module and OEM repair procedures."
    })