from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, Image
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from app.dtc_library import lookup_dtc
from app.adas_rules import detect_adas_operations, impact_area_label


LOGO_PATH = "assets/logo.png"


def p(text, style):
    return Paragraph(str(text).replace("\n", "<br/>"), style)


def build_pdf_report(data, output_path, report_type="customer"):
    dtcs = data.get("dtcs", [])
    vehicle_info = data.get("vehicle_info", {})
    intake = data.get("intake", {})

    impact_area = intake.get("impact_area", "")
    impact_label = impact_area_label(impact_area)

    adas_operations = detect_adas_operations(dtcs, impact_area=impact_area)

    is_insurance = report_type == "insurance"

    report_title = (
        "Insurance / Repair Documentation Report"
        if is_insurance
        else "Customer Ready Diagnostic & ADAS Report"
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    normal = ParagraphStyle(
        "NormalFixed",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12
    )

    table_text = ParagraphStyle(
        "TableText",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=11
    )

    table_label = ParagraphStyle(
        "TableLabel",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=11,
        fontName="Helvetica-Bold"
    )

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=14,
        leading=17,
        textColor=colors.white,
        alignment=1
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["BodyText"],
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=13,
        leading=15,
        textColor=colors.HexColor("#cc0000"),
        spaceBefore=14,
        spaceAfter=8
    )

    story = []

    # Header
    try:
        logo = Image(LOGO_PATH, width=2.65 * inch, height=1.15 * inch)
    except Exception:
        logo = p("<b><font color='white'>EXPRESS DIAGNOSTICS</font></b>", title_style)

    header_right = [
        [p(f"<b><font color='white'>{report_title.upper()}</font></b>", title_style)],
        [p("<font color='white'>Precision. Safety. Confidence.</font>", subtitle_style)],
    ]

    right_table = Table(header_right, colWidths=[260])

    header_table = Table(
        [[logo, right_table]],
        colWidths=[225, 295]
    )

    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#111111")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    story.append(header_table)
    story.append(Spacer(1, 14))

    # Intake / Job Info
    story.append(p("Job / Intake Information", section_style))

    intake_data = [
        [p("Customer Name", table_label), p(intake.get("customer_name", "Not provided"), table_text)],
        [p("RO Number", table_label), p(intake.get("ro_number", "Not provided"), table_text)],
        [p("Insurance Company", table_label), p(intake.get("insurance_company", "Not provided"), table_text)],
        [p("Claim Number", table_label), p(intake.get("claim_number", "Not provided"), table_text)],
        [p("Technician", table_label), p(intake.get("technician", "Not provided"), table_text)],
        [p("Repair Facility", table_label), p(intake.get("repair_facility", "Not provided"), table_text)],
        [p("Primary Impact Area", table_label), p(impact_label, table_text)],
    ]

    intake_table = Table(intake_data, colWidths=[125, 385])
    intake_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(intake_table)
    story.append(Spacer(1, 14))

    # Vehicle Info
    story.append(p("Vehicle Information", section_style))

    summary_data = [
        [p("Vehicle", table_label), p(vehicle_info.get("vehicle", "Not detected"), table_text)],
        [p("VIN", table_label), p(vehicle_info.get("vin", "Not detected"), table_text)],
        [p("Mileage", table_label), p(vehicle_info.get("mileage", "Not detected"), table_text)],
        [p("Scan Date", table_label), p(vehicle_info.get("scan_date", "Not detected"), table_text)],
        [p("Scan Type", table_label), p(vehicle_info.get("scan_type", "Diagnostic Scan"), table_text)],
        [p("DTCs Found", table_label), p(str(len(dtcs)), table_text)],
    ]

    summary_table = Table(summary_data, colWidths=[125, 385])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 14))

    # Scan Summary
    story.append(p("Scan Summary", section_style))

    if is_insurance:
        summary_text = (
            "This report documents diagnostic trouble codes, affected systems, primary impact area, "
            "and recommended ADAS-related operations for repair planning, insurance documentation, "
            "and post-repair verification."
        )
    else:
        summary_text = (
            "This report explains the fault codes found during the scan and identifies safety-related "
            "systems that may require additional inspection, repair, calibration, or verification."
        )

    story.append(p(summary_text, normal))
    story.append(Spacer(1, 10))

    # DTC Section
    story.append(p("Detected DTCs & Professional Analysis", section_style))

    if not dtcs:
        story.append(p("No DTCs were detected in this scan report.", normal))

    for d in dtcs:
        module = d.get("module", "Unknown Module")
        code = d.get("code", "")
        desc = d.get("description", "")
        intel = lookup_dtc(code)

        causes = "<br/>".join([f"• {x}" for x in intel["causes"]])
        fixes = "<br/>".join([f"• {x}" for x in intel["fixes"]])

        impact_col_label = "ADAS / Safety / Repair Impact" if is_insurance else "Safety System Impact"
        action_label = "Recommended Repair Documentation Actions" if is_insurance else "Recommended Next Steps"

        dtc_data = [
            [p("Module", table_label), p(module, table_text)],
            [p("DTC", table_label), p(code, table_text)],
            [p("Description", table_label), p(desc, table_text)],
            [p("What This Means", table_label), p(intel["meaning"], table_text)],
            [p("Possible Causes", table_label), p(causes, table_text)],
            [p(action_label, table_label), p(fixes, table_text)],
            [p(impact_col_label, table_label), p(intel["adas_impact"], table_text)],
        ]

        dtc_table = Table(dtc_data, colWidths=[130, 380])
        dtc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f9fafb")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))

        story.append(dtc_table)
        story.append(Spacer(1, 12))

    # Calibration Logic
    story.append(p(
        "Calibration / ADAS Recommendation Engine"
        if is_insurance
        else "Recommended Safety System Checks",
        section_style
    ))

    calibration_intro = (
        f"Primary impact area selected: <b>{impact_label}</b>. "
        "The following recommendations were generated from scan results, affected modules, DTCs, and impact-area logic."
    )

    story.append(p(calibration_intro, normal))
    story.append(Spacer(1, 8))

    story.append(ListFlowable([
        ListItem(p(x, normal), leftIndent=12)
        for x in adas_operations
    ], bulletType="bullet"))

    story.append(Spacer(1, 14))

    # Technician Notes
    notes = intake.get("technician_notes", "None provided")
    if notes and notes != "None provided":
        story.append(p("Technician Notes", section_style))
        story.append(p(notes, normal))
        story.append(Spacer(1, 12))

    # Statement
    if is_insurance:
        story.append(p("Insurance / Repair Documentation Statement", section_style))
        statement = """
        <b>Repair Documentation Statement:</b><br/>
        Diagnostic Trouble Codes, ADAS module concerns, impact area, and communication faults must be evaluated
        according to OEM repair procedures. Clearing codes alone does not confirm system integrity.
        Any affected ADAS, safety, camera, radar, steering, suspension, body, or network-related system
        should be verified through post-scan documentation, calibration when required, and functional
        road testing. This report supports repair planning, calibration justification, and final
        documentation of safety-related system review.
        """
    else:
        story.append(p("Customer Summary", section_style))
        statement = """
        <b>Customer Note:</b><br/>
        This report explains the fault codes found during the scan in easier-to-understand language.
        Some systems may affect safety features such as cameras, parking sensors, blind spot monitoring,
        steering assist, braking systems, or collision avoidance features. Final repair decisions should
        be based on proper diagnostics and manufacturer repair procedures.
        """

    story.append(p(statement, normal))
    story.append(Spacer(1, 18))

    story.append(p("<b>EXPRESS DIAGNOSTICS</b> — Precision. Safety. Confidence.", normal))

    doc.build(story)