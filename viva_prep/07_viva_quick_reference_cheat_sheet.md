# Viva Quick-Reference Exam Cheat Sheet

---

## ⚡ 1. The 30-Second Elevator Pitch

> "Industrial Wireless Sensor Networks are severely vulnerable to identity spoofing attacks. While continuous ECDSA signatures provide 100% security, verifying a signature consumes 90 mJ per packet, draining Cluster Head batteries within 1.16 hours. 
> To solve this, we created **IAH-EDSD**—an Energy-Adaptive Event-Driven framework. IAH-EDSD replaces continuous crypto with physical-layer RSSI screening ($5\,\mu\text{J}$) and dynamic multi-factor trust ($T = \alpha T_{\text{auth}} + \beta T_{\text{behavior}} + \gamma T_{\text{energy}}$). 
> Heavy ECDSA audits are triggered on only **0.53% of packets**, cutting per-packet energy consumption by **99.40%** ($0.540\text{ mJ}$ vs $90.00\text{ mJ}$), maintaining **98.18% detection accuracy** with a **0.03% false positive rate**, and extending network lifetime by **over 130×**."

---

## 📊 2. Critical Metrics Cheat Table (Memorize These Numbers)

| Parameter / Metric | Exact Value | Key Comparison / Context |
| :--- | :--- | :--- |
| **Network Scale** | $401$ Nodes | $1\text{ Sink} + 40\text{ CHs} + 359\text{ Leaf}$ ($1000\text{ m} \times 1000\text{ m}$) |
| **Attacker Ratio** | $15\%$ Population | $54\text{--}60$ Active Spoofing Attackers |
| **Evaluated Workload** | $1,120,555$ Packets | NS-3 Discrete-Event Industry Telemetry |
| **Detection Rate (TPR)** | **$98.18\%$** | Vs $88.5\%$ (Pure PHY), $92.5\%$ (DynTrust) |
| **False Positive Rate** | **$0.03\%$** | Vs $5.40\%$ (Pure PHY), $1.85\%$ (DynTrust) |
| **Crypto Audit Rate** | **$0.53\%$** | $99.47\%$ Steady-State Event Bypass Rate |
| **Per-Packet Energy** | **$0.540\text{ mJ}$** | **$99.40\%$ Reduction** vs $90.00\text{ mJ}$ Baseline |
| **Cluster Head Lifetime**| **$151.3\text{ Hours}$** | **$>130\times$ Extension** vs $1.16\text{ Hours}$ Baseline |
| **Hardware Target** | TI MSP430 MCU | 16-bit @ $8\text{ MHz}$, $<10\text{ KB}$ RAM ($645\text{ B}$ footprint) |

---

## 💡 3. Key Formulas & Equations Summary

### 1. Spatial RSSI Deviation:
$$\Delta\text{RSSI}_i = \left| \text{RSSI}_{\text{obs}}^{(i, j)} - \overline{\text{RSSI}}_{\text{exp}}^{(i, j)} \right|$$

### 2. Multi-Factor Trust Equation:
$$T_i(t) = \alpha(t) T_{\text{auth}}^{(i)}(t) + \beta(t) T_{\text{behavior}}^{(i)}(t) + \gamma(t) T_{\text{energy}}^{(i)}(t)$$

### 3. Weight Normalization Condition:
$$\alpha(t) + \beta(t) + \gamma(t) = 1.0 \quad \forall t$$

### 4. Event Trigger Condition:
$$\Phi(p_k) = \mathbb{I}\left( \Delta\text{RSSI}_i > 5.0\text{ dBm} \;\lor\; |\Delta S_i - 1| > 2 \;\lor\; R_i > 10\text{ pkts/s} \right)$$

### 5. Three-Tier Energy Mode Selection:
$$\mathcal{M} = \begin{cases} \text{FULL}, & E_{\text{ratio}} > 0.70 \\ \text{LIGHT}, & 0.30 < E_{\text{ratio}} \le 0.70 \\ \text{EVENT\_ONLY}, & E_{\text{ratio}} \le 0.30 \end{cases}$$

---

## 🎯 4. Top 5 Viva Examiner Defenses

1. **"Why not deep learning?"** $\rightarrow$ Deep Learning requires $>100\text{ KB}$ RAM; MSP430 has only $10\text{ KB}$ RAM. IAH-EDSD takes only $645\text{ bytes}$.
2. **"Why not continuous ECDSA?"** $\rightarrow$ Continuous ECDSA costs $90\text{ mJ/pkt}$, killing node battery in $1.16\text{ hours}$. IAH-EDSD cuts cost to $0.540\text{ mJ/pkt}$ ($130\times$ lifetime).
3. **"How do you handle shadow fading?"** $\rightarrow$ Early Warning Score (EWS) window ($W=50$) filters transient noise dips; targeted ECDSA audit verifies genuine credentials, keeping FPR at $0.03\%$.
4. **"What if the attacker is at the same distance?"** $\rightarrow$ Distance symmetry lowers RSSI deviation, but rate spikes and sequence gaps depress $T_{\text{behavior}}$, triggering targeted ECDSA verification.
5. **"Is this scalable?"** $\rightarrow$ Processing is distributed hierarchically across 40 Cluster Heads in $O(1)$ constant time per packet.
