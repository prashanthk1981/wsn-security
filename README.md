# Hybrid Event Driven Spoofing Detection in Energy Constrained Wireless Sensor Networks

Official repository for **"Hybrid Event Driven Spoofing Detection in Energy Constrained Wireless Sensor Networks"** (Submitted to **ICICNIS 2026**, IEEE Conference ID: `#70805`).

---

## 📌 Overview

Resource-constrained Wireless Sensor Networks (WSNs) deployed in industrial monitoring remain vulnerable to identity spoofing attacks due to shared wireless channels and unencrypted MAC headers. While continuous cryptographic verification offers origin authentication, signature verification consumes an unsustainable $90\,\text{mJ}$ per packet on 16-bit microcontrollers, leading to rapid Cluster Head battery exhaustion within 3 days.

**HEDSD** (Hybrid Event-Driven Spoofing Detection) reconciles this energy-security trade-off by dynamically fusing:
1. **Spatial RSSI Deviation** ($\Delta\text{RSSI}_i > 5.0\,\text{dBm}$)
2. **Packet Inter-Arrival Timing Anomaly** ($\lambda_{\text{IAT}}^{(i)}$)
3. **Receiver Battery Drain Acceleration** ($\dot{E}_i = dE_i/dt$)

HEDSD gates high-cost public-key signature verification (ECDSA NIST P-256) to **$0.53\%$ of incoming packets**, achieving:
* ⚡ **$99.4\%$ Energy Savings** ($0.540\,\text{mJ/pkt}$ vs. $90.0\,\text{mJ/pkt}$)
* 🔋 **$132.3\times$ Battery Longevity Extension** ($3.0\,\text{days} \to 397.0\,\text{days}$ under active attack)
* 🎯 **$98.18\%$ Detection Recall & $0.03\%$ FPR** across 5-fold spatial cross-validation
* ⏱️ **$0.85\,\text{s}$ Threat Isolation Latency** (subsecond containment)

---

## 📂 Repository Structure

```
.
├── paper/                          # LaTeX paper sources & compiled PDFs
│   ├── ieee_conference_paper.tex   # ICICNIS 2026 IEEE Conference Paper
│   ├── ieee_conference_paper.pdf   # Compiled PDF (8 Pages)
│   ├── IEEEtran.cls                # Official IEEE LaTeX class file
│   └── icicnis_2026_submission.zip # Complete submission package
├── esp32/                          # Physical hardware testbed firmware
│   └── esp32_hedsd_firmware.cpp    # ESP-NOW C++ testbed routines
├── paper/src/                      # NS-3 & Python simulation scripts
│   ├── wsn_simulation.py           # 401-node WSN discrete-event simulator
│   ├── feature_extraction.py      # Online Welford single-pass algorithm
│   └── detection_model.py          # Battery-adaptive state machine
├── paper/results/                  # Datasets & benchmark output CSVs
│   ├── extracted_features_35k.csv  # Telemetry feature dataset
│   └── 5fold_cross_val_benchmark.csv # Spatial CV benchmark results
├── plot_spoofing_results.py        # MATLAB B&W plot generator script
└── README.md                       # Repository documentation
```

---

## 🛠️ Quick Start & Reproducibility

### 1. Requirements & Dependencies
```bash
pip install numpy matplotlib pandas scikit-learn
```

### 2. Regenerate Publication Plots (MATLAB B&W Style)
```bash
python3 plot_spoofing_results.py
```

### 3. Recompile Conference Paper PDF
```bash
cd paper
pdflatex ieee_conference_paper.tex
pdflatex ieee_conference_paper.tex
```

---

## 📜 Citation & License

If you find this work useful in your research, please consider citing:

```bibtex
@inproceedings{hedsd2026icicnis,
  title={Event-Driven Multi-Feature Spoofing Detection and Battery-Adaptive Verification in Wireless Sensor Networks},
  author={Prashanth K and Usha J},
  booktitle={7th International Conference on IoT Based Control Networks and Intelligent Systems (ICICNIS 2026)},
  year={2026},
  organization={IEEE},
  note={IEEE Conference ID: \#70805}
}
```

Distributed under the **MIT License**. See `LICENSE` for details.
