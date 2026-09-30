# ESP32 Realistic WSN Spoofing Attack Scenario Design & Signal Signatures

This document details the experimental design, firmware implementation, and physical channel signatures for evaluating spoofing attacks on wireless sensor networks using physical ESP32 hardware.

---

## 1. Physical Testbed Topology & Hardware Setup

```
[ Victim Node N1 ] (Distance = 5m, Transmit Power = 0 dBm)
      |
      +-------------> [ Cluster Head Receiver (CH) ] <------------- [ Attacker Node A1 ]
                             (ESP32 + INA219)                (Distance = 12m, Spoofs N1 MAC)
```

- **Legitimate Victim Node ($N_1$)**: Positioned $5\text{ m}$ from Cluster Head (CH). Transmits periodic telemetry packets every $100\text{ ms}$.
- **Attacker Node ($A_1$)**: Positioned $12\text{ m}$ from CH in a different spatial direction (different multipath environment). Clones $N_1$'s MAC address (`24:6F:28:11:22:33`) and Node ID (`0x01`).
- **Cluster Head ($CH$)**: Collects physical layer features (RSSI in dBm, arrival timestamps in $\mu\text{s}$, Inter-Arrival Times $\text{IAT}$, sequence number jumps $\Delta s$).

---

## 2. Attack Implementation Details

### A. MAC Address & Identity Spoofing
In 802.11 / ESP-NOW, identity is established via the 6-byte source MAC address in the frame header. On ESP32, MAC spoofing is achieved via the ESP-IDF Wi-Fi API before initializing ESP-NOW:

```cpp
uint8_t spoofedMacAddress[] = {0x24, 0x6F, 0x28, 0x11, 0x22, 0x33}; // MAC of Victim N1
esp_wifi_set_mac(WIFI_IF_STA, spoofedMacAddress); // Overrides hardware eFuse MAC
```

---

## 3. Evaluated Attack Scenarios

### Scenario 1: Normal Legitimate Traffic Baseline
- **Behavior**: Only Victim Node $N_1$ is active. Transmits every $100\text{ ms}$ ($\pm 3\text{ ms}$ jitter).
- **Physical RSSI Signature**: Stable Gaussian/Rayleigh distribution around $-52\text{ dBm}$ ($\sigma^2_{\text{RSSI}} \approx 1.2\text{ dB}^2$).
- **Timing Signature**: Single tight peak in Inter-Arrival Time ($\text{IAT}$) histogram centered at $100,000\text{ }\mu\text{s}$ ($100\text{ ms}$). Sequence jumps are strictly $\Delta s = 1$.

### Scenario 2: High-Rate Injection Attack (DoS / Buffer Exhaustion)
- **Behavior**: Attacker $A_1$ floods the receiver with spoofed frames at high frequency ($10-20\text{ ms}$ intervals) while $N_1$ continues normal transmission.
- **Physical RSSI Signature**: Severe RSSI fluctuation as receiver alternates between $N_1$ ($-52\text{ dBm}$) and $A_1$ ($-71\text{ dBm}$ due to $12\text{ m}$ path loss).
- **Timing Signature**: Bimodal / short-skewed $\text{IAT}$ distribution with massive collapse down to $10,000 - 20,000\text{ }\mu\text{s}$. Frequent sequence number collisions ($\Delta s \neq 1$) as $A_1$'s clock and sequence counter collide with $N_1$'s stream.

### Scenario 3: Timing Mimicry Attack (Stealth Identity Theft)
- **Behavior**: Attacker $A_1$ attempts to evade rate-limiting filters by matching $N_1$'s nominal $100\text{ ms}$ transmission period, injecting packets mid-slot between $N_1$'s transmissions.
- **Physical RSSI Signature**: Discrete bimodal RSSI peaks ($-52\text{ dBm}$ from $N_1$ and $-71\text{ dBm}$ from $A_1$). High sliding window RSSI variance ($\sigma^2_{\text{RSSI}} > 18.5\text{ dB}^2$).
- **Timing Signature**: Mean $\text{IAT}$ remains near $100\text{ ms}$ over long windows, but phase-shifted arrivals create microsecond inter-packet clustering ($40\text{ ms} / 60\text{ ms}$ alternating intervals).

---

## 4. Signal Signatures & Detection Features Comparison

| Metric / Feature | Scenario 1: Normal | Scenario 2: High-Rate Injection | Scenario 3: Timing Mimicry |
| :--- | :--- | :--- | :--- |
| **Mean RSSI ($\mu_{\text{RSSI}}$)** | $-52.3\text{ dBm}$ | $-63.1\text{ dBm}$ (Composite mean) | $-61.5\text{ dBm}$ |
| **RSSI Variance ($\sigma^2_{\text{RSSI}}$)** | $1.2\text{ dB}^2$ (Low) | $28.4\text{ dB}^2$ (Extremely High) | $19.8\text{ dB}^2$ (High / Bimodal) |
| **Mean IAT ($\mu_{\text{IAT}}$)** | $100.1\text{ ms}$ | $18.4\text{ ms}$ (Collapsed) | $50.2\text{ ms}$ (Interleaved) |
| **IAT Standard Dev ($\sigma_{\text{IAT}}$)** | $2.8\text{ ms}$ | $14.2\text{ ms}$ | $22.5\text{ ms}$ |
| **Seq Num Jumps ($\Delta s$)** | Strict $+1$ | Erratic (Negative/Large Positive) | Alternating / Out-of-order |
| **HEDSD Detection Trigger** | Pass (State 0: Normal) | Anomaly Filter Trigger (State 1) | Spatial RSSI Variance Trigger (State 1) |
| **Selective ECDSA Action** | Suppressed ($0\text{ mJ}$) | Flagged $\to$ ECDSA Audit ($0.54\text{ mJ}$) | Flagged $\to$ ECDSA Audit ($0.54\text{ mJ}$) |
