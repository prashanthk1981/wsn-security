# Experimental Procedure for Physical WSN Spoofing Detection Validation

This document presents a step-by-step, publication-grade experimental procedure for empirical validation of the **Hybrid Event-Driven Spoofing Detection (HEDSD)** framework on an 8-node physical ESP32 microcontroller testbed, suitable for inclusion in IEEE transactions / IEEE Access journal manuscripts.

---

## Section V.F: Physical Testbed Experimental Procedure

```
+-----------------------------------------------------------------------------------+
|                        PHYSICAL EXPERIMENTAL WORKFLOW                             |
|                                                                                   |
|  [Stage 1: Setup]  -->  [Stage 2: Baseline]  -->  [Stage 3: Attacks]             |
|  - Node placement        - N1-N6 active           - High-rate injection           |
|  - INA219 calibration    - 10 Hz telemetry        - Timing mimicry                |
|  - Channel selection     - 30 min duration        - MAC spoofing                  |
|                                                                                   |
|            -------------------------------------------------                      |
|           |                                                 |                     |
|           v                                                 v                     |
|  [Stage 4: Data Logging]                        [Stage 5: Multi-Trial]            |
|  - Serial CSV stream (115.2k)                   - 10 independent trials           |
|  - Microsecond arrival time                     - LOS vs NLOS environments        |
|  - 10 kHz current sampling                      - 95% Confidence Intervals        |
+-----------------------------------------------------------------------------------+
```

### 1. Setup Initialization & Environmental Calibration
1. **Node Provisioning**: Program 6 ESP32 microcontrollers as legitimate sensor nodes ($N_1 - N_6$), 1 ESP32 as the Cluster Head ($CH$) receiver, and 1 ESP32 as the rogue attacker node ($A_1$) using the firmware suite in [`esp32/`](file:///home/kp/SpoofingAttack/esp32).
2. **Power Hardware Calibration**: Connect an INA219 high-side DC current sensor between the $5\text{V}$ power source and the Cluster Head ESP32. Calibrate the INA219 sampling frequency to $10\text{ kHz}$ to monitor instantaneous current draw ($\text{mA}$) during frame processing.
3. **RF Channel Assignment**: Lock all ESP32 devices to Wi-Fi Channel 1 ($2.412\text{ GHz}$) in ESP-NOW station mode (`WIFI_STA`), disabling 802.11 power-saving sleep modes to prevent artificial latency jitter.
4. **Physical Topology Alignment**:
   - Place $CH$ at coordinate $(0, 0)\text{ m}$.
   - Deploy legitimate nodes $N_1 - N_6$ in a semi-circular topology at radii ranging from $3\text{ m}$ to $8\text{ m}$ from $CH$.
   - Position Attacker Node $A_1$ at a distance of $12\text{ m}$ from $CH$ at a $45^\circ$ angular offset to establish distinct multipath channel fading characteristics.

---

### 2. Normal Telemetry Baseline Collection Phase
1. **Execution**: Power on legitimate nodes $N_1 - N_6$. Operate the network uninterrupted for **30 minutes** in a clean environment.
2. **Traffic Specification**: Each legitimate node transmits telemetry frames over ESP-NOW at a nominal period of $100\text{ ms}$ ($10\text{ Hz}$ frequency) with standard physical clock drift ($\pm 3\text{ ms}$).
3. **Yield**: Accumulate approximately **$108,000$ legitimate frames** ($18,000$ packets per node) to establish baseline statistical distributions for RSSI ($\mu_{\text{RSSI}}, \sigma^2_{\text{RSSI}}$), Inter-Arrival Time ($\text{IAT}$), and base current consumption ($120.5\text{ mA}$).

---

### 3. Controlled Attack Injection Phase
Execute three distinct spoofing attack scenarios targeting Victim Node $N_1$ ($MAC = \text{24:6F:28:11:22:33}$):

1. **Scenario A (MAC Identity Spoofing Baseline)**:
   - Program $A_1$ to clone $N_1$'s MAC address via `esp_wifi_set_mac()` and transmit forged packets at normal $100\text{ ms}$ intervals.
2. **Scenario B (High-Rate Injection Attack / DoS Burst)**:
   - Program $A_1$ to inject high-frequency spoofed telemetry bursts every $10 - 20\text{ ms}$ for a duration of **10 minutes**, attempting to induce receiver queue overflow and desynchronize $N_1$'s sequence counter.
3. **Scenario C (Timing Mimicry Stealth Attack)**:
   - Program $A_1$ to transmit spoofed packets matching $N_1$'s nominal $100\text{ ms}$ period, but phase-shifted by $40\text{ ms}$ mid-slot to bypass simple threshold-based rate filters.

---

### 4. Data Logging & Measurement Process
1. **Serial Telemetry Stream**: Capture real-time binary payload frames from the $CH$ USB Serial interface at $115,200\text{ baud}$ using [`collect_esp32_telemetry.py`](file:///home/kp/SpoofingAttack/esp32/collect_esp32_telemetry.py).
2. **Metrics Captured per Packet**:
   - Microsecond arrival timestamp $t_k$ (`micros()`).
   - Physical Received Signal Strength Indicator ($\text{RSSI}_k$ in $\text{dBm}$).
   - Inter-Arrival Time ($\text{IAT}_k = t_k - t_{k-1}$).
   - Sequence jump ($\Delta s_k = s_k - s_{k-1}$).
   - Ground-truth attack label ($0 =$ normal, $1 =$ spoofed).
3. **Energy Measurement**: Synchronously log INA219 current draw readings at $10\text{ kHz}$ onto a secondary channel to compute packet-level energy expenditure ($\text{mJ/pkt}$) during normal operation vs. cryptographic fallback verification.

---

### 5. Multi-Trial Repetition & Statistical Reliability
To ensure academic rigor and reproducibility in accordance with IEEE experimental standards:
1. **Trial Repetition**: Perform **$N = 10$ independent experimental runs** per attack scenario.
2. **Environmental Variation**: Conduct 5 trials under Line-of-Sight (LOS) conditions and 5 trials under Non-Line-of-Sight (NLOS) conditions with artificial obstacle shadowing (concrete/wood barriers).
3. **Statistical Aggregation**: Report performance metrics (Recall, Precision, Balanced Accuracy, FPR, Latency, Energy) as mean values accompanied by **95% Confidence Intervals ($\pm \text{CI}_{95}$)**.
