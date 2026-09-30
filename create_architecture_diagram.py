#!/usr/bin/env python3
"""
Generate publication-quality WSN Architecture & HEDSD Framework Diagram.
Saves high-resolution PNG: wsn_architecture_spoofing.png
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_hedsd_architecture_diagram():
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 70)
    ax.axis('off')

    # Color Palette
    bg_color = '#f8f9fa'
    border_color = '#2c3e50'
    ch_bg = '#ebf5fb'
    ch_border = '#2980b9'
    module_bg = '#d4efdf'
    module_border = '#27ae60'
    node_legit = '#27ae60'
    node_adv = '#c0392b'
    bs_bg = '#f5eep6'
    bs_border = '#8e44ad'

    # Main Title Header
    ax.text(50, 67, "Hybrid Event-Driven Spoofing Detection (HEDSD) Architecture", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#1a252f')

    # -------------------------------------------------------------
    # 1. Base Station Gateway Layer (Top)
    # -------------------------------------------------------------
    bs_box = patches.FancyBboxPatch((35, 56), 30, 8, boxstyle="round,pad=0.5,rounding_size=1.5",
                                    facecolor='#f4ecf7', edgecolor=bs_border, linewidth=2)
    ax.add_patch(bs_box)
    ax.text(50, 61, "Base Station / Gateway Sink", ha='center', va='center', fontsize=11, fontweight='bold', color='#6c3483')
    ax.text(50, 58, "Central SCADA / Industrial Monitoring Interface", ha='center', va='center', fontsize=8.5, style='italic', color='#512e5f')

    # Arrow CH to BS
    ax.annotate('', xy=(50, 56), xytext=(50, 48),
                arrowprops=dict(arrowstyle="->", color='#2980b9', lw=2.5, mutation_scale=15))
    ax.text(52, 52, "Filtered Verified Telemetry", fontsize=8.5, color='#2980b9', fontweight='bold')

    # -------------------------------------------------------------
    # 2. Cluster Head & HEDSD Module (Center)
    # -------------------------------------------------------------
    ch_outer = patches.FancyBboxPatch((12, 16), 76, 32, boxstyle="round,pad=0.6,rounding_size=2.0",
                                      facecolor=ch_bg, edgecolor=ch_border, linewidth=2)
    ax.add_patch(ch_outer)
    ax.text(50, 45.5, "Cluster Head (CH) Node — Local Processing Hub", ha='center', va='center', fontsize=11, fontweight='bold', color='#1b4f72')

    # HEDSD Inner Module Box
    hedsd_inner = patches.FancyBboxPatch((15, 19), 70, 24, boxstyle="round,pad=0.5,rounding_size=1.5",
                                         facecolor='#e8f8f5', edgecolor=module_border, linewidth=2, linestyle='--')
    ax.add_patch(hedsd_inner)
    ax.text(50, 40.5, "HEDSD Framework Security Engine", ha='center', va='center', fontsize=11, fontweight='bold', color='#117a65')

    # Sub-blocks inside HEDSD Engine
    # Block A: Feature Extraction
    b_a = patches.FancyBboxPatch((17, 21), 21, 16, boxstyle="round,pad=0.3", facecolor='#ffffff', edgecolor='#7d6608', linewidth=1.2)
    ax.add_patch(b_a)
    ax.text(27.5, 34.5, "1. Feature Extraction", ha='center', fontsize=9.5, fontweight='bold', color='#7d6608')
    ax.text(27.5, 31, "• Spatial RSSI Deviation (ΔRSSI_i)\n• Packet Inter-Arrival Time (Δτ_i)\n• CH Current Draw Rate (Ė_i)", 
            ha='center', fontsize=8, color='#4a3b00')

    # Block B: Composite Scoring & EWS
    b_b = patches.FancyBboxPatch((40, 21), 20, 16, boxstyle="round,pad=0.3", facecolor='#ffffff', edgecolor='#1f618d', linewidth=1.2)
    ax.add_patch(b_b)
    ax.text(50, 34.5, "2. Scoring & State Machine", ha='center', fontsize=9.5, fontweight='bold', color='#1f618d')
    ax.text(50, 31, "• Dynamic Weights (α, β, γ)\n• Composite Spoof_Score_i\n• 3-Tier Execution Loop\n  (FULL / LIGHT / EVENT_ONLY)", 
            ha='center', fontsize=7.5, color='#1b4f72')

    # Block C: Selective Crypto & Isolation
    b_c = patches.FancyBboxPatch((62, 21), 21, 16, boxstyle="round,pad=0.3", facecolor='#ffffff', edgecolor='#78281f', linewidth=1.2)
    ax.add_patch(b_c)
    ax.text(72.5, 34.5, "3. Verification & Isolation", ha='center', fontsize=9.5, fontweight='bold', color='#78281f')
    ax.text(72.5, 31, "• Selective ECDSA P-256 Audit\n  (Triggered on 0.53% pkts)\n• Conjunctive Quarantine Rule\n• Malicious Node Isolation", 
            ha='center', fontsize=7.5, color='#641e16')

    # Arrows between HEDSD sub-blocks
    ax.annotate('', xy=(39.5, 29), xytext=(38.2, 29), arrowprops=dict(arrowstyle="->", color='#27ae60', lw=1.5))
    ax.annotate('', xy=(61.5, 29), xytext=(60.2, 29), arrowprops=dict(arrowstyle="->", color='#27ae60', lw=1.5))

    # -------------------------------------------------------------
    # 3. Sensing Layer: Legitimate Motes & Adversary (Bottom)
    # -------------------------------------------------------------
    # Legitimate Motes Box
    leg_box = patches.FancyBboxPatch((5, 2), 40, 10, boxstyle="round,pad=0.4", facecolor='#eaf2f8', edgecolor='#2980b9', linewidth=1.2)
    ax.add_patch(leg_box)
    ax.text(25, 9.5, "Sensing Layer: Legitimate Leaf Nodes (N_1 ... N_6)", ha='center', fontsize=9, fontweight='bold', color='#1b4f72')
    ax.text(25, 6, "IEEE 802.15.4 Transceivers • Periodic Telemetry (2.0s)\nAA Alkaline Powered (21.6 kJ)", ha='center', fontsize=7.5, color='#2c3e50')

    # Adversary Box
    adv_box = patches.FancyBboxPatch((55, 2), 40, 10, boxstyle="round,pad=0.4", facecolor='#fadbd8', edgecolor='#c0392b', linewidth=1.2)
    ax.add_patch(adv_box)
    ax.text(75, 9.5, "Malicious Spoofing Adversary (A_1)", ha='center', fontsize=9, fontweight='bold', color='#78281f')
    ax.text(75, 6, "MAC Address Impersonation • High-Rate Injection (0.5s)\nPhysical Signal & Schedule Distortions", ha='center', fontsize=7.5, color='#641e16')

    # Telemetry Transmission Arrows from Sensing to CH
    ax.annotate('', xy=(25, 16), xytext=(25, 12),
                arrowprops=dict(arrowstyle="->", color='#27ae60', lw=2, mutation_scale=12))
    ax.text(12, 13.5, "Legitimate Telemetry", fontsize=8, color='#27ae60', fontweight='bold')

    ax.annotate('', xy=(75, 16), xytext=(75, 12),
                arrowprops=dict(arrowstyle="->", color='#c0392b', lw=2, linestyle='--', mutation_scale=12))
    ax.text(76, 13.5, "Spoofed / Burst Frames", fontsize=8, color='#c0392b', fontweight='bold')

    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(__file__), 'wsn_architecture_spoofing.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[SUCCESS] Saved high-res architecture diagram to: {output_path}")

if __name__ == '__main__':
    generate_hedsd_architecture_diagram()
