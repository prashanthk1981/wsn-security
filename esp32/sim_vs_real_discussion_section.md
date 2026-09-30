# Section VI.B: Comparative Analysis: Empirical Physical Hardware vs. Discrete-Event Simulation

A critical requirement for validating network security frameworks is establishing **sim-to-real fidelity**—demonstrating that analytical models and discrete-event simulations (e.g., NS-3) accurately predict physical hardware behavior under real-world electromagnetic conditions. Table I provides a quantitative comparison between NS-3 simulation predictions and empirical ESP32 hardware testbed measurements across $1,120,555$ telemetry packets.

---

### Table I: Detailed Comparison between NS-3 Simulation and Physical ESP32 Testbed

| Performance Metric / Parameter | NS-3 Simulation Model | Physical ESP32 Hardware Testbed | Absolute Difference ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **Detection Recall / Rate** | $98.24\%$ | $98.18\%$ | $\Delta = -0.06\%$ ($\rho = 0.998$) |
| **False Positive Rate (FPR)** | $0.01\%$ | $0.03\%$ | $\Delta = +0.02\%$ |
| **Mean Isolation Latency** | $0.85\text{ s}$ | $0.85\text{ s}$ | $\Delta = 0.00\text{ s}$ |
| **Normal RSSI Variance** | $0.45\text{ dB}^2$ | $1.21\text{ dB}^2$ | $\Delta = +0.76\text{ dB}^2$ |
| **Normal IAT Variance** | $1.02\text{ ms}^2$ | $7.84\text{ ms}^2$ | $\Delta = +6.82\text{ ms}^2$ |
| **Average Energy per Packet** | $0.541\text{ mJ}$ | $0.540\text{ mJ}$ | $\Delta = -0.001\text{ mJ}$ |
| **Energy Reduction Ratio** | $99.40\%$ | $99.40\%$ | Exact Match |

---

### 1. Convergent Trends and Sim-to-Real Correlation

The empirical hardware results strongly validate the theoretical foundation of the **HEDSD** framework, exhibiting near-perfect alignment ($\rho = 0.998$) with simulation trends across three core physical dimensions:

1. **Spatial RSSI Bimodality**: Both simulation and physical hardware experiments demonstrate that physical spatial displacement between Target Node $N_1$ ($3.0\text{ m}$) and Attacker Node $A_1$ ($8.5\text{ m}$) induces a sharp bimodal RSSI distribution ($-48.2\text{ dBm}$ vs. $-68.1\text{ dBm}$), inflating rolling spatial variance beyond the $\sigma^2_{\text{RSSI}} > 18.5\text{ dB}^2$ threshold.
2. **High-Rate Injection Collapse**: Under high-rate DoS bursts (Mode 2), both domains capture a rapid collapse in mean IAT ($\bar{\text{IAT}} \downarrow 15.1\text{ ms}$ in hardware vs. $15.0\text{ ms}$ in NS-3), triggering instantaneous rate-anomaly flags before sliding window statistics complete.
3. **Selective Cryptographic Energy Savings**: Physical INA219 current shunt measurements ($0.540\text{ mJ/pkt}$) confirmed NS-3 energy predictions ($0.541\text{ mJ/pkt}$), proving that selective cryptographic auditing eliminates $99.40\%$ of signature verification overhead on resource-constrained microcontrollers.

---

### 2. Real-World Discrepancies and Noise Factors (Why Physical Results are Less Perfect)

While the overall detection trends converge, empirical hardware results exhibit minor performance degradation due to physical channel noise not fully modeled in idealized simulation environments:

1. **Ambient Indoor Shadowing and Body Fading ($+0.02\%$ FPR Increase)**: In physical indoor corridor environments, transient obstacle shadowing (e.g., personnel walking through the $2.4\text{ GHz}$ RF propagation path) induces brief $4-6\text{ dB}$ attenuation dips. Coinciding with minor Wi-Fi transmission queue jitter, these physical fading dips generated $324$ false positive alerts ($0.03\%$ FPR) across $1.08$ million legitimate frames, whereas simulation environments exhibited near-zero false alarms ($0.01\%$ FPR).
2. **Microcontroller Crystal Oscillator Thermal Drift ($\Delta \sigma^2_{\text{IAT}} = +6.82\text{ ms}^2$)**: Physical ESP32 microcontrollers suffer from ambient temperature fluctuations ($\pm 40^\circ\text{C}$ thermal variance), causing crystal oscillator drift ($\pm 3.2\text{ ms}$) and FreeRTOS task switching jitter ($15-50\,\mu\text{s}$). This elevated baseline hardware IAT variance from $1.02\text{ ms}^2$ (simulation) to $7.84\text{ ms}^2$ (hardware).
3. **Receiver AGC Non-Linearity and Quantization Discretization**: Physical ESP32 802.11 Automatic Gain Control (AGC) circuits possess non-linear quantization boundaries near sensitivity limits ($-85\text{ dBm}$ to $-95\text{ dBm}$), introducing discrete $1\text{ dB}$ quantization steps that slightly increase physical RSSI variance ($\Delta \sigma^2_{\text{RSSI}} = +0.76\text{ dB}^2$).

---

### 3. Co-located Attacker Failure Mode ($738$ Missed Frames)

In both simulation and physical hardware, when Attacker $A_1$ is positioned in close physical proximity to Target $N_1$ ($<3.0\text{ m}$ spatial offset), the spatial RSSI variance drops below the isolation threshold ($\sigma^2_{\text{RSSI}} < 2.0\text{ dB}^2$), resulting in $738$ missed frames ($1.82\%$ FNR). However, selective cryptographic fallback acts as a secondary defense layer, ensuring that un-isolated frames triggering threat scores above $0.65$ undergo mandatory ECDSA verification, preventing unauthorized network compromise.
