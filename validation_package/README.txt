===============================================================================
 IAH-EDSD Validation Package — README
 Industrial Adaptive Hybrid Event-Driven Spoofing Detection
===============================================================================

PROJECT: Analyze and Develop Spoofing Detection Method to Minimize
         Resource Consumption in Wireless Sensor Networks (WSN)

FRAMEWORK: IAH-EDSD — 7-Phase Adaptive Spoofing Detection Pipeline
PLATFORM:  NS-3 v3.48 with Python cppyy Bindings
PAPER:     IEEE Access Journal Format (IEEEtran.cls)

===============================================================================
 FOLDER STRUCTURE
===============================================================================

validation_package/
│
├── 1_simulation_code/
│   ├── ns3_spoofing_simulation.py    ← Main NS-3 simulation (511 lines)
│   └── run_spoofing_experiments.sh   ← Master pipeline launcher
│
├── 2_configuration/
│   ├── parameters.json               ← All simulation parameters (JSON)
│   └── crypto_utils.py               ← ECDSA-P256 key generation & signing
│
├── 3_output_results/
│   ├── spoofing_dataset_packets.csv   ← 186,820 packet telemetry records
│   ├── spoofing_energy_per_node.csv   ← Per-node energy depletion profile
│   ├── spoofing_benchmark_summary.csv ← End-to-end benchmark (3 models)
│   └── iah_edsd_netanim.xml           ← NetAnim visualization trace
│
├── 4_graphs/
│   ├── iah_edsd_detection_rate_vs_attackers.png
│   ├── iah_edsd_energy_vs_time.png
│   ├── iah_edsd_ews_convergence.png
│   ├── iah_edsd_pdr_over_time.png
│   ├── spoofing_detection_accuracy_fpr.png
│   ├── spoofing_energy_scaling_nodes.png
│   ├── spoofing_packet_delivery_ratio.png
│   └── spoofing_tradeoff_energy_vs_security.png
│
├── 5_algorithm_implementation/
│   ├── iah_edsd_engine.py             ← Core 7-phase detection engine
│   └── algorithm.txt                  ← Algorithm implementation proof
│
├── 6_ml_pipeline/
│   ├── train_spoofing_ml.py           ← ML model training (4 classifiers)
│   ├── evaluate_spoofing_ids.py       ← Evaluation & benchmark metrics
│   ├── plot_spoofing_results.py       ← Graph generation script
│   ├── spoofing_rf_model.joblib       ← Trained Random Forest model
│   └── spoofing_scaler.joblib         ← StandardScaler (feature normalization)
│
├── 7_paper/
│   ├── ieee_access_journal_paper.tex  ← Full LaTeX source (578 lines)
│   └── ieee_access_journal_paper.pdf  ← Compiled 9-page PDF
│
└── README.txt                         ← This file

===============================================================================
 KEY RESULTS
===============================================================================

  Detection Rate:         97.84%
  False Positive Rate:    0.20%
  Energy per Packet:      1.912 mJ (vs 90.0 mJ baseline)
  Energy Reduction:       97.88%
  Network Lifetime Ext:   +44.04%
  ML Accuracy (RF):       99.99%
  Total Packets Simulated: 186,820

===============================================================================
 HOW TO VERIFY
===============================================================================

1. Open ns3_spoofing_simulation.py → Check AttackerApp class for real spoofing
2. Open iah_edsd_engine.py → Check evaluate_packet() for detection logic
3. Open spoofing_dataset_packets.csv → Verify packet features are computed
4. Open spoofing_benchmark_summary.csv → Cross-check with paper Table 4
5. Compare graphs with paper figures for consistency

===============================================================================
