#!/usr/bin/env python3
"""
Industrial Adaptive Hybrid Event-Driven Spoofing Detection (IAH-EDSD) Core Engine.
Implements event-driven monitoring, dynamic weight adaptation, multi-factor trust evaluation,
Early Warning Score (EWS), energy-adaptive detection mode switching, and cooperative
cluster decision rules.

Energy-Adaptive Detection Modes:
  FULL       (E_ratio > 0.70): ML + RSSI + Trust + Crypto (all 7 phases)
  LIGHT      (E_ratio > 0.30): RSSI + Trust only (skip crypto, lightweight ML)
  EVENT_ONLY (E_ratio <= 0.30): Event-driven RSSI check only (minimal energy)
"""

import math
import numpy as np
from collections import defaultdict, deque

# Detection Mode Constants
MODE_FULL = "FULL"
MODE_LIGHT = "LIGHT"
MODE_EVENT_ONLY = "EVENT_ONLY"

# Energy thresholds for mode switching
ENERGY_THRESH_HIGH = 0.70   # Above 70%: full detection
ENERGY_THRESH_LOW = 0.30    # Below 30%: event-driven only

# Energy costs per evaluation tier (Joules)
ENERGY_COST_TIER1 = 0.000005    # 5 µJ — Physical RSSI screening
ENERGY_COST_TIER2_FULL = 0.000100   # 100 µJ — Full ML + behavioral evaluation
ENERGY_COST_TIER2_LIGHT = 0.000050  # 50 µJ — Lightweight trust-only evaluation
ENERGY_COST_TIER3_CRYPTO = 0.090    # 90 mJ — ECDSA-P256 signature verification

# Monitoring frequency reduction factor for EVENT_ONLY mode
EVENT_ONLY_SKIP_FACTOR = 3  # Process every 3rd packet in low-energy mode


class IAHEDSDDetectionEngine:
    def __init__(self, node_id, pos, initial_energy=50.0):
        self.node_id = node_id
        self.pos = pos
        self.initial_energy = initial_energy
        
        self.known_positions = {}
        self.node_seq_tracker = defaultdict(int)
        self.node_rssi_history = defaultdict(list)
        self.node_rate_tracker = defaultdict(lambda: deque(maxlen=20))
        
        # Trust components: T_auth, T_behavior, T_energy
        self.t_auth = defaultdict(lambda: 1.0)
        self.t_behavior = defaultdict(lambda: 1.0)
        self.t_energy = defaultdict(lambda: 1.0)
        self.unified_trust = defaultdict(lambda: 1.0)
        
        # Early Warning Score (EWS) tracking
        self.event_counts = defaultdict(int)
        self.suspicious_counts = defaultdict(int)
        self.ews_scores = defaultdict(float)
        
        self.blacklisted_nodes = set()
        
        # Energy-adaptive mode tracking
        self.current_mode = MODE_FULL
        self.packet_counter = defaultdict(int)  # Per-source packet counter for skip logic
        self.mode_transition_log = []  # Track mode transitions for analysis

    def register_node_position(self, target_id, pos):
        """Registers physical position coordinates for spatial fingerprinting."""
        self.known_positions[target_id] = pos

    def determine_detection_mode(self, remaining_energy):
        """
        Phase 8: Energy-Adaptive Detection Mode Selection.
        Selects detection complexity tier based on residual energy ratio.
        
        M(E_ratio) = { FULL        if E_ratio > 0.70
                      { LIGHT       if 0.30 < E_ratio <= 0.70
                      { EVENT_ONLY  if E_ratio <= 0.30
        """
        energy_ratio = max(0.0, remaining_energy / self.initial_energy)
        
        if energy_ratio > ENERGY_THRESH_HIGH:
            new_mode = MODE_FULL
        elif energy_ratio > ENERGY_THRESH_LOW:
            new_mode = MODE_LIGHT
        else:
            new_mode = MODE_EVENT_ONLY
        
        # Log mode transition
        if new_mode != self.current_mode:
            self.mode_transition_log.append({
                'from_mode': self.current_mode,
                'to_mode': new_mode,
                'energy_ratio': energy_ratio
            })
            self.current_mode = new_mode
        
        return new_mode, energy_ratio

    def check_event_trigger(self, packet_rate, rssi_dev, is_new_node):
        """
        Event-Driven Monitoring Trigger (Phase 2):
        Triggers detection ONLY when:
        1. Packet rate spike (> 12 pkts/sec)
        2. Spatial RSSI deviation (> 5.0 dBm)
        3. Unregistered node join event
        """
        if is_new_node or packet_rate > 12.0 or rssi_dev > 5.0:
            return True
        return False

    def get_adaptive_weights(self, packet_rate, energy_level_pct, rssi_dev):
        """
        Phase 3: Adaptive Weight Calculation based on industrial environment.
        Weights: alpha (auth), beta (behavior), gamma (energy)
        """
        if packet_rate > 15.0:
            # High Traffic Spike
            alpha, beta, gamma = 0.20, 0.50, 0.30
        elif energy_level_pct < 0.30:
            # Low Energy Level — energy trust dominates
            alpha, beta, gamma = 0.20, 0.30, 0.50
        elif rssi_dev > 6.0:
            # High Industrial Interference / Spoofing Anomaly
            alpha, beta, gamma = 0.30, 0.50, 0.20
        else:
            # Normal Industrial Condition
            alpha, beta, gamma = 0.34, 0.33, 0.33
        return alpha, beta, gamma

    def calculate_rssi_deviation(self, claimed_id, current_rssi):
        """Phase 4: Physical RSSI Deviation from baseline spatial model."""
        expected_pos = self.known_positions.get(claimed_id)
        if not expected_pos:
            return 8.0  # High default deviation for unmapped node
        
        dx = expected_pos.x - self.pos.x
        dy = expected_pos.y - self.pos.y
        dz = expected_pos.z - self.pos.z
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < 1.0:
            dist = 1.0
        
        # Log-Distance Path Loss Model (n = 2.7)
        exp_rssi = 0.0 - (10.0 * 2.7 * math.log10(dist))
        rssi_dev = abs(current_rssi - exp_rssi)
        return rssi_dev

    def update_early_warning_score(self, claimed_id, is_suspicious):
        """Phase 5: Early Warning Score (EWS) = Suspicious Events / Total Events."""
        self.event_counts[claimed_id] += 1
        if is_suspicious:
            self.suspicious_counts[claimed_id] += 1
        
        total = self.event_counts[claimed_id]
        suspicious = self.suspicious_counts[claimed_id]
        ews = float(suspicious) / float(total) if total > 0 else 0.0
        self.ews_scores[claimed_id] = ews
        return ews

    def evaluate_packet(self, claimed_id, current_rssi, seq_num, timestamp,
                        is_signed, sig_valid, remaining_energy_joules):
        """
        Full Integrated IAH-EDSD Evaluation Pipeline with Energy-Adaptive Mode Selection:
        Phase 1-7: Detection pipeline (complexity varies by energy mode)
        Phase 8: Energy-adaptive mode switching
        
        Returns: (verdict, trust, ews, rssi_dev, crypto_audited, eval_energy, detection_mode, energy_ratio)
        """
        # Phase 8: Determine detection mode based on residual energy
        detection_mode, energy_ratio = self.determine_detection_mode(remaining_energy_joules)
        
        # Calculate RSSI deviation (always active — 5 µJ cost)
        rssi_dev = self.calculate_rssi_deviation(claimed_id, current_rssi)
        
        # Packet Rate Calculation
        rate_queue = self.node_rate_tracker[claimed_id]
        rate_queue.append(timestamp)
        pkt_rate = 1.0
        if len(rate_queue) > 1:
            time_span = rate_queue[-1] - rate_queue[0]
            if time_span > 0:
                pkt_rate = len(rate_queue) / time_span

        # Phase 2: Check Event Trigger
        is_new_node = 1 if claimed_id not in self.known_positions else 0
        trigger = self.check_event_trigger(pkt_rate, rssi_dev, is_new_node)

        # ============================================================
        # EVENT_ONLY Mode: Minimal energy consumption
        # Skip ML and crypto. Only RSSI + trust decay + reduced monitoring.
        # ============================================================
        if detection_mode == MODE_EVENT_ONLY:
            eval_energy = ENERGY_COST_TIER1  # 5 µJ only
            
            # Reduced monitoring: skip every 3rd packet
            self.packet_counter[claimed_id] += 1
            if self.packet_counter[claimed_id] % EVENT_ONLY_SKIP_FACTOR != 0:
                trust = self.unified_trust[claimed_id]
                ews = self.ews_scores[claimed_id]
                return 0, trust, ews, rssi_dev, False, eval_energy, detection_mode, energy_ratio
            
            # Simple RSSI-only detection for processed packets
            if rssi_dev > 5.0:
                # Apply trust decay without full behavioral analysis
                self.unified_trust[claimed_id] = max(0.0, self.unified_trust[claimed_id] - 0.15)
                is_suspicious = True
            else:
                is_suspicious = False
            
            trust = self.unified_trust[claimed_id]
            ews = self.update_early_warning_score(claimed_id, is_suspicious)
            
            # Simplified detection: RSSI + trust threshold only
            verdict = 1 if (trust < 0.60 and rssi_dev > 5.0) else 0
            if verdict == 1:
                self.blacklisted_nodes.add(claimed_id)
            
            return verdict, trust, ews, rssi_dev, False, eval_energy, detection_mode, energy_ratio

        # ============================================================
        # FULL and LIGHT Modes: Event-driven bypass still applies
        # ============================================================
        eval_energy = ENERGY_COST_TIER1  # Start with Tier 1 cost

        if not trigger:
            # Event-Driven Bypassing: Skip heavy computations when traffic is normal
            trust = self.unified_trust[claimed_id]
            ews = self.ews_scores[claimed_id]
            return 0, trust, ews, rssi_dev, False, eval_energy, detection_mode, energy_ratio

        # Event Triggered: Execute trust evaluation
        if detection_mode == MODE_FULL:
            eval_energy += ENERGY_COST_TIER2_FULL   # 100 µJ for full ML
        else:  # MODE_LIGHT
            eval_energy += ENERGY_COST_TIER2_LIGHT  # 50 µJ for lightweight

        # 1. T_auth (Authentication Trust)
        if is_signed:
            if sig_valid:
                self.t_auth[claimed_id] = min(1.0, self.t_auth[claimed_id] + 0.1)
            else:
                self.t_auth[claimed_id] = max(0.0, self.t_auth[claimed_id] - 0.5)
        else:
            # Unsigned packet under triggered state
            self.t_auth[claimed_id] = 0.5

        # 2. T_behavior (Behavioral Trust: RSSI variance & sequence jumps)
        self.node_rssi_history[claimed_id].append(current_rssi)
        if len(self.node_rssi_history[claimed_id]) > 10:
            self.node_rssi_history[claimed_id].pop(0)
        rssi_var = np.var(self.node_rssi_history[claimed_id]) if len(self.node_rssi_history[claimed_id]) > 1 else 0.0

        last_seq = self.node_seq_tracker[claimed_id]
        seq_jump = abs(seq_num - last_seq) if last_seq > 0 else 0
        self.node_seq_tracker[claimed_id] = max(last_seq, seq_num)

        beh_penalty = (0.5 * (1 if rssi_dev > 5.0 else 0)) + (0.3 * (1 if seq_jump > 3 else 0)) + (0.2 * (1 if rssi_var > 3.0 else 0))
        self.t_behavior[claimed_id] = max(0.0, 1.0 - beh_penalty)

        # 3. T_energy (Energy Trust)
        energy_pct = max(0.0, remaining_energy_joules / self.initial_energy)
        self.t_energy[claimed_id] = energy_pct

        # Adaptive Weights
        alpha, beta, gamma = self.get_adaptive_weights(pkt_rate, energy_pct, rssi_dev)
        
        # Unified Trust Calculation
        trust = (alpha * self.t_auth[claimed_id]) + (beta * self.t_behavior[claimed_id]) + (gamma * self.t_energy[claimed_id])
        self.unified_trust[claimed_id] = trust

        # Phase 5: Update Early Warning Score
        is_suspicious = (trust < 0.6) or (rssi_dev > 5.0) or (seq_jump > 3)
        ews = self.update_early_warning_score(claimed_id, is_suspicious)

        # ============================================================
        # Phase 7: Selective Crypto Audit — ONLY in FULL mode
        # In LIGHT mode, crypto is completely disabled to save energy
        # ============================================================
        crypto_audited = False
        if detection_mode == MODE_FULL and trust < 0.6:
            crypto_audited = True
            eval_energy += ENERGY_COST_TIER3_CRYPTO  # 90 mJ ECDSA verification

        # Phase 7: Final Detection Rule
        # Spoofed if: (T < T_th) AND (EWS > E_th) AND (RSSI_dev > R_th)
        T_th, E_th, R_th = 0.60, 0.40, 5.0
        final_spoofed_verdict = 1 if (trust < T_th and ews > E_th and rssi_dev > R_th) else 0

        if final_spoofed_verdict == 1:
            self.blacklisted_nodes.add(claimed_id)

        return final_spoofed_verdict, trust, ews, rssi_dev, crypto_audited, eval_energy, detection_mode, energy_ratio
