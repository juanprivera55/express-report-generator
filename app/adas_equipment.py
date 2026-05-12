def detect_probable_adas_equipment(vehicle_info):
    vehicle = str(vehicle_info.get("vehicle", "")).lower()
    make = str(vehicle_info.get("decoded_make", "")).lower()
    model = str(vehicle_info.get("decoded_model", "")).lower()
    trim = str(vehicle_info.get("decoded_trim", "")).lower()
    year = str(vehicle_info.get("decoded_year", "")).lower()

    text = " ".join([vehicle, make, model, trim, year])

    equipment = []

    def add(name, confidence, reason):
        equipment.append({
            "name": name,
            "confidence": confidence,
            "reason": reason
        })

    if any(x in text for x in ["ford", "lincoln"]):
        add("Forward camera / lane keeping system", "Likely", "Ford/Lincoln models commonly use IPMA/IPMB camera systems when equipped.")
        add("Pre-collision assist / forward warning", "Likely", "Ford/Lincoln ADAS packages commonly include camera-based collision warning.")
        add("Blind spot monitoring", "Possible", "Availability depends on trim and option package.")
        add("Parking aid sensors", "Possible", "Common on higher trim Ford/Lincoln models.")

    elif any(x in text for x in ["chevrolet", "chevy", "gmc", "cadillac", "buick"]):
        add("Forward camera system", "Possible", "GM vehicles may use forward vision camera systems depending on trim.")
        add("Forward radar / adaptive cruise", "Possible", "Often trim/package dependent.")
        add("Side blind zone alert", "Possible", "Common on many GM models.")
        add("Parking assist sensors", "Possible", "Common on trucks, SUVs, and higher trims.")

    elif any(x in text for x in ["toyota", "lexus"]):
        add("Toyota Safety Sense / Lexus Safety System", "Likely", "Many late-model Toyota/Lexus vehicles include camera/radar safety systems.")
        add("Forward camera", "Likely", "Lane departure and pre-collision systems commonly use windshield-mounted camera.")
        add("Millimeter wave radar", "Likely", "Pre-collision/adaptive cruise commonly uses front radar.")
        add("Blind spot monitoring", "Possible", "Trim/package dependent.")

    elif any(x in text for x in ["honda", "acura"]):
        add("Honda Sensing / AcuraWatch", "Likely", "Many late-model Honda/Acura vehicles include camera/radar safety systems.")
        add("Forward camera / LKAS", "Likely", "Lane keeping assist commonly uses windshield-mounted camera.")
        add("Adaptive cruise / radar", "Likely", "ACC commonly uses radar depending on model/year.")
        add("Blind spot monitoring", "Possible", "Trim/package dependent.")

    elif any(x in text for x in ["nissan", "infiniti"]):
        add("Safety Shield / ProPILOT-related systems", "Possible", "Nissan/Infiniti ADAS equipment varies by trim and package.")
        add("Forward camera", "Possible", "Used for lane and forward warning features when equipped.")
        add("Forward radar / ICC", "Possible", "Intelligent cruise control may use radar.")
        add("Around view / parking cameras", "Possible", "Common on higher trims.")

    elif any(x in text for x in ["hyundai", "kia", "genesis"]):
        add("Forward collision avoidance system", "Likely", "Many Hyundai/Kia/Genesis models include FCA systems.")
        add("Lane keeping assist camera", "Likely", "Common late-model ADAS feature.")
        add("Smart cruise radar", "Possible", "Trim/package dependent.")
        add("Blind spot collision warning", "Possible", "Trim/package dependent.")

    elif any(x in text for x in ["volkswagen", "vw", "audi"]):
        add("Front Assist / lane assist camera", "Possible", "VW/Audi commonly use front camera modules when equipped.")
        add("Adaptive cruise radar", "Possible", "Common on ADAS-equipped VW/Audi models.")
        add("Lane change assist / blind spot radar", "Possible", "Trim/package dependent.")
        add("Parking aid / park assist", "Possible", "Often package dependent.")

    elif any(x in text for x in ["bmw", "mini"]):
        add("KAFAS forward camera", "Possible", "BMW/Mini driver assistance systems commonly use KAFAS camera when equipped.")
        add("Active cruise radar", "Possible", "Depends on driver assistance package.")
        add("Parking distance control", "Possible", "Common on many BMW/Mini models.")
        add("Blind spot / lane change warning", "Possible", "Package dependent.")

    elif any(x in text for x in ["mercedes", "benz"]):
        add("Multifunction camera", "Possible", "Mercedes driver assistance systems may use windshield-mounted multifunction camera.")
        add("Distronic radar", "Possible", "Adaptive cruise/Distronic uses radar when equipped.")
        add("Blind spot assist", "Possible", "Package dependent.")
        add("Parktronic / parking sensors", "Possible", "Common on many Mercedes models.")

    elif "subaru" in text:
        add("EyeSight stereo camera system", "Likely", "Many late-model Subaru vehicles include EyeSight camera-based ADAS.")
        add("Pre-collision braking", "Likely", "EyeSight supports camera-based collision mitigation.")
        add("Lane departure / lane centering", "Likely", "EyeSight supports lane assistance features.")
        add("Blind spot detection", "Possible", "Trim/package dependent.")

    elif any(x in text for x in ["jeep", "dodge", "ram", "chrysler", "fiat", "alfa romeo"]):
        add("Forward collision warning / camera-radar system", "Possible", "Stellantis ADAS equipment varies by model and package.")
        add("Adaptive cruise radar", "Possible", "Available on many trims/packages.")
        add("Blind spot monitoring", "Possible", "Common on many models.")
        add("ParkSense / parking assist", "Possible", "Common on many models.")

    else:
        add("Forward camera system", "Unknown / Verify", "Equipment could not be confirmed from decoded vehicle data.")
        add("Forward radar system", "Unknown / Verify", "Verify by build data, scan modules, or physical inspection.")
        add("Blind spot monitoring", "Unknown / Verify", "Verify by scan modules or sensor inspection.")
        add("Parking aid sensors", "Unknown / Verify", "Verify by scan modules or physical inspection.")

    return equipment