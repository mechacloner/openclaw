import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle

# Register static CJK & Latin fonts
pdfmetrics.registerFont(TTFont("NotoSans", "/tmp/NotoSansSC-Regular.ttf"))
pdfmetrics.registerFont(TTFont("NotoSansBold", "/tmp/NotoSansSC-Bold.ttf"))

W, H = A4  # 595.27 x 841.89 pt
MARGIN = 38
CONTENT_W = W - 2 * MARGIN

# Refined Corporate Engineering Color Palette
CORP_NAVY = colors.HexColor("#0F172A")       # Deep slate-navy for primary headings & text
CORP_CHARCOAL = colors.HexColor("#1E293B")   # Secondary dark slate
CORP_MUTED = colors.HexColor("#475569")      # Muted gray for labels & footnotes
CORP_LIGHT_TEXT = colors.HexColor("#64748B")
BRAND_GREEN = colors.HexColor("#1B5E34")     # Refined corporate JIAER green
BRAND_ACCENT = colors.HexColor("#D9381E")    # Subtle JIAER warm accent for rule/badge
TABLE_HEADER_BG = colors.HexColor("#16222F") # Executive dark slate table header
TABLE_ALT_ROW = colors.HexColor("#F8FAFC")   # Very subtle cool gray alternating row
PANEL_BG = colors.HexColor("#F8FAFC")        # Subtle corporate card fill
BORDER_LINE = colors.HexColor("#CBD5E1")     # Crisp 0.5pt engineering border
LIGHT_RULE = colors.HexColor("#E2E8F0")

def draw_paragraph(c, text, x, y, max_w, font_name, font_size, leading, color):
    style = ParagraphStyle(
        name="corp",
        fontName=font_name,
        fontSize=font_size,
        leading=leading,
        textColor=color,
    )
    p = Paragraph(text, style)
    w, h = p.wrap(max_w, 500)
    p.drawOn(c, x, y - h)
    return y - h

def draw_section_header(c, y, num_str, title_str, right_note=None):
    """Draws a sleek corporate section header with a left accent bar and bottom rule."""
    # Small green vertical pill
    c.setFillColor(BRAND_GREEN)
    c.rect(MARGIN, y - 1, 3.5, 12, stroke=0, fill=1)

    c.setFillColor(BRAND_GREEN)
    c.setFont("NotoSansBold", 9.5)
    c.drawString(MARGIN + 9, y, num_str)

    c.setFillColor(CORP_NAVY)
    c.setFont("NotoSansBold", 9.8)
    c.drawString(MARGIN + 26, y, title_str)

    if right_note:
        c.setFillColor(CORP_LIGHT_TEXT)
        c.setFont("NotoSans", 7.5)
        c.drawRightString(W - MARGIN, y + 0.5, right_note)

    c.setStrokeColor(BORDER_LINE)
    c.setLineWidth(0.6)
    c.line(MARGIN, y - 5, W - MARGIN, y - 5)
    return y - 16

def build_pdf(out_path):
    c = canvas.Canvas(out_path, pagesize=A4)
    c.setTitle("JIAER MT51-WS-1 Technical Datasheet - 佳尔橡塑")

    logo_path = "/home/user/openclaw/assets/jiaer_logo_transparent.png"
    wm_path = "/home/user/openclaw/assets/jiaer_watermark.png"

    # Page white background
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # Top Corporate Header Bar (4pt solid dark slate + 2pt brand green accent)
    c.setFillColor(CORP_NAVY)
    c.rect(0, H - 5, W * 0.72, 5, stroke=0, fill=1)
    c.setFillColor(BRAND_GREEN)
    c.rect(W * 0.72, H - 5, W * 0.28, 5, stroke=0, fill=1)

    # 1. CORPORATE HEADER BLOCK
    header_top = H - 22
    # Brand Logo on Left
    c.drawImage(logo_path, MARGIN, header_top - 66, width=66, height=66, mask="auto")

    # Company Name & Document Type beside Logo
    hx = MARGIN + 78
    c.setFillColor(BRAND_GREEN)
    c.setFont("NotoSansBold", 8.5)
    c.drawString(hx, header_top - 11, "JIAER RUBBER & PLASTIC CO.   |   佳尔橡塑 · JIAERXIANGSU")

    c.setFillColor(CORP_NAVY)
    c.setFont("NotoSansBold", 18.5)
    c.drawString(hx, header_top - 33, "MT51-WS-1")

    # Badge beside model number
    c.setFillColor(PANEL_BG)
    c.setStrokeColor(BORDER_LINE)
    c.setLineWidth(0.6)
    c.roundRect(hx + 108, header_top - 36, 132, 16, 2, stroke=1, fill=1)
    c.setFillColor(BRAND_GREEN)
    c.setFont("NotoSansBold", 7.8)
    c.drawCentredString(hx + 108 + 66, header_top - 30.5, "TECHNICAL DATA SHEET")

    c.setFillColor(CORP_CHARCOAL)
    c.setFont("NotoSansBold", 8.8)
    c.drawString(hx, header_top - 50, "High-Performance Weather-Resistant & Water-Sealing Elastomer")

    c.setFillColor(CORP_MUTED)
    c.setFont("NotoSans", 7.5)
    c.drawString(hx, header_top - 63, "Engineered Polymer Formulation for Industrial Sealing & Insulation")

    # Document Control Metadata Box on Far Right of Header
    meta_w = 132
    meta_x = W - MARGIN - meta_w
    meta_y = header_top - 66
    c.setFillColor(PANEL_BG)
    c.setStrokeColor(BORDER_LINE)
    c.setLineWidth(0.6)
    c.rect(meta_x, meta_y, meta_w, 62, stroke=1, fill=1)

    meta_rows = [
        ("DOCUMENT NO.", "JE-TDS-MT51-WS-1"),
        ("REVISION", "Rev 2026.10"),
        ("QUALITY GRADE", "Industrial / OEM"),
        ("STATUS", "Certified Release"),
    ]
    my = header_top - 15
    for k, v in meta_rows:
        c.setFillColor(CORP_LIGHT_TEXT)
        c.setFont("NotoSansBold", 6.5)
        c.drawString(meta_x + 7, my, k)
        c.setFillColor(CORP_NAVY)
        c.setFont("NotoSansBold", 7.2)
        c.drawRightString(meta_x + meta_w - 7, my, v)
        if k != "STATUS":
            c.setStrokeColor(LIGHT_RULE)
            c.setLineWidth(0.4)
            c.line(meta_x + 5, my - 4, meta_x + meta_w - 5, my - 4)
        my -= 14.5

    # Horizontal divider below header
    div_y = header_top - 76
    c.setStrokeColor(CORP_NAVY)
    c.setLineWidth(1.0)
    c.line(MARGIN, div_y, W - MARGIN, div_y)

    # 2. SECTION 01: PRODUCT OVERVIEW & BRAND WATERMARK BESIDE THE TEXT
    s1_y = draw_section_header(
        c,
        div_y - 18,
        "01",
        "EXECUTIVE PRODUCT OVERVIEW & COMMERCIAL ADVANTAGE",
        "Material Family: Cross-Linkable Elastomer (WS-1)"
    )

    # Clean two-column layout: Left 74% is crisp corporate text & value bullets,
    # Right 26% is a dedicated, clean Brand Watermark column BESIDE the text (no overlap!)
    overview_box_h = 128
    overview_box_y = s1_y - overview_box_h

    c.setFillColor(PANEL_BG)
    c.setStrokeColor(BORDER_LINE)
    c.setLineWidth(0.6)
    c.rect(MARGIN, overview_box_y, CONTENT_W, overview_box_h, stroke=1, fill=1)

    # Subtle vertical divider separating the text on the left and the Brand Watermark on the right
    wm_panel_w = 134
    wm_panel_x = W - MARGIN - wm_panel_w
    c.setStrokeColor(LIGHT_RULE)
    c.setLineWidth(0.6)
    c.line(wm_panel_x, overview_box_y + 8, wm_panel_x, overview_box_y + overview_box_h - 8)

    # Brand Watermark cleanly centered in the right panel BESIDE the text
    c.drawImage(wm_path, wm_panel_x + 13, overview_box_y + 14, width=108, height=108, mask="auto")

    # Overview Text on the left
    text_w = wm_panel_x - (MARGIN + 14) - 14
    overview_copy = (
        "<b>JIAER MT51-WS-1</b> is an advanced, commercial-grade polymer and elastomer formulation "
        "developed by <b>Jiaer Rubber & Plastic (佳尔橡塑 · JIAERXIANGSU)</b> for demanding industrial "
        "sealing, waterproofing, and structural insulation applications. Engineered to maximize operational "
        "uptime and reduce total lifecycle maintenance costs, MT51-WS-1 combines high tensile resilience, "
        "hydrophobic weather sealing, and superior thermal-oxidative stability."
    )
    cy = draw_paragraph(c, overview_copy, MARGIN + 12, s1_y - 8, text_w, "NotoSans", 8.5, 12.5, CORP_CHARCOAL)

    # 3 Structured Key Pillars below paragraph
    pillars = [
        ("Maximum ROI & Longevity", "Extended service life under continuous compression & UV exposure."),
        ("Process & OEM Efficiency", "Consistent rheology & stability for high-yield extrusion/molding."),
        ("Zero-Leakage Reliability", "Hydrophobic WS-1 barrier preventing water and vapor ingress."),
    ]
    py = cy - 12
    for p_title, p_desc in pillars:
        c.setFillColor(BRAND_GREEN)
        c.rect(MARGIN + 12, py + 1.5, 4, 4, stroke=0, fill=1)
        c.setFillColor(CORP_NAVY)
        c.setFont("NotoSansBold", 7.8)
        c.drawString(MARGIN + 20, py, p_title + ":")
        c.setFillColor(CORP_MUTED)
        c.setFont("NotoSans", 7.8)
        c.drawString(MARGIN + 126, py, p_desc)
        py -= 13

    # 3. KEY ENGINEERING BENCHMARK STRIP (4 Clean Corporate Specification Callouts)
    strip_top = overview_box_y - 10
    strip_h = 44
    strip_y = strip_top - strip_h
    cell_w = CONTENT_W / 4.0

    c.setFillColor(colors.white)
    c.setStrokeColor(BORDER_LINE)
    c.setLineWidth(0.6)
    c.rect(MARGIN, strip_y, CONTENT_W, strip_h, stroke=1, fill=1)

    benchmarks = [
        ("TENSILE STRENGTH", "≥ 14.5 MPa", "ASTM D412 / ISO 37"),
        ("ELONGATION AT BREAK", "≥ 420 %", "High Elastic Recovery"),
        ("SERVICE TEMPERATURE", "-40°C to +125°C", "Continuous Thermal Rating"),
        ("WATER RESISTANCE", "WS-1 Grade", "≤ 0.8% Absorption (24h)"),
    ]
    for i, (b_lbl, b_val, b_sub) in enumerate(benchmarks):
        bx = MARGIN + i * cell_w
        if i > 0:
            c.setStrokeColor(LIGHT_RULE)
            c.setLineWidth(0.6)
            c.line(bx, strip_y + 6, bx, strip_y + strip_h - 6)
        c.setFillColor(CORP_LIGHT_TEXT)
        c.setFont("NotoSansBold", 6.8)
        c.drawString(bx + 10, strip_y + 31, b_lbl)

        c.setFillColor(CORP_NAVY)
        c.setFont("NotoSansBold", 11.5)
        c.drawString(bx + 10, strip_y + 16, b_val)

        c.setFillColor(BRAND_GREEN)
        c.setFont("NotoSans", 7.0)
        c.drawString(bx + 10, strip_y + 5.5, b_sub)

    # 4. SECTION 02: TECHNICAL SPECIFICATIONS & PHYSICAL PROPERTIES TABLE
    s2_y = draw_section_header(
        c,
        strip_y - 18,
        "02",
        "TECHNICAL SPECIFICATIONS & PHYSICAL PROPERTIES",
        "Standard Test Conditions: 23°C ± 2°C, 50% ± 5% RH"
    )

    table_data = [
        ["Property / Parameter", "Test Method / Standard", "Unit", "MT51-WS-1 Specification"],
        ["Material Classification", "JIAER Internal / ISO 1629", "—", "Modified Weather-Sealing Elastomer (WS-1)"],
        ["Appearance & Color", "Visual Inspection", "—", "Uniform Smooth Surface / Black or Custom OEM"],
        ["Specific Gravity / Density", "ASTM D297 / ISO 2781", "g/cm³", "1.18 ± 0.03"],
        ["Hardness (Shore A)", "ASTM D2240 / ISO 7619-1", "Shore A", "60 ± 5  (Customizable Range: 50–75)"],
        ["Tensile Strength (Min.)", "ASTM D412 / ISO 37", "MPa", "≥ 14.5"],
        ["Elongation at Break (Min.)", "ASTM D412 / ISO 37", "%", "≥ 420"],
        ["Tear Resistance (Die C)", "ASTM D624", "kN/m", "≥ 38.0"],
        ["Compression Set (70°C × 22h)", "ASTM D395 Method B", "%", "≤ 22"],
        ["Water Absorption (23°C × 24h)", "ASTM D471", "%", "≤ 0.8  (Hydrophobic WS-1 Barrier Grade)"],
        ["Ozone & Weathering Resistance", "ASTM D1149 (50 pphm, 72h)", "Rating", "No Cracks  /  Pass Grade A"],
        ["Thermal Air Aging (100°C × 70h)", "ASTM D573", "Δ Value", "Hardness: ≤ +5 Shore A   |   Tensile: ≤ -10%"],
    ]

    col_widths = [156, 122, 52, CONTENT_W - 156 - 122 - 52]
    t = Table(table_data, colWidths=col_widths, rowHeights=[20] + [17.5] * (len(table_data) - 1))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "NotoSansBold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.2),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("ALIGN", (2, 0), (2, -1), "CENTER"),
        ("FONTNAME", (0, 1), (2, -1), "NotoSans"),
        ("FONTNAME", (0, 1), (0, -1), "NotoSansBold"),
        ("FONTSIZE", (0, 1), (-1, -1), 8.0),
        ("TEXTCOLOR", (0, 1), (2, -1), CORP_CHARCOAL),
        ("FONTNAME", (3, 1), (3, -1), "NotoSansBold"),
        ("TEXTCOLOR", (3, 1), (3, -1), CORP_NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, TABLE_ALT_ROW]),
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, BRAND_GREEN),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, LIGHT_RULE),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER_LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, LIGHT_RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    tw, th = t.wrapOn(c, CONTENT_W, 400)
    table_y = s2_y - th
    t.drawOn(c, MARGIN, table_y)

    # 5. SECTION 03: INDUSTRIAL APPLICATIONS, PROCESSING & QUALITY ASSURANCE
    s3_y = draw_section_header(
        c,
        table_y - 18,
        "03",
        "APPLICATIONS, PROCESSING GUIDELINES & QUALITY ASSURANCE",
        "ISO 9001 / RoHS / REACH Compliant"
    )

    bottom_h = 114
    bottom_y = s3_y - bottom_h

    # Three-column layout at bottom:
    # Col 1: Target Industrial Applications
    # Col 2: Processing, Storage & Packaging
    # Col 3: Brand Watermark & Quality Certification Seal beside the text
    col1_w = 205
    col2_w = 210
    col3_w = CONTENT_W - col1_w - col2_w - 16

    # Box 1: Industrial Applications
    x1 = MARGIN
    c.setFillColor(PANEL_BG)
    c.setStrokeColor(BORDER_LINE)
    c.setLineWidth(0.6)
    c.rect(x1, bottom_y, col1_w, bottom_h, stroke=1, fill=1)
    c.setFillColor(CORP_NAVY)
    c.rect(x1, bottom_y + bottom_h - 2.5, col1_w, 2.5, stroke=0, fill=1)

    c.setFillColor(CORP_NAVY)
    c.setFont("NotoSansBold", 8.5)
    c.drawString(x1 + 10, s3_y - 16, "TARGET INDUSTRIAL APPLICATIONS")

    apps = [
        "• Automotive & Commercial Weatherstripping",
        "• Architectural Curtain Wall & Glazing Seals",
        "• Waterproof Conduit, Cable & Pipe Gaskets",
        "• HVAC Vibration Damping & Insulation",
        "• Heavy Machinery Environmental Profiles",
    ]
    ay = s3_y - 33
    c.setFillColor(CORP_CHARCOAL)
    c.setFont("NotoSans", 7.8)
    for app in apps:
        c.drawString(x1 + 10, ay, app)
        ay -= 15

    # Box 2: Processing, Packaging & Storage
    x2 = x1 + col1_w + 8
    c.setFillColor(PANEL_BG)
    c.setStrokeColor(BORDER_LINE)
    c.setLineWidth(0.6)
    c.rect(x2, bottom_y, col2_w, bottom_h, stroke=1, fill=1)
    c.setFillColor(BRAND_GREEN)
    c.rect(x2, bottom_y + bottom_h - 2.5, col2_w, 2.5, stroke=0, fill=1)

    c.setFillColor(CORP_NAVY)
    c.setFont("NotoSansBold", 8.5)
    c.drawString(x2 + 10, s3_y - 16, "PROCESSING, PACKAGING & STORAGE")

    proc_lines = [
        "• Process: Extrusion, Compression & Injection",
        "• Packaging: 25 kg barrier bags / 500 kg pallet",
        "• Shelf Life: 12 months in dry storage (<30°C)",
        "• Compliance: RoHS, REACH & ISO 9001 Certified",
        "• Custom OEM: Hardness, color & cure profiles",
    ]
    py = s3_y - 33
    c.setFillColor(CORP_CHARCOAL)
    c.setFont("NotoSans", 7.8)
    for line in proc_lines:
        c.drawString(x2 + 10, py, line)
        py -= 15

    # Box 3: Dedicated Brand Watermark Emblem Beside Text
    x3 = x2 + col2_w + 8
    c.setFillColor(colors.white)
    c.setStrokeColor(BORDER_LINE)
    c.setLineWidth(0.6)
    c.rect(x3, bottom_y, col3_w, bottom_h, stroke=1, fill=1)

    c.drawImage(wm_path, x3 + (col3_w - 76) / 2.0, bottom_y + 24, width=76, height=76, mask="auto")
    c.setFillColor(CORP_LIGHT_TEXT)
    c.setFont("NotoSansBold", 6.5)
    c.drawCentredString(x3 + col3_w / 2.0, bottom_y + 14, "AUTHENTIC OEM MATERIAL")
    c.setFillColor(BRAND_GREEN)
    c.setFont("NotoSansBold", 6.5)
    c.drawCentredString(x3 + col3_w / 2.0, bottom_y + 5.5, "佳尔橡塑 · JIAERXIANGSU")

    # 6. CORPORATE FOOTER
    footer_y = 28
    c.setStrokeColor(BORDER_LINE)
    c.setLineWidth(0.6)
    c.line(MARGIN, footer_y + 18, W - MARGIN, footer_y + 18)

    c.drawImage(logo_path, MARGIN, footer_y - 12, width=26, height=26, mask="auto")

    c.setFillColor(CORP_NAVY)
    c.setFont("NotoSansBold", 7.8)
    c.drawString(MARGIN + 32, footer_y + 3, "佳尔橡塑  |  JIAERXIANGSU  —  Advanced Rubber & Plastic Engineering")

    c.setFillColor(CORP_LIGHT_TEXT)
    c.setFont("NotoSans", 6.8)
    c.drawString(
        MARGIN + 32,
        footer_y - 7,
        "Disclaimer: Typical technical values are provided for engineering reference and do not constitute a binding specification without OEM batch certification."
    )

    c.setFillColor(CORP_NAVY)
    c.setFont("NotoSansBold", 7.5)
    c.drawRightString(W - MARGIN, footer_y + 3, "Page 1 of 1")

    c.showPage()
    c.save()

if __name__ == "__main__":
    build_pdf("/home/user/openclaw/JIAER_MT51-WS-1_Technical_Datasheet.pdf")
