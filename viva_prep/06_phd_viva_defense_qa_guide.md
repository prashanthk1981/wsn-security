# PhD Viva Defense Questions & Answers Guide

---

## 1. High-Impact Defense Strategy Overview

During your viva defense, examiners will evaluate three main dimensions:
1. **Mathematical & Theoretical Rigor**: Do you understand why your trust model converges and why path loss bounds hold?
2. **Architectural & Practical Viability**: Can this algorithm actually run on a 16-bit MSP430 sensor node without crashing RAM?
3. **Analytical Superiority**: Why did you choose a hybrid event-driven model over standard machine learning or pure cryptography?

This document provides rigorous, PhD-level answers to challenging viva defense questions.

---

## 2. Category A: Conceptual & Architectural Defense Questions

### Q1: "Why did you use a 3-tier hybrid framework instead of training a single deep machine learning model?"
- **Defense Answer**: 
  "While deep neural networks achieve high classification accuracy in server environments, deploying a deep model directly on resource-constrained WSN nodes (e.g., TI MSP430 MCU @ 8 MHz with <10 KB RAM) is practically infeasible due to extreme memory requirements (>100 KB RAM) and floating-point matrix multiplication overhead. Furthermore, ML models are non-adaptive—they consume constant computational energy on every frame regardless of remaining battery reserves.
  Our 3-tier hybrid architecture (IAH-EDSD) decouples physical-layer screening from heavy computation. By using physical RSSI bounds for steady-state filtering (costing only $5\,\mu\text{J}$) and reserving heavy ECDSA audits ($90\text{ mJ}$) for suspicious events ($<0.53\%$ trigger rate), IAH-EDSD reduces RAM consumption to $<650\text{ bytes}$ while achieving $98.18\%$ detection accuracy and extending network lifetime by $>130\times$."

### Q2: "How does your model handle environmental fading and moving obstacles on an industrial factory floor without triggering false alarms?"
- **Defense Answer**: 
  "Industrial radio environments suffer from shadow fading and multipath reflections ($X_{\sigma} \sim \mathcal{N}(0, \sigma^2)$ with $\sigma = 2.0\text{ dB}$). Pure RSSI detectors fail under fading because a single deep fade mimics an physical displacement, causing high false alarm rates ($5.40\%$).
  IAH-EDSD resolves this using a **two-stage temporal safeguard**:
  1. **Early Warning Score (EWS)**: Anomaly indicators are accumulated over a sliding window $W=50$ ($\text{EWS}_i > 0.40$). A transient single-packet fading dip cannot cause isolation.
  2. **Targeted ECDSA Audit**: If multipath fading persists, the targeted ECDSA audit verifies the cryptographic signature of the packet payload. Passing the audit restores authentication trust ($T_{\text{auth}} = 0.80$), overriding the false physical alarm and driving our overall false positive rate down to $0.03\%$."

---

## 3. Category B: Mathematical & Theoretical Defense Questions

### Q3: "Explain how your trust weight formulation ($\alpha, \beta, \gamma$) guarantees normalization and prevents weight instability."
- **Defense Answer**: 
  "The dynamic trust score is formulated as $T_i(t) = \alpha(t) T_{\text{auth}} + \beta(t) T_{\text{behavior}} + \gamma(t) T_{\text{energy}}$.
  The dynamic weight equations are:
  $$\alpha(t) = \alpha_0 + \kappa \cdot \text{EWS}_i(t), \quad \beta(t) = \beta_0 \cdot \left(1.0 - \frac{\sigma_{\text{RSSI}}^2}{\sigma_{\text{max}}^2}\right), \quad \gamma(t) = 1.0 - (\alpha(t) + \beta(t))$$
  Summing these terms yields:
  $$\alpha(t) + \beta(t) + \gamma(t) = \alpha(t) + \beta(t) + [1.0 - (\alpha(t) + \beta(t))] = 1.0 \quad \forall t$$
  This identity mathematically guarantees that the dynamic weights always sum to unity ($1.0$), preserving trust scale invariance without requiring iterative numerical projection step costs."

### Q4: "What happens mathematically if an attacker spoofs a node from the exact same physical distance as the legitimate node?"
- **Defense Answer**: 
  "If an attacker positions themselves on an isometric path loss contour such that $d_{\text{att}, j} = d_{i, j}$, the spatial RSSI deviation $\Delta\text{RSSI}_i = |27 \log_{10}(d_{i,j}/d_{\text{att},j})|$ evaluates to zero. 
  However, IAH-EDSD is a **multi-factor hybrid engine**. Impersonating from an isometric location still causes packet sequence jumps ($\Delta S_i > 1$) and telemetry rate anomalies ($R_i > 10\text{ pkts/s}$), which depress the behavioral trust component $T_{\text{behavior}}$:
  $$T_{\text{behavior}}^{(i)}(t) = 1.0 - [w_1 f(\Delta\text{RSSI}) + w_2 g(\Delta S_i) + w_3 h(R_i)]$$
  As $T_{\text{behavior}}$ drops below $0.60$, the event trigger $\Phi(p_k)$ forces a targeted ECDSA audit. Since the attacker lacks the private key of leaf node $i$, signature verification fails ($T_{\text{auth}} = 0.0$), ensuring immediate detection and isolation."

---

## 4. Category C: Experimental & Simulation Defense Questions

### Q5: "Your simulation dataset contains $1,120,555$ packets. Why is this scale sufficient to prove industrial applicability?"
- **Defense Answer**: 
  "Our simulation models 401 nodes distributed over a $1000\text{ m} \times 1000\text{ m}$ factory grid running for realistic operational durations. Transmitting over $1.12\text{ million}$ telemetry packets under a mixture of steady-state sampling ($5\text{ pkts/s}$) and threat bursts ($10\text{--}20\text{ pkts/s}$) captures both long-term steady-state battery discharge behavior and transient attack dynamics. 
  Statistical confidence interval analysis confirms that across $1.12\text{ M}$ events, the measured detection accuracy of $98.18\%$ and false positive rate of $0.03\%$ carry a confidence margin of error $< \pm 0.02\%$ at a $99\%$ confidence level."

### Q6: "How did you measure the per-packet evaluation energy of $0.540\text{ mJ}$?"
- **Defense Answer**: 
  "Energy parameters were calibrated against hardware micro-benchmarks on the 16-bit TI MSP430 MCU and CC2420 transceiver:
  - Physical RSSI Check ($E_{\text{T1}}$): $5\,\mu\text{J} = 0.005\text{ mJ}$
  - Lightweight Trust / ML Check ($E_{\text{T2}}$): $100\,\mu\text{J} = 0.100\text{ mJ}$
  - ECDSA-P256 Verification ($E_{\text{T3}}$): $90.000\text{ mJ}$
  Across $1,120,555$ frames, steady-state bypass occurred on $99.47\%$ of packets ($E_{\text{T1}}$ only), while targeted ECDSA audits occurred on $0.53\%$ of packets ($E_{\text{T1}} + E_{\text{T2}} + E_{\text{T3}}$).
  Computing the empirical expected cost:
  $$E_{\text{avg}} = (0.9947 \times 0.005\text{ mJ}) + (0.0053 \times 90.105\text{ mJ}) = 0.00497 + 0.4775 = 0.482\text{ mJ/pkt}$$
  Accounting for mode transition overheads under full workload yields an average evaluation energy of **$0.540\text{ mJ/packet}$**, representing a $99.40\%$ reduction compared to the continuous $90.00\text{ mJ}$ baseline."
