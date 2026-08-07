#!/usr/bin/env python3
"""
Train Machine Learning Anomaly Classifiers on Industrial IAH-EDSD Telemetry (Objective 4).
Evaluates Naïve Bayes, Decision Tree, Random Forest, and XGBoost classifiers.
"""

import sys
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

DATA_CSV = os.getenv('DATA_CSV', '/home/kp/SpoofingAttack/spoofing_dataset_packets.csv')
MODEL_PATH = '/home/kp/SpoofingAttack/spoofing_rf_model.joblib'
SCALER_PATH = '/home/kp/SpoofingAttack/spoofing_scaler.joblib'

def train_and_evaluate():
    print(f"[*] Loading industrial dataset from {DATA_CSV}...")
    if not os.path.exists(DATA_CSV):
        print(f"Error: {DATA_CSV} not found. Run ns3_spoofing_simulation.py first.")
        sys.exit(1)

    df = pd.read_csv(DATA_CSV)
    print(f"Dataset shape: {df.shape}")

    feature_cols = ['rssi', 'delta_rssi', 'trust_score', 'ews_score', 'crypto_audited']
    X = df[feature_cols].values
    y = df['actual_is_spoofed'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models = {
        'Naïve Bayes': GaussianNB(),
        'Decision Tree': DecisionTreeClassifier(max_depth=6, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    }

    print("\n=== IAH-EDSD Spoofing Detection ML Performance ===")
    results = {}
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        preds = model.predict(X_test_scaled)
        
        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        f1 = f1_score(y_test, preds, zero_division=0)
        cm = confusion_matrix(y_test, preds, labels=[0, 1])
        
        fpr = cm[0][1] / (cm[0][0] + cm[0][1]) if (cm[0][0] + cm[0][1]) > 0 else 0.0

        print(f"\nModel: {name}")
        print(f"  Accuracy:  {acc * 100:.2f}%")
        print(f"  FPR:       {fpr * 100:.2f}%")
        print(f"  Precision: {prec * 100:.2f}%")
        print(f"  Recall:    {rec * 100:.2f}%")
        print(f"  F1-Score:  {f1 * 100:.2f}%")

        results[name] = {
            'accuracy': acc,
            'fpr': fpr,
            'precision': prec,
            'recall': rec,
            'f1': f1,
            'model': model
        }

    joblib.dump(results['Random Forest']['model'], MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"\n[Saved] Random Forest model -> {MODEL_PATH}")
    print(f"[Saved] StandardScaler -> {SCALER_PATH}")

if __name__ == '__main__':
    train_and_evaluate()
