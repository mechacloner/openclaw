import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle

# Register fonts
pdfmetrics.registerFont(TTFont("NotoSans", "/tmp/NotoSansSC-Regular.ttf"))
pdfmetrics.registerFont(TTFont("NotoSansBold", "/tmp/NotoSansSC-Bold.ttf"))

W, H = A4  # 595.27 x 841.89 pt

# Brand Colors from JIAER Logo
BRAND_GREEN = colors.HexColor("#1E6B3A")
BRAND_DARK_GREEN = colors.HexColor("#134626")
BRAND_RED = colors.HexColor("#DE380D")
BRAND_ORANGE = colors.HexColor("#EE761B")
BRAND_LIGHT_BLUE = colors.HexColor("#EEF7FE")
BRAND_ACCENT_BG = colors.HexColor("#F5F9FC")
DARK_INK = colors.HexColor("#121820")
MUTED_INK = colors.HexColor("#4A5568")
BORDER_GRAY = colors.HexColor("#D2DCE6")

def draw_wrapped_text(c, text, x, y, max_w, font_name, font_size, leading, color):
    style = ParagraphStyle(
        name="custom",
        fontName=font_name,
        fontSize=font_size,
        leading=leading,
        textColor=color,
    )
    p = Paragraph(text, style)
    w, h = p.wrap(max_w, 500)
    p.drawOn(c, x, y - h)
    return y - h

def build_pdf(out_path):
    c = canvas.Canvas(out_path, pagesize=A4)
    c.setTitle("JIAER MT51-WS-1 Technical Datasheet - 佳尔橡塑")

    # 1. Page background & top tricolor bar
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    c.setFillColor(BRAND_GREEN)
    c.rect(0, H - 8, W * 0.45, 8, stroke=0, fill=1)
    c.setFillColor(BRAND_RED)
    c.rect(W * 0.45, H - 8, W * 0.28, 8, stroke=0, fill=1)
    c.setFillColor(BRAND_ORANGE)
    c.rect(W * 0.73, H - 8, W * 0.27, 8, stroke=0, fill=1)

    # 2. Header Banner
    header_h = 104
    header_y = H - 8 - header_h
    c.setFillColor(BRAND_LIGHT_BLUE)
    c.rect(0, header_y, W, header_h, stroke=0, fill=1)

    c.setStrokeColor(BRAND_GREEN)
    c.setLineWidth(1.5)
    c.line(34, header_y, W - 34, header_y)

    logo_path = "/home/user/openclaw/assets/jiaer_logo_transparent.png"
    wm_path = "/home/user/openclaw/assets/jiaer_watermark.png"

    # Full-color Brand Logo on Left of Header
    c.drawImage(logo_path, 34, header_y + 10, width=84, height=84, mask="auto")

    # Header Text in Center
    c.setFillColor(BRAND_GREEN)
    c.setFont("NotoSansBold", 9.5)
    c.drawString(128, header_y + 75, "JIAER RUBBER & PLASTIC  |  佳尔橡塑 · 高性能工业橡塑解决方案")

    c.setFillColor(DARK_INK)
    c.setFont("NotoSansBold", 20)
    c.drawString(128, header_y + 47, "MT51-WS-1  TECHNICAL DATASHEET")

    c.setFillColor(BRAND_RED)
    c.setFont("NotoSansBold", 10.2)
    c.drawString(128, header_y + 27, "High-Performance Weather-Resistant & Water-Sealing Elastomer")

    c.setFillColor(MUTED_INK)
    c.setFont("NotoSans", 8.2)
    c.drawString(128, header_y + 11, "Doc Ref: JE-TDS-MT51-WS-1   |   Rev: 2026.10   |   Grade: Industrial / OEM Certified")

    # Brand Watermark BESIDE Header Text (Right side)
    c.drawImage(wm_path, W - 114, header_y + 10, width=82, height=82, mask="auto")

    # 3. Lucrative Executive Value Proposition Box + Dedicated Brand Watermark Panel Beside Text
    sec1_top = header_y - 14
    sec1_h = 156
    sec1_y = sec1_top - sec1_h

    c.setFillColor(BRAND_ACCENT_BG)
    c.setStrokeColor(BORDER_GRAY)
    c.setLineWidth(0.8)
    c.roundRect(34, sec1_y, W - 68, sec1_h, 6, stroke=1, fill=1)

    c.setFillColor(BRAND_GREEN)
    c.roundRect(34, sec1_y, 5, sec1_h, 2, stroke=0, fill=1)

    # Dedicated Brand Watermark Panel BESIDE the text on the right side of the card
    wm_box_w = 142
    wm_box_x = W - 34 - wm_box_w - 10
    c.saveState()
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.Color(0.12, 0.42, 0.23, alpha=0.22))
    c.setLineWidth(0.9)
    c.roundRect(wm_box_x, sec1_y + 10, wm_box_w, sec1_h - 20, 6, stroke=1, fill=1)
    c.restoreState()

    c.drawImage(wm_path, wm_box_x + 8, sec1_y + 16, width=126, height=126, mask="auto")

    # Left side text area width (strictly to the left of wm_box_x)
    text_max_w = wm_box_x - 50 - 12

    c.setFillColor(BRAND_DARK_GREEN)
    c.setFont("NotoSansBold", 11.2)
    c.drawString(50, sec1_top - 21, "EXECUTIVE PRODUCT OVERVIEW & COMMERCIAL ADVANTAGE")

    overview_text = (
        "<b>JIAER MT51-WS-1</b> is an advanced, commercial-grade polymer & elastomer "
        "formulation engineered by <b>Jiaer Rubber & Plastic (佳尔橡塑 · JIAERXIANGSU)</b> "
        "for demanding industrial sealing, waterproofing, and insulation applications. "
        "Built to maximize operational uptime and lower lifecycle maintenance costs, "
        "MT51-WS-1 delivers superior tensile resilience and hydrophobic weather sealing."
    )
    curr_y = draw_wrapped_text(c, overview_text, 50, sec1_top - 28, text_max_w, "NotoSans", 8.9, 12.8, DARK_INK)

    bullets = [
        ("● Maximum ROI & Longevity:", "Extended service life under continuous compression & UV."),
        ("● Process & OEM Efficiency:", "Consistent rheology for high-yield extrusion & molding."),
        ("● Zero-Leakage Reliability:", "Hydrophobic WS-1 barrier preventing moisture ingress."),
    ]
    by = curr_y - 13
    for b_title, b_desc in bullets:
        c.setFillColor(BRAND_RED)
        c.setFont("NotoSansBold", 8.3)
        c.drawString(50, by, b_title)
        c.setFillColor(DARK_INK)
        c.setFont("NotoSans", 8.3)
        c.drawString(168, by, b_desc)
        by -= 13.5

    # 4. Key Performance Highlights (4 Lucrative Metric Cards)
    cards_top = sec1_y - 12
    card_h = 52
    cards_y = cards_top - card_h
    card_w = (W - 68 - 3 * 10) / 4.0

    metrics = [
        ("TENSILE STRENGTH", "≥ 14.5 MPa", "High Mechanical Integrity", BRAND_GREEN),
        ("ELONGATION AT BREAK", "≥ 420 %", "Superior Elastic Recovery", BRAND_RED),
        ("OPERATING TEMP", "-40°C to +125°C", "All-Climate Thermal Stability", BRAND_ORANGE),
        ("WATER RESISTANCE", "WS-1 Grade", "Hydrophobic Sealing Barrier", BRAND_GREEN),
    ]
    for idx, (m_label, m_val, m_sub, m_col) in enumerate(metrics):
        cx_card = 34 + idx * (card_w + 10)
        c.setFillColor(colors.white)
        c.setStrokeColor(BORDER_GRAY)
        c.setLineWidth(0.8)
        c.roundRect(cx_card, cards_y, card_w, card_h, 5, stroke=1, fill=1)
        c.setFillColor(m_col)
        c.rect(cx_card, cards_y + card_h - 4, card_w, 4, stroke=0, fill=1)

        c.setFillColor(MUTED_INK)
        c.setFont("NotoSansBold", 7.3)
        c.drawCentredString(cx_card + card_w / 2, cards_y + 35, m_label)

        c.setFillColor(DARK_INK)
        c.setFont("NotoSansBold", 12.5)
        c.drawCentredString(cx_card + card_w / 2, cards_y + 18, m_val)

        c.setFillColor(m_col)
        c.setFont("NotoSans", 7.3)
        c.drawCentredString(cx_card + card_w / 2, cards_y + 6, m_sub)

    # 5. Technical Specifications Table + Brand Watermark Beside Table
    sec2_top = cards_y - 18
    c.setFillColor(BRAND_DARK_GREEN)
    c.setFont("NotoSansBold", 11)
    c.drawString(34, sec2_top, "TECHNICAL SPECIFICATIONS & PHYSICAL PROPERTIES (MT51-WS-1)")

    c.setFillColor(MUTED_INK)
    c.setFont("NotoSans", 7.8)
    c.drawRightString(W - 34, sec2_top, "*Standard Lab Conditions: 23°C ± 2°C, 50% RH")

    table_data = [
        ["Property / Parameter", "Test Standard", "Unit", "MT51-WS-1 Specification"],
        ["Material Classification", "JIAER / ISO 1629", "—", "Modified Weather-Sealing Elastomer (WS-1)"],
        ["Appearance & Color", "Visual Inspection", "—", "Smooth Homogeneous / Black or Custom OEM"],
        ["Specific Gravity / Density", "ASTM D297 / ISO 2781", "g/cm³", "1.18 ± 0.03"],
        ["Hardness (Shore A)", "ASTM D2240 / ISO 7619", "Shore A", "60 ± 5 (Customizable 50–75)"],
        ["Tensile Strength (Min.)", "ASTM D412 / ISO 37", "MPa", "≥ 14.5"],
        ["Elongation at Break (Min.)", "ASTM D412 / ISO 37", "%", "≥ 420"],
        ["Tear Resistance (Die C)", "ASTM D624", "kN/m", "≥ 38.0"],
        ["Compression Set (70°C × 22h)", "ASTM D395 Method B", "%", "≤ 22"],
        ["Water Absorption (23°C × 24h)", "ASTM D471", "%", "≤ 0.8 (Hydrophobic WS-1 Grade)"],
        ["Ozone & Weathering (72h)", "ASTM D1149 (50 pphm)", "Rating", "No Cracks / Pass Grade A"],
        ["Thermal Aging (100°C × 70h)", "ASTM D573", "Change", "Hardness ≤ +5 ShA  |  Tensile ≤ -10%"],
    ]

    col_widths = [155, 118, 56, 198]
    t = Table(table_data, colWidths=col_widths, rowHeights=[19.5] + [17] * (len(table_data) - 1))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "NotoSansBold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.6),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("ALIGN", (2, 0), (2, -1), "CENTER"),
        ("FONTNAME", (0, 1), (-1, -1), "NotoSans"),
        ("FONTSIZE", (0, 1), (-1, -1), 8.2),
        ("TEXTCOLOR", (0, 1), (-1, -1), DARK_INK),
        ("FONTNAME", (3, 1), (3, -1), "NotoSansBold"),
        ("TEXTCOLOR", (3, 1), (3, -1), BRAND_DARK_GREEN),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BRAND_ACCENT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    tw, th = t.wrapOn(c, W - 68, 400)
    table_y = sec2_top - 7 - th
    t.drawOn(c, 34, table_y)

    # Watermark placed beside the specification values on the right side
    c.drawImage(wm_path, W - 132, table_y + 26, width=90, height=90, mask="auto")

    # 6. Applications & Processing (Two-Column Layout with Watermark Beside Text in Each Column)
    sec3_top = table_y - 14
    sec3_h = 132
    sec3_y = sec3_top - sec3_h
    col_box_w = (W - 68 - 14) / 2.0

    # Left Box: Target Applications
    c.setFillColor(BRAND_ACCENT_BG)
    c.setStrokeColor(BORDER_GRAY)
    c.roundRect(34, sec3_y, col_box_w, sec3_h, 5, stroke=1, fill=1)
    c.setFillColor(BRAND_RED)
    c.rect(34, sec3_y + sec3_h - 4, col_box_w, 4, stroke=0, fill=1)

    c.setFillColor(BRAND_RED)
    c.setFont("NotoSansBold", 9.8)
    c.drawString(46, sec3_top - 20, "HIGH-VALUE INDUSTRIAL APPLICATIONS")

    c.drawImage(wm_path, 34 + col_box_w - 78, sec3_y + 8, width=68, height=68, mask="auto")

    apps = [
        "• Automotive & Commercial Weatherstripping",
        "• Architectural Curtain Wall & Glazing Seals",
        "• Waterproof Conduit, Cable & Pipe Gaskets",
        "• HVAC Vibration Damping & Insulation",
        "• Heavy Machinery Environmental Profiles",
    ]
    ay = sec3_top - 38
    c.setFillColor(DARK_INK)
    c.setFont("NotoSans", 8.2)
    for app in apps:
        c.drawString(46, ay, app)
        ay -= 16.5

    # Right Box: Processing, Packaging & Storage
    rx = 34 + col_box_w + 14
    c.setFillColor(BRAND_ACCENT_BG)
    c.setStrokeColor(BORDER_GRAY)
    c.roundRect(rx, sec3_y, col_box_w, sec3_h, 5, stroke=1, fill=1)
    c.setFillColor(BRAND_ORANGE)
    c.rect(rx, sec3_y + sec3_h - 4, col_box_w, 4, stroke=0, fill=1)

    c.setFillColor(BRAND_DARK_GREEN)
    c.setFont("NotoSansBold", 9.8)
    c.drawString(rx + 12, sec3_top - 20, "PROCESSING, PACKAGING & QUALITY")

    c.drawImage(wm_path, rx + col_box_w - 78, sec3_y + 8, width=68, height=68, mask="auto")

    proc_lines = [
        "• Process: Extrusion, Compression & Injection",
        "• Packaging: 25 kg barrier bags / 500 kg pallet",
        "• Storage: 12 months in dry conditions (<30°C)",
        "• Compliance: RoHS, REACH & ISO 9001 Certified",
        "• Custom OEM: Hardness, color & cure profiles",
    ]
    py = sec3_top - 38
    c.setFillColor(DARK_INK)
    c.setFont("NotoSans", 8.2)
    for line in proc_lines:
        c.drawString(rx + 12, py, line)
        py -= 16.5

    # 7. Footer Banner (Light-tinted bar so brand logo & watermark are crisp and legible)
    footer_h = 46
    c.setFillColor(BRAND_LIGHT_BLUE)
    c.rect(0, 0, W, footer_h, stroke=0, fill=1)

    c.setFillColor(BRAND_GREEN)
    c.rect(0, footer_h, W * 0.45, 3, stroke=0, fill=1)
    c.setFillColor(BRAND_RED)
    c.rect(W * 0.45, footer_h, W * 0.28, 3, stroke=0, fill=1)
    c.setFillColor(BRAND_ORANGE)
    c.rect(W * 0.73, footer_h, W * 0.27, 3, stroke=0, fill=1)

    c.drawImage(logo_path, 34, 4, width=38, height=38, mask="auto")

    c.setFillColor(DARK_INK)
    c.setFont("NotoSansBold", 9.2)
    c.drawString(80, 25, "佳尔橡塑  |  JIAERXIANGSU  —  Premier Rubber & Plastic Engineering")

    c.setFillColor(MUTED_INK)
    c.setFont("NotoSans", 7.6)
    c.drawString(80, 11, "Official Technical Documentation  •  OEM Quality Verified  •  Model: MT51-WS-1")

    c.setFillColor(BRAND_GREEN)
    c.setFont("NotoSansBold", 8.2)
    c.drawRightString(W - 34, 18, "AUTHENTIC JIAER SPECIFICATION")

    c.showPage()
    c.save()

if __name__ == "__main__":
    build_pdf("/home/user/openclaw/JIAER_MT51-WS-1_Technical_Datasheet.pdf")
