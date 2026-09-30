/*
 * ESP32 WSN Telemetry & Spoofing Transmitter Firmware
 * 
 * Hardware: ESP32 NodeMCU / WROOM-32
 * Protocol: ESP-NOW (2.4 GHz 802.11 b/g/n Action Frames)
 * 
 * Features:
 *  - Configurable Node ID and transmit period (default: 100 ms / 10 Hz)
 *  - Supports Normal Mode vs. Attacker Injection Mode (burst spoofing)
 *  - Includes microsecond timestamp, sequence number, and sensor telemetry
 * 
 * Target: WSN Spoofing Detection Research Testbed
 */

#include <esp_now.h>
#include <WiFi.h>
#include <esp_wifi.h>

// ============================================================================
// CONFIGURATION PARAMETERS
// ============================================================================
#define NODE_ID             1            // Unique Node ID (1 to 6 = Legitimate, 99 = Attacker)
#define DEFAULT_INTERVAL_MS 100          // Telemetry period: 100 ms (10 Hz)
#define WIFI_CHANNEL        1            // Wi-Fi Channel (Must match Cluster Head)

// Receiver (Cluster Head) MAC Address
// REPLACE WITH YOUR RECEIVER ESP32 MAC ADDRESS (e.g. {0x24, 0x6F, 0x28, 0xAB, 0xCD, 0xEF})
uint8_t receiverAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}; // Broadcast by default

// Mode selection: 0 = Legitimate Periodic Sensor, 1 = Attacker Burst Spoofing
#define IS_ATTACKER_NODE    0

// Packet Payload Structure (14 bytes packed)
typedef struct __attribute__((packed)) {
    uint8_t  node_id;       // Sensor Node ID
    uint32_t seq_num;       // Sequential Packet ID
    uint32_t send_time_us;  // Microsecond timestamp at transmit
    float    telemetry_val; // Simulated sensor reading (e.g., temperature °C)
    uint8_t  flags;         // Status flags (Bit 0: Attack flag for ground-truth labeling)
} TelemetryPacket;

// Global variables
TelemetryPacket txPacket;
uint32_t sequenceCounter = 0;
unsigned long lastTxTime = 0;
esp_now_peer_info_t peerInfo;

// Send Callback
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    // Callback reserved for ACK/transmission status tracking if needed
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("=================================================");
    Serial.printf(" ESP32 Transmitter Init | Node ID: %d\n", NODE_ID);
    Serial.println("=================================================");

    // Set Wi-Fi to Station Mode
    WiFi.mode(WIFI_STA);
    
    // Set Wi-Fi Channel explicitly
    esp_wifi_set_promiscuous(true);
    esp_wifi_set_channel(WIFI_CHANNEL, WIFI_SECOND_CHAN_NONE);
    esp_wifi_set_promiscuous(false);

    Serial.print("Transmitter MAC Address: ");
    Serial.println(WiFi.macAddress());

    // Initialize ESP-NOW
    if (esp_now_init() != ESP_OK) {
        Serial.println("[ERROR] ESP-NOW Initialization Failed!");
        return;
    }

    // Register Send Callback
    esp_now_register_send_cb(OnDataSent);

    // Register Peer (Receiver Cluster Head)
    memcpy(peerInfo.peer_addr, receiverAddress, 6);
    peerInfo.channel = WIFI_CHANNEL;
    peerInfo.encrypt = false; // Unencrypted for low-latency physical layer measurement

    if (esp_now_add_peer(&peerInfo) != ESP_OK) {
        Serial.println("[WARNING] Failed to add peer! (Broadcasting will still work if 0xFF used)");
    }
}

void loop() {
    unsigned long currentMillis = millis();
    
    #if IS_ATTACKER_NODE
    // Attacker behavior: High-frequency burst injection with randomized intervals (10-30 ms)
    uint32_t interval = random(10, 30);
    #else
    // Normal node behavior: Strict periodic transmission (100 ms with +/- 5 ms random jitter)
    uint32_t interval = DEFAULT_INTERVAL_MS + random(-5, 6);
    #endif

    if (currentMillis - lastTxTime >= interval) {
        lastTxTime = currentMillis;

        // Build Telemetry Packet
        txPacket.node_id = NODE_ID;
        txPacket.seq_num = ++sequenceCounter;
        txPacket.send_time_us = micros();
        txPacket.telemetry_val = 25.0 + (float)random(-20, 20) / 10.0; // Simulated 23.0°C - 27.0°C
        txPacket.flags = IS_ATTACKER_NODE ? 0x01 : 0x00;

        // Transmit Packet over ESP-NOW
        esp_err_t result = esp_now_send(receiverAddress, (uint8_t *)&txPacket, sizeof(txPacket));
        
        if (result == ESP_OK) {
            Serial.printf("[TX] Seq: %u | Node: %d | Time: %u us | Sent OK\n", 
                          txPacket.seq_num, txPacket.node_id, txPacket.send_time_us);
        } else {
            Serial.printf("[TX ERROR] Code: %d\n", result);
        }
    }
}
