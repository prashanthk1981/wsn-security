# Mathematical Formulation & Step-by-Step Derivation Guide

---

## 1. Mathematical Symbol Notation & System Parameters

| Symbol | Description | Dimensions / Units | Default Value |
| :--- | :--- | :--- | :--- |
| $\mathcal{A}$ | Physical industrial deployment area | $\text{m}^2$ | $1000\text{ m} \times 1000\text{ m}$ |
| $N$ | Total network node population | Count | $401$ ($1\text{ BS} + 40\text{ CHs} + 359\text{ Leaf}$) |
| $i, j$ | Sender leaf node ID and Cluster Head ID | Index | $i \in \{1 \dots 359\}, j \in \{1 \dots 40\}$ |
| $\boldsymbol{p}_i, \boldsymbol{p}_j$ | Spatial position coordinates of node $i$ and CH $j$ | Vector $\mathbb{R}^2$ | $(x_i, y_i), (x_j, y_j)$ |
| $P_{\text{tx}}$ | Transmit signal power | $\text{dBm} / \text{mW}$ | $0.0\text{ dBm} = 1.0\text{ mW}$ |
| $n$ | Industrial path loss exponent | Scalar | $2.7$ |
| $\sigma$ | Shadow fading standard deviation | $\text{dB}$ | $2.0\text{ dB}$ |
| $\text{RSSI}_{\text{obs}}^{(i, j)}(t)$ | Observed Received Signal Strength Indicator | $\text{dBm}$ | Measured per frame |
| $\overline{\text{RSSI}}_{\text{exp}}^{(i, j)}$ | Expected theoretical RSSI based on topology | $\text{dBm}$ | Calculated off-line |
| $\Delta\text{RSSI}_i(t)$ | Absolute spatial RSSI deviation | $\text{dBm}$ | $\ge 0.0$ |
| $T_i(t)$ | Total composite trust score of node $i$ | Scalar $\in [0, 1]$ | Initial $T_i(0) = 1.0$ |
| $T_{\text{auth}}^{(i)}(t)$ | Cryptographic authentication trust metric | Scalar $\in [0, 1]$ | Initial $1.0$ |
| $T_{\text{behavior}}^{(i)}(t)$ | Multi-attribute physical/behavioral trust | Scalar $\in [0, 1]$ | Initial $1.0$ |
| $T_{\text{energy}}^{(i)}(t)$ | Residual energy ratio trust metric | Scalar $\in [0, 1]$ | Initial $1.0$ |
| $\alpha(t), \beta(t), \gamma(t)$ | Dynamic context-aware weights for trust metrics | Scalar | $\alpha + \beta + \gamma = 1.0$ |
| $\text{EWS}_i(t)$ | Early Warning Score accumulator | Scalar $\in [0, 1]$ | Window $W=50$ |
| $\Phi(p_k)$ | Binary event-driven trigger function | $\{0, 1\}$ | $0$ (Bypass), $1$ (Audit) |
| $E_{\text{rem}}^{(i)}(t)$ | Residual energy of node $i$ at time $t$ | Joules ($\text{J}$) | Leaf $5.0\text{ J}$, CH $50.0\text{ J}$ |
| $E_{\text{eval}}(\mathcal{M})$ | Per-packet evaluation energy cost in mode $\mathcal{M}$ | Joules ($\text{J}$) | Depends on $\mathcal{M}$ |

---

## 2. Physical-Layer Log-Normal Path Loss & RSSI Deviation Derivation

### Step 2.1 Theoretical Expected RSSI Derivation
According to the Log-Normal Shadowing Model for indoor industrial radio propagation, the signal power received by Cluster Head $j$ from legitimate leaf node $i$ located at distance $d_{i,j} = \|\boldsymbol{p}_i - \boldsymbol{p}_j\|_2$ is:

$$P_{\text{rx}}(d_{i,j}) = P_{\text{tx}} - P_{\text{L}}(d_0) - 10 n \log_{10}\left(\frac{d_{i,j}}{d_0}\right) + X_{\sigma}$$

where $P_{\text{L}}(d_0) = 40.0\text{ dB}$ at reference distance $d_0 = 1.0\text{ m}$, path loss exponent $n = 2.7$, and shadow fading random variable $X_{\sigma} \sim \mathcal{N}(0, \sigma^2)$ with $\sigma = 2.0\text{ dB}$.

Taking the expected value across random shadow fading ($E[X_{\sigma}] = 0$):

$$\overline{\text{RSSI}}_{\text{exp}}^{(i, j)} = \mathbb{E}[P_{\text{rx}}(d_{i,j})] = P_{\text{tx}} - 40.0 - 27.0 \log_{10}\left(\|\boldsymbol{p}_i - \boldsymbol{p}_j\|_2\right)$$

### Step 2.2 Impersonation Signal Model
When an adversary located at physical coordinates $\boldsymbol{p}_{\text{att}} \neq \boldsymbol{p}_i$ transmits a spoofed packet claiming identity $i$, the actual physical transmission distance to CH $j$ is $d_{\text{att}, j} = \|\boldsymbol{p}_{\text{att}} - \boldsymbol{p}_j\|_2$.

The observed RSSI at CH $j$ is:

$$\text{RSSI}_{\text{obs}}^{(i, j)}(t) = P_{\text{tx}} - 40.0 - 27.0 \log_{10}\left(\|\boldsymbol{p}_{\text{att}} - \boldsymbol{p}_j\|_2\right) + X_{\sigma}(t)$$

### Step 2.3 Spatial RSSI Anomaly Formula
The instantaneous spatial RSSI deviation $\Delta\text{RSSI}_i(t)$ is:

$$\Delta\text{RSSI}_i(t) = \left| \text{RSSI}_{\text{obs}}^{(i, j)}(t) - \overline{\text{RSSI}}_{\text{exp}}^{(i, j)} \right| = \left| 27.0 \log_{10}\left( \frac{\|\boldsymbol{p}_i - \boldsymbol{p}_j\|_2}{\|\boldsymbol{p}_{\text{att}} - \boldsymbol{p}_j\|_2} \right) + X_{\sigma}(t) \right|$$

**Lemma 1**: For any non-collocated attacker ($\boldsymbol{p}_{\text{att}} \neq \boldsymbol{p}_i$), the deterministic distance ratio term $\left|27.0 \log_{10}\left(\frac{d_{i,j}}{d_{\text{att},j}}\right)\right|$ creates a constant positive bias that exceeds shadow fading variance $3\sigma = 6.0\text{ dB}$ with probability $P(\Delta\text{RSSI} > 5.0\text{ dBm}) > 0.985$.

---

## 3. Dynamic Multi-Factor Trust Accumulation Engine

### Step 3.1 Composite Trust Formula
Node trust $T_i(t) \in [0, 1]$ is expressed as:

$$T_i(t) = \alpha(t) T_{\text{auth}}^{(i)}(t) + \beta(t) T_{\text{behavior}}^{(i)}(t) + \gamma(t) T_{\text{energy}}^{(i)}(t)$$

### Step 3.2 Component Formulation & Bounds

#### 1. Authentication Trust Component ($T_{\text{auth}}$)
When a cryptographic audit (ECDSA-P256) is triggered:

$$T_{\text{auth}}^{(i)}(t) = \begin{cases}
1.0, & \text{Signature Valid} \\
0.0, & \text{Signature Invalid / Corrupted} \\
T_{\text{auth}}^{(i)}(t-1), & \text{Audit Bypassed (Cached State)}
\end{cases}$$

#### 2. Behavioral Trust Component ($T_{\text{behavior}}$)
Behavioral trust integrates physical RSSI deviation, sequence numbering jumps, and packet rate spikes:

$$T_{\text{behavior}}^{(i)}(t) = 1.0 - \left[ w_1 \cdot \min\left(1.0, \frac{\Delta\text{RSSI}_i(t)}{15.0}\right) + w_2 \cdot \min\left(1.0, \frac{|\Delta S_i - 1|}{10}\right) + w_3 \cdot \min\left(1.0, \frac{\max(0, R_i - R_{\text{normal}})}{R_{\text{burst\_max}}}\right) \right]$$

where $w_1 = 0.50, w_2 = 0.30, w_3 = 0.20$.

#### 3. Energy Trust Component ($T_{\text{energy}}$)
Evaluates residual energy relative to initial leaf node allocation:

$$T_{\text{energy}}^{(i)}(t) = \frac{E_{\text{rem}}^{(i)}(t)}{E_{\text{leaf}}^{(0)}} = \frac{E_{\text{rem}}^{(i)}(t)}{5.0\text{ J}}$$

---

## 4. Context-Aware Dynamic Weight Updating Derivation

Static weights fail under dynamic threat variations. Weight updates must automatically shift reliance toward cryptographic proof during active attacks while prioritizing behavioral/energy metrics during steady state.

### Weight Adaptation Equations:
$$\alpha(t) = \alpha_0 + \kappa \cdot \text{EWS}_i(t)$$
$$\beta(t) = \beta_0 \cdot \left(1.0 - \frac{\sigma_{\text{RSSI}}^2}{\sigma_{\text{max}}^2}\right)$$
$$\gamma(t) = 1.0 - (\alpha(t) + \beta(t))$$

where base parameters are $\alpha_0 = 0.40, \beta_0 = 0.40, \gamma_0 = 0.20$, and amplification factor $\kappa = 0.30$.

**Normalization Proof**:
$$\alpha(t) + \beta(t) + \gamma(t) = \alpha(t) + \beta(t) + [1.0 - (\alpha(t) + \beta(t))] = 1.0 \quad \blacksquare$$

---

## 5. Event-Driven Trigger $\Phi(p_k)$ Formulation

To prevent running heavy algorithms on every steady-state frame, the binary event trigger $\Phi(p_k) \in \{0, 1\}$ is defined as:

$$\Phi(p_k) = \mathbb{I}\left( \Delta\text{RSSI}_i(t) > \tau_{\text{RSSI}} \;\lor\; |\Delta S_i - 1| > 2 \;\lor\; R_i(t) > R_{\text{thresh}} \right)$$

where $\tau_{\text{RSSI}} = 5.0\text{ dBm}$ and $R_{\text{thresh}} = 10\text{ pkts/s}$.

- If $\Phi(p_k) = 0$: Heavy processing is bypassed. Per-packet energy = $5\,\mu\text{J}$ (Tier 1 RSSI check only).
- If $\Phi(p_k) = 1$: Event anomaly flagged; packet proceeds to Mode-Adaptive Trust Evaluation.

---

## 6. Three-Tier Energy-Adaptive Mode Switching Model

The active detection mode $\mathcal{M}(t)$ is governed by the residual energy ratio $E_{\text{ratio}}^{(j)}(t) = \frac{E_{\text{rem}}^{(j)}(t)}{E_{\text{CH}}^{(0)}}$ of Cluster Head $j$:

$$\mathcal{M}(t) = \begin{cases}
\text{FULL}, & E_{\text{ratio}}^{(j)}(t) > 0.70 \\
\text{LIGHT}, & 0.30 < E_{\text{ratio}}^{(j)}(t) \le 0.70 \\
\text{EVENT\_ONLY}, & E_{\text{ratio}}^{(j)}(t) \le 0.30
\end{cases}$$

### Energy Cost Equation per Mode:
$$E_{\text{eval}}(\mathcal{M}) = \begin{cases}
E_{\text{T1}} + E_{\text{T2\_ML}} + P_{\text{audit}} \cdot E_{\text{T3\_ECDSA}}, & \text{FULL Mode} \quad (0.540\text{ mJ}) \\
E_{\text{T1}} + E_{\text{T2\_LIGHT}}, & \text{LIGHT Mode} \quad (0.055\text{ mJ}) \\
\frac{1}{3} E_{\text{T1}}, & \text{EVENT\_ONLY Mode} \quad (0.0016\text{ mJ})
\end{cases}$$

where $E_{\text{T1}} = 0.005\text{ mJ}$, $E_{\text{T2\_ML}} = 0.100\text{ mJ}$, $E_{\text{T2\_LIGHT}} = 0.050\text{ mJ}$, $E_{\text{T3\_ECDSA}} = 90.00\text{ mJ}$, and empirical audit probability $P_{\text{audit}} = 0.0053$.

---

## 7. Early Warning Score (EWS) Temporal Accumulator

To prevent transient channel noise from triggering false alarms, EWS accumulates historical anomaly events over a sliding window $W = 50$:

$$\text{EWS}_i(t) = \frac{1}{W} \sum_{k=t-W+1}^{t} \mathbb{I}\left( \Delta\text{RSSI}_i(k) > 5.0\text{ dBm} \;\lor\; \Delta S_i(k) > 1 \right)$$

### Final Isolation Decision Criteria:
Node $i$ is isolated ($\text{Isolate}_i = 1$) if and only if all three joint conditions hold:

$$\text{Isolate}_i(t) = \mathbb{I}\left( T_i(t) < 0.60 \;\land\; \text{EWS}_i(t) > 0.40 \;\land\; \Delta\text{RSSI}_i(t) > 5.0\text{ dBm} \right)$$
