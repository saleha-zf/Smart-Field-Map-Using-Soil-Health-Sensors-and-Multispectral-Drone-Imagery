#include <WiFi.h>
#include <HTTPClient.h>

// Wokwi WiFi
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// =====================
// STORED REAL NPK DATA
// =====================
int nitrogenData[]   = {12, 14, 10, 9, 15};
int phosphorusData[] = {7, 8, 6, 5, 9};
int potassiumData[]  = {11, 10, 12, 9, 13};

int dataSize = 5;
int indexVal = 0;

// =====================
// SETUP
// =====================
void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected!");
}

// =====================
// MAIN LOOP
// =====================
void loop() {
  int nitrogen, phosphorus, potassium;

  // 1️⃣ Replay stored real data
  if (indexVal < dataSize) {
    nitrogen   = nitrogenData[indexVal];
    phosphorus = phosphorusData[indexVal];
    potassium  = potassiumData[indexVal];
    indexVal++;
  }
  // 2️⃣ Generate future simulated data
  else {
    nitrogen   = random(8, 20);
    phosphorus = random(5, 15);
    potassium  = random(7, 18);
  }

  // Send to website
  sendToServer(nitrogen, phosphorus, potassium);

  delay(5000); // every 5 seconds
}

// =====================
// SEND DATA FUNCTION
// =====================
void sendToServer(int n, int p, int k) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // 🔴 CHANGE THIS URL
    http.begin("http://YOUR_SERVER_IP/npk-api.php");
    http.addHeader("Content-Type", "application/json");

    String payload = "{";
    payload += "\"sensor_id\":\"ESP32_01\",";
    payload += "\"nitrogen\":" + String(n) + ",";
    payload += "\"phosphorus\":" + String(p) + ",";
    payload += "\"potassium\":" + String(k);
    payload += "}";

    int responseCode = http.POST(payload);

    Serial.println("Sent → " + payload);
    Serial.print("Server Response: ");
    Serial.println(responseCode);

    http.end();
  }
}
