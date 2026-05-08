from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from pathlib import Path
import uuid

from app.scan_parser import extract_text_from_pdf, parse_scan_text
from app.report_builder import build_pdf_report
from app.unknown_dtc_tracker import track_unknown_dtcs

app = FastAPI()

UPLOAD_DIR = Path("uploads")
REPORT_DIR = Path("generated_reports")
UPLOAD_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <body style="font-family:Arial; max-width:900px; margin:40px auto; padding:20px;">
        <h1>Express Diagnostics Report Generator</h1>
        <p>Upload a scan report and add job details before generating the customer or insurance report.</p>

        <form id="form">
            <h3>Scan Upload</h3>
            <input type="file" id="file" accept=".pdf" required>

            <h3>Report Version</h3>
            <select id="report_type">
                <option value="customer">Customer Ready Report</option>
                <option value="insurance">Insurance / Repair Documentation Report</option>
            </select>

            <h3>Editable Intake Fields</h3>

            <label>Customer Name</label><br>
            <input id="customer_name" style="width:100%; padding:8px;"><br><br>

            <label>Repair Order / RO Number</label><br>
            <input id="ro_number" style="width:100%; padding:8px;"><br><br>

            <label>Insurance Company</label><br>
            <input id="insurance_company" style="width:100%; padding:8px;"><br><br>

            <label>Claim Number</label><br>
            <input id="claim_number" style="width:100%; padding:8px;"><br><br>

            <label>Technician</label><br>
            <input id="technician" style="width:100%; padding:8px;"><br><br>

            <label>Repair Facility / Shop</label><br>
            <input id="repair_facility" style="width:100%; padding:8px;"><br><br>

            <label>Primary Impact Area</label><br>
            <select id="impact_area" style="width:100%; padding:8px;">
                <option value="">Not specified</option>
                <option value="front">Front Impact</option>
                <option value="rear">Rear Impact</option>
                <option value="left_side">Left Side Impact</option>
                <option value="right_side">Right Side Impact</option>
                <option value="roof_glass">Roof / Windshield / Glass</option>
                <option value="suspension_steering">Suspension / Steering</option>
                <option value="undercarriage">Undercarriage</option>
                <option value="multiple">Multiple Impact Areas</option>
            </select><br><br>

            <label>Technician Notes</label><br>
            <textarea id="technician_notes" style="width:100%; height:90px; padding:8px;"></textarea><br><br>

            <button type="button" onclick="generatePdf()">Generate PDF Report</button>
            <button type="button" onclick="debugText()">View Extracted Text</button>

            <br><br>
            <a href="/unknown-dtcs" target="_blank">
                <button type="button">Download Unknown DTC Database</button>
            </a>
        </form>

        <p id="status"></p>
        <pre id="output" style="text-align:left; margin-top:30px; white-space:pre-wrap; background:#f5f5f5; padding:15px;"></pre>

        <script>
        async function sendFile(endpoint) {
            const fileInput = document.getElementById("file");
            const file = fileInput.files[0];

            const formData = new FormData();
            formData.append("file", file);
            formData.append("report_type", document.getElementById("report_type").value);
            formData.append("customer_name", document.getElementById("customer_name").value);
            formData.append("ro_number", document.getElementById("ro_number").value);
            formData.append("insurance_company", document.getElementById("insurance_company").value);
            formData.append("claim_number", document.getElementById("claim_number").value);
            formData.append("technician", document.getElementById("technician").value);
            formData.append("repair_facility", document.getElementById("repair_facility").value);
            formData.append("impact_area", document.getElementById("impact_area").value);
            formData.append("technician_notes", document.getElementById("technician_notes").value);

            return await fetch(endpoint, {
                method: "POST",
                body: formData
            });
        }

        async function generatePdf() {
            document.getElementById("status").textContent = "Generating report...";

            const res = await sendFile("/upload");

            if (!res.ok) {
                const errorText = await res.text();
                document.getElementById("status").textContent = "Error generating report.";
                document.getElementById("output").textContent = errorText;
                return;
            }

            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);

            const reportType = document.getElementById("report_type").value;
            const filename = reportType === "insurance"
                ? "Express_Diagnostics_Insurance_Report.pdf"
                : "Express_Diagnostics_Customer_Report.pdf";

            const a = document.createElement("a");
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();

            document.getElementById("status").textContent = "Report downloaded.";
        }

        async function debugText() {
            document.getElementById("status").textContent = "Reading extracted text...";

            const res = await sendFile("/debug-text");
            const text = await res.text();

            document.getElementById("output").textContent = text;
            document.getElementById("status").textContent = "Extracted text displayed below.";
        }
        </script>
    </body>
    </html>
    """


@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    report_type: str = Form("customer"),
    customer_name: str = Form(""),
    ro_number: str = Form(""),
    insurance_company: str = Form(""),
    claim_number: str = Form(""),
    technician: str = Form(""),
    repair_facility: str = Form(""),
    impact_area: str = Form(""),
    technician_notes: str = Form("")
):
    file_id = str(uuid.uuid4())
    upload_path = UPLOAD_DIR / f"{file_id}.pdf"
    report_path = REPORT_DIR / f"Express_Diagnostics_Report_{file_id}.pdf"

    with open(upload_path, "wb") as f:
        f.write(await file.read())

    raw_text = extract_text_from_pdf(str(upload_path))
    parsed = parse_scan_text(raw_text)

    parsed["intake"] = {
        "customer_name": customer_name or "Not provided",
        "ro_number": ro_number or "Not provided",
        "insurance_company": insurance_company or "Not provided",
        "claim_number": claim_number or "Not provided",
        "technician": technician or "Not provided",
        "repair_facility": repair_facility or "Not provided",
        "impact_area": impact_area or "Not specified",
        "technician_notes": technician_notes or "None provided"
    }

    track_unknown_dtcs(parsed)

    build_pdf_report(parsed, str(report_path), report_type=report_type)

    filename = (
        "Express_Diagnostics_Insurance_Report.pdf"
        if report_type == "insurance"
        else "Express_Diagnostics_Customer_Report.pdf"
    )

    return FileResponse(
        path=str(report_path),
        filename=filename,
        media_type="application/pdf"
    )


@app.post("/debug-text")
async def debug_text(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    upload_path = UPLOAD_DIR / f"debug_{file_id}.pdf"

    with open(upload_path, "wb") as f:
        f.write(await file.read())

    raw_text = extract_text_from_pdf(str(upload_path))

    return PlainTextResponse(raw_text[:12000])


@app.get("/unknown-dtcs")
async def download_unknown_dtcs():
    path = Path("unknown_dtcs.csv")

    if not path.exists():
        path.write_text(
            "timestamp,vehicle,vin,make_model,ro_number,impact_area,module,code,description,reviewed,meaning,possible_causes,recommended_fixes,adas_impact\n",
            encoding="utf-8"
        )

    return FileResponse(
        path=str(path),
        filename="unknown_dtcs.csv",
        media_type="text/csv"
    )