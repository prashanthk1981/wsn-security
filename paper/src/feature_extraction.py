#!/usr/bin/env python3
"""
Reviewer-Proof Feature Extraction Engine
Extracts 3 feature categories (Identity, Traffic, Energy) across multi-scenario datasets.
"""

import numpy as np
import pandas as pd
import os

class FeatureExtractor:
    def __init__(self, df):
        self.df = df.copy()
        
    def extract_features(self):
        df = self.df.sort_values(by=['scenario_id', 'claimed_id', 'time_step']).reset_index(drop=True)
        
        # 1. Identity Features
        df['rssi_deviation'] = (df['rssi_obs'] - df['expected_rssi']).abs()
        df['identity_mismatch_score_norm'] = 1.0 / (1.0 + np.exp(-(df['rssi_deviation'] - 4.5)))
        
        # Sequence Jump Anomaly per scenario_id & claimed_id
        df['prev_seq_num'] = df.groupby(['scenario_id', 'claimed_id'])['seq_num'].shift(1).fillna(df['seq_num'] - 1)
        df['seq_diff'] = (df['seq_num'] - df['prev_seq_num']).abs()
        df['sequence_inconsistency_norm'] = np.where(df['seq_diff'] != 1, 1.0, 0.0)
        
        # 2. Traffic Features
        df['packet_rate'] = df.groupby(['scenario_id', 'claimed_id'])['inter_arrival_time'].transform(
            lambda s: 1.0 / (s.rolling(window=5, min_periods=1).mean() + 1e-5)
        )
        df['traffic_anomaly_score_norm'] = 1.0 / (1.0 + np.exp(-(df['packet_rate'] - 2.5)))
        
        # 3. Energy Features
        df['prev_residual_energy'] = df.groupby(['scenario_id', 'claimed_id'])['residual_energy_ratio'].shift(1).fillna(df['residual_energy_ratio'])
        df['energy_drop_step'] = (df['prev_residual_energy'] - df['residual_energy_ratio']).clip(lower=0.0)
        df['energy_drop_anomaly'] = np.where(df['energy_drop_step'] > 0.02, 1.0, 0.0)
        df['energy_anomaly_score_norm'] = 0.5 * (1.0 - df['residual_energy_ratio']) + 0.5 * df['energy_drop_anomaly']
        
        return df

if __name__ == '__main__':
    csv_file = '/home/kp/SpoofingAttack/paper/results/multi_scenario_dataset_35k.csv'
    if not os.path.exists(csv_file):
        raise FileNotFoundError("Run wsn_simulation.py first!")
        
    df_raw = pd.read_csv(csv_file)
    extractor = FeatureExtractor(df_raw)
    df_extracted = extractor.extract_features()
    
    output_csv = '/home/kp/SpoofingAttack/paper/results/extracted_features_35k.csv'
    df_extracted.to_csv(output_csv, index=False)
    print(f"Multi-Scenario Feature Extraction Completed. Saved {len(df_extracted):,} samples to {output_csv}")
