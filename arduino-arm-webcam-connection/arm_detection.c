#include <Servo.h>  // Biblioteca para controlar motores servo

// Variável para armazenar o dado recebido via Serial
char incomingData;

// Cria objeto servo
Servo servo;

void setup() {
    // Define o pino do Arduino onde o servo está conectado (pino 9)
    servo.attach(9);

    // Inicializa a comunicação serial com baud rate 9600
    Serial.begin(9600);

    // Inicializa o servo na posição central (90°)
    servo.write(90);
}

void loop() {
    // Verifica se há dados disponíveis na porta Serial
    if (Serial.available() > 0) {
        // Lê um caractere enviado pelo Python
        incomingData = Serial.read();

        // Ajusta a posição do servo com base no caractere recebido
        if (incomingData == 'A') {
            servo.write(45);   // Movimenta o servo para 45° (ex.: braço levantado)
        }
        else if (incomingData == 'B') {
            servo.write(90);   // Retorna à posição central (90°)
        }
        else if (incomingData == 'C') {
            servo.write(170);  // Movimenta o servo para 170° (ex.: braço totalmente abaixado)
        }
    }
}
