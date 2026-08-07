# Multi-Layer System Architecture & Architectural Defense Guide

---

## 1. Multi-Layer System Architecture Overview

The **Industrial Adaptive Hybrid Event-Driven Spoofing Detection (IAH-EDSD)** system employs a hierarchical, 3-tier architectural design optimized for industrial Wireless Sensor Networks (IWSNs).

```
===================================================================================
                      IAH-EDSD HIERARCHICAL SYSTEM ARCHITECTURE
===================================================================================

       ┌─────────────────────────────────────────────────────────────┐
       │                   LAYER 3: BASE STATION (SINK)               │
       │  • Unlimited Energy (1000 J)    • Global Network Map        │
       │  • Blacklist Distribution       • Model Retraining Engine   │
       └──────────────────────────────▲──────────────────────────────┘
                                      │ Encrypted Aggregated Reports
                                      │ (IEEE 802.15.4 / IP)
       ┌──────────────────────────────┴──────────────────────────────┐
       │                 LAYER 2: CLUSTER HEAD (CH) LAYER            │
       │  • Initial Energy: 50.0 J       • 8x5 Grid Layout (40 CHs)  │
       │  • Local Event Trigger Engine   • 3-Tier Mode Controller    │
       │  • Multi-Factor Trust Engine    • Selective Crypto Auditor  │
       └──────────────────────────────▲──────────────────────────────┘
                                      │ Raw Telemetry & RSSI Signals
                                      │ (2.4 GHz ISM Band)
       ┌──────────────────────────────┴──────────────────────────────┐
       │                 LAYER 1: LEAF SENSOR NODE LAYER             │
       │  • Initial Energy: 5.0 J        • 359 Distributed Nodes     │
       │  • Periodic/Burst Telemetry     • CC2420 Transceiver        │
       │  • Lightweight MSP430 MCU       • RSSI & Sequence Headers   │
       └─────────────────────────────────────────────────────────────┘
===================================================================================
```

---

## 2. Layer-by-Layer Architectural Breakdown

### Layer 1: Leaf Sensor Node Layer ($N_{\text{leaf}} = 359$)
- **Hardware Profile**: 16-bit Texas Instruments MSP430 MCU @ $8\text{ MHz}$, $<10\text{ KB}$ RAM, CC2420 RF Transceiver ($2.4\text{ GHz}$ ISM band, $250\text{ kbps}$).
- **Energy Supply**: Initial battery capacity $E_{\text{leaf}}^{(0)} = 5.0\text{ J}$.
- **Functionality**: Collects industrial environment metrics (temperature, vibration, pressure) and transmits periodic telemetry frames ($5\text{ pkts/s}$) or burst traffic ($10\text{--}20\text{ pkts/s}$) to assigned Cluster Heads. Leaves operate without running local intrusion detection to preserve maximum battery for sensing.

### Layer 2: Cluster Head (CH) Layer ($N_{\text{CH}} = 40$)
- **Topology**: $40$ Cluster Heads arranged in an $8 \times 5$ uniform spatial grid across the $1000\text{ m} \times 1000\text{ m}$ factory floor. Initial energy $E_{\text{CH}}^{(0)} = 50.0\text{ J}$.
- **Functionality**: Serves as the primary operational execution point for IAH-EDSD:
  1. **Event Monitoring Module**: Extracts PHY-layer RSSI and packet sequence numbers.
  2. **Energy Mode Controller**: Dynamically selects mode (`FULL`, `LIGHT`, `EVENT_ONLY`) based on residual battery $E_{\text{ratio}}$.
  3. **Multi-Factor Trust Engine**: Maintains dynamic neighbor trust tables ($T_{\text{auth}}, T_{\text{behavior}}, T_{\text{energy}}$).
  4. **Targeted Crypto Auditor**: Executes ECDSA-P256 signature verification on untrusted nodes ($T_i < 0.60$).
  5. **Isolation Enforcement**: Drops packets from isolated nodes and issues local isolation alerts.

### Layer 3: Base Station (Sink) Layer ($N_{\text{BS}} = 1$)
- **Hardware Profile**: Industrial gateway positioned at center coordinates $(500.0, 500.0)\text{ m}$ with mains power / large battery ($E_{\text{BS}} = 1000.0\text{ J}$).
- **Functionality**:
  1. Receives aggregated cluster health reports and isolation alerts.
  2. Maintains a global network topology map and broadcast blacklist across all clusters.
  3. Periodically updates expected RSSI path loss parameters ($\overline{\text{RSSI}}_{\text{exp}}$) under ambient environmental changes.

---

## 3. Detailed Data Flow Architecture

```
[Incoming Frame at CH] ──► [PHY Header Extraction: RSSI_obs, Sender ID i, Seq_k]
                                  │
                                  ▼
                     [Compute Delta_RSSI_i & Rate R_i]
                                  │
                                  ▼
                     [Check Energy Mode M(t)]
                                  │
             ┌────────────────────┼────────────────────┐
             │ (Mode = FULL)      │ (Mode = LIGHT)     │ (Mode = EVENT_ONLY)
             ▼                    ▼                    ▼
     [Evaluate Phi(p_k)]    [Skip Crypto]        [Process 1 in 3 Pkts]
             │              [Use Light Trust]    [RSSI Screening Only]
     ┌───────┴───────┐            │                    │
     │ (Phi = 0)     │ (Phi = 1)  │                    │
     ▼               ▼            │                    │
[Fast Bypass]  [Check T_i < 0.60] │                    │
 (5 uJ)              │            │                    │
             ┌───────┴───────┐    │                    │
             │ (Trust >= 0.6)│ (Trust < 0.6)           │
             ▼               ▼    │                    │
       [Cached Trust] [ECDSA Audit]│                   │
             │               │    │                    │
             └───────┬───────┘    │                    │
                     ▼            ▼                    ▼
             [Update Composite Trust T_i(t) & Accumulate EWS_i(t)]
                                  │
                                  ▼
             [Decision: Is T_i < 0.60 AND EWS_i > 0.40 AND Delta_RSSI > 5.0?]
                                  │
                     ┌────────────┴────────────┐
                     │ (YES)                   │ (NO)
                     ▼                         ▼
            [FLAG & ISOLATE NODE]      [FORWARD TELEMETRY TO SINK]
```

---

## 4. Architectural Justification: Why Hierarchical over Centralized?

| Evaluation Criteria | Centralized Architecture (Sink-Only) | Proposed Hierarchical IAH-EDSD | Viva Defense Justification |
| :--- | :--- | :--- | :--- |
| **Communication Overhead** | Extreme (All raw packets forwarded to Sink) | Low (Filtered locally at Cluster Heads) | Hierarchical reduces multi-hop packet forwarding energy by $>85\%$. |
| **Detection Latency** | High ($50\text{--}200\text{ ms}$ multi-hop delay) | Ultra-Fast ($<1.2\ \mu\text{s}$ for steady-state bypass) | Threat isolation occurs locally at CH within 1 packet transmission interval. |
| **Single Point of Failure** | Vulnerable (Sink overload causes network blackout) | Distributed (CHs isolate threats independently) | Cluster Head failure affects only 1 cluster ($1/40\text{th}$ of network). |
| **Scalability** | Non-scalable ($O(N^2)$ congestion at Sink) | Highly Scalable ($O(N/N_{\text{CH}})$ per cluster) | Adding leaf nodes increases local cluster density without overloading Sink. |

---

## 5. Architectural Diagram Drawing Instructions for Viva Presentation

When presenting the architecture during viva defense or drawing on a board:
1. **Draw 3 Horizontal Stacked Layers**: Label top as Base Station Layer (Sink), middle as Cluster Head Grid ($8 \times 5$), bottom as Distributed Sensor Leaves.
2. **Highlight the Execution Pipeline inside Layer 2 (Cluster Head)**:
   - Box 1: **PHY/MAC Header Extractor** ($\text{RSSI}_{\text{obs}}$, $\text{Seq}_k$).
   - Box 2: **Event Trigger Filter** ($\Phi(p_k)$).
   - Box 3: **Energy Mode Switch** (`FULL`/`LIGHT`/`EVENT_ONLY`).
   - Box 4: **Dynamic Trust Engine** ($\alpha T_{\text{auth}} + \beta T_{\text{behavior}} + \gamma T_{\text{energy}}$).
   - Box 5: **Selective Targeted Crypto Audit** (ECDSA-P256 on trigger).
3. **Annotate Energy Costs next to each box**:
   - Event Trigger Bypass: $5\,\mu\text{J}$
   - Light Trust Check: $50\,\mu\text{J}$
   - ML Anomaly Check: $100\,\mu\text{J}$
   - Targeted ECDSA Audit: $90.00\text{ mJ}$ ($<0.53\%$ rate)
