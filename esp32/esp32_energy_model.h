/*
 * ESP32 Software-Based Energy Estimator Library
 * 
 * Based on State-Based Current Accounting (Contiki EnerGest Model)
 * Operating Voltage V_CC = 3.3V
 * 
 * Datasheet & Empirical State Parameters:
 *  - I_TX (ESP-NOW @ +19.5 dBm): 190 mA
 *  - I_RX (ESP-NOW Listening):   100 mA
 *  - I_CPU (Active 160 MHz):      50 mA
 *  - I_CRYPTO (ECDSA 240 MHz):    68 mA
 *  - I_SLEEP (Light Sleep):        0.8 mA
 */

#ifndef ESP32_ENERGY_MODEL_H
#define ESP32_ENERGY_MODEL_H

#include <Arduino.h>

class ESP32EnergyEstimator {
private:
    const float V_CC = 3.3; // Operating Voltage (Volts)

    // Current draw in Amperes (A)
    const float I_TX     = 0.190; // 190 mA
    const float I_RX     = 0.100; // 100 mA
    const float I_CPU    = 0.050; // 50 mA
    const float I_CRYPTO = 0.068; // 68 mA
    const float I_SLEEP  = 0.0008;// 0.8 mA

    // Accumulated state durations in microseconds (us)
    uint64_t total_tx_us;
    uint64_t total_rx_us;
    uint64_t total_cpu_us;
    uint64_t total_crypto_us;
    uint64_t total_sleep_us;

    uint32_t last_state_change_us;
    uint8_t  current_state; // 0: CPU, 1: TX, 2: RX, 3: CRYPTO, 4: SLEEP

public:
    ESP32EnergyEstimator() {
        total_tx_us = 0;
        total_rx_us = 0;
        total_cpu_us = 0;
        total_crypto_us = 0;
        total_sleep_us = 0;
        last_state_change_us = micros();
        current_state = 0;
    }

    void setState(uint8_t newState) {
        uint32_t now = micros();
        uint32_t elapsed = now - last_state_change_us;
        last_state_change_us = now;

        switch (current_state) {
            case 0: total_cpu_us    += elapsed; break;
            case 1: total_tx_us     += elapsed; break;
            case 2: total_rx_us     += elapsed; break;
            case 3: total_crypto_us += elapsed; break;
            case 4: total_sleep_us  += elapsed; break;
        }
        current_state = newState;
    }

    // Calculates total energy consumed in milliJoules (mJ)
    float getTotalEnergy_mJ() {
        setState(current_state); // Update pending elapsed time

        double e_tx     = V_CC * I_TX     * (total_tx_us     / 1000000.0);
        double e_rx     = V_CC * I_RX     * (total_rx_us     / 1000000.0);
        double e_cpu    = V_CC * I_CPU    * (total_cpu_us    / 1000000.0);
        double e_crypto = V_CC * I_CRYPTO * (total_crypto_us / 1000000.0);
        double e_sleep  = V_CC * I_SLEEP  * (total_sleep_us  / 1000000.0);

        return (float)((e_tx + e_rx + e_cpu + e_crypto + e_sleep) * 1000.0);
    }

    // Single Packet Energy Estimation Utilities
    static float getSingleTxPacketEnergy_mJ(uint32_t duration_us = 2110) {
        return 3.3f * 0.190f * (duration_us / 1000.0f); // ~1.323 mJ
    }

    static float getSingleRxPacketEnergy_mJ(uint32_t duration_us = 1800) {
        return 3.3f * 0.100f * (duration_us / 1000.0f); // ~0.594 mJ
    }

    static float getSingleCryptoVerifyEnergy_mJ(uint32_t duration_us = 3200) {
        return 3.3f * 0.068f * (duration_us / 1000.0f); // ~0.718 mJ
    }
};

#endif // ESP32_ENERGY_MODEL_H
