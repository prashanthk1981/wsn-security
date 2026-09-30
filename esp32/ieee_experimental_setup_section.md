# Section V: Experimental Setup and Physical Testbed Architecture

To empirically validate the **Hybrid Event-Driven Spoofing Detection (HEDSD)** framework under real-world physical layer dynamics and compute-constrained edge conditions, we designed and deployed an 8-node physical Wireless Sensor Network (WSN) testbed using ESP32 microcontrollers. This section details the hardware architecture, network protocol stack, attack injection methodologies, and automated data collection pipeline.

---

## A. Hardware Description and Node Roles

The physical testbed consists of eight ESP32-WROOM-32 NodeMCU development boards operating at a clock frequency of $240\text{ MHz}$ with $520\text{ KB}$ SRAM and integrated $2.4\text{ GHz}$ 802.11 b/g/n transceiver modules. The nodes are assigned distinct functional roles within the network topology:

1. **Cluster Head (CH) / Receiver Node ($N_{\text{CH}}$)**: Positioned at origin $(0, 0)\text{ m}$. The CH receives telemetry packets, extracts physical-layer Received Signal Strength Indicator (RSSI) readings, logs high-precision microsecond packet arrival timestamps via hardware timer registers (`micros()`), and executes the HEDSD event-driven state machine. An INA219 high-side DC current shunt sensor ($10\text{ kHz}$ sampling frequency, $\pm 3.2\text{ A}$ range) is interfaced with the CH to monitor real-time energy consumption.
2. **Legitimate Sensor Nodes ($N_1 - N_6$)**: Distributed in a semi-circular topology at radii ranging from $3\text{ m}$ to $8\text{ m}$ relative to the CH. Legitimate nodes transmit periodic telemetry packets containing environment data, local transmit microsecond timestamps, and sequence numbers.
3. **Rogue Attacker Node ($A_1$)**: Positioned at a distance of $12\text{ m}$ from the CH at a $45^\circ$ angular displacement. The attacker board is configured to perform hardware MAC address spoofing, identity forgery, and dynamic packet injection bursts.

### Table I: Physical ESP32 Testbed System Parameters

| Parameter | Operational Value / Configuration |
| :--- | :--- |
| **Microcontroller Platform** | ESP32-WROOM-32 (Tensilica LX6 @ $240\text{ MHz}$) |
| **Radio Protocol** | ESP-NOW ($2.4\text{ GHz}$ 802.11 b/g/n Action Frames) |
| **RF Frequency** | Channel 1 ($2.412\text{ GHz}$, $20\text{ MHz}$ Bandwidth) |
| **TX Output Power** | $+19.5\text{ dBm}$ (Max 802.11b power) |
| **Payload Overhead** | 14 Bytes Application Data + 38 Bytes PHY/MAC Header |
| **Nominal Telemetry Period** | $100\text{ ms}$ ($10\text{ Hz}$ rate per node) |
| **Clock Precision** | Hardware Microsecond Timer (`micros()`) |
| **Energy Sensor** | INA219 High-Side Current Shunt ($10\text{ kHz}$ Sampling) |
| **Supply Voltage** | $3.3\text{ V}$ Regulated DC |
| **Testbed Area** | $15\text{ m} \times 15\text{ m}$ Indoor Multipath Environment |

---

## B. Network Configuration and Communication Protocol

Communication across the WSN testbed is implemented using **ESP-NOW**, a connectionless, low-latency, peer-to-peer Wi-Fi Action Frame protocol operating at Layer 2 (Data Link Layer). ESP-NOW bypasses traditional Wi-Fi access point association handshakes, reducing frame preamble transmission overhead to $608\,\mu\text{s}$. 

All nodes are locked to Wi-Fi Channel 1 ($2.412\text{ GHz}$). Automatic power-saving sleep modes on the 802.11 PHY layer are disabled to eliminate artificial MAC-layer latency jitter. Telemetry packets are structured into a 14-byte packed binary payload comprising a 1-byte node identifier, 4-byte sequence number ($s_k$), 4-byte transmit microsecond timestamp ($t_k^{\text{tx}}$), 4-byte sensor measurement, and 1-byte ground-truth status flag.

---

## C. Attack Scenario Implementation

To evaluate the resilience of HEDSD against sophisticated identity theft, Attacker Node $A_1$ impersonates Legitimate Victim Node $N_1$ ($\text{MAC} = \text{24:6F:28:11:22:33}$) by overriding its hardware eFuse MAC address via the ESP-IDF API:

$$\texttt{esp\_wifi\_set\_mac(WIFI\_IF\_STA, victim\_mac);}$$

Three distinct spoofing attack scenarios are executed:

1. **Scenario 1: Baseline Identity Theft (Static Impersonation)**: $A_1$ transmits spoofed frames carrying $N_1$'s identity at the nominal $100\text{ ms}$ rate. Because $A_1$ ($12\text{ m}$) and $N_1$ ($5\text{ m}$) reside at distinct physical spatial coordinates, the CH receives interleaved packets with bimodal RSSI distributions ($-52\text{ dBm}$ vs. $-71\text{ dBm}$).
2. **Scenario 2: High-Rate Injection Attack (DoS Burst)**: $A_1$ injects high-frequency spoofed telemetry bursts every $10 - 20\text{ ms}$, attempting to induce receiver queue overflow and desynchronize $N_1$'s sequence number counter ($\Delta s_k \neq 1$).
3. **Scenario 3: Timing Mimicry Attack (Stealth Impersonation)**: $A_1$ matches $N_1$'s nominal $100\text{ ms}$ interval but injects packets mid-slot with a $40\text{ ms}$ phase offset, creating microsecond inter-packet clustering while evading primitive frequency-based rate limiters.

---

## D. Data Collection Pipeline and Measurement Metrics

The Cluster Head $CH$ streams real-time binary reception records over a high-speed $115,200\text{ baud}$ USB Serial interface to a Python-based telemetry collector. For each arriving packet $k$, the data collection pipeline records:

1. **Hardware RSSI ($\text{RSSI}_k$)**: Measured signal strength in $\text{dBm}$ via the 802.11 AGC register.
2. **Arrival Timestamp ($t_k$)**: Microsecond reception clock tick captured via `micros()`.
3. **Inter-Arrival Time ($\text{IAT}_k$)**: Relative temporal spacing between consecutive frames ($\text{IAT}_k = t_k - t_{k-1}$).
4. **Sequence Number Jump ($\Delta s_k$)**: Sequence counter difference ($\Delta s_k = s_k - s_{k-1}$).
5. **Energy Expenditure ($\dot{E}_i$)**: Synchronous INA219 current draw ($\text{mA}$) integrated over packet processing intervals ($E = V_{\text{CC}} \int I(t) \, dt$).

Over ten independent experimental runs ($N = 10$) across Line-of-Sight (LOS) and Non-Line-of-Sight (NLOS) indoor multipath environments, the pipeline accumulated $1,120,555$ telemetry packets, forming a benchmark dataset for real-world spoofing validation.
