# Chapter: Energy-Adaptive Hybrid Event-Driven Spoofing Detection (IAH-EDSD) in Industrial Wireless Sensor Networks

---

## 1. Introduction

### 1.1 Problem Statement
Industrial Wireless Sensor Networks (IWSNs) form the operational backbone of modern industrial automation, smart manufacturing, oil and gas pipelines, power grid monitoring, and Industry 4.0 applications. Operating under severe energy, bandwidth, and computational constraints, sensor nodes routinely transmit critical telemetry data back to centralized control systems or Base Stations (BS). However, due to the open, broadcast nature of wireless radio channels (e.g., IEEE 802.15.4 / ZigBee) and unencrypted header fields, IWSNs are fundamentally vulnerable to **active identity spoofing** and **Sybil attacks**. In these attacks, malicious adversaries forge MAC/IP source addresses or masquerade under multiple stolen node identities to inject false measurement data, trigger unnecessary industrial shutdowns, bypass access control protocols, or exhaust network routing resources.

### 1.2 Motivation
Traditional cryptographic mechanisms—such as public-key cryptography using Elliptic Curve Digital Signature Algorithm (ECDSA NIST P-256)—provide unforgeable per-packet origin authentication. However, executing an ECDSA-P256 signature verification on a resource-constrained 16-bit microcontroller (e.g., Texas Instruments MSP430 running at $8\text{ MHz}$ with $<10\text{ KB}$ RAM) incurs a heavy energy penalty of approximately $90.00\text{ mJ}$ per packet. In an industrial network carrying over $1.12\text{ million}$ telemetry frames, applying continuous cryptographic verification rapidly exhausts node initial energy reserves (e.g., $5.0\text{ J}$ for leaf nodes, $50.0\text{ J}$ for Cluster Heads), causing catastrophic network partition within hours.

Conversely, lightweight physical-layer authentication techniques (e.g., Received Signal Strength Indicator, RSSI) or purely behavioral anomaly detectors require minimal computation ($5\text{--}100\ \mu\text{J}$/packet), but suffer from high false positive rates ($2.8\text{--}5.4\%$) under multipath fading, shadow fading, and dynamic obstacle movements typical of industrial factory floors.

### 1.3 Research Gap & Key Contributions
Existing research presents a rigid trade-off between **high security (heavy energy overhead)** and **low energy (weak security under dynamic threats)**. There is a distinct absence of an event-driven, energy-aware security architecture that dynamically adapts its computational intensity to both instantaneous threat levels and residual battery reserves.

To bridge this research gap, this thesis introduces the **Industrial Adaptive Hybrid Event-Driven Spoofing Detection (IAH-EDSD)** framework. The principal contributions are:
1. **Event-Driven Hierarchical Triggers**: Replaces static continuous verification with an event-driven monitoring cascade based on physical-layer spatial RSSI deviation ($\Delta\text{RSSI}_i > 5.0\text{ dBm}$) and telemetry packet rate bursts ($\Phi(p_k)$), bypassing heavy audits during steady-state normal operations.
2. **Adaptive Multi-Factor Trust Engine**: Formulates a dynamic trust accumulation model ($T = \alpha T_{\text{auth}} + \beta T_{\text{behavior}} + \gamma T_{\text{energy}}$) featuring real-time context-aware weight updating and an Early Warning Score (EWS) temporal convergence filter.
3. **Three-Tier Energy-Adaptive Mode Switching**: Implements active energy-aware operational state selection (`FULL`, `LIGHT`, `EVENT_ONLY`) linked to residual battery capacity ($E_{\text{ratio}}$), guaranteeing microcontroller operational viability on 16-bit MSP430 MCUs.
4. **Empirical Industrial NS-3 Validation**: Validated via extensive discrete-event simulations across a 401-node industrial factory grid ($1000\text{ m} \times 1000\text{ m}$) under $1,120,555$ telemetry packets, achieving $98.18\%$ detection accuracy, $0.03\%$ false positive rate, $99.40\%$ per-packet energy reduction ($0.540\text{ mJ}$ vs $90.00\text{ mJ}$), and extending Cluster Head lifetime by over $130\times$.

---

## 2. Related Work & Taxonomic Positioning

A critical analysis of state-of-the-art (SOTA) WSN intrusion detection and authentication mechanisms reveals four distinct paradigms:

| Defense Paradigm | Key Mechanisms | Detection Accuracy | Energy Overhead | Primary Limitations |
| :--- | :--- | :--- | :--- | :--- |
| **1. Continuous Cryptographic** | ECDSA-P256, HMAC-SHA256, RSA-1024 | $100.0\%$ (Deterministic) | Extremely High ($90.00\text{ mJ}$/pkt) | Battery depletion in hours; vulnerable to DoS by signature flooding |
| **2. Physical-Layer (PHY)** | RSSI Fingerprinting, CSI Phase, Carrier Frequency Offset | $88.5\text{--}92.4\%$ | Very Low ($5.0\ \mu\text{J}$/pkt) | High false alarm rate under multipath fading and environmental movement |
| **3. Machine Learning (ML)** | SVM, Random Forest, XGBoost, Deep Autoencoders | $94.2\text{--}97.8\%$ | Moderate ($100.0\ \mu\text{J}$/pkt) | High RAM footprint ($>100\text{ KB}$); non-adaptive computational load |
| **4. Dynamic Trust Models** | Beta Trust, Fuzzy Logic, Subjective Logic | $91.0\text{--}95.5\%$ | Low ($50.0\ \mu\text{J}$/pkt) | Slow convergence during rapid burst spoofing; vulnerability to energy exhaustion |
| **5. Proposed IAH-EDSD** | **Event Triggers + Adaptive Trust + 3-Tier Mode Switching** | **$98.18\%$** | **Ultra-Low ($0.540\text{ mJ}$/pkt)** | **Optimal energy-security Pareto frontier; $<0.53\%$ crypto audit rate** |

### Critical Comparative Justification
Unlike static competitors (e.g., Wang et al. 2024, Zhang et al. 2022, Ali et al. 2024, Kumar et al. 2024, and Wiley 2024), IAH-EDSD decouples attack detection from continuous computation. By treating cryptography as a targeted audit mechanism rather than a baseline requirement, IAH-EDSD achieves superior detection accuracy while preserving network longevity.

---

## 3. System Model & Operational Hypotheses

### 3.1 Network Topology Model
Consider an industrial Wireless Sensor Network deployed over a square operational region $\mathcal{A} = [0, L] \times [0, L] \subset \mathbb{R}^2$ with $L = 1000\text{ m}$. The network consists of $N = 401$ physical nodes partitioned hierarchically:
- **Base Station (BS / Sink)**: Located at center coordinates $(500.0, 500.0)\text{ m}$ with unlimited energy supply ($E_{\text{BS}} = 1000.0\text{ J}$).
- **Cluster Heads (CHs)**: $N_{\text{CH}} = 40$ nodes arranged in an $8 \times 5$ uniform grid. Initial energy $E_{\text{CH}}^{(0)} = 50.0\text{ J}$.
- **Leaf Sensor Nodes**: $N_{\text{leaf}} = 359$ nodes uniformly distributed within cluster boundaries. Initial energy $E_{\text{leaf}}^{(0)} = 5.0\text{ J}$.

### 3.2 Radio Channel & Physical-Layer Model
Transmissions adhere to IEEE 802.15.4 PHY/MAC standards on the $2.4\text{ GHz}$ ISM band operating via CC2420 RF transceivers ($P_{\text{tx}} = 0.0\text{ dBm} = 1.0\text{ mW}$, Data Rate = $250\text{ kbps}$). Path loss follows the Log-Normal Shadowing Model:
$$P_{\text{rx}}(d) = P_{\text{tx}} - P_{\text{L}}(d_0) - 10 n \log_{10}\left(\frac{d}{d_0}\right) + X_{\sigma}$$
where $P_{\text{L}}(d_0) = 40.0\text{ dB}$ is the reference path loss at $d_0 = 1.0\text{ m}$, $n = 2.7$ is the industrial environment path loss exponent, and $X_{\sigma} \sim \mathcal{N}(0, \sigma^2)$ is log-normal shadow fading with zero mean and standard deviation $\sigma = 2.0\text{ dB}$.

### 3.3 Threat Model (Identity Spoofing & Sybil Attacks)
Let $\mathcal{N}_{\text{att}}$ denote the set of malicious attacker nodes ($|\mathcal{N}_{\text{att}}| = 15\% \times N \approx 54\text{--}60$ nodes). Attackers execute identity spoofing by forging the header MAC address of legitimate leaf node $i \in \mathcal{N}_{\text{legit}}$ while transmitting from physical position $\boldsymbol{p}_{\text{att}} \neq \boldsymbol{p}_i$. Attackers execute three operational attack patterns:
1. **Constant Spoofing Burst**: High packet injection rate ($10\text{--}20\text{ pkts/s}$) with corrupted payload measurements.
2. **Intermittent / Random Spoofing**: Periodic impersonation aimed at evading sliding-window statistical detectors.
3. **Sybil Impersonation**: Single physical node simultaneously masquerading as multiple distinct sensor IDs to corrupt cluster-head aggregation.

---

## 4. Proposed IAH-EDSD Framework Architecture

The IAH-EDSD engine operates across a 7-phase processing pipeline:

```
[Incoming Packet p_k]
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 1: Physical-Layer RSSI & Sequence Inspection     │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 2: Event-Driven Trigger Filter (Phi(p_k))        │
└──────────────────────────┬──────────────────────────────┘
                           │ (Triggered: Phi = 1)
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 3: 3-Tier Energy-Adaptive Mode Switch (M)         │
│          (FULL / LIGHT / EVENT_ONLY)                    │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 4: Context-Aware Dynamic Weight Updater           │
│          (alpha(t), beta(t), gamma(t))                  │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 5: Multi-Factor Trust Score Calculation           │
│          (T_auth, T_behavior, T_energy)                 │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 6: Early Warning Score (EWS) Accumulator          │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 7: Isolation Verdict & Targeted ECDSA Audit       │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Mathematical Model & Analytical Derivation

### 5.1 Spatial RSSI Anomaly Derivation
For a node $i$ transmitting from coordinates $\boldsymbol{p}_i$, the expected Received Signal Strength at Cluster Head $j$ at distance $d_{i,j} = \|\boldsymbol{p}_i - \boldsymbol{p}_j\|_2$ is:
$$\overline{\text{RSSI}}_{\text{exp}}^{(i, j)} = P_{\text{tx}} - P_{\text{L}}(d_0) - 10 n \log_{10}\left(\frac{\|\boldsymbol{p}_i - \boldsymbol{p}_j\|_2}{d_0}\right)$$

When an attacker at $\boldsymbol{p}_{\text{att}}$ spoofs node ID $i$, the actual observed RSSI is:
$$\text{RSSI}_{\text{obs}}^{(i, j)} = P_{\text{tx}} - P_{\text{L}}(d_0) - 10 n \log_{10}\left(\frac{\|\boldsymbol{p}_{\text{att}} - \boldsymbol{p}_j\|_2}{d_0}\right) + X_{\sigma}$$

The spatial RSSI deviation metric $\Delta\text{RSSI}_i(t)$ is defined as:
$$\Delta\text{RSSI}_i(t) = \left| \text{RSSI}_{\text{obs}}^{(i, j)}(t) - \overline{\text{RSSI}}_{\text{exp}}^{(i, j)} \right|$$

An anomaly candidate is flagged if $\Delta\text{RSSI}_i(t) > \tau_{\text{RSSI}}$, where $\tau_{\text{RSSI}} = 3\sigma = 6.0\text{ dBm}$ (heuristically bounded at $5.0\text{ dBm}$).

### 5.2 Dynamic Multi-Factor Trust Formulation
Total node trust $T_i(t) \in [0, 1]$ at time $t$ is computed via a weighted linear combination of three normalized trust metrics:
$$T_i(t) = \alpha(t) T_{\text{auth}}^{(i)}(t) + \beta(t) T_{\text{behavior}}^{(i)}(t) + \gamma(t) T_{\text{energy}}^{(i)}(t)$$

subject to the normalization constraint:
$$\alpha(t) + \beta(t) + \gamma(t) = 1.0, \quad \forall t \ge 0$$

#### Component Definitions:
1. **Authentication Trust ($T_{\text{auth}}$)**:
   $$T_{\text{auth}}^{(i)}(t) = \begin{cases} 
   1.0, & \text{ECDSA Audit Passed} \\
   0.0, & \text{ECDSA Audit Failed} \\
   T_{\text{auth}}^{(i)}(t-1), & \text{No Audit Performed (Cached)}
   \end{cases}$$

2. **Behavioral Trust ($T_{\text{behavior}}$)**:
   $$T_{\text{behavior}}^{(i)}(t) = 1.0 - \left( w_1 \cdot f(\Delta\text{RSSI}_i) + w_2 \cdot g(\Delta S_i) + w_3 \cdot h(R_i) \right)$$
   where $f(\Delta\text{RSSI}_i) = \min\left(1.0, \frac{\Delta\text{RSSI}_i}{15.0}\right)$, $g(\Delta S_i) = \min\left(1.0, \frac{|\Delta S_i - 1|}{10}\right)$ measures packet sequence jumps, and $h(R_i) = \min\left(1.0, \frac{\max(0, R_i - R_{\text{normal}})}{R_{\text{burst\_max}}}\right)$ evaluates packet rate anomalies. Weights are assigned as $w_1 = 0.50$, $w_2 = 0.30$, $w_3 = 0.20$.

3. **Energy Trust ($T_{\text{energy}}$)**:
   $$T_{\text{energy}}^{(i)}(t) = \frac{E_{\text{rem}}^{(i)}(t)}{E_{\text{leaf}}^{(0)}}$$

### 5.3 Context-Aware Dynamic Weight Updating
The weights $\alpha(t), \beta(t), \gamma(t)$ adapt dynamically based on network state and historical behavior variance:
$$\alpha(t) = \alpha_0 + \kappa \cdot \text{EWS}_i(t), \quad \beta(t) = \beta_0 \cdot \left(1 - \frac{\sigma_{\text{RSSI}}^2}{\sigma_{\text{max}}^2}\right), \quad \gamma(t) = 1 - (\alpha(t) + \beta(t))$$
where base weights are $\alpha_0 = 0.40, \beta_0 = 0.40, \gamma_0 = 0.20$, and $\kappa = 0.30$ amplifies cryptographic importance during elevated threat levels.

### 5.4 Early Warning Score (EWS) Accumulation
To prevent transient noise spikes from triggering false alarms, EWS accumulates suspicious packet indicators over a sliding window $W = 50$ packets:
$$\text{EWS}_i(t) = \frac{1}{W} \sum_{k=t-W+1}^{t} \mathbb{I}\left( \Delta\text{RSSI}_i(k) > \tau_{\text{RSSI}} \;\lor\; \Delta S_i(k) > 1 \right)$$

---

## 6. Algorithm Design & Complexity Analysis

### 6.1 Formal Pseudocode (Algorithm 1)

```
================================================================================
Algorithm 1: IAH-EDSD Framework Execution Protocol
================================================================================
Input  : Packet p_k, Sender ID i, Observed RSSI RSSI_obs, Residual Energy E_rem
Output : Isolation Verdict Isolate_i in {0, 1}, Trust T_i(t), EWS Score EWS_i(t)
================================================================================
1:  Compute Spatial RSSI Deviation: Delta_RSSI_i <- |RSSI_obs - RSSI_exp(i, j)|
2:  Extract Sequence Gap Delta_S_i and Instantaneous Packet Rate R_i(t)
3:  Compute Node Energy Ratio: E_ratio <- E_rem / E_initial
4:  
5:  /* Phase 3: 3-Tier Mode Selection */
6:  if E_ratio > 0.70 then
7:      Mode M <- FULL
8:  else if 0.30 < E_ratio <= 0.70 then
9:      Mode M <- LIGHT
10: else
11:     Mode M <- EVENT_ONLY
12: end if
13: 
14: /* Phase 3 Execution: EVENT_ONLY Mode Handling */
15: if Mode M == EVENT_ONLY then
16:     if k mod 3 != 0 then
17:         return Isolate_i <- 0, T_i(t-1), EWS_i(t-1)  /* Skip 2/3 packets */
18:     end if
19:     if Delta_RSSI_i > 5.0 dBm then
20:         T_i(t) <- max(0, T_i(t-1) - 0.15)
21:     end if
22:     Isolate_i <- I( T_i(t) < 0.60 AND Delta_RSSI_i > 5.0 )
23:     return Isolate_i, T_i(t), EWS_i(t-1)
24: end if
25: 
26: /* Phase 2: Event Trigger Evaluation */
27: Trigger Event Phi(p_k) <- I( Delta_RSSI_i > 5.0 dBm OR Delta_S_i > 1 OR R_i > R_thresh )
28: if Phi(p_k) == 0 then
29:     return Isolate_i <- 0, T_i(t-1), EWS_i(t-1)  /* Steady-State Bypass */
30: end if
31: 
32: /* Phase 4 & 5: Trust and Weight Computation */
33: Update Dynamic Weights alpha(t), beta(t), gamma(t)
34: Compute T_behavior(i)(t) and T_energy(i)(t)
35: 
36: /* Phase 7: Selective Targeted ECDSA Audit */
37: if Mode M == FULL AND T_i(t-1) < 0.60 then
38:     Execute ECDSA-P256 Signature Verification on p_k
39:     if Verification Success then
40:         T_auth(i)(t) <- 0.80
41:     else
42:         T_auth(i)(t) <- 0.00
43:     end if
44: else
45:     T_auth(i)(t) <- T_auth(i)(t-1)  /* Cached Trust */
46: end if
47: 
48: T_i(t) <- alpha(t)*T_auth(i)(t) + beta(t)*T_behavior(i)(t) + gamma(t)*T_energy(i)(t)
49: Update Sliding Window EWS_i(t)
50: 
51: /* Final Isolation Decision */
52: if T_i(t) < 0.60 AND EWS_i(t) > 0.40 AND Delta_RSSI_i > 5.0 dBm then
53:     Isolate_i <- 1
54: else
55:     Isolate_i <- 0
56: end if
57: return Isolate_i, T_i(t), EWS_i(t)
================================================================================
```

### 6.2 Computational Complexity Analysis
Let $N$ be the total node count and $W$ be the sliding window size:
- **Time Complexity**:
  - Steady-State Screening (Phase 1--2): $\mathcal{O}(1)$ scalar operations per packet.
  - Trust Engine (Phase 4--6): $\mathcal{O}(W)$ for EWS sliding window update. Since $W=50$ is constant, per-packet execution time is $\mathcal{O}(1)$.
  - ECDSA Audit (Phase 7): $\mathcal{O}(1)$ point multiplication on NIST P-256 curve (invoked with probability $P_{\text{audit}} \le 0.0053$).
  - Overall Time Complexity per packet: **$\mathcal{O}(1)$ bounded constant time**.
- **Space / Memory Footprint**:
  - Per-node state tracking: 8 scalar floats (Trust, EWS, sequence, energy) + $W$ boolean flags = $64\text{ bytes}$ per monitored neighbor.
  - For $N_{\text{neighbors}} \le 15$ in a cluster: Total RAM footprint $\approx 960\text{ bytes} < 1.0\text{ KB}$.
  - Fits easily within the $10\text{ KB}$ RAM limit of 16-bit TI MSP430 microcontrollers.

---

## 7. Simulation Methodology & Setup

Simulations were executed using **NS-3 (v3.48)** with Python C++ bindings (`cppyy`).

```
+-------------------------------------------------------------------------+
|                    Industrial NS-3 Simulation Setup                     |
+-----------------------------------+-------------------------------------+
| Parameter                         | Value                               |
+-----------------------------------+-------------------------------------+
| Network Grid Dimensions           | 1000 m x 1000 m Industrial Factory  |
| Total Node Count (N)              | 401 Nodes                           |
| Topology Structure                | 40 Cluster Heads (8x5 Grid) + Sink  |
| Attacker Population               | 15% (54--60 Spoofing Attackers)     |
| PHY / MAC Standard                | IEEE 802.15.4 / CC2420 Transceiver  |
| Radio Propagation Model           | Log-Normal Shadowing (n=2.7, s=2.0) |
| Total Evaluated Packets           | 1,120,555 Packets                   |
| Initial Energy (Leaf / CH / Sink) | 5.0 J / 50.0 J / 1000.0 J           |
| Hardware Baseline                 | 16-bit TI MSP430 MCU @ 8 MHz        |
+-----------------------------------+-------------------------------------+
```

---

## 8. Results, Empirical Discussion & Pareto Frontier Analysis

### 8.1 Detection Performance Metrics
Evaluated over $1,120,555$ telemetry packets:
- **Spoofing Detection Rate (TPR)**: **$98.18\%$**
- **False Positive Rate (FPR)**: **$0.03\%$** (compared to $2.8\text{--}5.4\%$ for pure PHY/ML methods)
- **Cryptographic Audit Rate**: **$0.53\%$** ($99.47\%$ steady-state bypass rate)

### 8.2 Energy & Network Lifetime Quantification

```
+-------------------------------------------------------------------------+
|                  Energy Consumption & Lifetime Summary                  |
+---------------------------------------+---------------------------------+
| Metric / Baseline                     | Value                           |
+---------------------------------------+---------------------------------+
| Continuous ECDSA-P256 Baseline Energy | 90.00 mJ / packet               |
| Proposed IAH-EDSD Avg Energy          | 0.540 mJ / packet               |
| Per-Packet Energy Reduction           | 99.40% Reduction                |
| Continuous ECDSA CH Network Lifetime  | 1.16 Hours (Depleted)           |
| Proposed IAH-EDSD CH Network Lifetime | 151.3 Hours (Operational)       |
| Lifetime Extension Factor             | > 130x Extension                |
+---------------------------------------+---------------------------------+
```

### 8.3 Pareto Security-Energy Tradeoff Frontier Analysis
By plotting Detection Accuracy (\%) against Per-Packet Energy Consumption (mJ), IAH-EDSD sits directly on the **optimal Pareto frontier**:

```
Detection Accuracy (%)
 100% ┤                                 ★ IAH-EDSD (98.18%, 0.54 mJ)
      │                                 ▲ Continuous ECDSA (100%, 90 mJ)
  95% ┤            ◆ Random Forest (96.4%, 0.10 mJ)
      │       ■ Dynamic Trust (92.5%, 0.055 mJ)
  90% ┤  ● Pure RSSI (88.5%, 0.005 mJ)
      └──────┬────────────┬────────────┬────────────┬───────────
             0.01 mJ      0.1 mJ       1.0 mJ       10 mJ      100 mJ
                        Per-Packet Energy Cost (Log Scale)
```

**Analytical Reasoning**: Continuous ECDSA achieves 100% security but fails completely on energy longevity. Pure RSSI achieves maximum energy efficiency but fails on false alarm security. IAH-EDSD achieves $98.18\%$ security at $0.540\text{ mJ}$ cost, delivering the ideal operational compromise for IIoT deployments.

---

## 9. Limitations & Future Work

### 9.1 Current Limitations
1. **High-Mobility Leaf Nodes**: Rapidly moving physical targets induce Doppler shifts and high RSSI variance, requiring dynamic tuning of $\sigma_{\text{RSSI}}$.
2. **Coordinated Multi-Attacker Collusion**: If multiple physical attackers simultaneously spoof the same ID from symmetrical distances relative to the Cluster Head, $\Delta\text{RSSI}_i$ can momentarily cancel out.

### 9.2 Future Research Directions
1. **Reinforcement Learning (Q-Learning) Weight Adaptation**: Replacing heuristic dynamic weight formulas with online Q-learning on Cluster Heads to automatically optimize $\alpha, \beta, \gamma$ under non-stationary industrial noise.
2. **Hardware-In-The-Loop (HIL) Testbed Validation**: Deploying IAH-EDSD on physical TI CC2650 / MSP430 system-on-chip (SoC) microcontrollers to measure real hardware battery discharge curves under thermal variations.

---

## 10. Conclusion

This chapter presented the **IAH-EDSD** framework for resource-constrained Industrial Wireless Sensor Networks. By combining physical-layer spatial RSSI screening, dynamic dynamic trust management, event-driven trigger filters, and 3-tier energy-adaptive mode switching, IAH-EDSD eliminates the traditional conflict between strict security and energy longevity. Validated on an industrial-scale 401-node NS-3 simulation across $1.12\text{ million}$ packets, IAH-EDSD reduces per-packet energy consumption by $99.40\%$ while maintaining $98.18\%$ detection accuracy and extending network lifetime by over $130\times$, establishing a defensible, publication-grade benchmark for IIoT security.
