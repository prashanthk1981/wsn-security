#!/usr/bin/env python3
"""
ESP32 Telemetry Collector & Dataset Generator for WSN Spoofing Detection

Connects to the ESP32 Receiver (Cluster Head) via USB Serial, captures real-time CSV
telemetry, validates packet structures, and saves the output to a CSV dataset.

Usage:
    python collect_esp32_telemetry.py --port /dev/ttyUSB0 --baud 115200 --output esp32_telemetry.csv
"""

import sys
import time
import argparse

require_pyserial = True
try:
    import serial
except ImportError:
    require_pyserial = False


def main():
    parser = argparse.ArgumentParser(description="ESP32 WSN Telemetry Serial Collector")
    parser.add_argument("--port", type=str, default="/dev/ttyUSB0", help="Serial port (e.g. /dev/ttyUSB0 or COM3)")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("--output", type=str, default="esp32_telemetry_dataset.csv", help="Output CSV filepath")
    parser.add_argument("--max-packets", type=int, default=10000, help="Stop logging after N packets")
    args = parser.parse_args()

    if not require_pyserial:
        print("[ERROR] 'pyserial' package is not installed. Run: pip install pyserial")
        sys.exit(1)

    print(f"===========================================================")
    print(f" ESP32 WSN Telemetry Collector")
    print(f" Port: {args.port} | Baud: {args.baud} | Output: {args.output}")
    print(f"===========================================================")

    try:
        ser = serial.Serial(args.port, args.baud, timeout=2.0)
        print(f"[SUCCESS] Connected to {args.port}")
    except Exception as e:
        print(f"[ERROR] Failed to open serial port {args.port}: {e}")
        sys.exit(1)

    packet_count = 0
    with open(args.output, "w") as f:
        print("[INFO] Listening for incoming telemetry packets... Press Ctrl+C to stop.")
        
        while packet_count < args.max_packets:
            try:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue

                # Header detection
                if "Timestamp_us" in line:
                    print(f"[HEADER RECV] {line}")
                    f.write(line + "\n")
                    f.flush()
                    continue

                parts = line.split(",")
                if len(parts) == 8:
                    packet_count += 1
                    f.write(line + "\n")
                    f.flush()

                    if packet_count % 50 == 0:
                        timestamp, node_id, seq_num, rssi, iat_us, delta_seq, mac, flag = parts
                        print(f"[{packet_count}/{args.max_packets}] Node {node_id} | Seq {seq_num} | RSSI: {rssi} dBm | IAT: {iat_us} us | Flag: {flag}")

            except KeyboardInterrupt:
                print("\n[INFO] Collection stopped by user.")
                break
            except Exception as e:
                print(f"[WARNING] Serial read error: {e}")

    ser.close()
    print(f"[DONE] Saved {packet_count} packets to {args.output}")


if __name__ == "__main__":
    main()
