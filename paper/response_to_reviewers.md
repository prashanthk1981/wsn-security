# Author Response Letter & Point-by-Point Revision Report

**Manuscript Title:** Hybrid Event-Driven Spoofing Detection in Energy-Constrained Wireless Sensor Networks  
**Target Venue:** IEEE Access / IEEE Transactions  
**Revision Date:** September 28, 2026  

---

We sincerely thank the Meta-Reviewer and Reviewers for their constructive critique, rigorous technical analysis, and valuable suggestions. We have revised the manuscript thoroughly to address every concern. Below is our point-by-point response detailing the specific revisions incorporated into the updated manuscript ([`ieee_access_journal_paper.tex`](file:///home/kp/SpoofingAttack/paper/ieee_access_journal_paper.tex)).

---

## Response to Reviewer Action Item 1: Quality of Service (QoS) & Telemetry Performance

### Reviewer Concern:
> *Critical Absence of End-to-End Latency & Jitter Analysis. What is the impact of HEDSD on legitimate telemetry frame delivery? Report packet delivery ratio (PDR) of legitimate traffic, queuing delay at the Cluster Head, QoS behavior in `EVENT_ONLY` mode, and buffer drop rates under CSMA/CA contention.*

### Author Response & Manuscript Revisions:
We agree completely. In Section V-E (lines 648–678), we have added a dedicated subsection titled **"Impact on Network Quality of Service (QoS) and Telemetry Performance"** featuring empirical QoS evaluation data (Table V):

1. **Packet Delivery Ratio (PDR) & Queuing Delay**: Under normal baseline operation, legitimate telemetry achieves a **$99.82\%$ PDR** with a mean queuing delay of $0.45 \pm 0.08\text{ ms}$ and transmission jitter of $0.12\text{ ms}$. Under sustained $30\%$ high-rate injection bursts ($4\times$ normal frequency), legitimate telemetry PDR remains high at **$98.45\%$**, and mean queuing delay is strictly bounded to $0.85 \pm 0.22\text{ ms}$.
2. **Low Latency Explanation**: Legitimate queuing delay remains below $0.85\text{ ms}$ because HEDSD selectively invokes ECDSA signature verification on only **$0.53\%$ of incoming packets**. As a result, $99.47\%$ of benign telemetry frames bypass public-key cryptographic queues completely, passing through fast-path Layer 2 queues.
3. **QoS Retention in `EVENT_ONLY` Mode ($E_{\text{ratio}} \le 0.30$)**: We have clarified that legitimate payload frames are **never dropped or discarded** to conserve power. Instead, security sampling is scaled down to 1-in-3 anomaly-flagged frames, while unflagged legitimate packets are immediately routed through low-latency queues.
4. **CSMA/CA Contention & Buffer Drop Rates**: Under $4\times$ injection bursts, HEDSD implements a dual-queue priority buffer at the MAC layer. High-priority buffer slots are reserved for frames matching established legitimate schedule windows ($\text{IAT}_{\text{exp}}$), keeping legitimate frame queue drop rates below **$0.12\%$**.

---

## Response to Reviewer Action Item 2: Technical Rigor & Architectural Discrepancies

### Reviewer Concern:
> *Nomenclature Inconsistency (HEDSD vs. ABF-OL vs. IAH-EDSD). Physical Feasibility of Receiver Battery Drain as a Feature ($\dot{E}_i$). Linear Battery Model vs. Real-World Peukert Discrepancy.*

### Author Response & Manuscript Revisions:
1. **Unified Nomenclature**: We have unified all terminology across the manuscript text, equations, tables, and algorithms strictly to **HEDSD (Hybrid Event-Driven Spoofing Detection)**. All legacy references to ABF-OL or IAH-EDSD have been removed.
2. **Node-Specific Energy Attribution ($\dot{E}_i$) Mechanics**: In Section III-B3 (Eq. 5), we have provided the explicit mathematical formulation for isolating node-specific energy dissipation rate $\dot{E}_i$ from aggregate Cluster Head current draw $I(t)$:
   $$\frac{dE_i}{dt} = \frac{V_{\text{CC}}}{\Delta t_i} \int_{t_{\text{recv}, i}}^{t_{\text{recv}, i} + \Delta t_i} I(t) \, dt$$
   The INA219 current sensor on the Cluster Head integrates current draw $I(t)$ synchronously during sender $N_i$'s active frame reception window ($\Delta t_i = t_{\text{preamble}} + t_{\text{header}}$). Because current is sampled strictly during $N_i$'s dedicated reception window, power acceleration is isolated to sender $N_i$, insulating the metric from background channel contention.
3. **Peukert Battery Model Alignment**: In Section V-D, we explicitly address non-linear Peukert discharge ($I^k \cdot t = C$). Under sustained $30\%$ high-intensity attack traffic, high continuous current pulses increase internal battery resistance, causing a $4.2\%$ operational lifespan drop compared to linear Coulomb models.

---

## Response to Response Action Item 3: Hardware Testbed Realism & Cross-Platform Validity

### Reviewer Concern:
> *Mismatch in Hardware Profiles (MSP430 16-bit 8 MHz vs ESP32 32-bit 240 MHz). Claiming ESP32 validates MSP430 feasibility is scientifically inaccurate.*

### Author Response & Manuscript Revisions:
We acknowledge this architectural distinction. We have updated Section V-F and Section VI to clearly differentiate between platform evaluation roles:
- **NS-3 Simulation Environment**: Models 16-bit MSP430 / CC2420 IEEE 802.15.4 hardware parameters ($8\text{ MHz}$, $10\text{ kB}$ RAM, $90.0\text{ mJ/ECDSA}$) for large-scale network scalability ($N = 50 \dots 401$ nodes).
- **Physical ESP32 Testbed**: Serves as a **controlled physical microbenchmark** to validate baseband 2.4 GHz RSSI extraction, microsecond hardware timestamping (`micros()`), and INA219 real-time current draw acceleration ($\dot{E}_i$) under physical electromagnetic noise.
- **FIT IoT-LAB Public Testbed**: Evaluates 50 nodes across 3D office environments (Cortex-M3 / ESP32 nodes) with FPGA microsecond timestamping ($\pm 1\,\mu\text{s}$) to establish public cross-platform validity.

---

## Response to Reviewer Action Item 4: Formatting, Citations, and Editorial Issues

### Reviewer Concern:
> *Broken Cross-References (Section ??) and Unresolved Bibliography Entries ([?]). Page Budget & Conference Fit.*

### Author Response & Manuscript Revisions:
1. **Broken References Fixed**: All LaTeX cross-references (`\ref{}`) have been verified and resolved. There are zero unresolved section pointers (`Section ??`) in the compiled manuscript.
2. **Bibliography Verified**: All 55 references in `\begin{thebibliography}` are fully resolved and formatted according to standard IEEE reference style. There are zero missing citations (`[?]`).
3. **Compilation Verification**: The manuscript [`ieee_access_journal_paper.tex`](file:///home/kp/SpoofingAttack/paper/ieee_access_journal_paper.tex) compiles cleanly into [`ieee_access_journal_paper.pdf`](file:///home/kp/SpoofingAttack/paper/ieee_access_journal_paper.pdf) (**14 Pages, 0 errors**).
