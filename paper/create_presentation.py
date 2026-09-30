import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # Set slide dimensions to Widescreen 16:9 (13.333 x 7.5 inches)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # blank layout

    # Color Palette
    BG_DARK = RGBColor(15, 23, 42)      # Deep Slate Blue #0F172A
    CARD_BG = RGBColor(30, 41, 59)      # Card Slate #1E293B
    TEXT_LIGHT = RGBColor(248, 250, 252)# Bright White #F8FAFC
    TEXT_MUTED = RGBColor(148, 163, 184)# Muted Slate #94A3B8
    CYAN_ACCENT = RGBColor(56, 189, 248)# Electric Cyan #38BDF8
    GOLD_ACCENT = RGBColor(245, 158, 11) # Emerald Gold #F59E0B
    GREEN_ACCENT = RGBColor(52, 211, 153)# Mint Green #34D399

    def add_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()

    def add_header(slide, title_text, category_text="NKCON-2026 CONFERENCE PRESENTATION"):
        # Category label
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = CYAN_ACCENT

        # Title label
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_LIGHT

    def add_card(slide, left, top, width, height, bg_color=CARD_BG):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = RGBColor(51, 65, 85) # subtle border #334155
        card.line.width = Pt(1)
        return card

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    add_bg(slide1)

    # Accent Card behind Title
    add_card(slide1, Inches(1.0), Inches(1.2), Inches(11.333), Inches(5.1), CARD_BG)

    # Conference Tag
    tag_box = slide1.shapes.add_textbox(Inches(1.4), Inches(1.6), Inches(10.5), Inches(0.4))
    tf_tag = tag_box.text_frame
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = "NKCON-2026 • FULL RESEARCH PAPER PRESENTATION"
    p_tag.font.size = Pt(13)
    p_tag.font.bold = True
    p_tag.font.color.rgb = CYAN_ACCENT

    # Main Paper Title
    t_box = slide1.shapes.add_textbox(Inches(1.4), Inches(2.1), Inches(10.5), Inches(1.8))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = "Energy-Aware Spoofing Attack Detection in\nWireless Sensor Networks Using Multi-Feature Analysis"
    p_t.font.size = Pt(32)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_LIGHT

    # Authors
    auth_box = slide1.shapes.add_textbox(Inches(1.4), Inches(4.2), Inches(10.5), Inches(1.0))
    tf_auth = auth_box.text_frame
    p_a1 = tf_auth.paragraphs[0]
    p_a1.text = "Authors: Prashanth K  |  Dr. Usha J"
    p_a1.font.size = Pt(18)
    p_a1.font.bold = True
    p_a1.font.color.rgb = GOLD_ACCENT

    p_a2 = tf_auth.add_paragraph()
    p_a2.text = "Department of Master of Computer Applications, RV College of Engineering (Affiliated to VTU, Belagavi), Bengaluru, India"
    p_a2.font.size = Pt(13)
    p_a2.font.color.rgb = TEXT_MUTED

    # Highlights Bar
    h_box = slide1.shapes.add_textbox(Inches(1.4), Inches(5.4), Inches(10.5), Inches(0.6))
    tf_h = h_box.text_frame
    p_h = tf_h.paragraphs[0]
    p_h.text = "Key Metrics: 98.18% Detection Rate  |  0.03% FPR  |  0.540 mJ/pkt Energy  |  130× CH Lifetime Extension"
    p_h.font.size = Pt(14)
    p_h.font.bold = True
    p_h.font.color.rgb = GREEN_ACCENT

    # =========================================================================
    # SLIDE 2: Problem Statement & Security-Energy Dilemma
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_bg(slide2)
    add_header(slide2, "The Security vs. Energy Impasse in Clustered WSNs")

    # Left Card: Cryptographic Bottleneck
    add_card(slide2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    cb1 = slide2.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.5))
    tf_cb1 = cb1.text_frame
    tf_cb1.word_wrap = True
    
    p = tf_cb1.paragraphs[0]
    p.text = "Continuous Cryptography Bottleneck"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    bullets1 = [
        ("ECDSA P-256 Signatures: ", "Provides mathematical origin guarantee."),
        ("Prohibitive Overhead: ", "Requires ~90.0 mJ per verification on 16-bit MSP430 motes (8 MHz, <10 KB RAM)."),
        ("Rapid Battery Exhaustion: ", "A Cluster Head (CH) under continuous verification exhausts 21.6 kJ dual-AA battery in <3.5 minutes."),
        ("Single Point of Failure: ", "Adversary induces denial-of-charge attack simply by injecting high-rate spoofed frames.")
    ]
    for b_title, b_desc in bullets1:
        p = tf_cb1.add_paragraph()
        p.text = "• " + b_title
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = TEXT_LIGHT
        run = p.add_run()
        run.text = b_desc
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right Card: Physical Screening Bottleneck
    add_card(slide2, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
    cb2 = slide2.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.5))
    tf_cb2 = cb2.text_frame
    tf_cb2.word_wrap = True

    p = tf_cb2.paragraphs[0]
    p.text = "Physical RSSI Screening Limitations"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    bullets2 = [
        ("Lightweight Overhead: ", "Consumes only ~5 µJ per packet evaluation."),
        ("Channel Fading Vulnerability: ", "Multipath propagation & shadowing cause ±4 dBm signal variance."),
        ("High False Positive Rate (FPR): ", "False alarm rates exceed 12% in real propagation environments."),
        ("Unnecessary Escalation: ", "High FPR triggers unnecessary ECDSA verification, undermining energy savings.")
    ]
    for b_title, b_desc in bullets2:
        p = tf_cb2.add_paragraph()
        p.text = "• " + b_title
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = TEXT_LIGHT
        run = p.add_run()
        run.text = b_desc
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 3: Proposed HEDSD Framework Architecture
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_bg(slide3)
    add_header(slide3, "Hybrid Event-Driven Spoofing Detection (HEDSD)")

    # 3 Mode Cards
    modes = [
        ("FULL MODE", "E_ratio > 0.70", "0.540 mJ / pkt", "Full trust evaluation with selective ECDSA audits on flagged packets crossing threshold.", CYAN_ACCENT),
        ("LIGHT MODE", "0.30 < E_ratio <= 0.70", "0.055 mJ / pkt", "Cryptographic checks suppressed for frames passing RSSI screen; sliding window trust accumulation.", GOLD_ACCENT),
        ("EVENT_ONLY MODE", "E_ratio <= 0.30", "0.0016 mJ / pkt", "Sampled evaluation (1-in-3 pkts) to preserve residual capacity for emergency event reporting.", GREEN_ACCENT)
    ]

    for i, (m_name, m_cond, m_cost, m_desc, m_color) in enumerate(modes):
        left_pos = Inches(0.8 + i * 4.0)
        add_card(slide3, left_pos, Inches(1.8), Inches(3.7), Inches(5.0))
        
        box = slide3.shapes.add_textbox(left_pos + Inches(0.2), Inches(2.0), Inches(3.3), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = m_name
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = m_color

        p2 = tf.add_paragraph()
        p2.text = f"Trigger: {m_cond}"
        p2.font.size = Pt(12)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_MUTED

        p3 = tf.add_paragraph()
        p3.text = f"Mean Cost: {m_cost}"
        p3.font.size = Pt(15)
        p3.font.bold = True
        p3.font.color.rgb = TEXT_LIGHT

        p4 = tf.add_paragraph()
        p4.text = "\n" + m_desc
        p4.font.size = Pt(13)
        p4.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 4: Multi-Feature Scoring Engine & Dynamic Weighting
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_bg(slide4)
    add_header(slide4, "Multi-Feature Composite Anomaly Engine")

    # Left Card: Anomaly Components & Equation
    add_card(slide4, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0))
    c41 = slide4.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.1), Inches(4.5))
    tf41 = c41.text_frame
    tf41.word_wrap = True

    p = tf41.paragraphs[0]
    p.text = "Composite Spoof Score Formulation"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    p = tf41.add_paragraph()
    p.text = "Spoof_Score_i = α · Identity_Anomaly + β · Traffic_Anomaly + γ · Energy_Anomaly"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    feats = [
        ("1. Identity Anomaly (Spatial RSSI):", "Measures physical transmitter displacement |RSSI_obs - RSSI_exp| / 5.0 dBm."),
        ("2. Traffic Anomaly (Inter-Arrival Time):", "Tracks injection rate spikes |IAT_obs - IAT_exp| / IAT_exp."),
        ("3. Energy Anomaly (Battery Drain Rate):", "Monitors Cluster Head battery dissipation spikes dE_i/dt relative to baseline.")
    ]
    for f_title, f_desc in feats:
        p = tf41.add_paragraph()
        p.text = "\n" + f_title
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_LIGHT
        run = p.add_run()
        run.text = "\n" + f_desc
        run.font.bold = False
        run.font.size = Pt(12)
        run.font.color.rgb = TEXT_MUTED

    # Right Card: Dynamic Weighting & Isolation Conjunction Rule
    add_card(slide4, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
    c42 = slide4.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.5))
    tf42 = c42.text_frame
    tf42.word_wrap = True

    p = tf42.paragraphs[0]
    p.text = "Dynamic Adaptation & Conjunction Isolation"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACCENT

    p = tf42.add_paragraph()
    p.text = "Channel-Aware Weighting:\nNominal: α_0=0.40, β_0=0.40, γ_0=0.20\n• Elevated EWS increases α (spatial weight).\n• High RSSI noise attenuates β (prevents fading false alarms)."
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_LIGHT

    p = tf42.add_paragraph()
    p.text = "\nStrict 3-Condition Isolation Criterion:"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    p = tf42.add_paragraph()
    p.text = "Isolate_i = True IF (Spoof_Score > 0.65  AND  EWS > 0.40  AND  ΔRSSI > 5.0 dBm)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    p = tf42.add_paragraph()
    p.text = "Why Conjunction? Single condition can trigger on noise; simultaneous satisfaction is statistically improbable without active impersonation."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 5: Experimental Setup & Network Parameters
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_bg(slide5)
    add_header(slide5, "Discrete-Event Simulation Setup (NS-3)")

    # 4 Parameter Cards in a Grid
    params_cards = [
        ("NETWORK TOPOLOGY", [("Area:", "1000 m × 1000 m"), ("Total Nodes:", "N = 401 nodes"), ("Cluster Heads:", "40 CHs (8 × 5 Grid)"), ("Leaf Sensor Motes:", "359 leaf nodes")]),
        ("ATTACK SCENARIOS", [("Attacker Density:", "60 Active Attackers (15%)"), ("Low Intensity:", "5% (1 Spoofer/Cluster)"), ("Medium Intensity:", "15% (3 Spoofers/Cluster)"), ("High Intensity:", "30% (5 Spoofers/Cluster)")]),
        ("HARDWARE & BATTERY", [("Leaf Battery:", "2 × AA Alkaline (21.6 kJ)"), ("Operating Voltage:", "3.0 V (2.0 Ah capacity)"), ("CH Reserve:", "50.0 kJ initial capacity"), ("Transceiver:", "CC2420 (50 nJ/bit electronics)")]),
        ("EVALUATION DATASET", [("Simulation Frames:", "1,120,555 Total Packets"), ("Attack Frames:", "5,938 Spoofed Packets"), ("Legitimate Frames:", "1,114,617 Benign Packets"), ("Validation Scheme:", "5-Fold Cross-Validation")])
    ]

    for idx, (title, items) in enumerate(params_cards):
        r, c = idx // 2, idx % 2
        left_pos = Inches(0.8 + c * 6.0)
        top_pos = Inches(1.8 + r * 2.6)
        
        add_card(slide5, left_pos, top_pos, Inches(5.7), Inches(2.4))
        box = slide5.shapes.add_textbox(left_pos + Inches(0.2), top_pos + Inches(0.15), Inches(5.3), Inches(2.1))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT

        for label, val in items:
            p = tf.add_paragraph()
            p.text = f"• {label} "
            p.font.bold = True
            p.font.size = Pt(13)
            p.font.color.rgb = TEXT_LIGHT
            run = p.add_run()
            run.text = val
            run.font.bold = False
            run.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 6: Primary Classification Results
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_bg(slide6)
    add_header(slide6, "Classification & Security Performance")

    # Left: Big Metric Stat Cards
    stat_boxes = [
        ("99.96%", "Overall Classification Accuracy", CYAN_ACCENT),
        ("98.18%", "Spoofing Detection Recall", GREEN_ACCENT),
        ("0.03%", "False Positive Rate (FPR)", GOLD_ACCENT),
        ("0.998", "Area Under ROC Curve (AUC)", CYAN_ACCENT)
    ]

    for idx, (val_txt, lbl_txt, col) in enumerate(stat_boxes):
        r, c = idx // 2, idx % 2
        left_pos = Inches(0.8 + c * 2.8)
        top_pos = Inches(1.8 + r * 2.5)

        add_card(slide6, left_pos, top_pos, Inches(2.6), Inches(2.3))
        b = slide6.shapes.add_textbox(left_pos + Inches(0.1), top_pos + Inches(0.3), Inches(2.4), Inches(1.7))
        tf = b.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = val_txt
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(32)
        p.font.bold = True
        p.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = lbl_txt
        p2.alignment = PP_ALIGN.CENTER
        p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_LIGHT

    # Right Card: Detailed Metric Summary Table
    add_card(slide6, Inches(6.6), Inches(1.8), Inches(5.9), Inches(5.0))
    c62 = slide6.shapes.add_textbox(Inches(6.9), Inches(2.0), Inches(5.3), Inches(4.5))
    tf62 = c62.text_frame
    tf62.word_wrap = True

    p = tf62.paragraphs[0]
    p.text = "Instance-Level Evaluation Summary"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    summary_bullets = [
        ("Correct Attack Isolations (TP):", "5,830 of 5,938 attack frames (98.18% Recall)."),
        ("Legitimate Frames Accepted (TN):", "1,114,301 of 1,114,617 benign frames."),
        ("False Alarms (FP Rate):", "Only 316 false alarms out of 1.11M frames (0.03% FPR)."),
        ("Selectivity Advantage:", "Confines heavy ECDSA verifications to just 0.53% of frames."),
        ("Precision & F1-Score:", "Precision: 94.86%  |  F1-Score: 96.49%.")
    ]
    for b_title, b_desc in summary_bullets:
        p = tf62.add_paragraph()
        p.text = "• " + b_title
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_LIGHT
        run = p.add_run()
        run.text = " " + b_desc
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 7: Feature Importance & Ablation Study
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_bg(slide7)
    add_header(slide7, "Feature Importance & Ablation Proof")

    # Left Card: Gini Importance Ranking
    add_card(slide7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    c71 = slide7.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.5))
    tf71 = c71.text_frame
    tf71.word_wrap = True

    p = tf71.paragraphs[0]
    p.text = "Gini Feature Importance Ranking"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    gini_items = [
        ("Spatial RSSI Deviation (ΔRSSI): ", "44.2% Importance", "Primary physical location validation."),
        ("Battery Energy Drain Rate (dE/dt): ", "31.8% Importance", "Early attack burst detection signal."),
        ("Inter-Packet Interval (IAT): ", "18.5% Importance", "Telemetry transmission rate tracking."),
        ("Early Warning Score (EWS): ", "5.5% Importance", "Transient channel noise filtering.")
    ]
    for g_title, g_val, g_role in gini_items:
        p = tf71.add_paragraph()
        p.text = "• " + g_title
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_LIGHT
        run1 = p.add_run()
        run1.text = g_val + "\n"
        run1.font.bold = True
        run1.font.color.rgb = GOLD_ACCENT
        run2 = p.add_run()
        run2.text = "  Role: " + g_role
        run2.font.bold = False
        run2.font.color.rgb = TEXT_MUTED

    # Right Card: Ablation Study
    add_card(slide7, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
    c72 = slide7.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.5))
    tf72 = c72.text_frame
    tf72.word_wrap = True

    p = tf72.paragraphs[0]
    p.text = "Ablation Study: Impact of Energy Feature"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACCENT

    ablation_bullets = [
        ("Baseline (Without dE/dt):", "F1-Score: 90.13%  |  FPR: 1.42%."),
        ("Proposed HEDSD (With dE/dt):", "F1-Score: 96.49%  |  FPR: 0.03%."),
        ("Relative Improvement:", "+6.36 Points F1-Score  |  -97.9% FPR Reduction."),
        ("Why Real-Time Energy Tracking Matters:", "Attack bursts accelerate CH battery drain rate within the first 1-2 frames—before spatial RSSI averages fully stabilize. Energy drain is essentially FREE to compute from onboard hardware.")
    ]
    for b_title, b_desc in ablation_bullets:
        p = tf72.add_paragraph()
        p.text = "• " + b_title
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_LIGHT
        run = p.add_run()
        run.text = "\n  " + b_desc
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 8: Scalability, Latency & Network Lifetime Extension
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_bg(slide8)
    add_header(slide8, "Latency, Scalability & Battery Longevity")

    # Card 1: Sub-Second Latency
    add_card(slide8, Inches(0.8), Inches(1.8), Inches(3.7), Inches(5.0))
    b81 = slide8.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(3.3), Inches(4.5))
    tf81 = b81.text_frame
    tf81.word_wrap = True
    p = tf81.paragraphs[0]
    p.text = "Sub-Second Isolation"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT
    l_info = [
        ("5% Attackers:", "1.24 ± 0.05 s (2.48 pkts)"),
        ("15% Attackers:", "0.85 ± 0.03 s (1.70 pkts)"),
        ("30% Attackers:", "0.42 ± 0.02 s (0.84 pkts)"),
        ("Key Insight:", "Inverse relationship—higher attack intensity accelerates detection!")
    ]
    for lbl, val in l_info:
        p = tf81.add_paragraph()
        p.text = "• " + lbl + " "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_LIGHT
        run = p.add_run()
        run.text = val
        run.font.color.rgb = TEXT_MUTED

    # Card 2: O(1) Scalability
    add_card(slide8, Inches(4.8), Inches(1.8), Inches(3.7), Inches(5.0))
    b82 = slide8.shapes.add_textbox(Inches(5.0), Inches(2.0), Inches(3.3), Inches(4.5))
    tf82 = b82.text_frame
    tf82.word_wrap = True
    p = tf82.paragraphs[0]
    p.text = "Analytical Scalability"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT
    s_info = [
        ("N = 50 Nodes:", "99.98% Acc | 0.15 KB RAM"),
        ("N = 100 Nodes:", "99.97% Acc | 0.28 KB RAM"),
        ("N = 200 Nodes:", "99.96% Acc | 0.55 KB RAM"),
        ("N = 401 Nodes:", "99.96% Acc | 1.08 KB RAM"),
        ("Why O(1) Scale:", "Distributed cluster computation with zero inter-cluster sync overhead.")
    ]
    for lbl, val in s_info:
        p = tf82.add_paragraph()
        p.text = "• " + lbl + " "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_LIGHT
        run = p.add_run()
        run.text = val
        run.font.color.rgb = TEXT_MUTED

    # Card 3: 130x Lifetime Extension
    add_card(slide8, Inches(8.8), Inches(1.8), Inches(3.7), Inches(5.0))
    b83 = slide8.shapes.add_textbox(Inches(9.0), Inches(2.0), Inches(3.3), Inches(4.5))
    tf83 = b83.text_frame
    tf83.word_wrap = True
    p = tf83.paragraphs[0]
    p.text = "130× Lifetime Extension"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACCENT
    e_info = [
        ("Continuous ECDSA:", "CH battery exhausted in 3.0 seconds under continuous verifications."),
        ("Proposed HEDSD:", "CH operational span extended to 397.0 seconds under simulated attack."),
        ("Operational Value:", "Converts infeasible security into multi-year field deployment longevity.")
    ]
    for lbl, val in e_info:
        p = tf83.add_paragraph()
        p.text = "• " + lbl + "\n  "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_LIGHT
        run = p.add_run()
        run.text = val
        run.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 9: Benchmark Comparison Against SOTA Baselines
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_bg(slide9)
    add_header(slide9, "Benchmarking Against State-of-the-Art Baselines")

    add_card(slide9, Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    c9 = slide9.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(11.1), Inches(4.5))
    tf9 = c9.text_frame
    tf9.word_wrap = True

    p = tf9.paragraphs[0]
    p.text = "Quantitative Comparative Benchmark Table"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    sota_bullets = [
        ("RSSI-Based Filter (Yang et al.):", "0.005 mJ/pkt | 94.80% Acc | 2.10% FPR — Fails under multipath fading."),
        ("Dynamic Trust Management (IEEE TMC '24):", "0.065 mJ/pkt | 95.20% Acc | 1.80% FPR — Static parameters, high FPR."),
        ("SVM Spoofing Classifier (IEEE Sensors '22):", "0.450 mJ/pkt | 97.10% Acc | 0.90% FPR — High MCU matrix compute cost."),
        ("Multi-Attribute Physical Auth (MDPI '24):", "0.120 mJ/pkt | 94.80% Acc | 2.10% FPR — Single physical modality limitation."),
        ("Federated Trust-ML Auth (IEEE IoTJ '24):", "2.500 mJ/pkt | 98.50% Acc | 0.40% FPR — Heavy federated parameter aggregation."),
        ("Continuous ECDSA-P256 Benchmark:", "90.000 mJ/pkt | 100.0% Acc | 0.00% FPR — Infeasible per-packet energy draw."),
        ("PROPOSED HEDSD (THIS WORK):", "0.540 mJ/pkt | 98.18% Recall | 0.03% FPR — Occupies Optimal Pareto Frontier!")
    ]
    for b_title, b_desc in sota_bullets:
        p = tf9.add_paragraph()
        if "PROPOSED" in b_title:
            p.text = "★ " + b_title + " "
            p.font.bold = True
            p.font.size = Pt(13)
            p.font.color.rgb = GOLD_ACCENT
            run = p.add_run()
            run.text = b_desc
            run.font.bold = True
            run.font.color.rgb = GREEN_ACCENT
        else:
            p.text = "• " + b_title + " "
            p.font.bold = True
            p.font.size = Pt(12)
            p.font.color.rgb = TEXT_LIGHT
            run = p.add_run()
            run.text = b_desc
            run.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 10: Conclusion & Q&A
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    add_bg(slide10)
    add_header(slide10, "Conclusion & Key Takeaways")

    add_card(slide10, Inches(1.5), Inches(1.8), Inches(10.333), Inches(5.0))
    c10 = slide10.shapes.add_textbox(Inches(1.8), Inches(2.1), Inches(9.7), Inches(4.4))
    tf10 = c10.text_frame
    tf10.word_wrap = True

    p = tf10.paragraphs[0]
    p.text = "Summary of Contributions & Future Work"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    concl_bullets = [
        ("Resolved Security-Energy Dilemma:", "Demonstrated that event-driven cryptographic invocation reduces WSN evaluation cost by 99.40% (down to 0.540 mJ/pkt) without sacrificing security."),
        ("High Detection Fidelity:", "Achieves 98.18% detection rate, 96.49% F1-score, 0.998 AUC, and a low 0.03% false positive rate across 1.12 million evaluation frames."),
        ("Real-Time Feasibility:", "Sub-second isolation latency (0.85 s mean response) limits malicious telemetry propagation to at most one packet period."),
        ("Real-World IIoT Relevance:", "Directly applicable to industrial IoT, smart grid, and precision agriculture deployments requiring multi-year unattended operation."),
        ("Future Roadmap:", "Physical hardware prototyping on STM32/ESP32 platforms, incorporation of Peukert-corrected non-linear battery models, and extension to mobile topologies.")
    ]
    for b_title, b_desc in concl_bullets:
        p = tf10.add_paragraph()
        p.text = "✔ " + b_title + " "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = CYAN_ACCENT
        run = p.add_run()
        run.text = b_desc
        run.font.bold = False
        run.font.color.rgb = TEXT_LIGHT

    # Q&A Footer
    p_qa = tf10.add_paragraph()
    p_qa.text = "\nThank You! Questions & Discussion Welcome."
    p_qa.alignment = PP_ALIGN.CENTER
    p_qa.font.size = Pt(18)
    p_qa.font.bold = True
    p_qa.font.color.rgb = GREEN_ACCENT

    # Save presentation
    output_path = "/home/kp/SpoofingAttack/paper/nkcon_2026_presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    create_deck()
