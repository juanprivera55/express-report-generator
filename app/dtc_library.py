DTC_LIBRARY = {
    # Communication / network
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
    "U1123": {
        "meaning": "Manufacturer-specific communication/data bus fault.",
        "causes": [
            "CAN/LIN network communication interruption",
            "Module coding/adaptation issue",
            "Low voltage event",
            "Disconnected module or damaged wiring"
        ],
        "fixes": [
            "Perform full network scan",
            "Verify battery voltage and module communication",
            "Inspect related wiring/connectors",
            "Perform coding/adaptation checks if required"
        ],
        "adas_impact": "Communication faults may affect camera, radar, parking, stability, and driver assistance systems."
    },

    # Camera / ADAS
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

    # Body / lighting
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
    },

    # Common powertrain
    "P0300": {
        "meaning": "Random or multiple cylinder misfire detected.",
        "causes": [
            "Ignition coil or spark plug issue",
            "Fuel delivery concern",
            "Vacuum leak",
            "Engine mechanical issue"
        ],
        "fixes": [
            "Check misfire data and freeze frame",
            "Inspect ignition and fuel systems",
            "Perform compression/leakdown testing if needed",
            "Repair root cause and verify misfire counters"
        ],
        "adas_impact": "Engine performance faults may affect adaptive cruise, stability control, and drivability-related safety features."
    },
    "P0420": {
        "meaning": "Catalyst system efficiency below threshold.",
        "causes": [
            "Failing catalytic converter",
            "Exhaust leak",
            "Oxygen sensor concern",
            "Engine running condition issue"
        ],
        "fixes": [
            "Inspect exhaust system",
            "Review fuel trim and oxygen sensor data",
            "Repair engine performance concerns first",
            "Verify catalyst operation"
        ],
        "adas_impact": "Usually not directly ADAS-related, but should be resolved for emissions and drivability compliance."
    },
}


def generic_by_code_family(code: str):
    code = code.upper()

    if code.startswith("P"):
        return {
            "meaning": "Powertrain-related diagnostic trouble code detected.",
            "causes": [
                "Engine, transmission, emissions, or drivability system concern",
                "Sensor or actuator fault",
                "Wiring or connector issue",
                "Low voltage or intermittent operating condition"
            ],
            "fixes": [
                "Review freeze frame and scan data",
                "Perform pinpoint diagnostics for affected system",
                "Inspect wiring, sensors, and connectors",
                "Repair root cause and complete post-repair verification"
            ],
            "adas_impact": "Powertrain faults may affect adaptive cruise, stability control, or drivability-related safety systems depending on the vehicle."
        }

    if code.startswith("B"):
        return {
            "meaning": "Body or comfort/safety system diagnostic trouble code detected.",
            "causes": [
                "Body control module concern",
                "Lighting, door, restraint, camera, or interior electronics issue",
                "Wiring or connector damage",
                "Module configuration or calibration concern"
            ],
            "fixes": [
                "Identify affected body/safety system",
                "Inspect related harnesses and connectors",
                "Verify module communication and configuration",
                "Perform calibration or initialization if required"
            ],
            "adas_impact": "Body faults may affect cameras, lighting, parking systems, blind spot systems, restraints, or other safety-related features."
        }

    if code.startswith("C"):
        return {
            "meaning": "Chassis-related diagnostic trouble code detected.",
            "causes": [
                "ABS/stability control concern",
                "Steering angle, wheel speed, suspension, or brake system fault",
                "Alignment or impact-related sensor issue",
                "Wiring or connector problem"
            ],
            "fixes": [
                "Inspect chassis and suspension-related sensors",
                "Check wheel speed, steering angle, and stability control data",
                "Verify alignment and steering/suspension repairs",
                "Perform required calibrations and road test"
            ],
            "adas_impact": "Chassis faults can directly affect lane keeping, adaptive cruise, collision avoidance, ABS, and stability control systems."
        }

    if code.startswith("U"):
        return {
            "meaning": "Network communication diagnostic trouble code detected.",
            "causes": [
                "CAN/LIN/FlexRay communication issue",
                "Low voltage or module reset",
                "Disconnected or damaged module",
                "Gateway or network wiring concern"
            ],
            "fixes": [
                "Perform network health check",
                "Verify battery voltage and grounds",
                "Inspect affected module connectors",
                "Confirm communication returns after repair"
            ],
            "adas_impact": "Network faults can prevent ADAS modules from communicating, calibrating, or reporting accurate system status."
        }

    # European/manufacturer numeric or hex codes
    return {
        "meaning": "Manufacturer-specific diagnostic trouble code detected.",
        "causes": [
            "Manufacturer-specific module fault",
            "Sensor, actuator, wiring, or communication concern",
            "Module coding/adaptation issue",
            "Low voltage or intermittent fault"
        ],
        "fixes": [
            "Review the affected module and scan description",
            "Check OEM service information for code-specific diagnostics",
            "Inspect related wiring, connectors, sensors, and mounting points",
            "Perform coding, adaptation, calibration, or initialization if required"
        ],
        "adas_impact": "Manufacturer-specific faults should be reviewed with the affected module. If related to camera, radar, steering, braking, parking, gateway, or body systems, ADAS verification may be required."
    }


def lookup_dtc(code: str, vehicle_info=None):
    vehicle_info = vehicle_info or {}

    base = code.split(":")[0].split("-")[0].upper()

    # EXACT MATCHES
    if base in DTC_LIBRARY:
        return DTC_LIBRARY[base]

    vehicle_text = " ".join([
        str(vehicle_info.get("vehicle", "")),
        str(vehicle_info.get("decoded_make", "")),
        str(vehicle_info.get("decoded_model", ""))
    ]).lower()

    # GM / CHEVY ENHANCED FALLBACK
    if any(x in vehicle_text for x in [
        "chevrolet",
        "chevy",
        "gmc",
        "cadillac",
        "buick"
    ]):

        if base.startswith("U"):
            return {
                "meaning": "GM/Chevrolet network communication fault detected.",
                "causes": [
                    "Low battery voltage or module reset during repair",
                    "CAN communication interruption",
                    "Disconnected module or loose connector",
                    "Gateway/body network communication issue",
                    "Module programming or wake-up concern"
                ],
                "fixes": [
                    "Perform full GM network scan and identify all offline or non-communicating modules",
                    "Verify battery voltage, grounds, and module power feeds",
                    "Inspect connectors and wiring in the affected repair area",
                    "Perform post-scan after repairs and verify communication restoration",
                    "Road test and verify all safety systems operate normally"
                ],
                "adas_impact": "GM communication faults may affect forward camera, radar, park assist, blind zone alert, steering, braking, restraint, and other ADAS-related modules."
            }

        if base.startswith("B"):
            return {
                "meaning": "GM/Chevrolet body, restraint, lighting, camera, or convenience system fault detected.",
                "causes": [
                    "Body control module or subsystem concern",
                    "Lighting, restraint, camera, hatch, or park assist issue",
                    "Collision-area wiring or connector damage",
                    "Module initialization or calibration concern",
                    "Repair-related low voltage or disconnected module"
                ],
                "fixes": [
                    "Identify the GM module reporting the fault",
                    "Inspect related wiring, connectors, grounds, and mounting locations",
                    "Verify body/safety module communication",
                    "Perform required setup, calibration, or initialization procedures",
                    "Perform final post-scan verification"
                ],
                "adas_impact": "GM body/safety faults may affect park assist, side blind zone alert, cameras, lighting, restraint systems, door/hatch systems, and ADAS calibration readiness."
            }

        if base.startswith("C"):
            return {
                "meaning": "GM/Chevrolet chassis, steering, suspension, brake, or stability system fault detected.",
                "causes": [
                    "Wheel speed, steering angle, yaw, brake, or stability system issue",
                    "Suspension or alignment-related repair concern",
                    "Sensor wiring or connector damage",
                    "Steering angle or chassis learn/calibration needed",
                    "ABS/StabiliTrak module or sensor issue"
                ],
                "fixes": [
                    "Inspect steering, suspension, brake, and wheel speed sensor circuits",
                    "Verify alignment and steering angle values",
                    "Perform ABS/StabiliTrak diagnostics",
                    "Complete steering angle or chassis learn procedures if required",
                    "Road test and verify stability control data after repairs"
                ],
                "adas_impact": "GM chassis faults may affect lane keep assist, adaptive cruise, automatic emergency braking, steering assist, traction control, and calibration eligibility."
            }

        if base.startswith("P"):
            return {
                "meaning": "GM/Chevrolet powertrain or emissions diagnostic fault detected.",
                "causes": [
                    "Engine, transmission, fuel, emissions, or drivability concern",
                    "Sensor or actuator malfunction",
                    "Wiring, connector, or voltage issue",
                    "Repair-related disconnect or intermittent operating condition"
                ],
                "fixes": [
                    "Review freeze-frame and live data",
                    "Perform GM pinpoint diagnostics for the affected system",
                    "Inspect wiring, connectors, and related components",
                    "Repair root cause before clearing codes",
                    "Verify code does not return after road test"
                ],
                "adas_impact": "GM powertrain faults may affect adaptive cruise, traction control, stability control, and drivability-related safety features depending on vehicle configuration."
            }

        return {
            "meaning": "GM/Chevrolet manufacturer-specific diagnostic trouble code detected.",
            "causes": [
                "Manufacturer-specific module concern",
                "Sensor, actuator, circuit, or communication fault",
                "Repair-area wiring or connector issue",
                "Module setup, learn, programming, or calibration requirement"
            ],
            "fixes": [
                "Identify the reporting GM module and subsystem",
                "Review GM service information for code-specific diagnostics",
                "Inspect affected wiring, connectors, sensors, and mounting points",
                "Perform setup, learn, calibration, or programming as required",
                "Complete final post-scan and functional validation"
            ],
            "adas_impact": "GM manufacturer-specific codes should be reviewed against affected modules. If related to camera, radar, park assist, blind zone, steering, brake, restraint, or network systems, ADAS verification may be required."
        }

    # GENERIC FALLBACK
    return generic_by_code_family(base)
def is_known_dtc(code: str):
    base = code.split(":")[0].split("-")[0].upper()

    if base in DTC_LIBRARY:
        return True

    if len(base) > 5 and base[:5] in DTC_LIBRARY:
        return True

    if len(base) > 4 and base[:4] in DTC_LIBRARY:
        return True

    return False