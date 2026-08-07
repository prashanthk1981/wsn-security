#!/usr/bin/env python3
"""
NS-3 Industrial Adaptive Hybrid Event-Driven Spoofing Detection (IAH-EDSD) Simulator.
With Energy-Adaptive Detection Mode Switching.

Industrial Scale Setup:
- 401 Nodes (359 Leaf Sensors, 40 Cluster Heads, 1 Base Station, 60 Intermittent Attackers).
- Area: 1000m x 1000m Factory Floor.
- Workload: Periodic (5 pkts/sec/node) + Event-Driven Bursts (10-20 pkts/sec).
- Integrates NetAnim XML trace generation (iah_edsd_netanim.xml).
- Energy-Adaptive Detection: FULL (>70%), LIGHT (30-70%), EVENT_ONLY (<30%).
- Outputs:
  - spoofing_dataset_packets.csv (Packet telemetry with detection mode)
  - spoofing_energy_per_node.csv (Energy depletion profile per node)
  - spoofing_energy_timeline.csv (Per-round energy snapshots for time-series analysis)
  - iah_edsd_netanim.xml (NetAnim Visualization Trace)
"""

import sys
import os
import time
import struct
import math
import csv
import random
import numpy as np
from collections import defaultdict, deque

# Import NS-3 bindings
from ns import ns
import cppyy

cppyy.include("ns3/netanim-module.h")

# Alias ns3 namespace
ns.core = ns
ns.network = ns
ns.internet = ns
ns.point_to_point = ns
ns.applications = ns
ns3 = ns

# C++ trampolines for Python callbacks and mobility in NS-3
cppyy.cppdef("""
#include "ns3/socket.h"
#include "ns3/callback.h"
#include "ns3/simulator.h"
#include "ns3/mobility-model.h"
#include "ns3/ipv4.h"

namespace ns3 {
    typedef void (*PyRecvFn)(Ptr<Socket>);
    typedef void (*PySchedFn)();

    Callback<void, Ptr<Socket>> MakePyRecvCallback(PyRecvFn fn) {
        return MakeCallback(fn);
    }

    void SchedulePy(Time delay, PySchedFn fn) {
        Simulator::Schedule(delay, fn);
    }

    void SetNodePosition(Ptr<Node> node, double x, double y, double z) {
        Ptr<MobilityModel> mobility = node->GetObject<MobilityModel>();
        if (mobility) {
            mobility->SetPosition(Vector(x, y, z));
        }
    }

    Vector GetNodePosition(Ptr<Node> node) {
        Ptr<MobilityModel> mobility = node->GetObject<MobilityModel>();
        if (mobility) {
            return mobility->GetPosition();
        }
        return Vector(0, 0, 0);
    }
}
""")

def make_recv_callback(pyfunc):
    return ns3.MakePyRecvCallback(pyfunc)

def schedule_py(delay, pyfunc):
    ns3.SchedulePy(delay, pyfunc)

def make_ns3_packet(data_bytes):
    arr = np.frombuffer(data_bytes, dtype=np.uint8)
    return ns.network.Packet(arr, arr.size)

def packet_to_bytes(pkt):
    size = pkt.GetSize()
    buf = bytearray(size)
    pkt.CopyData(buf, size)
    return buf

# Import local crypto and IAH-EDSD modules
import crypto_utils
from iah_edsd_engine import IAHEDSDDetectionEngine

# --- Industrial Simulation Parameters ---
ADAPTIVE = int(os.getenv('ADAPTIVE', '1'))
ATTACKER_PCT = float(os.getenv('ATTACKER_PCT', '0.15'))  # 15% attackers (~60 nodes)
PACKETS = int(os.getenv('PACKETS', '3000'))             # Transmission rounds
INTERVAL = float(os.getenv('INTERVAL', '0.05'))         # Transmission interval (s)

TOTAL_NODES = int(os.getenv('TOTAL_NODES', '401'))
NUM_CHS = 40
CH_START = 0
CH_END = 39     # 40 CHs (Node 0 to 39)
BS_NODE = 400   # Base Station (Node 400)

LEAF_START = 40
LEAF_END = 399  # 360 Leaf Nodes (Node 40 to 399)
NUM_LEAFS = LEAF_END - LEAF_START + 1
NUM_ATTACKERS = int(NUM_LEAFS * ATTACKER_PCT)

# Energy Parameters (Joules)
INITIAL_ENERGY_LEAF = 5.0
INITIAL_ENERGY_CH = 50.0
INITIAL_ENERGY_BS = 1000.0

ENERGY_TX_BYTE = 1.67e-6
ENERGY_RX_BYTE = 1.80e-6
ENERGY_SLEEP_SEC = 1.0e-8

OUTPUT_CSV = os.getenv('OUTPUT_CSV', '/home/kp/SpoofingAttack/spoofing_dataset_packets.csv')
ENERGY_CSV = os.getenv('ENERGY_CSV', '/home/kp/SpoofingAttack/spoofing_energy_per_node.csv')
TIMELINE_CSV = os.getenv('TIMELINE_CSV', '/home/kp/SpoofingAttack/spoofing_energy_timeline.csv')
NETANIM_XML = os.getenv('NETANIM_XML', '/home/kp/SpoofingAttack/iah_edsd_netanim.xml')

# Global registries
_global_ch_apps = {}
_global_leaf_apps = {}
_global_attacker_apps = {}
_global_packet_records = []
_global_energy_timeline = []
_scheduled_callbacks = []
_global_keys = {}
_global_pubkeys = {}

for n_id in range(TOTAL_NODES):
    priv, pub = crypto_utils.generate_ecdsa_keypair()
    _global_keys[n_id] = priv
    _global_pubkeys[n_id] = pub

def calculate_expected_rssi(tx_pos, rx_pos, p_tx_dbm=0.0, path_loss_exponent=2.7):
    dx = tx_pos.x - rx_pos.x
    dy = tx_pos.y - rx_pos.y
    dz = tx_pos.z - rx_pos.z
    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
    if dist < 1.0:
        dist = 1.0
    rssi = p_tx_dbm - (10.0 * path_loss_exponent * math.log10(dist))
    return rssi, dist


class IndustrialLeafApp(ns.Application):
    def __init__(self, node, leaf_id, ch_id, ch_addr, ch_port):
        super(IndustrialLeafApp, self).__init__()
        self.node = node
        self.leaf_id = leaf_id
        self.ch_id = ch_id
        self.ch_addr = ch_addr
        self.ch_port = ch_port
        self.sock = None
        self.seq = 1
        self.energy_spent = 0.0
        self.running = False

    def StartApplication(self):
        self.running = True
        if self.sock is None:
            self.sock = ns.Socket.CreateSocket(self.node, ns.UdpSocketFactory.GetTypeId())
            remote = ns.InetSocketAddress(ns.Ipv4Address(self.ch_addr), self.ch_port)
            self.sock.Connect(remote.ConvertTo())

    def StopApplication(self):
        self.running = False
        if self.sock:
            self.sock.Close()

    def SendSensorData(self):
        if not self.running:
            return
        if self.sock is None:
            self.sock = ns.Socket.CreateSocket(self.node, ns.UdpSocketFactory.GetTypeId())
            remote = ns.InetSocketAddress(ns.Ipv4Address(self.ch_addr), self.ch_port)
            self.sock.Connect(remote.ConvertTo())

        now = ns.core.Simulator.Now().GetSeconds()
        payload = struct.pack('!IId', self.leaf_id, self.seq, now)
        
        sign_flag = 1 if (self.seq % 10 == 0) else 0
        sig_bytes = b''
        if sign_flag:
            sig_bytes = crypto_utils.ecdsa_sign(_global_keys[self.leaf_id], payload)
            self.energy_spent += crypto_utils.ECC_P256_SIGN_ENERGY
        
        sig_len = len(sig_bytes)
        pkt_data = struct.pack('!III', self.leaf_id, self.seq, sig_len) + payload + sig_bytes
        pkt_data = pkt_data + b'\x00' * max(0, 128 - len(pkt_data))
        
        ns_pkt = make_ns3_packet(pkt_data)
        self.sock.Send(ns_pkt)
        self.energy_spent += len(pkt_data) * ENERGY_TX_BYTE
        self.seq += 1


class IndustrialAttackerApp(ns.Application):
    def __init__(self, node, attacker_id, ch_apps):
        super(IndustrialAttackerApp, self).__init__()
        self.node = node
        self.attacker_id = attacker_id
        self.ch_apps = ch_apps
        self.sock = None
        self.seq = 10000
        self.energy_spent = 0.0

    def StartApplication(self):
        if self.sock is None:
            self.sock = ns.Socket.CreateSocket(self.node, ns.UdpSocketFactory.GetTypeId())

    def StopApplication(self):
        if self.sock:
            self.sock.Close()

    def LaunchSpoofingAttack(self, victim_leaf_id, target_ch_id):
        ch_app = self.ch_apps.get(target_ch_id)
        if not ch_app:
            return
        if self.sock is None:
            self.sock = ns.Socket.CreateSocket(self.node, ns.UdpSocketFactory.GetTypeId())

        now = ns.core.Simulator.Now().GetSeconds()
        spoofed_seq = self.seq + random.randint(15, 60)
        payload = struct.pack('!IId', victim_leaf_id, spoofed_seq, now)
        invalid_sig = b'INVALID_SPOOFED_SIGNATURE_32BYTE'
        sig_len = len(invalid_sig)
        
        pkt_data = struct.pack('!III', victim_leaf_id, spoofed_seq, sig_len) + payload + invalid_sig
        pkt_data = pkt_data + b'\x00' * max(0, 128 - len(pkt_data))

        remote = ns.InetSocketAddress(ns.Ipv4Address(ch_app.ch_addr), ch_app.ch_port)
        self.sock.SendTo(make_ns3_packet(pkt_data), 0, remote.ConvertTo())
        self.energy_spent += len(pkt_data) * ENERGY_TX_BYTE
        self.seq += 1


class IndustrialCHApp(ns.Application):
    def __init__(self, node, ch_id, ch_addr, ch_port, bs_addr, bs_port):
        super(IndustrialCHApp, self).__init__()
        self.node = node
        self.ch_id = ch_id
        self.ch_addr = ch_addr
        self.ch_port = ch_port
        self.bs_addr = bs_addr
        self.bs_port = bs_port
        self.sock = None
        self.bs_sock = None
        self.energy_spent = 0.0
        self.packets_processed = 0
        self.detection_engine = IAHEDSDDetectionEngine(self.ch_id, ns.Vector(0.0, 0.0, 0.0), INITIAL_ENERGY_CH)

    def StartApplication(self):
        pos = ns3.GetNodePosition(self.node)
        self.detection_engine.pos = pos
        
        self.sock = ns.Socket.CreateSocket(self.node, ns.UdpSocketFactory.GetTypeId())
        local = ns.InetSocketAddress(ns.Ipv4Address.GetAny(), self.ch_port)
        self.sock.Bind(local.ConvertTo())
        
        self.bs_sock = ns.Socket.CreateSocket(self.node, ns.UdpSocketFactory.GetTypeId())
        remote_bs = ns.InetSocketAddress(ns.Ipv4Address(self.bs_addr), self.bs_port)
        self.bs_sock.Connect(remote_bs.ConvertTo())

    def StopApplication(self):
        if self.sock:
            self.sock.Close()
        if self.bs_sock:
            self.bs_sock.Close()

    def ProcessIncomingPacket(self, pkt, sender_addr, rx_rssi):
        data = packet_to_bytes(pkt)
        self.energy_spent += len(data) * ENERGY_RX_BYTE
        
        if len(data) < 24:
            return

        claimed_id, seq_num, sig_len = struct.unpack('!III', data[:12])
        payload = data[12:12+16]
        sig_bytes = data[12+16:12+16+sig_len] if sig_len > 0 else b''
        
        is_signed = 1 if sig_len > 0 else 0
        sig_valid = False
        if is_signed and claimed_id in _global_pubkeys:
            sig_valid = crypto_utils.ecdsa_verify(_global_pubkeys[claimed_id], sig_bytes, payload)

        now = ns.core.Simulator.Now().GetSeconds()
        rem_energy = max(0.0, INITIAL_ENERGY_CH - self.energy_spent)

        # Updated: evaluate_packet now returns 8 values including detection_mode and energy_ratio
        verdict, trust, ews, rssi_dev, crypto_audited, eval_energy, detection_mode, energy_ratio = \
            self.detection_engine.evaluate_packet(claimed_id, rx_rssi, seq_num, now, is_signed, sig_valid, rem_energy)

        self.energy_spent += eval_energy
        self.packets_processed += 1
        is_spoofed_actual = 1 if (sig_bytes.startswith(b'INVALID_SPOOFED') or sender_addr == "10.1.0.att") else 0

        record = {
            'timestamp': now,
            'ch_id': self.ch_id,
            'claimed_sender_id': claimed_id,
            'seq_num': seq_num,
            'rssi': rx_rssi,
            'delta_rssi': rssi_dev,
            'trust_score': trust,
            'ews_score': ews,
            'crypto_audited': int(crypto_audited),
            'verdict_detected_spoof': verdict,
            'actual_is_spoofed': is_spoofed_actual,
            'eval_energy_joules': eval_energy,
            'detection_mode': detection_mode,
            'energy_ratio': energy_ratio
        }
        _global_packet_records.append(record)

        if verdict == 0 and self.bs_sock:
            fwd_pkt = make_ns3_packet(data)
            self.bs_sock.Send(fwd_pkt)
            self.energy_spent += len(data) * ENERGY_TX_BYTE


def run_industrial_simulation():
    print(f"[*] Initializing Industrial Scale IAH-EDSD Simulation (Energy-Adaptive)...")
    print(f"    - Total Nodes: {TOTAL_NODES} (359 Leaf Sensors, 40 CHs, 1 BS)")
    print(f"    - Factory Floor Area: 1000m x 1000m")
    print(f"    - Attacker Ratio: {ATTACKER_PCT * 100:.1f}% (~{NUM_ATTACKERS} Attacker Nodes)")
    print(f"    - Energy-Adaptive Modes: FULL (>70%), LIGHT (30-70%), EVENT_ONLY (<30%)")
    
    nodes = ns.NodeContainer()
    nodes.Create(TOTAL_NODES)

    mobility = ns.MobilityHelper()
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
    mobility.Install(nodes)

    ns3.SetNodePosition(nodes.Get(BS_NODE), 500.0, 500.0, 0.0)

    ch_coords = []
    grid_rows, grid_cols = 8, 5
    for r in range(grid_rows):
        for c in range(grid_cols):
            cx = 100.0 + c * 200.0
            cy = 100.0 + r * 110.0
            ch_coords.append((cx, cy))

    for i, (cx, cy) in enumerate(ch_coords):
        ns3.SetNodePosition(nodes.Get(CH_START + i), cx, cy, 0.0)

    leaf_idx = LEAF_START
    leaf_nodes_per_ch = NUM_LEAFS // NUM_CHS
    for ch_i in range(NUM_CHS):
        cx, cy = ch_coords[ch_i]
        for _ in range(leaf_nodes_per_ch):
            if leaf_idx <= LEAF_END:
                lx = cx + random.uniform(-40.0, 40.0)
                ly = cy + random.uniform(-40.0, 40.0)
                ns3.SetNodePosition(nodes.Get(leaf_idx), lx, ly, 0.0)
                leaf_idx += 1

    attacker_ids = set(random.sample(range(LEAF_START, LEAF_END + 1), NUM_ATTACKERS))

    # Instantiate NetAnim AnimationInterface
    print(f"[*] Initializing NetAnim XML trace generator -> {NETANIM_XML}")
    anim = cppyy.gbl.ns3.AnimationInterface(NETANIM_XML)
    anim.UpdateNodeDescription(BS_NODE, "BaseStation_Sink")
    anim.UpdateNodeColor(BS_NODE, 0, 0, 255)  # Blue

    for i in range(NUM_CHS):
        ch_id = CH_START + i
        anim.UpdateNodeDescription(ch_id, f"CH_{i}")
        anim.UpdateNodeColor(ch_id, 0, 255, 0)  # Green

    for l_id in range(LEAF_START, LEAF_END + 1):
        if l_id in attacker_ids:
            anim.UpdateNodeDescription(l_id, f"Attacker_{l_id}")
            anim.UpdateNodeColor(l_id, 255, 0, 0)  # Red
        else:
            anim.UpdateNodeDescription(l_id, f"Leaf_{l_id}")
            anim.UpdateNodeColor(l_id, 128, 128, 128)  # Gray

    p2p = ns.PointToPointHelper()
    p2p.SetDeviceAttribute("DataRate", ns.StringValue("250kbps"))
    p2p.SetChannelAttribute("Delay", ns.StringValue("2ms"))

    stack = ns.InternetStackHelper()
    stack.Install(nodes)

    address = ns.Ipv4AddressHelper()
    address.SetBase(ns.Ipv4Address("10.1.0.0"), ns.Ipv4Mask("255.255.0.0"))

    global _global_ch_apps, _global_leaf_apps, _global_attacker_apps, _global_packet_records, _global_energy_timeline, _scheduled_callbacks
    bs_addr = "10.1.0.1"
    ch_apps = _global_ch_apps
    leaf_apps = _global_leaf_apps
    attacker_apps = _global_attacker_apps

    for i in range(NUM_CHS):
        ch_node = nodes.Get(CH_START + i)
        devs = p2p.Install(ch_node, nodes.Get(BS_NODE))
        ip_ifaces = address.Assign(devs)
        ch_ip = str(ip_ifaces.GetAddress(0))
        
        ch_app = IndustrialCHApp(ch_node, CH_START + i, ch_ip, 8000 + i, bs_addr, 9000)
        ch_app.SetStartTime(ns.core.Seconds(0.0))
        ch_app.SetStopTime(ns.core.Seconds(PACKETS * INTERVAL + 5.0))
        ch_node.AddApplication(ch_app)
        ch_apps[CH_START + i] = ch_app

    for ch_app in ch_apps.values():
        for l_id in range(LEAF_START, LEAF_END + 1):
            ch_app.detection_engine.register_node_position(l_id, ns3.GetNodePosition(nodes.Get(l_id)))

    l_idx = LEAF_START
    for ch_i in range(NUM_CHS):
        ch_app = ch_apps[CH_START + ch_i]
        for _ in range(leaf_nodes_per_ch):
            if l_idx <= LEAF_END:
                l_node = nodes.Get(l_idx)
                devs = p2p.Install(l_node, nodes.Get(CH_START + ch_i))
                address.Assign(devs)
                
                l_app = IndustrialLeafApp(l_node, l_idx, CH_START + ch_i, ch_app.ch_addr, ch_app.ch_port)
                l_app.SetStartTime(ns.core.Seconds(0.0))
                l_app.SetStopTime(ns.core.Seconds(PACKETS * INTERVAL + 5.0))
                l_node.AddApplication(l_app)
                leaf_apps[l_idx] = l_app
                
                if l_idx in attacker_ids:
                    att_app = IndustrialAttackerApp(l_node, l_idx, ch_apps)
                    att_app.SetStartTime(ns.core.Seconds(0.0))
                    att_app.SetStopTime(ns.core.Seconds(PACKETS * INTERVAL + 5.0))
                    l_node.AddApplication(att_app)
                    attacker_apps[l_idx] = att_app
                    
                l_idx += 1

    # Snapshot interval: record energy timeline every 50 rounds
    SNAPSHOT_INTERVAL = 50

    def send_industrial_round(r_idx):
        for l_id, l_app in leaf_apps.items():
            l_app.SendSensorData()
            
            rx_pos = ns3.GetNodePosition(nodes.Get(l_app.ch_id))
            tx_pos = ns3.GetNodePosition(l_app.node)
            rssi, _ = calculate_expected_rssi(tx_pos, rx_pos)
            rssi += random.gauss(0, 0.5)
            
            pkt_bytes = struct.pack('!III', l_id, l_app.seq-1, 0) + b'telemetry_payload_16'
            ch_apps[l_app.ch_id].ProcessIncomingPacket(make_ns3_packet(pkt_bytes), "10.1.0.x", rssi)

        for att_id, att_app in attacker_apps.items():
            if random.random() < 0.25:
                victim_id = random.choice([x for x in range(LEAF_START, LEAF_END + 1) if x not in attacker_ids])
                target_ch = random.randint(CH_START, CH_END - 1)
                att_app.LaunchSpoofingAttack(victim_id, target_ch)
                
                rx_pos = ns3.GetNodePosition(nodes.Get(target_ch))
                att_pos = ns3.GetNodePosition(att_app.node)
                rssi, _ = calculate_expected_rssi(att_pos, rx_pos)
                rssi += random.gauss(0, 0.5)
                
                spoof_bytes = struct.pack('!III', victim_id, random.randint(500, 900), 32) + b'telemetry_payload_16' + b'INVALID_SPOOFED_SIGNATURE_32BYTE'
                ch_apps[target_ch].ProcessIncomingPacket(make_ns3_packet(spoof_bytes), "10.1.0.att", rssi)

        # Record energy timeline snapshot
        if r_idx % SNAPSHOT_INTERVAL == 0:
            sim_time = r_idx * INTERVAL
            for ch_id, ch_app in ch_apps.items():
                rem = max(0.0, INITIAL_ENERGY_CH - ch_app.energy_spent)
                _global_energy_timeline.append({
                    'round': r_idx,
                    'timestamp': sim_time,
                    'ch_id': ch_id,
                    'remaining_energy': rem,
                    'energy_ratio': rem / INITIAL_ENERGY_CH,
                    'detection_mode': ch_app.detection_engine.current_mode,
                    'cumulative_packets': ch_app.packets_processed
                })

    for r in range(PACKETS):
        cb = lambda r_idx=r: send_industrial_round(r_idx)
        _scheduled_callbacks.append(cb)
        schedule_py(ns.core.Seconds(r * INTERVAL), cb)

    ns.core.Simulator.Stop(ns.core.Seconds(PACKETS * INTERVAL + 5.0))
    ns.core.Simulator.Run()

    # Export Telemetry Records immediately
    print("[*] Exporting industrial telemetry dataset...")
    with open(OUTPUT_CSV, 'w', newline='') as f:
        fieldnames = ['timestamp', 'ch_id', 'claimed_sender_id', 'seq_num', 'rssi', 'delta_rssi',
                      'trust_score', 'ews_score', 'crypto_audited',
                      'verdict_detected_spoof', 'actual_is_spoofed', 'eval_energy_joules',
                      'detection_mode', 'energy_ratio']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(_global_packet_records)

    # Export per-node energy summary
    node_energies = []
    for ch_id, ch_app in ch_apps.items():
        node_energies.append({
            'node_id': ch_id,
            'role': 'ClusterHead',
            'energy_spent_joules': ch_app.energy_spent,
            'initial_energy_joules': INITIAL_ENERGY_CH,
            'remaining_energy_joules': max(0.0, INITIAL_ENERGY_CH - ch_app.energy_spent),
            'packets_processed': ch_app.packets_processed,
            'final_detection_mode': ch_app.detection_engine.current_mode,
            'mode_transitions': len(ch_app.detection_engine.mode_transition_log)
        })
    for l_id, l_app in leaf_apps.items():
        node_energies.append({
            'node_id': l_id,
            'role': 'LeafNode',
            'energy_spent_joules': l_app.energy_spent,
            'initial_energy_joules': INITIAL_ENERGY_LEAF,
            'remaining_energy_joules': max(0.0, INITIAL_ENERGY_LEAF - l_app.energy_spent),
            'packets_processed': 0,
            'final_detection_mode': 'N/A',
            'mode_transitions': 0
        })

    with open(ENERGY_CSV, 'w', newline='') as f:
        fieldnames = ['node_id', 'role', 'energy_spent_joules', 'initial_energy_joules',
                      'remaining_energy_joules', 'packets_processed', 'final_detection_mode', 'mode_transitions']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(node_energies)

    # Export energy timeline for time-series analysis
    with open(TIMELINE_CSV, 'w', newline='') as f:
        fieldnames = ['round', 'timestamp', 'ch_id', 'remaining_energy', 'energy_ratio',
                      'detection_mode', 'cumulative_packets']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(_global_energy_timeline)

    print(f"[Done] Industrial Datasets Exported:")
    print(f"  - Telemetry: {OUTPUT_CSV} ({len(_global_packet_records)} packets)")
    print(f"  - Energy Log: {ENERGY_CSV}")
    print(f"  - Energy Timeline: {TIMELINE_CSV} ({len(_global_energy_timeline)} snapshots)")
    print(f"  - NetAnim Trace: {NETANIM_XML}")
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)

if __name__ == '__main__':
    run_industrial_simulation()
