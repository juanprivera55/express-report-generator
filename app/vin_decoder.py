import httpx


async def decode_vin(vin: str):
    vin = vin.strip().upper()

    if len(vin) != 17:
        return {}

    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url)

        data = response.json()

        results = data.get("Results", [])

        decoded = {}

        for item in results:
            variable = item.get("Variable", "")
            value = item.get("Value", "")

            if not value:
                continue

            decoded[variable] = value

        return {
            "vin": vin,
            "year": decoded.get("Model Year", "Unknown"),
            "make": decoded.get("Make", "Unknown"),
            "model": decoded.get("Model", "Unknown"),
            "trim": decoded.get("Trim", "Unknown"),
            "body_class": decoded.get("Body Class", "Unknown"),
            "vehicle_type": decoded.get("Vehicle Type", "Unknown"),
            "engine": decoded.get("Engine Model", "Unknown"),
            "drive_type": decoded.get("Drive Type", "Unknown"),
            "plant_country": decoded.get("Plant Country", "Unknown"),
            "plant_company": decoded.get("Plant Company Name", "Unknown")
        }

    except Exception as e:
        print("VIN decode error:", e)
        return {}