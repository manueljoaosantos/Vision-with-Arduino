#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// Credenciais WiFi
#include "credentials.h" // Defina ssid e password aqui

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
ESP8266WebServer server(80);

// Valor recebido do Python (0 a 100)
int handValue = 0;

// Função para desenhar barra horizontal e “confete”
void drawHand(int value) {
  display.clearDisplay();

  // Barra horizontal
  int barWidth = map(value, 0, 100, 0, SCREEN_WIDTH - 10);
  display.fillRect(5, SCREEN_HEIGHT/2 - 5, barWidth, 10, WHITE);

  // “Confete” aleatório
  for (int i = 0; i < 20; i++) {
    int x = random(SCREEN_WIDTH);
    int y = random(SCREEN_HEIGHT);
    display.drawPixel(x, y, WHITE);
  }

  // Texto
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(5, 5);
  display.print("Hand: ");
  display.print(value);

  display.display();
}

// Rota HTTP para atualizar valor
void handleUpdate() {
  if (server.hasArg("valor")) {
    handValue = server.arg("valor").toInt();
    Serial.print("Recebido: ");
    Serial.println(handValue);
    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "Faltou o parametro 'valor'");
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Inicializa OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("Erro: OLED nao encontrado"));
    for (;;);
  }
  display.clearDisplay();
  display.display();

  // Conecta WiFi
  Serial.print("Ligando ao WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // Rota /update
  server.on("/update", handleUpdate);
  server.begin();
  Serial.println("Servidor HTTP iniciado.");
}

void loop() {
  server.handleClient();    // Processa pedidos HTTP
  drawHand(handValue);      // Desenha valor recebido
  delay(100);               // Atualiza a cada 100ms
}
