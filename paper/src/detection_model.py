#!/usr/bin/env python3
"""
Energy-Aware Multi-Factor Spoofing Detection Model (Multi-Scenario Calibrated)
Computes Spoof_Score = alpha * Identity_Anomaly + beta * Traffic_Anomaly + gamma * Energy_Anomaly
Supports static thresholding vs. dynamic adaptive thresholding.
"""

import numpy as np
import pandas as pd
import os

class EnergyAwareSpoofingDetector:
    def __init__(self, alpha=0.55, beta=0.25, gamma=0.20, base_threshold=0.35):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.base_threshold = base_threshold
        
    def compute_spoof_score(self, df):
        identity_anomaly = 0.75 * df['identity_mismatch_score_norm'] + 0.25 * df['sequence_inconsistency_norm']
        traffic_anomaly = df['traffic_anomaly_score_norm']
        energy_anomaly = df['energy_anomaly_score_norm']
        
        spoof_score = (self.alpha * identity_anomaly + 
                       self.beta * traffic_anomaly + 
                       self.gamma * energy_anomaly)
        return spoof_score

    def compute_dynamic_threshold(self, df, eta=0.06, mu=0.04):
        avg_energy_ratio = df['residual_energy_ratio'].mean()
        traffic_load_ratio = df['traffic_anomaly_score_norm'].mean()
        
        dynamic_tau = self.base_threshold * (1.0 + eta * avg_energy_ratio - mu * traffic_load_ratio)
        return float(dynamic_tau)

    def predict(self, df, mode='dynamic'):
        df = df.copy()
        df['spoof_score'] = self.compute_spoof_score(df)
        
        if mode == 'static':
            threshold = self.base_threshold
        else: # dynamic
            threshold = self.compute_dynamic_threshold(df)
            
        df['predicted_is_attacker'] = (df['spoof_score'] >= threshold).astype(int)
        df['applied_threshold'] = threshold
        return df

if __name__ == '__main__':
    csv_file = '/home/kp/SpoofingAttack/paper/results/extracted_features_35k.csv'
    if not os.path.exists(csv_file):
        raise FileNotFoundError("Run feature_extraction.py first!")
        
    df_features = pd.read_csv(csv_file)
    detector = EnergyAwareSpoofingDetector(alpha=0.55, beta=0.25, gamma=0.20, base_threshold=0.35)
    
    df_dyn = detector.predict(df_features, mode='dynamic')
    dyn_acc = (df_dyn['predicted_is_attacker'] == df_dyn['is_attacker']).mean()
    
    print(f"Multi-Scenario Detection Model Executed.")
    print(f"Overall Dataset Accuracy across 35,000+ samples: {dyn_acc*100:.2f}%")
