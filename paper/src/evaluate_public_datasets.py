#!/usr/bin/env python3
"""
Multi-Dataset Evaluation & Cross-Benchmark Generalization Engine
Evaluates proposed multi-factor detection model on:
1. Custom WSN Simulation Dataset
2. TON-IoT Dataset (Primary Public Validation)
3. UNSW-NB15 Dataset (Secondary Benchmark)
Generates cross-dataset performance summary table and high-res comparative figures.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
import os
import sys

# Ensure src is in sys.path
sys.path.append('/home/kp/SpoofingAttack/paper/src')
from detection_model import EnergyAwareSpoofingDetector
from feature_mapping import run_feature_mapping

def compute_metrics(y_true, y_pred, y_prob=None):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    cm = confusion_matrix(y_true, y_pred)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    else:
        fpr = 0.0
        
    auc = roc_auc_score(y_true, y_prob) if y_prob is not None and len(np.unique(y_true)) > 1 else acc
    return {'accuracy': acc, 'precision': prec, 'recall': rec, 'f1': f1, 'fpr': fpr, 'roc_auc': auc}

def run_public_dataset_evaluations():
    results_dir = '/home/kp/SpoofingAttack/paper/results'
    os.makedirs(results_dir, exist_ok=True)
    
    # 1. Check & Ensure mapped datasets exist
    ton_csv = os.path.join(results_dir, 'ton_iot_mapped_features.csv')
    unsw_csv = os.path.join(results_dir, 'unsw_nb15_mapped_features.csv')
    wsn_csv = os.path.join(results_dir, 'extracted_features_35k.csv')
    
    if not (os.path.exists(ton_csv) and os.path.exists(unsw_csv)):
        run_feature_mapping()
        
    df_ton = pd.read_csv(ton_csv)
    df_unsw = pd.read_csv(unsw_csv)
    
    if os.path.exists(wsn_csv):
        df_wsn = pd.read_csv(wsn_csv)
    else:
        # Fallback load or generate
        from wsn_simulation import generate_reviewer_proof_dataset
        from feature_extraction import FeatureExtractor
        df_wsn_raw = generate_reviewer_proof_dataset()
        df_wsn = FeatureExtractor(df_wsn_raw).extract_features()
        
    detector = EnergyAwareSpoofingDetector(alpha=0.55, beta=0.25, gamma=0.20, base_threshold=0.35)
    
    datasets = [
        ('Custom WSN Simulation', df_wsn),
        ('TON-IoT (Public Validation)', df_ton),
        ('UNSW-NB15 (Public Benchmark)', df_unsw)
    ]
    
    eval_results = []
    
    for name, df in datasets:
        df_pred = detector.predict(df, mode='dynamic')
        y_true = df['is_attacker'].values
        y_pred = df_pred['predicted_is_attacker'].values
        y_prob = df_pred['spoof_score'].values
        
        m = compute_metrics(y_true, y_pred, y_prob)
        eval_results.append({
            'Dataset': name,
            'Total Samples': len(df),
            'Accuracy (%)': m['accuracy'] * 100,
            'Precision (%)': m['precision'] * 100,
            'Recall (%)': m['recall'] * 100,
            'F1-Score': m['f1'],
            'FPR (%)': m['fpr'] * 100,
            'ROC-AUC': m['roc_auc']
        })
        
    df_summary = pd.DataFrame(eval_results)
    output_csv = os.path.join(results_dir, 'public_dataset_benchmark.csv')
    df_summary.to_csv(output_csv, index=False)
    
    print("\n--- Multi-Dataset Validation Summary Table ---")
    print(df_summary.to_string(index=False))
    
    # --- Plotting Generalization & Derived Energy Figures ---
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    # Figure 1: Accuracy & F1-Score Generalization across Datasets
    plt.figure(figsize=(9, 5))
    names = df_summary['Dataset']
    accs = df_summary['Accuracy (%)']
    f1s = df_summary['F1-Score'] * 100
    
    x = np.arange(len(names))
    width = 0.35
    
    plt.bar(x - width/2, accs, width, label='Accuracy (%)', color='#2b5c8f')
    plt.bar(x + width/2, f1s, width, label='F1-Score (%)', color='#2ca02c')
    
    plt.xlabel('Evaluation Benchmark Dataset', fontsize=11, fontweight='bold')
    plt.ylabel('Percentage (%)', fontsize=11, fontweight='bold')
    plt.title('Cross-Dataset Model Generalization: Custom WSN vs. TON-IoT vs. UNSW-NB15', fontsize=12, fontweight='bold')
    plt.xticks(x, names, rotation=10, ha='right')
    plt.ylim(0, 105)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'public_dataset_generalization.png'), dpi=300)
    plt.close()
    
    # Figure 2: Derived Energy Anomaly Distribution in TON-IoT
    plt.figure(figsize=(7, 4.5))
    sns.kdeplot(data=df_ton, x='derived_energy_joules', hue='is_attacker', common_norm=False, fill=True, palette={0: '#2b5c8f', 1: '#d9534f'})
    plt.title('Derived Energy Consumption Distribution in TON-IoT Dataset', fontsize=12, fontweight='bold')
    plt.xlabel('Derived Energy (Joules per Session)', fontsize=10, fontweight='bold')
    plt.ylabel('Density', fontsize=10, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'derived_energy_distribution.png'), dpi=300)
    plt.close()
    
    print("\nMulti-Dataset Public Validation Figures Generated Successfully.")

if __name__ == '__main__':
    run_public_dataset_evaluations()
