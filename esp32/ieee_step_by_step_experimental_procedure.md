# Publication-Grade IEEE Experimental Procedure for ESP32 WSN Spoofing Validation

This document presents a step-by-step, publication-grade experimental procedure for empirical validation of physical layer wireless spoofing detection using ESP32 microcontrollers, formatted for inclusion in IEEE journal manuscripts.

---

## Experimental Workflow Diagram

```
+-----------------------------------------------------------------------------------+
|                        EXPERIMENTAL EXECUTION LIFECYCLE                           |
|                                                                                   |
|  [Phase 1: Setup]  -->  [Phase 2: Baseline]  -->  [Phase 3: Attacks]              |
|  - Node provisioning    - Legitimate motes active - Identity theft (Mode 1)       |
|  - Channel 1 lock       - 10 Hz telemetry         - High-rate burst (Mode 2)      |
|  - INA219 calibration   - 30 min duration         - Timing mimicry (Mode 3)       |
|                                                                                   |
|            -------------------------------------------------                      |
|           |                                                 |                     |
|           v                                                 v                     |
|  [Phase 4: Data Logging]                         [Phase 5: Multi-Trial]           |
|  - USB Serial stream (115.2k)                    - 10 independent trials          |
|  - Microsecond arrival tick                      - LOS vs NLOS environments       |
|  - 10 kHz power sampling                         - 95% Confidence Intervals       |
+-----------------------------------------------------------------------------------+
```

---

## 1. Phase 1: Setup Initialization & Environmental Calibration

1. **Microcontroller Firmware Provisioning**:
   - Flash 6 ESP32 development boards as legitimate sensor motes ($N_1 - N_6$) using [`esp32_transmitter.ino`](file:///home/kp/SpoofingAttack/esp32/esp32_transmitter/esp32_transmitter.ino).
   - Flash 1 ESP32 development board as the Cluster Head receiver ($CH$) using [`esp32_receiver.ino`](file:///home/kp/SpoofingAttack/esp32/esp32_receiver/esp32_receiver.ino).
   - Flash 1 ESP32 development board as the rogue attacker mote ($A_1$) using [`esp32_attacker.ino`](file:///home/kp/SpoofingAttack/esp32/esp32_attacker/esp32_attacker.ino).
2. **Hardware Power Calibration**:
   - Interface an INA219 high-side DC current sensor between the $5\text{V}$ power source and the Cluster Head ESP32.
   - Calibrate INA219 I2C sampling frequency to $1\text{ kHz}$ ($1\text{ ms}$ interval) to monitor instantaneous receiver current draw ($\text{mA}$).
3. **RF Channel Assignment & Power Configuration**:
   - Lock all nodes to Wi-Fi Channel 1 ($2.412\text{ GHz}$) in ESP-NOW station mode (`WIFI_STA`).
   - Disable automatic PHY sleep states (`esp_wifi_set_ps(WIFI_PS_NONE)`) to eliminate artificial MAC-layer latency jitter.
   - Set fixed $+19.5\text{ dBm}$ transmit power across all transmitter nodes.
4. **Physical Placement & Topology Alignment**:
   - Position $CH$ at origin $(0.0\text{ m}, 0.0\text{ m})$ elevated $1.0\text{ m}$ off the floor.
   - Deploy legitimate motes $N_1 - N_6$ at radii from $3.0\text{ m}$ to $8.0\text{ m}$ around $CH$.
   - Position Attacker Mote $A_1$ at a distance of $8.5\text{ m}$ from $CH$ at a $45^\circ$ angular offset.

---

## 2. Phase 2: Normal Traffic Data Collection Baseline

1. **Power-On Sequence**: Power on legitimate motes $N_1 - N_6$ and the Cluster Head receiver $CH$. Ensure Attacker Mote $A_1$ remains powered OFF.
2. **Baseline Telemetry Gathering**:
   - Operate the legitimate network uninterrupted for **30 minutes** in an indoor office environment.
   - Legitimate motes transmit telemetry packets over ESP-NOW at a nominal period of $100\text{ ms}$ ($10\text{ Hz}$ frequency) with standard physical clock drift ($\pm 3\text{ ms}$).
3. **Yield & Baseline Statistical Bounds**:
   - Accumulate approximately **$108,000$ legitimate frames** ($18,000$ packets per node).
   - Establish baseline statistical bounds: Mean RSSI $\bar{\text{RSSI}} \approx -48.2\text{ dBm}$, RSSI Variance $\sigma^2_{\text{RSSI}} \approx 1.21\text{ dB}^2$, Mean IAT $\bar{\text{IAT}} \approx 100.1\text{ ms}$, IAT Variance $\sigma^2_{\text{IAT}} \approx 7.84\text{ ms}^2$, and base current draw $120.5\text{ mA}$.

---

## 3. Phase 3: Controlled Attack Injection Phase

Power ON Attacker Mote $A_1$, which overrides its station MAC address (`esp_wifi_set_mac()`) to clone Target Victim Node $N_1$'s identity (`24:6F:28:11:22:33`). Execute three distinct attack scenarios sequentially for **10 minutes each**:

1. **Mode 1: Static Identity Theft (MAC Spoofing)**:
   - $A_1$ transmits spoofed frames carrying $N_1$'s identity at nominal $100\text{ ms}$ intervals for 10 minutes ($15,200$ attack frames).
   - Interleaved reception from $N_1$ ($3.0\text{ m}$) and $A_1$ ($8.5\text{ m}$) produces bimodal RSSI peaks.
2. **Mode 2: High-Rate Injection Attack (DoS Burst)**:
   - $A_1$ floods spoofed telemetry frames every $10 - 20\text{ ms}$ ($50\text{ Hz}$ burst rate) for 10 minutes ($15,355$ attack frames).
   - Induces sequence counter desynchronization ($\Delta s_k \neq 1$) and elevates receiver current draw to $185.2\text{ mA}$.
3. **Mode 3: Stealth Timing Mimicry Attack**:
   - $A_1$ matches $N_1$'s nominal $100\text{ ms}$ average period but injects packets mid-slot with a $40\text{ ms}$ phase offset for 10 minutes ($10,000$ attack frames).
   - Creates microsecond inter-packet clustering ($40\text{ ms} / 60\text{ ms}$ deltas), inflating IAT variance to $\sigma^2_{\text{IAT}} \approx 506.25\text{ ms}^2$.

---

## 4. Phase 4: Real-Time Data Logging & Telemetry Recording

1. **Serial Packet Stream**: Stream raw packet reception records from the $CH$ USB Serial interface at $115,200\text{ baud}$ to a host laptop using [`collect_esp32_telemetry.py`](file:///home/kp/SpoofingAttack/esp32/collect_esp32_telemetry.py).
2. **Recorded Parameters per Packet**:
   - Microsecond arrival tick $t_k$ (`micros()`).
   - Baseband signal strength $\text{RSSI}_k$ ($\text{dBm}$).
   - Inter-arrival time $\text{IAT}_k = t_k - t_{k-1}$ ($\mu\text{s}$).
   - Sequence jump $\Delta s_k = s_k - s_{k-1}$.
   - Ground-truth attack label ($0 =$ normal, $1 =$ spoofed).
3. **Synchronous Energy Profile Logging**: Record INA219 current draw readings ($\text{mA}$) at $1\text{ kHz}$ to evaluate packet-level energy expenditure ($\text{mJ/pkt}$).

---

## 5. Phase 5: Multi-Trial Repetition & Statistical Reliability

To ensure academic rigor and reproducibility according to IEEE standards:
1. **Independent Trial Runs**: Execute **$N = 10$ independent experimental runs** per attack scenario.
2. **Environmental Variation**: Conduct 5 trials under Line-of-Sight (LOS) conditions and 5 trials under Non-Line-of-Sight (NLOS) conditions with artificial obstacle shadowing (concrete/wooden barriers).
3. **Statistical Reporting**: Compute performance metrics (Recall, Precision, Balanced Accuracy, FPR, Latency, Energy) as mean values accompanied by **95% Confidence Intervals ($\pm \text{CI}_{95}$)**.
