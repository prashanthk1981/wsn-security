#!/usr/bin/env python3
"""
WSN Spoofing Detection Machine Learning Pipeline & Feature Extractor

Processes raw ESP32 CSV telemetry data, extracts sliding window temporal & physical
layer features, trains a Random Forest classifier, and evaluates performance.

Usage:
    python train_spoofing_classifier.py --data example_spoofing_telemetry.csv
"""

import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, recall_score, precision_score, f1_score


def extract_window_features(df, window_size=5):
    """
    Extracts sliding window statistical features from raw telemetry packet logs.
    
    Features computed per window:
      - mean_rssi, std_rssi, min_rssi, max_rssi
      - mean_iat, std_iat, min_iat, max_iat
      - seq_jump_abs, seq_discontinuity_count
    """
    features = []
    labels = []

    for i in range(window_size, len(df)):
        window = df.iloc[i - window_size : i]
        target_label = df.iloc[i]["label"]

        rssi_vals = window["rssi_dbm"].values
        iat_vals = window["iat_us"].values
        seq_jumps = np.abs(window["delta_seq"].values)

        mean_rssi = np.mean(rssi_vals)
        std_rssi = np.std(rssi_vals)
        min_rssi = np.min(rssi_vals)
        max_rssi = np.max(rssi_vals)

        mean_iat = np.mean(iat_vals)
        std_iat = np.std(iat_vals)
        min_iat = np.min(iat_vals)
        max_iat = np.max(iat_vals)

        seq_discontinuities = np.sum(seq_jumps != 1)

        feat_vector = [
            mean_rssi, std_rssi, min_rssi, max_rssi,
            mean_iat, std_iat, min_iat, max_iat,
            seq_discontinuities
        ]
        features.append(feat_vector)
        labels.append(target_label)

    feature_names = [
        "mean_rssi", "std_rssi", "min_rssi", "max_rssi",
        "mean_iat", "std_iat", "min_iat", "max_iat",
        "seq_discontinuities"
    ]

    return pd.DataFrame(features, columns=feature_names), np.array(labels)


def main():
    filepath = "example_spoofing_telemetry.csv"
    if len(sys.argv) > 1:
        filepath = sys.argv[1]

    print(f"===========================================================")
    print(f" Loading Telemetry Dataset: {filepath}")
    print(f"===========================================================")

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"[ERROR] Could not read dataset: {e}")
        sys.exit(1)

    print(f"[INFO] Loaded {len(df)} telemetry frames.")
    print(f"[INFO] Class Distribution: Normal (0) = {np.sum(df['label'] == 0)}, Spoofed (1) = {np.sum(df['label'] == 1)}")

    # Feature Engineering over sliding window = 5
    X, y = extract_window_features(df, window_size=5)

    if len(X) < 5:
        print("[WARNING] Not enough rows for windowed feature extraction. Running raw packet feature evaluation...")
        X = df[["rssi_dbm", "iat_us", "delta_seq"]]
        y = df["label"].values

    # Train / Test Split
    if len(X) >= 10:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    else:
        X_train, X_test, y_train, y_test = X, X, y, y

    # Train Random Forest Classifier
    clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    # Performance Evaluation
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print("\n===========================================================")
    print(" EVALUATION RESULTS")
    print("===========================================================")
    print(f" Accuracy:       {acc * 100:.2f}%")
    print(f" Precision:      {prec * 100:.2f}%")
    print(f" Recall:         {rec * 100:.2f}%")
    print(f" Macro F1-Score: {f1 * 100:.2f}%")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))


if __name__ == "__main__":
    main()
