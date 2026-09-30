# ESP32 WSN Telemetry & Spoofing Detection Testbed

This repository contains the production Arduino C++ firmware and Python collection scripts for evaluating **Hybrid Event-Driven Spoofing Detection (HEDSD)** on physical ESP32 microcontrollers.

---

## 1. Hardware Architecture & Requirements

| Role | Quantity | Description / Parameters |
| :--- | :--- | :--- |
| **Cluster Head (Receiver)** | 1 Node | ESP32 NodeMCU + INA219 Current Shunt Sensor ($10\text{ kHz}$ sampling) |
| **Legitimate Sensor Nodes** | 6 Nodes ($N_1 - N_6$) | ESP32 NodeMCU transmitting periodic telemetry ($10\text{ Hz}$, $100\text{ ms}$ period) |
| **Attacker Node** | 1 Node ($A_1$) | ESP32 NodeMCU executing MAC RSSI spoofing & packet injection bursts ($10-30\text{ ms}$ interval) |
| **Protocol** | ESP-NOW | 2.4 GHz 802.11 b/g/n Action Frames (Channel 1, Unencrypted peer-to-peer) |
| **Power Metering** | INA219 | High-side DC current sensor ($3.3\text{V} - 5\text{V}$, $\pm 3.2\text{A}$ range) |

---

## 2. Directory Structure

```
esp32/
├── esp32_transmitter/
│   └── esp32_transmitter.ino      # Firmware for Sensor Nodes (N1-N6) & Attacker (A1)
├── esp32_receiver/
│   └── esp32_receiver.ino         # Firmware for Cluster Head (Receiver)
├── collect_esp32_telemetry.py     # Python USB Serial logger & CSV exporter
└── README.md                      # Experimental guide & deployment manual
```

---

## 3. Deployment & Setup Instructions

### Step 1: Flashing Sensor & Attacker Nodes
1. Open [`esp32_transmitter.ino`](file:///home/kp/SpoofingAttack/esp32/esp32_transmitter/esp32_transmitter.ino) in Arduino IDE or PlatformIO.
2. For Legitimate Sensor Nodes ($N_1 - N_6$):
   - Set `#define NODE_ID 1` (increment 1 through 6 for each node).
   - Set `#define IS_ATTACKER_NODE 0`.
3. For Attacker Node ($A_1$):
   - Set `#define NODE_ID 99`.
   - Set `#define IS_ATTACKER_NODE 1`.
4. Upload firmware to each respective ESP32 device.

### Step 2: Flashing the Cluster Head Receiver
1. Open [`esp32_receiver.ino`](file:///home/kp/SpoofingAttack/esp32/esp32_receiver/esp32_receiver.ino).
2. Set `#define WIFI_CHANNEL 1` (Ensure it matches the channel set on transmitters).
3. Connect the ESP32 Receiver to your host machine via USB.
4. Upload firmware to the Receiver board.

### Step 3: Telemetry Collection & CSV Generation
1. Run the Python collection script:
   ```bash
   python collect_esp32_telemetry.py --port /dev/ttyUSB0 --baud 115200 --output esp32_telemetry_dataset.csv
   ```
2. The script logs real-time microsecond arrival times, RSSI values in dBm, Inter-Arrival Times ($\text{IAT}$), sequence numbers, MAC addresses, and ground-truth attack labels.

---

## 4. Telemetry CSV Data Schema

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `Timestamp_us` | `uint32` | Microsecond clock tick at Cluster Head reception (`micros()`) |
| `Node_ID` | `uint8` | ID of sending node ($1-6$ = Legitimate, $99$ = Attacker) |
| `Seq_Num` | `uint32` | Monotonically increasing transmit sequence counter |
| `RSSI_dBm` | `int32` | Hardware Received Signal Strength Indicator (dBm) |
| `IAT_us` | `uint32` | Inter-Arrival Time relative to previous frame ($\Delta t = t_k - t_{k-1}$) |
| `Delta_Seq` | `int32` | Difference in sequence numbers ($\Delta s = s_k - s_{k-1}$) |
| `MAC_Address` | `string` | Transmitter MAC Address (`XX:XX:XX:XX:XX:XX`) |
| `GroundTruth_Flag` | `uint8` | $0 =$ Normal frame, $1 =$ Spoofed / injected frame |
