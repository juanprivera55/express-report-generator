def score_recommendation(system, reason):
    text = f"{system} {reason}".lower()

    score = 0
    triggers = []

    if any(x in text for x in ["collision", "impact", "structural", "geometry", "centerline", "thrust angle"]):
        score += 30
        triggers.append("Collision/geometry-related repair influence")

    if any(x in text for x in ["camera", "radar", "adas", "aiming", "calibration"]):
        score += 25
        triggers.append("ADAS aiming/calibration-related system")

    if any(x in text for x in ["honda", "oem", "manufacturer", "repair procedures"]):
        score += 20
        triggers.append("OEM/manufacturer rule logic")

    if any(x in text for x in ["dtc", "fault", "communication", "module"]):
        score += 15
        triggers.append("Scan/module/DTC-related evidence")

    if any(x in text for x in ["estimate", "repair", "replace", "panel", "bumper", "windshield", "alignment"]):
        score += 15
        triggers.append("Estimate repair-operation evidence")

    if any(x in text for x in ["srs", "seat weight", "vsa", "safety"]):
        score += 20
        triggers.append("Safety-system procedure relationship")

    if score >= 75:
        tier = "CRITICAL"
    elif score >= 55:
        tier = "HIGH"
    elif score >= 35:
        tier = "MODERATE"
    else:
        tier = "LOW"

    if not triggers:
        triggers.append("General ADAS/OEM review logic")

    return {
        "score": min(score, 100),
        "tier": tier,
        "triggers": triggers
    }


def enrich_recommendations(recommendations):
    enriched = []

    for item in recommendations:
        system = item.get("system", "")
        reason = item.get("reason", "")

        confidence_data = score_recommendation(system, reason)

        enriched_item = dict(item)
        enriched_item["score"] = confidence_data["score"]
        enriched_item["tier"] = confidence_data["tier"]
        enriched_item["trigger_reasons"] = confidence_data["triggers"]

        enriched.append(enriched_item)

    return enriched