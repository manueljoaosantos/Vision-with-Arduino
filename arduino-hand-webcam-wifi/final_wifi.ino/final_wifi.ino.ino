#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include "credentials.h"  // Define ssid e password

// Configurações do display OLED
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Servidor HTTP
ESP8266WebServer server(80);

// Nomes dos dedos
const char* dedos[5] = {"Polegar", "Indicador", "Medio", "Anelar", "Mindinho"};

// Função para mostrar texto no OLED
void displayFingers(const String &stateStr) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);

  for (int i = 0; i < 5; i++) {
    if (i < stateStr.length()) {
      String status = (stateStr[i] == '1') ? "ABERTO" : "FECHADO";
      display.println(String(dedos[i]) + ": " + status);
    }
  }
  display.display();
}

// Função para tratar pedidos à rota /update
void handleUpdate() {
  if (server.hasArg("valor")) {
    String val = server.arg("valor");
    Serial.print("Recebido: ");
    Serial.println(val);
    displayFingers(val);
    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "Faltou o parametro 'valor'");
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Inicializa o OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("Erro: OLED nao encontrado"));
    for (;;);
  }
  display.clearDisplay();
  display.display();

  // Conecta ao WiFi
  Serial.print("A ligar ao WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi ligado!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0,0);
  display.println("IP: " + WiFi.localIP().toString());
  display.display();

  // Configura a rota /update
  server.on("/update", handleUpdate);
  server.begin();
  Serial.println("Servidor HTTP iniciado.");
}

void loop() {
  server.handleClient();  // processa pedidos HTTP
}
