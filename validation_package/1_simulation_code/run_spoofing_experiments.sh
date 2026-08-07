#!/usr/bin/env bash
# Master Execution Pipeline for WSN Spoofing Detection (Objective 4)

set -e

PROJECT_DIR="/home/kp/SpoofingAttack"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
NS3_DIR="/home/kp/Downloads/ns-3.48"

echo "=========================================================================="
echo " Starting End-to-End WSN Spoofing Detection Pipeline (Objective 4)"
echo "=========================================================================="

echo "[Step 1/4] Running NS-3 Discrete Event Simulation (Industrial WSN Topology)..."
cd "$NS3_DIR"
PATH="$PROJECT_DIR/venv/bin:$PATH" ./ns3 run "$PROJECT_DIR/ns3_spoofing_simulation.py"

echo "[Step 2/4] Training Lightweight Machine Learning Anomaly Classifiers..."
cd "$PROJECT_DIR"
"$VENV_PYTHON" "$PROJECT_DIR/train_spoofing_ml.py"

echo "[Step 3/4] Running Comparative Benchmark & Energy Accounting..."
"$VENV_PYTHON" "$PROJECT_DIR/evaluate_spoofing_ids.py"

echo "[Step 4/4] Generating Publication Figures..."
"$VENV_PYTHON" "$PROJECT_DIR/plot_spoofing_results.py"

echo "=========================================================================="
echo " All Steps Completed Successfully!"
echo " Results available in $PROJECT_DIR:"
echo "   - Dataset: spoofing_dataset_packets.csv"
echo "   - Energy Profile: spoofing_energy_per_node.csv"
echo "   - Benchmark Summary: spoofing_benchmark_summary.csv"
echo "   - Figures: spoofing_detection_accuracy_fpr.png, spoofing_tradeoff_energy_vs_security.png"
echo "=========================================================================="
