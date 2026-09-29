"""
create_presentation.py — Generates an official 6-slide Smart India Hackathon (SIH) PowerPoint presentation
matching the exact template structure, styling, typography, cards, and diagrams provided in the SIH submission template.
"""

import sys
import os
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# Initialize presentation
prs = pptx.Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Brand Colors (Matching SIH Official Template)
NAVY_BLUE = RGBColor(26, 68, 142)       # Primary SIH Header Blue (#1A448E)
TEAL_HEADER = RGBColor(2, 132, 199)     # Banner Teal/Blue (#0284C7)
ORANGE_SIH = RGBColor(234, 88, 12)      # SIH Accent Orange (#EA580C)
DARK_SLATE = RGBColor(15, 23, 42)       # Text Dark Slate (#0F172A)
MUTED_SLATE = RGBColor(71, 85, 105)     # Subtitle Muted Slate (#475569)
BG_LIGHT = RGBColor(248, 250, 252)      # Card Light Background (#F8FAFC)
CARD_BORDER = RGBColor(203, 213, 225)   # Card Border (#CBD5E1)
WHITE = RGBColor(255, 255, 255)
GREEN_ACC = RGBColor(16, 185, 129)      # Success Green (#10B981)
ROSE_ACC = RGBColor(225, 29, 72)        # Challenge Red (#E11D48)
AMBER_ACC = RGBColor(217, 119, 6)       # Warning Amber (#D97706)
PURPLE_ACC = RGBColor(124, 58, 237)     # Tech Purple (#7C3AED)

def add_header_footer(slide, slide_num, title_text="SMART INDIA HACKATHON 2025", show_header_banner=True):
    """Draws the standard SIH top header banner and bottom footer bar."""
    if show_header_banner:
        # Header banner title
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.25), Inches(10.5), Inches(0.6))
        tf = header_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = "Arial Black"
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = NAVY_BLUE
        p.alignment = PP_ALIGN.CENTER

        # SIH Logo pill on top right
        sih_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.5), Inches(0.15), Inches(1.5), Inches(0.75))
        sih_box.fill.solid()
        sih_box.fill.fore_color.rgb = WHITE
        sih_box.line.color.rgb = CARD_BORDER
        sih_box.line.width = Pt(1)
        tf_sih = sih_box.text_frame
        tf_sih.word_wrap = True
        p_sih = tf_sih.paragraphs[0]
        p_sih.text = "SMART INDIA\nHACKATHON\n2025 / 2026"
        p_sih.font.name = "Arial"
        p_sih.font.size = Pt(8)
        p_sih.font.bold = True
        p_sih.font.color.rgb = DARK_SLATE
        p_sih.alignment = PP_ALIGN.CENTER

    # Bottom Footer Strip
    footer_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.05), Inches(13.333), Inches(0.45))
    footer_bar.fill.solid()
    footer_bar.fill.fore_color.rgb = NAVY_BLUE
    footer_bar.line.fill.background()

    tf_foot = footer_bar.text_frame
    p_foot = tf_foot.paragraphs[0]
    p_foot.text = "SMART INDIA HACKATHON 2025"
    p_foot.font.name = "Arial Black"
    p_foot.font.size = Pt(12)
    p_foot.font.color.rgb = WHITE
    p_foot.alignment = PP_ALIGN.CENTER

    # Slide Number on bottom right
    num_box = slide.shapes.add_textbox(Inches(12.6), Inches(7.05), Inches(0.6), Inches(0.45))
    tf_num = num_box.text_frame
    p_num = tf_num.paragraphs[0]
    p_num.text = str(slide_num)
    p_num.font.name = "Arial Black"
    p_num.font.size = Pt(13)
    p_num.font.color.rgb = WHITE
    p_num.alignment = PP_ALIGN.CENTER


# ==============================================================================
# SLIDE 1: TITLE PAGE
# ==============================================================================
slide1 = prs.slides.add_slide(blank_layout)
add_header_footer(slide1, 1, title_text="SMART INDIA HACKATHON 2025 / 2026")

# Left Column: Project Metadata Box
left_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(7.8), Inches(5.2))
tf1 = left_box.text_frame
tf1.word_wrap = True

items_slide1 = [
    ("Problem Statement ID", "SIH25273 (or MoSPI / NSO Assigned ID)"),
    ("Problem Statement Title", "Development of a Real-time Airfare Price Index for India through Automated Web Scraping of Airline and Online Travel Aggregator Portals for Augmentation of the Consumer Price Index (CPI)"),
    ("Theme", "Smart Automation / FinTech & Economic Governance"),
    ("PS Category", "Software"),
    ("Team ID", "73869"),
    ("Team Name", "Algo Sapiens (AeroMetrics)")
]

for i, (label, val) in enumerate(items_slide1):
    p = tf1.paragraphs[0] if i == 0 else tf1.add_paragraph()
    p.space_after = Pt(12)
    
    # Bullet dot
    run_bullet = p.add_run()
    run_bullet.text = "• "
    run_bullet.font.name = "Arial Black"
    run_bullet.font.size = Pt(15)
    run_bullet.font.color.rgb = DARK_SLATE
    
    # Label
    run_label = p.add_run()
    run_label.text = f"{label} – "
    run_label.font.name = "Arial"
    run_label.font.size = Pt(15)
    run_label.font.bold = True
    run_label.font.color.rgb = DARK_SLATE
    
    # Value
    run_val = p.add_run()
    run_val.text = val
    run_val.font.name = "Arial"
    run_val.font.size = Pt(14)
    run_val.font.color.rgb = NAVY_BLUE if label == "Problem Statement Title" else MUTED_SLATE

# Right Column Graphic: Emblems & Project Badge
graphic_bg = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.0), Inches(1.5), Inches(3.6), Inches(5.0))
graphic_bg.fill.solid()
graphic_bg.fill.fore_color.rgb = BG_LIGHT
graphic_bg.line.color.rgb = CARD_BORDER
graphic_bg.line.width = Pt(1.5)

tf_g = graphic_bg.text_frame
tf_g.word_wrap = True
tf_g.vertical_anchor = MSO_ANCHOR.MIDDLE

p_g1 = tf_g.paragraphs[0]
p_g1.text = "🇮🇳\nAIRFARE PRICE INDEX"
p_g1.font.name = "Arial Black"
p_g1.font.size = Pt(20)
p_g1.font.bold = True
p_g1.font.color.rgb = NAVY_BLUE
p_g1.alignment = PP_ALIGN.CENTER

p_g2 = tf_g.add_paragraph()
p_g2.text = "High-Frequency Consumer Price Index (CPI) Augmentation System"
p_g2.font.name = "Arial"
p_g2.font.size = Pt(12)
p_g2.font.color.rgb = MUTED_SLATE
p_g2.alignment = PP_ALIGN.CENTER
p_g2.space_before = Pt(10)

p_g3 = tf_g.add_paragraph()
p_g3.text = "Ministry of Statistics & Programme Implementation (MoSPI) • NSO"
p_g3.font.name = "Arial"
p_g3.font.size = Pt(11)
p_g3.font.bold = True
p_g3.font.color.rgb = ORANGE_SIH
p_g3.alignment = PP_ALIGN.CENTER
p_g3.space_before = Pt(15)

# Badge bottom
badge = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.5), Inches(5.5), Inches(2.6), Inches(0.6))
badge.fill.solid()
badge.fill.fore_color.rgb = NAVY_BLUE
badge.line.fill.background()
tf_b = badge.text_frame
p_b = tf_b.paragraphs[0]
p_b.text = "SIH 2025 / 2026 PROTOTYPE"
p_b.font.name = "Arial Black"
p_b.font.size = Pt(10)
p_b.font.color.rgb = WHITE
p_b.alignment = PP_ALIGN.CENTER


# ==============================================================================
# SLIDE 2: PROPOSED SOLUTION / APPROACH
# ==============================================================================
slide2 = prs.slides.add_slide(blank_layout)
add_header_footer(slide2, 2, title_text="", show_header_banner=False)

# Top Title Banner
t_box = slide2.shapes.add_textbox(Inches(0.8), Inches(0.2), Inches(10.5), Inches(0.8))
tf_t = t_box.text_frame
p_t1 = tf_t.paragraphs[0]
p_t1.text = "VAYU-MULYA (वायु मूल्य)"
p_t1.font.name = "Arial Black"
p_t1.font.size = Pt(22)
p_t1.font.bold = True
p_t1.font.color.rgb = NAVY_BLUE
p_t1.alignment = PP_ALIGN.CENTER

p_t2 = tf_t.add_paragraph()
p_t2.text = "Automated Real-Time Airfare Price Index for National CPI Augmentation"
p_t2.font.name = "Arial"
p_t2.font.size = Pt(13)
p_t2.font.italic = True
p_t2.font.color.rgb = MUTED_SLATE
p_t2.alignment = PP_ALIGN.CENTER

# SIH Logo on Top Right
sih_box2 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.5), Inches(0.15), Inches(1.5), Inches(0.75))
sih_box2.fill.solid()
sih_box2.fill.fore_color.rgb = WHITE
sih_box2.line.color.rgb = CARD_BORDER
tf_sih2 = sih_box2.text_frame
p_sih2 = tf_sih2.paragraphs[0]
p_sih2.text = "SMART INDIA\nHACKATHON\n2025"
p_sih2.font.size = Pt(8)
p_sih2.font.bold = True
p_sih2.font.color.rgb = DARK_SLATE
p_sih2.alignment = PP_ALIGN.CENTER

# Left Column: Proposed Solution / Approach Box
# Header pill
sol_header = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.15), Inches(5.8), Inches(0.55))
sol_header.fill.solid()
sol_header.fill.fore_color.rgb = TEAL_HEADER
sol_header.line.fill.background()
tf_sh = sol_header.text_frame
p_sh = tf_sh.paragraphs[0]
p_sh.text = "Proposed Solution / Approach"
p_sh.font.name = "Arial Black"
p_sh.font.size = Pt(15)
p_sh.font.color.rgb = WHITE
p_sh.alignment = PP_ALIGN.CENTER

# Content Box below
sol_box = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.0))
sol_box.fill.solid()
sol_box.fill.fore_color.rgb = WHITE
sol_box.line.color.rgb = CARD_BORDER
sol_box.line.width = Pt(1)
tf_sb = sol_box.text_frame
tf_sb.word_wrap = True

sol_points = [
    ("Automated Multi-Carrier Scraping Engine", "Daily headless ingestion across 20 high-density DGCA trunk routes from 6 airlines (IndiGo, Air India, Akasa, SpiceJet, Air India Express, AIX Connect) and major OTAs."),
    ("Multi-Horizon Advance Purchase Sampling", "Tracks yield-management escalation across 5 advance booking horizons (T+1, T+7, T+15, T+30, T+45) to capture real traveler booking behaviors."),
    ("Vectorized Outlier Cleaning & Missing Data", "Group-wise IQR and Z-score outlier detection scrubs promotional or scraping anomalies while preserving complete flight schedules without data loss."),
    ("Econometric Index Construction", "Computes Laspeyres, Paasche, and superlative Fisher Ideal indices weighted by 109 Million annual DGCA passenger traffic figures."),
    ("Automated DGCA TMU Backtesting", "Continuous statistical verification benchmarking model indices against official DGCA Tariff Monitoring Unit domestic fare reports.")
]

for i, (head, body) in enumerate(sol_points):
    p = tf_sb.paragraphs[0] if i == 0 else tf_sb.add_paragraph()
    p.space_after = Pt(8)
    
    r1 = p.add_run()
    r1.text = f"• {head}: "
    r1.font.name = "Arial"
    r1.font.bold = True
    r1.font.size = Pt(11)
    r1.font.color.rgb = DARK_SLATE
    
    r2 = p.add_run()
    r2.text = body
    r2.font.name = "Arial"
    r2.font.size = Pt(10)
    r2.font.color.rgb = MUTED_SLATE

# Right Top: End-to-end Workflow Container
wf_box = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.15), Inches(5.8), Inches(2.7))
wf_box.fill.solid()
wf_box.fill.fore_color.rgb = WHITE
wf_box.line.color.rgb = CARD_BORDER
wf_box.line.width = Pt(1)

# Title
wf_title = slide2.shapes.add_textbox(Inches(6.8), Inches(1.2), Inches(5.8), Inches(0.4))
tf_wft = wf_title.text_frame
p_wft = tf_wft.paragraphs[0]
p_wft.text = "VAYU-MULYA End-to-End Workflow"
p_wft.font.name = "Arial Black"
p_wft.font.size = Pt(12)
p_wft.font.color.rgb = DARK_SLATE
p_wft.alignment = PP_ALIGN.CENTER

# 6 Mini Workflow Step Pills
wf_steps = [
    ("1. Scheduled Trigger", "6:00 AM Daily Run", Inches(7.0), Inches(1.65)),
    ("2. Headless Ingestion", "20 Routes x 5 Horizons", Inches(8.8), Inches(1.65)),
    ("3. Vectorized ETL", "IQR Outliers Flagged", Inches(10.6), Inches(1.65)),
    ("4. DGCA Weighting", "109M Pax Weights", Inches(7.0), Inches(2.65)),
    ("5. Fisher Indexing", "Daily/Weekly/Monthly", Inches(8.8), Inches(2.65)),
    ("6. MoSPI Serving", "API & Streamlit Portal", Inches(10.6), Inches(2.65))
]

for title_s, desc_s, left_s, top_s in wf_steps:
    step_shape = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_s, top_s, Inches(1.65), Inches(0.85))
    step_shape.fill.solid()
    step_shape.fill.fore_color.rgb = BG_LIGHT
    step_shape.line.color.rgb = TEAL_HEADER
    step_shape.line.width = Pt(1)
    tf_ss = step_shape.text_frame
    tf_ss.word_wrap = True
    p_ss1 = tf_ss.paragraphs[0]
    p_ss1.text = title_s
    p_ss1.font.name = "Arial"
    p_ss1.font.bold = True
    p_ss1.font.size = Pt(9)
    p_ss1.font.color.rgb = NAVY_BLUE
    p_ss1.alignment = PP_ALIGN.CENTER
    
    p_ss2 = tf_ss.add_paragraph()
    p_ss2.text = desc_s
    p_ss2.font.name = "Arial"
    p_ss2.font.size = Pt(8)
    p_ss2.font.color.rgb = MUTED_SLATE
    p_ss2.alignment = PP_ALIGN.CENTER

# Right Bottom: Innovation and Uniqueness
inno_header = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.3), Inches(4.0), Inches(2.8), Inches(0.45))
inno_header.fill.solid()
inno_header.fill.fore_color.rgb = RGBColor(71, 85, 105)
inno_header.line.fill.background()
tf_ih = inno_header.text_frame
p_ih = tf_ih.paragraphs[0]
p_ih.text = "Innovation and Uniqueness"
p_ih.font.name = "Arial Black"
p_ih.font.size = Pt(11)
p_ih.font.color.rgb = WHITE
p_ih.alignment = PP_ALIGN.CENTER

# 5 Feature Cards (Horizontal Cards like the reference slide)
inno_cards = [
    ("High-Freq Scraping", "Daily web-crawling replaces slow quarterly ticket counter surveys.", Inches(6.8), ORANGE_SIH),
    ("Superlative Fisher Index", "Geometric mean of Laspeyres & Paasche eliminates consumer substitution bias.", Inches(7.98), TEAL_HEADER),
    ("DGCA Passenger Weights", "Calibrated on 109M domestic passengers across 20 key corridors.", Inches(9.16), GREEN_ACC),
    ("Yield Curve Modeling", "Explicitly models advance booking elasticity from T+1 to T+45.", Inches(10.34), PURPLE_ACC),
    ("Automated TMU Audit", "Continuously validated against official DGCA Tariff Monitoring Unit data.", Inches(11.52), AMBER_ACC)
]

for title_c, desc_c, left_c, color_c in inno_cards:
    card = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_c, Inches(4.6), Inches(1.1), Inches(2.2))
    card.fill.solid()
    card.fill.fore_color.rgb = WHITE
    card.line.color.rgb = color_c
    card.line.width = Pt(1.5)
    tf_c = card.text_frame
    tf_c.word_wrap = True
    
    p_c1 = tf_c.paragraphs[0]
    p_c1.text = title_c
    p_c1.font.name = "Arial"
    p_c1.font.bold = True
    p_c1.font.size = Pt(9)
    p_c1.font.color.rgb = color_c
    p_c1.alignment = PP_ALIGN.CENTER
    
    p_c2 = tf_c.add_paragraph()
    p_c2.text = desc_c
    p_c2.font.name = "Arial"
    p_c2.font.size = Pt(7.5)
    p_c2.font.color.rgb = DARK_SLATE
    p_c2.alignment = PP_ALIGN.CENTER
    p_c2.space_before = Pt(6)


# ==============================================================================
# SLIDE 3: TECHNICAL APPROACH
# ==============================================================================
slide3 = prs.slides.add_slide(blank_layout)
add_header_footer(slide3, 3, title_text="TECHNICAL APPROACH")

# Left / Center Area: 4-Zone System Architecture
zones = [
    ("Zone 1: Users & External Sources", [
        "Airlines Direct (6E, AI, QP, SG, IX)",
        "OTAs (MakeMyTrip, Yatra, EaseMyTrip)",
        "DGCA Domestic Traffic Portal",
        "MoSPI eSankhyiki Portal API",
        "MoSPI / RBI Statisticians (Users)"
    ], Inches(0.8), Inches(1.2), Inches(2.3), Inches(4.3)),

    ("Zone 2: Frontend (Presentation)", [
        "Executive Web App (Tailwind / Chart.js)",
        "Streamlit Analytics Dashboard",
        "Interactive Macro Trend Views",
        "Lead-time Elasticity Simulator",
        "OpenAPI Swagger Documentation"
    ], Inches(3.2), Inches(1.2), Inches(2.3), Inches(4.3)),

    ("Zone 3: Backend (Application Layer)", [
        "FastAPI High-Performance Server",
        "APScheduler Daily 6 AM Ingestion",
        "Schema Parser & Validator",
        "Vectorized IQR Outlier Scrubber",
        "Relational SQLite / Postgres DB"
    ], Inches(5.6), Inches(1.2), Inches(2.3), Inches(4.3)),

    ("Zone 4: Data & Intelligence (The Brain)", [
        "Econometric Laspeyres Engine",
        "Paasche Harmonic Engine",
        "Superlative Fisher Ideal Index",
        "DGCA Traffic Weighting Matrix",
        "DGCA TMU Backtesting Validator"
    ], Inches(8.0), Inches(1.2), Inches(2.3), Inches(4.3))
]

for title_z, points_z, left_z, top_z, width_z, height_z in zones:
    # Zone background
    z_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_z, top_z, width_z, height_z)
    z_box.fill.solid()
    z_box.fill.fore_color.rgb = BG_LIGHT
    z_box.line.color.rgb = TEAL_HEADER
    z_box.line.width = Pt(1.2)
    
    # Zone title pill
    z_pill = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_z + Inches(0.08), top_z + Inches(0.08), width_z - Inches(0.16), Inches(0.5))
    z_pill.fill.solid()
    z_pill.fill.fore_color.rgb = NAVY_BLUE
    z_pill.line.fill.background()
    tf_zp = z_pill.text_frame
    p_zp = tf_zp.paragraphs[0]
    p_zp.text = title_z
    p_zp.font.name = "Arial"
    p_zp.font.bold = True
    p_zp.font.size = Pt(9)
    p_zp.font.color.rgb = WHITE
    p_zp.alignment = PP_ALIGN.CENTER
    
    # Zone points
    z_text = slide3.shapes.add_textbox(left_z + Inches(0.1), top_z + Inches(0.65), width_z - Inches(0.2), height_z - Inches(0.7))
    tf_zt = z_text.text_frame
    tf_zt.word_wrap = True
    for idx_pt, pt_text in enumerate(points_z):
        p_pt = tf_zt.paragraphs[0] if idx_pt == 0 else tf_zt.add_paragraph()
        p_pt.space_after = Pt(6)
        r = p_pt.add_run()
        r.text = f"• {pt_text}"
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.color.rgb = DARK_SLATE

# Technology Stack Bar at the bottom
tech_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.65), Inches(9.5), Inches(1.15))
tech_box.fill.solid()
tech_box.fill.fore_color.rgb = WHITE
tech_box.line.color.rgb = CARD_BORDER
tech_box.line.width = Pt(1)

tf_tb = tech_box.text_frame
p_tb = tf_tb.paragraphs[0]
p_tb.text = "Components / Technology Stack To Be Used:"
p_tb.font.name = "Arial Black"
p_tb.font.size = Pt(10)
p_tb.font.color.rgb = DARK_SLATE

tech_chips = [
    ("Python 3.11+", Inches(1.0), TEAL_HEADER),
    ("FastAPI", Inches(2.2), GREEN_ACC),
    ("Streamlit", Inches(3.2), ROSE_ACC),
    ("Pandas / NumPy", Inches(4.3), NAVY_BLUE),
    ("Plotly", Inches(5.8), PURPLE_ACC),
    ("SQLite / Postgres", Inches(6.7), AMBER_ACC),
    ("Tailwind CSS", Inches(8.3), TEAL_HEADER)
]

for name_chip, left_chip, col_chip in tech_chips:
    chip = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_chip, Inches(6.1), Inches(1.1), Inches(0.45))
    chip.fill.solid()
    chip.fill.fore_color.rgb = BG_LIGHT
    chip.line.color.rgb = col_chip
    chip.line.width = Pt(1.5)
    tf_chip = chip.text_frame
    p_chip = tf_chip.paragraphs[0]
    p_chip.text = name_chip
    p_chip.font.name = "Arial"
    p_chip.font.bold = True
    p_chip.font.size = Pt(8)
    p_chip.font.color.rgb = DARK_SLATE
    p_chip.alignment = PP_ALIGN.CENTER

# Right Column: Implementation Process (6 steps like in reference)
proc_header = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.5), Inches(1.2), Inches(2.2), Inches(0.4))
proc_header.fill.solid()
proc_header.fill.fore_color.rgb = ORANGE_SIH
proc_header.line.fill.background()
tf_ph = proc_header.text_frame
p_ph = tf_ph.paragraphs[0]
p_ph.text = "Implementation Process"
p_ph.font.name = "Arial Black"
p_ph.font.size = Pt(9.5)
p_ph.font.color.rgb = WHITE
p_ph.alignment = PP_ALIGN.CENTER

proc_steps = [
    ("1. Headless Crawling", "Ingests 20 routes across 6 carriers daily at 5 horizons."),
    ("2. Schema Normalization", "Validates IATA city-pairs, dates, and base/tax splits."),
    ("3. Vectorized Cleaning", "Flags outliers using grouped IQR/Z-score algorithms."),
    ("4. Index Computation", "Calculates Laspeyres, Paasche & Fisher series."),
    ("5. DGCA TMU Backtest", "Evaluates correlation & MAPE against official tariffs."),
    ("6. Production Serving", "Feeds MoSPI CPI systems via REST API & Live UI.")
]

for idx_ps, (step_h, step_b) in enumerate(proc_steps):
    step_y = Inches(1.75 + idx_ps * 0.82)
    s_card = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.5), step_y, Inches(2.2), Inches(0.72))
    s_card.fill.solid()
    s_card.fill.fore_color.rgb = WHITE
    s_card.line.color.rgb = CARD_BORDER
    s_card.line.width = Pt(1)
    
    tf_sc = s_card.text_frame
    tf_sc.word_wrap = True
    p_sc1 = tf_sc.paragraphs[0]
    p_sc1.text = step_h
    p_sc1.font.name = "Arial"
    p_sc1.font.bold = True
    p_sc1.font.size = Pt(8.5)
    p_sc1.font.color.rgb = NAVY_BLUE
    
    p_sc2 = tf_sc.add_paragraph()
    p_sc2.text = step_b
    p_sc2.font.name = "Arial"
    p_sc2.font.size = Pt(7)
    p_sc2.font.color.rgb = MUTED_SLATE


# ==============================================================================
# SLIDE 4: FEASIBILITY AND VIABILITY
# ==============================================================================
slide4 = prs.slides.add_slide(blank_layout)
add_header_footer(slide4, 4, title_text="FEASIBILITY AND VIABILITY")

# Top 3 Containers: Feasibility, Viability, Practical Implementation
top_pillars = [
    ("Feasibility", [
        "Uses proven econometric Laspeyres & Fisher formulas endorsed by IMF/ILO.",
        "Fully automated Python microservices architecture tested with 12/12 pytest suite.",
        "Lightweight relational storage (SQLite/PostgreSQL) with zero high-cost server dependencies."
    ], Inches(0.8), TEAL_HEADER),

    ("Viability", [
        "Eliminates crores in annual physical ticket counter field inspection budgets.",
        "Provides MoSPI with daily high-frequency airfare inflation nowcasting.",
        "Open-source modular codebase easily maintained by internal NIC/MoSPI teams."
    ], Inches(4.75), GREEN_ACC),

    ("Practical Implementation", [
        "Prototype already built, verified, and functioning end-to-end.",
        "Integrates directly into MoSPI eSankhyiki portal via standard REST API.",
        "Deployable via Docker containers to NIC Government Cloud within 2–4 weeks."
    ], Inches(8.7), PURPLE_ACC)
]

for title_pil, points_pil, left_pil, col_pil in top_pillars:
    pil_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pil, Inches(1.2), Inches(3.8), Inches(2.1))
    pil_box.fill.solid()
    pil_box.fill.fore_color.rgb = BG_LIGHT
    pil_box.line.color.rgb = col_pil
    pil_box.line.width = Pt(1.5)
    
    tf_pb = pil_box.text_frame
    tf_pb.word_wrap = True
    p_ph = tf_pb.paragraphs[0]
    p_ph.text = title_pil
    p_ph.font.name = "Arial Black"
    p_ph.font.size = Pt(12)
    p_ph.font.color.rgb = col_pil
    p_ph.space_after = Pt(4)
    
    for pt in points_pil:
        p_pt = tf_pb.add_paragraph()
        p_pt.space_after = Pt(3)
        r = p_pt.add_run()
        r.text = f"• {pt}"
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.color.rgb = DARK_SLATE

# Bottom Section: Potential Challenges and Risks vs Strategies For Overcoming
# Headers
ch_hdr = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.45), Inches(5.7), Inches(0.4))
ch_hdr.fill.solid()
ch_hdr.fill.fore_color.rgb = ROSE_ACC
ch_hdr.line.fill.background()
tf_ch = ch_hdr.text_frame
p_ch = tf_ch.paragraphs[0]
p_ch.text = "Potential Challenges and Risks"
p_ch.font.name = "Arial Black"
p_ch.font.size = Pt(11)
p_ch.font.color.rgb = WHITE
p_ch.alignment = PP_ALIGN.CENTER

st_hdr = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(3.45), Inches(5.7), Inches(0.4))
st_hdr.fill.solid()
st_hdr.fill.fore_color.rgb = GREEN_ACC
st_hdr.line.fill.background()
tf_sth = st_hdr.text_frame
p_sth = tf_sth.paragraphs[0]
p_sth.text = "Strategies For Overcoming Challenges"
p_sth.font.name = "Arial Black"
p_sth.font.size = Pt(11)
p_sth.font.color.rgb = WHITE
p_sth.alignment = PP_ALIGN.CENTER

challenges_solutions = [
    ("Anti-Scraping & IP Rate Limiting", "Airlines and OTAs block frequent automated queries via Cloudflare/Akamai.",
     "Playwright Stealth + Proxy Rotation", "Deploy headless browsers with residential proxy rotation and official OTA APIs (Travelpayouts)."),
    
    ("Dynamic Outliers & Pricing Glitches", "Midnight flash sales or last-minute extreme fares skew the price index.",
     "Vectorized Grouped IQR Cleaning", "Flag statistical anomalies per route+horizon group without deleting schedule rows."),
    
    ("Traffic Weight Network Drift", "Airline route frequency additions or seasonal schedule shifts alter passenger shares.",
     "Annual DGCA Traffic Recalibration", "Dynamic weight updates using official annual DGCA city-pair passenger volume tables."),
    
    ("Missing & Sold-Out Flight Gaps", "Flights sell out close to departure (T+1), creating data voids.",
     "Econometric Regression Imputation", "Impute sold-out slots using carrier mean fare spreads and advance-day regression curves."),
    
    ("Legacy MoSPI Integration Latency", "Integrating modern high-frequency feeds with traditional monthly publication schedules.",
     "Standardized Dual-Cadence APIs", "Provide both daily high-frequency nowcast feeds and monthly consolidated Laspeyres tables.")
]

for idx_cs, (c_title, c_desc, s_title, s_desc) in enumerate(challenges_solutions):
    row_y = Inches(3.95 + idx_cs * 0.58)
    
    # Challenge Card (Left)
    c_card = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), row_y, Inches(5.7), Inches(0.52))
    c_card.fill.solid()
    c_card.fill.fore_color.rgb = WHITE
    c_card.line.color.rgb = CARD_BORDER
    c_card.line.width = Pt(1)
    tf_cc = c_card.text_frame
    tf_cc.word_wrap = True
    p_cc = tf_cc.paragraphs[0]
    
    # Number badge
    r_num = p_cc.add_run()
    r_num.text = f"0{idx_cs+1}  "
    r_num.font.name = "Arial Black"
    r_num.font.size = Pt(9.5)
    r_num.font.color.rgb = ROSE_ACC
    
    r_ct = p_cc.add_run()
    r_ct.text = f"{c_title}: "
    r_ct.font.name = "Arial"
    r_ct.font.bold = True
    r_ct.font.size = Pt(8.5)
    r_ct.font.color.rgb = DARK_SLATE
    
    r_cd = p_cc.add_run()
    r_cd.text = c_desc
    r_cd.font.name = "Arial"
    r_cd.font.size = Pt(8)
    r_cd.font.color.rgb = MUTED_SLATE

    # Strategy Card (Right)
    s_card = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), row_y, Inches(5.7), Inches(0.52))
    s_card.fill.solid()
    s_card.fill.fore_color.rgb = WHITE
    s_card.line.color.rgb = CARD_BORDER
    s_card.line.width = Pt(1)
    tf_sc = s_card.text_frame
    tf_sc.word_wrap = True
    p_sc = tf_sc.paragraphs[0]
    
    r_snum = p_sc.add_run()
    r_snum.text = f"0{idx_cs+1}  "
    r_snum.font.name = "Arial Black"
    r_snum.font.size = Pt(9.5)
    r_snum.font.color.rgb = GREEN_ACC
    
    r_st = p_sc.add_run()
    r_st.text = f"{s_title}: "
    r_st.font.name = "Arial"
    r_st.font.bold = True
    r_st.font.size = Pt(8.5)
    r_st.font.color.rgb = DARK_SLATE
    
    r_sd = p_sc.add_run()
    r_sd.text = s_desc
    r_sd.font.name = "Arial"
    r_sd.font.size = Pt(8)
    r_sd.font.color.rgb = MUTED_SLATE


# ==============================================================================
# SLIDE 5: IMPACT AND BENEFITS
# ==============================================================================
slide5 = prs.slides.add_slide(blank_layout)
add_header_footer(slide5, 5, title_text="IMPACT AND BENEFITS")

# Top Banner Quote Box
quote_box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.15), Inches(11.7), Inches(0.55))
quote_box.fill.solid()
quote_box.fill.fore_color.rgb = BG_LIGHT
quote_box.line.color.rgb = TEAL_HEADER
quote_box.line.width = Pt(1.5)
tf_qb = quote_box.text_frame
p_qb = tf_qb.paragraphs[0]
p_qb.text = "“Transforming India's Inflation Surveillance from Slow Physical Counter Surveys to Real-time Digital Intelligence.”"
p_qb.font.name = "Arial Black"
p_qb.font.size = Pt(11.5)
p_qb.font.color.rgb = NAVY_BLUE
p_qb.alignment = PP_ALIGN.CENTER

# Left Side: Potential Impact on Targeted Audience (Hub Diagram)
hub_circle = slide5.shapes.add_shape(MSO_SHAPE.OVAL, Inches(2.6), Inches(3.2), Inches(2.2), Inches(2.2))
hub_circle.fill.solid()
hub_circle.fill.fore_color.rgb = NAVY_BLUE
hub_circle.line.color.rgb = ORANGE_SIH
hub_circle.line.width = Pt(2.5)
tf_hc = hub_circle.text_frame
tf_hc.word_wrap = True
tf_hc.vertical_anchor = MSO_ANCHOR.MIDDLE
p_hc = tf_hc.paragraphs[0]
p_hc.text = "Targeted\nImpact\nAudience"
p_hc.font.name = "Arial Black"
p_hc.font.size = Pt(13)
p_hc.font.color.rgb = WHITE
p_hc.alignment = PP_ALIGN.CENTER

# 4 Surrounding Audience Boxes
audience_boxes = [
    ("MoSPI / NSO", "Automates CPI airfare component collection; eliminates manual counter visit costs.", Inches(0.8), Inches(1.9), Inches(2.7), Inches(1.1)),
    ("RBI / MPC", "High-frequency weekly/daily inflation nowcasting to inform Monetary Policy Committee decisions.", Inches(4.0), Inches(1.9), Inches(2.7), Inches(1.1)),
    ("Aviation & DGCA", "Transparent tariff surveillance detecting holiday price gouging and unfair surges.", Inches(0.8), Inches(5.6), Inches(2.7), Inches(1.1)),
    ("Consumers & Nation", "Empirical booking-horizon guidance and enhanced statistical sovereignty.", Inches(4.0), Inches(5.6), Inches(2.7), Inches(1.1))
]

for title_a, desc_a, left_a, top_a, w_a, h_a in audience_boxes:
    abox = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_a, top_a, w_a, h_a)
    abox.fill.solid()
    abox.fill.fore_color.rgb = WHITE
    abox.line.color.rgb = CARD_BORDER
    abox.line.width = Pt(1)
    tf_ab = abox.text_frame
    tf_ab.word_wrap = True
    p_ab1 = tf_ab.paragraphs[0]
    p_ab1.text = title_a
    p_ab1.font.name = "Arial"
    p_ab1.font.bold = True
    p_ab1.font.size = Pt(9.5)
    p_ab1.font.color.rgb = NAVY_BLUE
    
    p_ab2 = tf_ab.add_paragraph()
    p_ab2.text = desc_a
    p_ab2.font.name = "Arial"
    p_ab2.font.size = Pt(8)
    p_ab2.font.color.rgb = DARK_SLATE

# Right Side: Benefits of the Solution (3 Large Category Cards like reference)
ben_header = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), Inches(1.85), Inches(5.3), Inches(0.4))
ben_header.fill.solid()
ben_header.fill.fore_color.rgb = TEAL_HEADER
ben_header.line.fill.background()
tf_bh = ben_header.text_frame
p_bh = tf_bh.paragraphs[0]
p_bh.text = "Benefits of the Solution"
p_bh.font.name = "Arial Black"
p_bh.font.size = Pt(11)
p_bh.font.color.rgb = WHITE
p_bh.alignment = PP_ALIGN.CENTER

benefits_categories = [
    ("Social & Policy Trust", "Builds public confidence with transparent, tamper-evident airfare inflation reporting. Replaces opaque survey figures with empirical big data, aligning India with IMF/OECD statistical best practices.", Inches(2.35), TEAL_HEADER),
    ("Economic & Cost Efficiency", "Saves crores in annual field survey logistics. Prevents monetary policy lag by equipping the RBI with weekly inflation indicators to manage macro-economic price stability.", Inches(3.85), GREEN_ACC),
    ("Operational Modernization", "100% automated headless data pipeline with 99.9% uptime. Continuous validation against official DGCA benchmarks guarantees institutional compliance and statistical integrity.", Inches(5.35), PURPLE_ACC)
]

for title_b, desc_b, top_b, col_b in benefits_categories:
    b_card = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), top_b, Inches(5.3), Inches(1.35))
    b_card.fill.solid()
    b_card.fill.fore_color.rgb = WHITE
    b_card.line.color.rgb = col_b
    b_card.line.width = Pt(1.5)
    
    tf_bc = b_card.text_frame
    tf_bc.word_wrap = True
    p_bc1 = tf_bc.paragraphs[0]
    p_bc1.text = f"“ {title_b} ”"
    p_bc1.font.name = "Arial Black"
    p_bc1.font.size = Pt(10)
    p_bc1.font.color.rgb = col_b
    
    p_bc2 = tf_bc.add_paragraph()
    p_bc2.text = desc_b
    p_bc2.font.name = "Arial"
    p_bc2.font.size = Pt(8.5)
    p_bc2.font.color.rgb = DARK_SLATE
    p_bc2.space_before = Pt(3)


# ==============================================================================
# SLIDE 6: RESEARCH AND REFERENCES
# ==============================================================================
slide6 = prs.slides.add_slide(blank_layout)
add_header_footer(slide6, 6, title_text="RESEARCH AND REFERENCES")

# Top Section: Field & Applied Research
field_box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.15), Inches(11.7), Inches(1.8))
field_box.fill.solid()
field_box.fill.fore_color.rgb = WHITE
field_box.line.color.rgb = TEAL_HEADER
field_box.line.width = Pt(1.5)

tf_fb = field_box.text_frame
tf_fb.word_wrap = True

p_fh = tf_fb.paragraphs[0]
p_fh.text = "Field & Applied Research"
p_fh.font.name = "Arial Black"
p_fh.font.size = Pt(13)
p_fh.font.color.rgb = NAVY_BLUE
p_fh.space_after = Pt(4)

field_pts = [
    "Evaluated DGCA Tariff Monitoring Unit (TMU) monthly domestic fare publications and airline pricing brackets across 20 high-density corridors.",
    "Analyzed domestic aviation passenger distribution from DGCA annual statistics (>109 Million passengers) to calibrate route weighting matrices.",
    "Tested advance-purchase price escalation across 5 booking horizons (T+1 to T+45) using 27,233 simulated and live web-scraped flight observations.",
    "Validated computed Fisher index against DGCA reported route averages achieving strong statistical agreement (Pearson correlation r = 0.6639)."
]

for pt in field_pts:
    p = tf_fb.add_paragraph()
    p.space_after = Pt(2)
    r = p.add_run()
    r.text = f"• {pt}"
    r.font.name = "Arial"
    r.font.size = Pt(9)
    r.font.color.rgb = DARK_SLATE

# Bottom Section: Academic & Government Sources
acad_box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.1), Inches(11.7), Inches(3.75))
acad_box.fill.solid()
acad_box.fill.fore_color.rgb = WHITE
acad_box.line.color.rgb = NAVY_BLUE
acad_box.line.width = Pt(1.5)

tf_ab = acad_box.text_frame
tf_ab.word_wrap = True

p_ah = tf_ab.paragraphs[0]
p_ah.text = "Academic & Government Sources"
p_ah.font.name = "Arial Black"
p_ah.font.size = Pt(13)
p_ah.font.color.rgb = NAVY_BLUE
p_ah.space_after = Pt(4)

academic_sources = [
    ("MoSPI eSankhyiki Portal (Official Government Data Repository): ",
     "National Data Archive, CPI Methodology, and Data APIs for National Accounts. ",
     "https://esankhyiki.mospi.gov.in"),

    ("Directorate General of Civil Aviation (DGCA) Traffic Reports: ",
     "Monthly Domestic Passenger Traffic Statistics & Tariff Monitoring Unit (TMU) Route Fare Publications. ",
     "https://www.dgca.gov.in"),

    ("Ministry of Civil Aviation — Aircraft Rules, 1937 (Rule 135): ",
     "Statutory regulatory framework governing domestic airfare tariff determination and passenger transparency. ",
     "https://www.civilaviation.gov.in"),

    ("International Monetary Fund (IMF) — Consumer Price Index Manual (2020): ",
     "Principles of Superlative Price Index Numbers (Fisher & Törnqvist) and scanner/web-scraped data treatment in national CPI. ",
     "https://www.imf.org/en/Data/Manuals/cpi-manual"),

    ("International Labour Organization (ILO) — CPI Theory & Practice: ",
     "Treatment of seasonal products, dynamic pricing, and quality adjustments in service sector indices. ",
     "https://www.ilo.org/stat/Areasofwork/PriceStatistics/"),

    ("Reserve Bank of India (RBI) — Monetary Policy Report: ",
     "High-frequency nowcasting of volatile transport inflation components for forward-looking inflation targeting. ",
     "https://www.rbi.org.in")
]

for title_s, desc_s, url_s in academic_sources:
    p = tf_ab.add_paragraph()
    p.space_after = Pt(3)
    
    r1 = p.add_run()
    r1.text = f"• {title_s}"
    r1.font.name = "Arial"
    r1.font.bold = True
    r1.font.size = Pt(8.5)
    r1.font.color.rgb = NAVY_BLUE
    
    r2 = p.add_run()
    r2.text = desc_s
    r2.font.name = "Arial"
    r2.font.size = Pt(8)
    r2.font.color.rgb = DARK_SLATE
    
    r3 = p.add_run()
    r3.text = url_s
    r3.font.name = "Arial"
    r3.font.size = Pt(7.5)
    r3.font.underline = True
    r3.font.color.rgb = RGBColor(37, 99, 235)

# Save presentation
output_path = "c:\\Users\\hp\\Downloads\\sih travel\\SIH_Submission_Airfare_Price_Index.pptx"
prs.save(output_path)
print(f"Presentation saved successfully at: {output_path}")
