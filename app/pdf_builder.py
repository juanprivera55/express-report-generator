from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from pathlib import Path
from .dtc_library import lookup_dtc


def p(text, style):
    text = str(text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(text, style)


def bullet_list(items, style):
    return ListFlowable([ListItem(p(i, style), leftIndent=12) for i in items], bulletType="bullet", start="circle")


def build_pdf(scan: dict, adas_ops: list, output_path: str, company="EXPRESS DIAGNOSTICS", tagline="Precision. Safety. Confidence."):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=42, leftMargin=42, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("EDTitle", parent=styles["Title"], fontSize=22, leading=26, alignment=1, textColor=colors.HexColor("#111827"))
    subtitle = ParagraphStyle("EDSub", parent=styles["Heading2"], fontSize=12, leading=15, alignment=1, textColor=colors.HexColor("#374151"))
    h1 = ParagraphStyle("EDH1", parent=styles["Heading1"], fontSize=15, leading=18, spaceBefore=12, spaceAfter=8, textColor=colors.HexColor("#111827"))
    h2 = ParagraphStyle("EDH2", parent=styles["Heading2"], fontSize=12, leading=15, spaceBefore=8, spaceAfter=5, textColor=colors.HexColor("#1f2937"))
    body = ParagraphStyle("EDBody", parent=styles["BodyText"], fontSize=9.5, leading=13)
    small = ParagraphStyle("EDSmall", parent=styles["BodyText"], fontSize=8, leading=10, textColor=colors.HexColor("#6b7280"))
    warn = ParagraphStyle("EDWarn", parent=body, textColor=colors.HexColor("#991b1b"), fontName="Helvetica-Bold")

    story = []
    story.append(p(company, title))
    story.append(p("Advanced Vehicle Diagnostic & ADAS Analysis Report", subtitle))
    story.append(Spacer(1, 0.15*inch))

    v = scan.get("vehicle", {})
    vehicle_rows = [
        ["Vehicle", v.get("vehicle", "Not detected")],
        ["VIN", v.get("vin", "Not detected")],
        ["Mileage", v.get("mileage", "Not detected")],
        ["Scan Date", v.get("date", "Not detected")],
        ["Report Type", "DTC Explanation + ADAS Operations Review"],
    ]
    t = Table(vehicle_rows, colWidths=[1.55*inch, 4.85*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0,0), (0,-1), colors.white),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("BACKGROUND", (1,0), (1,-1), colors.HexColor("#f9fafb")),
        ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#d1d5db")),
        ("PADDING", (0,0), (-1,-1), 7),
    ]))
    story.append(t)

    dtcs = scan.get("dtcs", [])
    modules = scan.get("modules", [])
    adas_modules = [m for m in modules if m.get("adas")]

    story.append(p("Executive Summary", h1))
    story.append(bullet_list([
        f"Detected DTC count: {len(dtcs)}",
        f"ADAS-related modules identified: {len(adas_modules)}",
        "This report explains detected fault codes, likely causes, recommended repair direction, and ADAS operations that should be verified according to OEM procedures.",
        "A cleared code does not prove the repair is complete. Final confirmation requires inspection, calibration where required, post-scan, and functional validation."
    ], body))

    story.append(p("ADAS Operations Needed / Recommended", h1))
    story.append(bullet_list(adas_ops, body))

    if adas_modules:
        story.append(p("ADAS Modules Detected", h2))
        adas_rows = [["Module", "Description"]] + [[m.get("abbr",""), m.get("name","")] for m in adas_modules]
        mt = Table(adas_rows, colWidths=[1.2*inch, 5.2*inch])
        mt.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e5e7eb")),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#d1d5db")),
            ("PADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(mt)

    story.append(p("Detected DTCs & Professional Analysis", h1))
    if not dtcs:
        story.append(p("No DTCs were detected from the uploaded/pasted scan text. If this scan is image-only and OCR missed the codes, paste the DTC section into the text box and generate again.", warn))
    else:
        for idx, d in enumerate(dtcs, 1):
            info = lookup_dtc(d["code"])
            story.append(p(f"{idx}. {d['code']} — {info.get('title')}", h2))
            story.append(p(f"<b>Module:</b> {d.get('module','Unknown')}", body))
            story.append(p(f"<b>Scan Description:</b> {d.get('description','')}", body))
            story.append(p(f"<b>What this means:</b> {info.get('meaning')}", body))
            story.append(p("<b>Potential Causes:</b>", body))
            story.append(bullet_list(info.get("causes", []), body))
            story.append(p("<b>Potential Fixes / Next Steps:</b>", body))
            story.append(bullet_list(info.get("fixes", []), body))
            story.append(p(f"<b>ADAS / Safety Impact:</b> {info.get('adas')}", body))
            story.append(Spacer(1, 0.08*inch))

    story.append(p("Shop / Insurance Statement", h1))
    story.append(p("This document is intended to support repair planning and post-repair validation. DTC analysis should be paired with OEM service information, diagnostic testing, required calibrations, post-scan documentation, and a final road test where applicable.", body))
    story.append(Spacer(1, 0.2*inch))
    story.append(p(f"{company} — {tagline}", small))

    doc.build(story)
    return output_path
