/*
 * ESP32 WSN Receiver & Cluster Head Spoofing Collector Firmware
 * 
 * Hardware: ESP32 NodeMCU / WROOM-32 (Receiver / Cluster Head)
 * Protocol: ESP-NOW (2.4 GHz 802.11 b/g/n)
 * 
 * Functionality:
 *  1. Receives packets from legitimate sensor nodes and attacker nodes.
 *  2. Records precise microsecond packet arrival timestamp via micros().
 *  3. Measures Received Signal Strength Indicator (RSSI) in dBm.
 *  4. Calculates Inter-Arrival Time (IAT = t_current - t_previous) per node.
 *  5. Computes sequence number jumps (Delta_Seq = seq_current - seq_previous).
 *  6. Outputs real-time CSV data stream to Serial for ML model processing & dataset generation.
 * 
 * Output CSV Format:
 *  Timestamp_us, Node_ID, Seq_Num, RSSI_dBm, IAT_us, Delta_Seq, MAC_Address, GroundTruth_Flag
 */

#include <esp_now.h>
#include <WiFi.h>
#include <esp_wifi.h>

#define MAX_NODES 256
#define WIFI_CHANNEL 1

// Packet Payload Structure (Must match Transmitter)
typedef struct __attribute__((packed)) {
    uint8_t  node_id;       // Sensor Node ID
    uint32_t seq_num;       // Sequential Packet ID
    uint32_t send_time_us;  // Microsecond timestamp at transmit
    float    telemetry_val; // Sensor telemetry payload
    uint8_t  flags;         // Status flags (0 = normal, 1 = attack)
} TelemetryPacket;

// Tracking state per Node ID
struct NodeState {
    uint32_t last_rx_micros;
    uint32_t last_seq_num;
    bool     initialized;
};

NodeState nodeTracker[MAX_NODES];
int last_rssi = 0; // Temp store for RSSI measurement

// Dual-Core ESP32 compatibility wrapper for ESP-NOW receive callback
#if defined(ESP_IDF_VERSION_MAJOR) && ESP_IDF_VERSION_MAJOR >= 5
void OnDataRecv(const esp_now_recv_info_t *recv_info, const uint8_t *incomingData, int len) {
    const uint8_t *mac_addr = recv_info->src_addr;
    int rssi = recv_info->rx_ctrl->rssi;
#else
void OnDataRecv(const uint8_t *mac_addr, const uint8_t *incomingData, int len) {
    int rssi = last_rssi; // Fallback RSSI
#endif

    uint32_t current_micros = micros();

    if (len < sizeof(TelemetryPacket)) {
        return; // Malformed frame ignored
    }

    TelemetryPacket pkt;
    memcpy(&pkt, incomingData, sizeof(TelemetryPacket));

    uint8_t nid = pkt.node_id;
    uint32_t iat_us = 0;
    int32_t delta_seq = 1;

    if (nid < MAX_NODES) {
        if (nodeTracker[nid].initialized) {
            iat_us = current_micros - nodeTracker[nid].last_rx_micros;
            delta_seq = pkt.seq_num - nodeTracker[nid].last_seq_num;
        } else {
            nodeTracker[nid].initialized = true;
            iat_us = 0;
            delta_seq = 1;
        }

        // Update tracking state
        nodeTracker[nid].last_rx_micros = current_micros;
        nodeTracker[nid].last_seq_num = pkt.seq_num;
    }

    // Format MAC Address as string
    char macStr[18];
    snprintf(macStr, sizeof(macStr), "%02X:%02X:%02X:%02X:%02X:%02X",
             mac_addr[0], mac_addr[1], mac_addr[2], mac_addr[3], mac_addr[4], mac_addr[5]);

    // Output clean CSV line to Serial
    // Format: Timestamp_us, Node_ID, Seq_Num, RSSI_dBm, IAT_us, Delta_Seq, MAC_Address, GroundTruth_Flag
    Serial.printf("%u,%u,%u,%d,%u,%d,%s,%u\n",
                  current_micros,
                  pkt.node_id,
                  pkt.seq_num,
                  rssi,
                  iat_us,
                  delta_seq,
                  macStr,
                  pkt.flags & 0x01);
}

// Promiscuous RX callback to capture hardware RSSI for all 802.11 frames
void promiscuous_rx_cb(void *buf, wifi_promiscuous_pkt_type_t type) {
    wifi_promiscuous_pkt_t *pkt = (wifi_promiscuous_pkt_t *)buf;
    last_rssi = pkt->rx_ctrl.rssi;
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    // Initialize node tracking array
    memset(nodeTracker, 0, sizeof(nodeTracker));

    // Print CSV Header to Serial
    Serial.println("Timestamp_us,Node_ID,Seq_Num,RSSI_dBm,IAT_us,Delta_Seq,MAC_Address,GroundTruth_Flag");

    // Initialize Wi-Fi in Station Mode
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();

    // Set Wi-Fi Channel
    esp_wifi_set_promiscuous(true);
    esp_wifi_set_channel(WIFI_CHANNEL, WIFI_SECOND_CHAN_NONE);
    esp_wifi_set_promiscuous_rx_cb(&promiscuous_rx_cb);

    // Initialize ESP-NOW
    if (esp_now_init() != ESP_OK) {
        Serial.println("[ERROR] ESP-NOW Init Failed!");
        return;
    }

    // Register Receive Callback
    esp_now_register_recv_cb(OnDataRecv);
}

void loop() {
    // Receiver works entirely via ESP-NOW interrupt callbacks
    vTaskDelay(pdMS_TO_TICKS(1000));
}
