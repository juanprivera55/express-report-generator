from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, Image, KeepTogether
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from app.dtc_library import lookup_dtc
from app.adas_rules import detect_adas_operations, impact_area_label
from app.adas_equipment import detect_probable_adas_equipment
from app.oem_calibration_matrix import build_oem_calibration_matrix


LOGO_PATH = "assets/logo.png"

BRAND_RED = colors.HexColor("#C40000")
DARK = colors.HexColor("#111111")
DARK_2 = colors.HexColor("#1F2937")
LIGHT_GRAY = colors.HexColor("#F3F4F6")
MID_GRAY = colors.HexColor("#D1D5DB")
TEXT_GRAY = colors.HexColor("#374151")
GREEN = colors.HexColor("#16803C")
YELLOW = colors.HexColor("#B7791F")
RED = colors.HexColor("#B91C1C")
BLUE = colors.HexColor("#1D4ED8")


def p(text, style):
    return Paragraph(str(text).replace("\n", "<br/>"), style)


def severity_for_dtc(code, module, desc):
    text = f"{code} {module} {desc}".upper()

    if any(x in text for x in ["CAMERA", "RADAR", "IPMA", "IPMB", "KAFAS", "DISTRONIC", "ADAS", "FORWARD", "LANE"]):
        return "ADAS", RED

    if code.upper().startswith("U") or "COMMUNICATION" in text or "GATEWAY" in text:
        return "NETWORK", YELLOW

    if any(x in text for x in ["ABS", "STABILITY", "BRAKE", "STEERING", "RESTRAINT", "AIRBAG", "RCM", "SRS"]):
        return "SAFETY", RED

    if code.upper().startswith("P"):
        return "POWERTRAIN", BLUE

    if code.upper().startswith("B"):
        return "BODY", YELLOW

    if code.upper().startswith("C"):
        return "CHASSIS", YELLOW

    return "REVIEW", TEXT_GRAY


def calibration_status(adas_operations):
    joined = " ".join(adas_operations).lower()

    if any(x in joined for x in ["calibration required", "camera calibration", "radar calibration", "aiming verification"]):
        return "Calibration Review Recommended", YELLOW

    if any(x in joined for x in ["verification", "validation", "adas"]):
        return "System Verification Recommended", YELLOW

    return "No ADAS Calibration Flag Detected", GREEN


def build_badge(text, bg_color):
    badge_style = ParagraphStyle(
        "Badge",
        fontSize=7,
        leading=9,
        textColor=colors.white,
        alignment=1,
        fontName="Helvetica-Bold"
    )

    table = Table([[p(text, badge_style)]], colWidths=[72])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_color),
        ("BOX", (0, 0), (-1, -1), 0.25, bg_color),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def make_section_header(title, styles):
    title_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontSize=12,
        leading=14,
        textColor=colors.white,
        fontName="Helvetica-Bold"
    )

    t = Table([[p(title.upper(), title_style)]], colWidths=[510])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_2),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


def make_info_table(rows, table_label, table_text):
    data = [[p(label, table_label), p(value, table_text)] for label, value in rows]
    t = Table(data, colWidths=[130, 380])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
        ("GRID", (0, 0), (-1, -1), 0.4, MID_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def build_pdf_report(data, output_path, report_type="customer"):
    dtcs = data.get("dtcs", [])
    vehicle_info = data.get("vehicle_info", {})
    intake = data.get("intake", {})

    impact_area = intake.get("impact_area", "")
    impact_label = impact_area_label(impact_area)

    adas_equipment = detect_probable_adas_equipment(vehicle_info)

    oem_matrix = build_oem_calibration_matrix(
        vehicle_info,
        dtcs,
        adas_equipment,
        impact_area
    )

    adas_operations = detect_adas_operations(
        dtcs,
        impact_area=impact_area,
        vehicle_info=vehicle_info
    )

    is_insurance = report_type == "insurance"

    report_title = (
        "Insurance / Repair Documentation Report"
        if is_insurance
        else "Customer Ready Diagnostic & ADAS Report"
    )

    calibration_flag, calibration_color = calibration_status(adas_operations)
    has_dtcs = len(dtcs) > 0
    has_adas_flag = calibration_flag != "No ADAS Calibration Flag Detected"

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=28,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    normal = ParagraphStyle(
        "NormalFixed",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        textColor=TEXT_GRAY
    )

    small = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontSize=7.5,
        leading=9,
        textColor=TEXT_GRAY
    )

    table_text = ParagraphStyle(
        "TableText",
        parent=styles["BodyText"],
        fontSize=8.3,
        leading=10.5,
        textColor=TEXT_GRAY
    )

    table_label = ParagraphStyle(
        "TableLabel",
        parent=styles["BodyText"],
        fontSize=8.3,
        leading=10.5,
        textColor=DARK,
        fontName="Helvetica-Bold"
    )

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=14,
        leading=17,
        textColor=colors.white,
        alignment=1,
        fontName="Helvetica-Bold"
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=10,
        textColor=colors.white,
        alignment=1
    )

    story = []

    # HEADER
    try:
        logo = Image(LOGO_PATH, width=2.6 * inch, height=1.1 * inch)
    except Exception:
        logo = p("<b><font color='white'>EXPRESS DIAGNOSTICS</font></b>", title_style)

    header_right = Table([
        [p(f"<b>{report_title.upper()}</b>", title_style)],
        [p("Precision. Safety. Confidence.", subtitle_style)],
    ], colWidths=[280])

    header = Table([[logo, header_right]], colWidths=[220, 300])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LINEBELOW", (0, 0), (-1, -1), 3, BRAND_RED),
    ]))

    story.append(header)
    story.append(Spacer(1, 12))

    # SUMMARY CARDS
    summary_card_style = ParagraphStyle(
        "SummaryCard",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10,
        textColor=DARK,
        alignment=1
    )

    summary_value_style = ParagraphStyle(
        "SummaryValue",
        parent=styles["BodyText"],
        fontSize=11,
        leading=13,
        textColor=DARK,
        alignment=1,
        fontName="Helvetica-Bold"
    )

    card_data = [
        [
            p("DTCs Found", summary_card_style),
            p("ADAS Review", summary_card_style),
            p("Calibration Status", summary_card_style),
            p("Impact Area", summary_card_style),
        ],
        [
            p(str(len(dtcs)), summary_value_style),
            p("Yes" if has_adas_flag else "Review", summary_value_style),
            p(calibration_flag, summary_value_style),
            p(impact_label, summary_value_style),
        ]
    ]

    cards = Table(card_data, colWidths=[127.5, 127.5, 127.5, 127.5])
    cards.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GRAY),
        ("BACKGROUND", (0, 1), (-1, 1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, MID_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(cards)
    story.append(Spacer(1, 12))

    # JOB INFO
    story.append(make_section_header("Job / Intake Information", styles))
    story.append(Spacer(1, 6))

    intake_rows = [
        ("Customer Name", intake.get("customer_name", "Not provided")),
        ("RO Number", intake.get("ro_number", "Not provided")),
        ("Insurance Company", intake.get("insurance_company", "Not provided")),
        ("Claim Number", intake.get("claim_number", "Not provided")),
        ("Technician", intake.get("technician", "Not provided")),
        ("Repair Facility", intake.get("repair_facility", "Not provided")),
        ("Primary Impact Area", impact_label),
    ]
    story.append(make_info_table(intake_rows, table_label, table_text))
    story.append(Spacer(1, 12))

    # VEHICLE INFO
    story.append(make_section_header("Vehicle Information", styles))
    story.append(Spacer(1, 6))

    vehicle_rows = [
        ("Vehicle", vehicle_info.get("vehicle", "Not detected")),
        ("VIN", vehicle_info.get("vin", "Not detected")),
        ("Mileage", vehicle_info.get("mileage", "Not detected")),
        ("Scan Date", vehicle_info.get("scan_date", "Not detected")),
        ("Scan Type", vehicle_info.get("scan_type", "Diagnostic Scan")),
        ("Body Class", vehicle_info.get("body_class", "Unknown")),
        ("Engine", vehicle_info.get("engine", "Unknown")),
        ("Drive Type", vehicle_info.get("drive_type", "Unknown")),
    ]
    story.append(make_info_table(vehicle_rows, table_label, table_text))
    story.append(Spacer(1, 12))

    # PROBABLE ADAS EQUIPMENT
    story.append(make_section_header("Probable ADAS Equipment", styles))
    story.append(Spacer(1, 6))

    adas_intro = """
    The following systems are likely equipped or potentially equipped based on VIN decoding,
    manufacturer patterns, trim analysis, and detected vehicle information.
    Final equipment confirmation should always be verified using OEM build data,
    scan tool module identification, or physical inspection.
    """

    adas_intro_table = Table([[p(adas_intro, normal)]], colWidths=[510])
    adas_intro_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#93C5FD")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(adas_intro_table)
    story.append(Spacer(1, 8))

    equipment_rows = []
    for item in adas_equipment:
        confidence = item.get("confidence", "Unknown")
        name = item.get("name", "Unknown System")
        reason = item.get("reason", "")

        if confidence == "Likely":
            conf_color = GREEN
        elif confidence == "Possible":
            conf_color = YELLOW
        else:
            conf_color = TEXT_GRAY

        equipment_rows.append([
            build_badge(confidence.upper(), conf_color),
            p(f"<b>{name}</b><br/>{reason}", table_text)
        ])

    if equipment_rows:
        equipment_table = Table(equipment_rows, colWidths=[110, 400])
        equipment_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.35, MID_GRAY),
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(equipment_table)

    story.append(Spacer(1, 12))

    # SCAN SUMMARY
    story.append(make_section_header("Scan Summary", styles))
    story.append(Spacer(1, 6))

    if is_insurance:
        summary_text = (
            "This report documents diagnostic trouble codes, affected systems, primary impact area, "
            "and recommended ADAS-related operations for repair planning, documentation, and post-repair verification."
        )
    else:
        summary_text = (
            "This report explains the fault codes found during the scan and identifies safety-related systems "
            "that may require inspection, repair, calibration, or verification."
        )

    scan_summary_table = Table([[p(summary_text, normal)]], colWidths=[510])
    scan_summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF7ED") if has_dtcs else colors.HexColor("#ECFDF5")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#FDBA74") if has_dtcs else colors.HexColor("#86EFAC")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(scan_summary_table)
    story.append(Spacer(1, 12))

    # DTC SECTION
    story.append(make_section_header("Detected DTCs & Professional Analysis", styles))
    story.append(Spacer(1, 6))

    if not dtcs:
        story.append(p("No DTCs were detected in this scan report.", normal))
        story.append(Spacer(1, 10))

    for d in dtcs:
        module = d.get("module", "Unknown Module")
        code = d.get("code", "")
        desc = d.get("description", "")
        intel = lookup_dtc(code)

        severity, sev_color = severity_for_dtc(code, module, desc)

        causes = "<br/>".join([f"• {x}" for x in intel["causes"]])
        fixes = "<br/>".join([f"• {x}" for x in intel["fixes"]])

        impact_col_label = "ADAS / Safety / Repair Impact" if is_insurance else "Safety System Impact"
        action_label = "Recommended Repair Documentation Actions" if is_insurance else "Recommended Next Steps"

        dtc_header = Table([
            [
                p(f"<b>{code}</b>", ParagraphStyle("DtcCode", parent=table_label, fontSize=11, leading=13)),
                build_badge(severity, sev_color)
            ]
        ], colWidths=[430, 80])
        dtc_header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEE2E2") if severity in ["ADAS", "SAFETY"] else LIGHT_GRAY),
            ("BOX", (0, 0), (-1, -1), 0.5, MID_GRAY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        dtc_data = [
            [p("Module", table_label), p(module, table_text)],
            [p("Description", table_label), p(desc, table_text)],
            [p("What This Means", table_label), p(intel["meaning"], table_text)],
            [p("Possible Causes", table_label), p(causes, table_text)],
            [p(action_label, table_label), p(fixes, table_text)],
            [p(impact_col_label, table_label), p(intel["adas_impact"], table_text)],
        ]

        dtc_table = Table(dtc_data, colWidths=[130, 380])
        dtc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F9FAFB")),
            ("GRID", (0, 0), (-1, -1), 0.4, MID_GRAY),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ]))

        story.append(KeepTogether([dtc_header, dtc_table, Spacer(1, 10)]))

    # OEM CALIBRATION MATRIX
    story.append(make_section_header("OEM-Style Calibration Matrix", styles))
    story.append(Spacer(1, 6))

    matrix_intro = """
    The following recommendations were generated using VIN-based equipment analysis,
    scan results, detected modules, DTC activity, and selected impact area.
    These recommendations are intended to support OEM repair planning and calibration review.
    Final repair requirements must always be verified using manufacturer repair procedures.
    """

    matrix_intro_table = Table([[p(matrix_intro, normal)]], colWidths=[510])
    matrix_intro_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F3FF")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#C4B5FD")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(matrix_intro_table)
    story.append(Spacer(1, 8))

    matrix_rows = []
    for item in oem_matrix:
        confidence = item.get("confidence", "MODERATE")
        system = item.get("system", "Unknown")
        reason = item.get("reason", "")

        if confidence == "HIGH":
            conf_color = RED
        elif confidence == "MODERATE":
            conf_color = YELLOW
        else:
            conf_color = TEXT_GRAY

        matrix_rows.append([
            build_badge(confidence, conf_color),
            p(f"<b>{system}</b><br/>{reason}", table_text)
        ])

    if matrix_rows:
        matrix_table = Table(matrix_rows, colWidths=[110, 400])
        matrix_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.35, MID_GRAY),
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(matrix_table)
    else:
        story.append(p("No specific OEM-style calibration matrix items were generated based on the current scan and impact inputs.", normal))

    story.append(Spacer(1, 12))

    # ADAS / CALIBRATION SECTION
    story.append(make_section_header(
        "Calibration / ADAS Recommendation Engine"
        if is_insurance
        else "Recommended Safety System Checks",
        styles
    ))
    story.append(Spacer(1, 6))

    calibration_intro = (
        f"Primary impact area selected: <b>{impact_label}</b>. "
        "The following recommendations were generated from scan results, affected modules, DTCs, and impact-area logic."
    )

    cal_table = Table([[p(calibration_intro, normal)]], colWidths=[510])
    cal_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#93C5FD")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(cal_table)
    story.append(Spacer(1, 8))

    story.append(ListFlowable([
        ListItem(p(x, normal), leftIndent=12)
        for x in adas_operations
    ], bulletType="bullet"))
    story.append(Spacer(1, 12))

    # TECH NOTES
    notes = intake.get("technician_notes", "None provided")
    if notes and notes != "None provided":
        story.append(make_section_header("Technician Notes", styles))
        story.append(Spacer(1, 6))
        story.append(p(notes, normal))
        story.append(Spacer(1, 12))

    # STATEMENT
    if is_insurance:
        story.append(make_section_header("Repair Documentation Statement", styles))
        statement = """
        <b>Repair Documentation Statement:</b><br/>
        Diagnostic Trouble Codes, ADAS module concerns, impact area, and communication faults must be evaluated
        according to OEM repair procedures. Clearing codes alone does not confirm system integrity.
        Any affected ADAS, safety, camera, radar, steering, suspension, body, or network-related system
        should be verified through post-scan documentation, calibration when required, and functional road testing.
        """
    else:
        story.append(make_section_header("Customer Summary", styles))
        statement = """
        <b>Customer Note:</b><br/>
        This report explains the fault codes found during the scan in easier-to-understand language.
        Some systems may affect safety features such as cameras, parking sensors, blind spot monitoring,
        steering assist, braking systems, or collision avoidance features. Final repair decisions should
        be based on proper diagnostics and manufacturer repair procedures.
        """

    story.append(Spacer(1, 6))
    story.append(p(statement, normal))
    story.append(Spacer(1, 14))

    # FOOTER
    footer_table = Table([
        [
            p("<b>EXPRESS DIAGNOSTICS</b><br/>Precision. Safety. Confidence.", small),
            p("Generated automatically from scan data.<br/>Final procedures must be verified using OEM repair information.", small)
        ]
    ], colWidths=[255, 255])
    footer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("BOX", (0, 0), (-1, -1), 0.4, MID_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(footer_table)

    doc.build(story)