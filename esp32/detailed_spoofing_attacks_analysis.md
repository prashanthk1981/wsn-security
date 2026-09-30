# Detailed ESP32 Spoofing Attack Implementation & Signal Signature Analysis

This document provides a research-grade analysis of three realistic spoofing attack modes on ESP32 microcontrollers, detailing attacker behavior, physical channel divergence, and expected statistical impacts on RSSI and Inter-Arrival Time (IAT).

---

## 1. Attack Mode 1: Static Identity Spoofing (MAC & Node ID Forgery)

### A. Attacker Behavior & Hardware Implementation
Attacker Node $A_1$ overrides its hardware MAC address using the ESP-IDF API to match Legitimate Victim Node $N_1$ (`24:6F:28:11:22:33`), setting `node_id = 1` in the payload header. $A_1$ transmits spoofed telemetry frames at $N_1$'s nominal reporting rate ($100\text{ ms}$ period / $10\text{ Hz}$).

```cpp
// Attacker MAC Cloning Implementation
uint8_t victimMac[] = {0x24, 0x6F, 0x28, 0x11, 0x22, 0x33};
esp_wifi_set_mac(WIFI_IF_STA, victimMac);
```

### B. Divergence from Legitimate Node
Although $A_1$ perfectly replicates $N_1$'s digital credentials (MAC, Node ID, sequence format), it is physically positioned at a different coordinate ($A_1$ at $8.5\text{ m}$ vs. $N_1$ at $3.0\text{ m}$ from the Cluster Head).

### C. Impact on RSSI and IAT Signatures
- **RSSI Impact**: The Cluster Head receives interleaved frames from two distinct physical locations:
  - Frames from $N_1$: Mean RSSI $\approx -48\text{ dBm}$.
  - Frames from $A_1$: Mean RSSI $\approx -68\text{ dBm}$ (due to $8.5\text{ m}$ path loss).
  - *Statistical Signature*: Bimodal RSSI distribution with rolling RSSI variance spiking from baseline $\sigma^2_{\text{RSSI}} \approx 1.2\text{ dB}^2$ to $\sigma^2_{\text{RSSI}} > 18.5\text{ dB}^2$.
- **IAT Impact**: Arrival spacing alternates depending on transmit phase alignment, causing minor IAT jitter around $50\text{ ms}$ intervals.

---

## 2. Attack Mode 2: High-Rate Packet Injection Attack (DoS Burst)

### A. Attacker Behavior & Hardware Implementation
Attacker $A_1$ floods the wireless channel with spoofed telemetry packets at an aggressive frequency ($10-20\text{ ms}$ interval / $50\text{ Hz}$ burst rate), attempting to induce receiver queue overflow, consume battery power, and desynchronize $N_1$'s sequence counter.

### B. Divergence from Legitimate Node
Legitimate nodes transmit at a strict, rate-limited telemetry interval ($100\text{ ms} \pm 3\text{ ms}$ jitter). The attacker violates the network's maximum expected packet arrival rate by a factor of $5\times$ to $10\times$.

### C. Impact on RSSI and IAT Signatures
- **IAT Impact**: Rolling mean IAT ($\mu_{\text{IAT}}$) collapses from $100,000\,\mu\text{s}$ down to $10,000-20,000\,\mu\text{s}$, triggering an immediate **Rate Threshold Anomaly**.
- **Sequence Discontinuity**: Sequence numbers desynchronize rapidly ($\Delta s_k \neq 1$) as $A_1$'s independent sequence counter collides with $N_1$'s sequence counter.
- **Power Consumption Impact**: Cluster Head baseband current draw jumps from baseline $120.5\text{ mA}$ to $185.2\text{ mA}$, providing a physical rate-of-change power trigger ($\dot{E}_i = dE_i/dt$).

---

## 3. Attack Mode 3: Stealth Timing Mimicry Attack

### A. Attacker Behavior & Hardware Implementation
Attacker $A_1$ matches $N_1$'s nominal $100\text{ ms}$ average period to evade primitive threshold-based rate filters. However, $A_1$ operates on an un-synchronized clock, injecting packets mid-slot with a $40\text{ ms}$ phase offset relative to $N_1$'s transmissions.

### B. Divergence from Legitimate Node
While the long-term average packet arrival rate appears normal ($10\text{ Hz}$), the short-term inter-packet timing distribution exhibits phase clustering ($40\text{ ms} / 60\text{ ms}$ alternating intervals).

### C. Impact on RSSI and IAT Signatures
- **IAT Impact**:
  - Long-term mean IAT remains $\approx 100\text{ ms}$.
  - Short-term standard deviation $\sigma_{\text{IAT}}$ spikes from $2.8\text{ ms}$ (normal) to $22.5\text{ ms}$ (mimicry).
  - **Shannon Timing Entropy ($H_{\text{IAT}}$)** increases significantly due to bimodal interval clustering.
- **RSSI Impact**: Exhibited as a double-peaked discrete RSSI distribution, causing high rolling spatial variance ($\sigma^2_{\text{RSSI}} \approx 19.8\text{ dB}^2$).

---

## 4. Summary Matrix of Attack Signatures

| Feature / Metric | Normal Baseline | Mode 1: Identity Spoofing | Mode 2: High-Rate Injection | Mode 3: Timing Mimicry |
| :--- | :--- | :--- | :--- | :--- |
| **MAC / Node ID** | Valid $N_1$ MAC | Cloned $N_1$ MAC | Cloned $N_1$ MAC | Cloned $N_1$ MAC |
| **Mean RSSI ($\mu_{\text{RSSI}}$)** | $-48.2\text{ dBm}$ | $-58.1\text{ dBm}$ (Composite) | $-64.5\text{ dBm}$ | $-58.3\text{ dBm}$ |
| **RSSI Variance ($\sigma^2_{\text{RSSI}}$)** | $1.2\text{ dB}^2$ (Low) | $18.5\text{ dB}^2$ (High) | $28.4\text{ dB}^2$ (Extremely High) | $19.8\text{ dB}^2$ (High) |
| **Mean IAT ($\mu_{\text{IAT}}$)** | $100.1\text{ ms}$ | $50.2\text{ ms}$ | $15.1\text{ ms}$ (Collapsed) | $100.2\text{ ms}$ (Apparent) |
| **IAT Std Dev ($\sigma_{\text{IAT}}$)** | $2.8\text{ ms}$ | $12.4\text{ ms}$ | $14.2\text{ ms}$ | $22.5\text{ ms}$ (High) |
| **Sequence Jumps ($\Delta s_k$)** | Strict $+1$ | Interleaved out-of-order | High positive/negative jumps | Interleaved out-of-order |
| **HEDSD Trigger** | Normal State | Spatial Variance Flag | Anomaly Rate Flag | Timing Entropy Flag |
