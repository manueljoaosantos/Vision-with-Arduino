#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include "credentials.h"  // inclui ssid e password

// Configurações do display OLED
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Servidor HTTP
ESP8266WebServer server(80);

// Função para mostrar texto no OLED
void displayMessage(const String &msg) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println(msg);
  display.display();
}

// Função para tratar pedidos à rota /update
void handleUpdate() {
  if (server.hasArg("valor")) {
    String val = server.arg("valor");
    Serial.print("Recebido: ");
    Serial.println(val);
    displayMessage("Valor: " + val);
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
    for (;;); // trava aqui
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
  displayMessage("IP: " + WiFi.localIP().toString());

  // Configura a rota /update
  server.on("/update", handleUpdate);
  server.begin();
  Serial.println("Servidor HTTP iniciado.");
}

void loop() {
  server.handleClient();  // processa pedidos HTTP
}
