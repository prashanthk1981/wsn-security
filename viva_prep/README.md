# Viva Preparation & Comprehensive Documentation Package

This directory contains the complete, PhD-level, IEEE-standard documentation for defending the thesis:

> **"Energy-Adaptive Hybrid Event-Driven Spoofing Detection in Industrial Wireless Sensor Networks (IAH-EDSD)"**

---

## 📂 Documentation Directory Contents

| File Name | Description & Document Type | Key Focus |
| :--- | :--- | :--- |
| 📄 **[01_master_thesis_chapter.md](file:///home/kp/SpoofingAttack/viva_prep/01_master_thesis_chapter.md)** | Complete 10-Section PhD Thesis Chapter | IEEE journal-level comprehensive technical write-up |
| 📐 **[02_mathematical_formulation_derivation.md](file:///home/kp/SpoofingAttack/viva_prep/02_mathematical_formulation_derivation.md)** | Step-by-Step Mathematical Derivation | Log-normal path loss, dynamic trust weight proof, RSSI bounds |
| ⚙️ **[03_formal_algorithm_and_complexity.md](file:///home/kp/SpoofingAttack/viva_prep/03_formal_algorithm_and_complexity.md)** | Algorithm Specification & $O(\cdot)$ Analysis | Algorithm 1 pseudocode, 3-tier mode logic, time/memory footprint |
| 🏗️ **[04_system_architecture_design.md](file:///home/kp/SpoofingAttack/viva_prep/04_system_architecture_design.md)** | Multi-Layer System Architecture | 3-tier topology, module interactions, viva diagram instructions |
| 📈 **[05_analytical_results_and_discussion.md](file:///home/kp/SpoofingAttack/viva_prep/05_analytical_results_and_discussion.md)** | Deep Analytical Results & Discussion | WHY results occur, 5-baseline comparative tables, Pareto frontier |
| 🧠 **[06_phd_viva_defense_qa_guide.md](file:///home/kp/SpoofingAttack/viva_prep/06_phd_viva_defense_qa_guide.md)** | PhD Viva Questions & Answers | Conceptual, mathematical, and architectural defense strategy |
| ⚡ **[07_viva_quick_reference_cheat_sheet.md](file:///home/kp/SpoofingAttack/viva_prep/07_viva_quick_reference_cheat_sheet.md)** | Exam Revision Cheat Sheet | 30-second pitch, key numbers table, core formula reference |

---

## 📊 Summary of Verified Experimental Baselines

- **Evaluated Packets**: $1,120,555$ telemetry packets in NS-3 discrete-event simulator.
- **Topology Scale**: 401 nodes ($1000\text{ m} \times 1000\text{ m}$ grid, 40 Cluster Heads, 1 Sink, 15% attackers).
- **Spoofing Detection Rate (TPR)**: **$98.18\%$**
- **False Positive Rate (FPR)**: **$0.03\%$**
- **Crypto Audit Trigger Rate**: **$0.53\%$** ($99.47\%$ steady-state bypass rate)
- **Average Energy per Packet**: **$0.540\text{ mJ}$** ($99.40\%$ reduction vs $90.00\text{ mJ}$ continuous ECDSA)
- **Cluster Head Lifetime Extension**: **$> 130\times$** ($151.3\text{ Hours}$ vs $1.16\text{ Hours}$ baseline)
- **Microcontroller Feasibility**: RAM footprint $<650\text{ bytes}$, executable on 16-bit TI MSP430 MCU.
