import re
import fitz
import pytesseract
from PIL import Image
import io
import os
import shutil

if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract") or "/usr/bin/tesseract"


STANDARD_DTC_RE = re.compile(
    r"\b([PCBU][0-9A-F]{4}(?::[0-9A-F]{2})?(?:-[0-9A-F]{2})?)\b\s*([^\n\r]*)",
    re.I
)

EURO_DTC_RE = re.compile(
    r"\b([0-9]{4,6}|[A-F0-9]{4}|[PCBU][0-9A-F]{5,7})\b\s*([^\n\r]*)",
    re.I
)

MODULE_RE = re.compile(r"^([A-Za-z0-9\-\/ ]{2,25})\(([^\)]*)\)", re.I)

VIN_LINE_RE = re.compile(r"VIN\s*[:\-]?\s*([A-Z0-9]{15,20})", re.I)
VIN_ANY_RE = re.compile(r"\b([A-HJ-NPR-Z0-9]{17})\b", re.I)

MILEAGE_PATTERNS = [
    re.compile(r"Odometer Reading\s*[:\-]?\s*([0-9,.]+)\s*miles?", re.I),
    re.compile(r"(?:Mileage|Odometer|Miles|Vehicle Mileage)\s*[:\-]?\s*([0-9,.]+)", re.I),
]

DATE_PATTERNS = [
    re.compile(r"Test Time\s*[:\-]?\s*([0-9]{4}[\/\-][0-9]{1,2}[\/\-][0-9]{1,2})", re.I),
    re.compile(r"(?:Date|Scan Date|Report Date|Created)\s*[:\-]?\s*([0-9]{1,4}[\/\-][0-9]{1,2}[\/\-][0-9]{1,4})", re.I),
]

VEHICLE_PATTERNS = [
    re.compile(r"(20[0-9]{2})\s+MY\(Model Year\)\s*/\s*([A-Za-z]+)\s*/\s*([A-Za-z0-9\- ]+)", re.I),
    re.compile(r"(20[0-9]{2})\s+MY\(Model Year\)\s+([A-Za-z]+)\s+([A-Za-z0-9\- ]+)", re.I),
    re.compile(r"\b(20[0-9]{2}|19[8-9][0-9])\s+([A-Za-z]+)\s+([A-Za-z0-9\- ]{2,40})", re.I),
]


def clean_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def normalize_possible_vin(vin: str) -> str:
    vin = vin.upper().strip().replace(" ", "")
    if len(vin) == 17 and vin.startswith("I"):
        vin = "1" + vin[1:]
    return vin


def extract_text_from_pdf(path: str) -> str:
    doc = fitz.open(path)

    text_parts = []
    for page in doc:
        text_parts.append(page.get_text("text") or "")

    combined_text = clean_text("\n".join(text_parts))

    if len(combined_text) > 50:
        return combined_text

    ocr_parts = []
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img, config="--psm 6")
        ocr_parts.append(text)

    return clean_text("\n".join(ocr_parts))


def extract_vehicle_info(text: str):
    vin = "Not detected"
    mileage = "Not detected"
    scan_date = "Not detected"
    vehicle = "Not detected"

    vin_match = VIN_LINE_RE.search(text)
    if vin_match:
        vin = normalize_possible_vin(vin_match.group(1))
    else:
        any_vin = VIN_ANY_RE.search(text)
        if any_vin:
            vin = normalize_possible_vin(any_vin.group(1))

    for pattern in MILEAGE_PATTERNS:
        match = pattern.search(text)
        if match:
            mileage = match.group(1).replace(",", "")
            break

    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if match:
            scan_date = match.group(1)
            break

    for pattern in VEHICLE_PATTERNS:
        match = pattern.search(text)
        if match:
            year = match.group(1).strip()
            make = match.group(2).strip()
            model = match.group(3).strip().strip("/")
            model = re.sub(r"\s+", " ", model)
            vehicle = f"{year} {make} {model}"
            break

    return {
        "vin": vin,
        "vehicle": vehicle,
        "mileage": mileage,
        "scan_date": scan_date,
        "scan_type": detect_scan_type(text)
    }


def detect_scan_type(text: str):
    lower = text.lower()

    if ("pre-scan report" in lower or "pre scan" in lower) and ("post-scan report" in lower or "post scan" in lower):
        return "Pre & Post Scan"
    if "pre-scan report" in lower or "pre scan" in lower:
        return "Pre-Scan"
    if "post-scan report" in lower or "post scan" in lower:
        return "Post-Scan"

    return "Diagnostic Scan"


def looks_like_bad_code(code: str):
    code = code.upper().strip()

    bad_words = {
        "PAGE", "TIME", "DATE", "NAME", "NOTE", "TEST", "SCAN",
        "VIN", "HTTP", "WWW", "AUTO", "TRUE", "FALSE"
    }

    if code in bad_words:
        return True

    # Prevent years from being captured as DTCs
    if code.isdigit():
        number = int(code)
        if 1980 <= number <= 2099:
            return True

    return False


def line_is_dtc_context(line: str, in_dtc_section: bool):
    lower = line.lower()

    if in_dtc_section:
        return True

    context_words = [
        "dtc",
        "fault",
        "trouble code",
        "description",
        "status",
        "stored",
        "current",
        "history",
        "intermittent",
        "cmdtcs"
    ]

    return any(word in lower for word in context_words)


def parse_scan_text(text: str):
    dtcs = []
    seen = set()
    current_module = "Unknown Module"
    in_dtc_section = False

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        if "pre-scan dtc" in lower or "post-scan dtc" in lower or "dtc description status" in lower:
            in_dtc_section = True

        if "technician notes" in lower or "vehicle information" in lower or "customer information" in lower:
            in_dtc_section = False

        module_match = MODULE_RE.match(line)
        if module_match:
            current_module = f"{module_match.group(1).strip()} ({module_match.group(2).strip()})"

        matches = list(STANDARD_DTC_RE.finditer(line))

        # European/manufacturer numeric codes only count inside a DTC/fault context
        if not matches and line_is_dtc_context(line, in_dtc_section):
            matches = list(EURO_DTC_RE.finditer(line))

        for match in matches:
            code = match.group(1).upper().strip()
            desc = match.group(2).strip()

            if looks_like_bad_code(code):
                continue

            key = f"{current_module}-{code}"

            if key not in seen:
                dtcs.append({
                    "module": current_module,
                    "code": code,
                    "description": desc if desc else "Manufacturer-specific fault code detected"
                })
                seen.add(key)

    return {
        "vehicle_info": extract_vehicle_info(text),
        "dtcs": dtcs
    }