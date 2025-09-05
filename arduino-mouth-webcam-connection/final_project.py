import cv2             # OpenCV → processamento de imagem e acesso à webcam
import mediapipe as mp # MediaPipe → detecção de landmarks faciais (FaceMesh)
import serial          # PySerial → comunicação entre Python e Arduino
import os              # OS → manipulação de variáveis de ambiente
import math            # Math → funções matemáticas (ex.: sqrt)

# 🔇 Silenciar logs do MediaPipe/TFLite
# Ajusta o nível de log da biblioteca TFLite para evitar mensagens no terminal.
# 0 = mostra tudo, 1 = INFO, 2 = WARNING, 3 = ERROR
os.environ["GLOG_minloglevel"] = "2"

# Inicializa a webcam
# 0 → primeira câmera conectada (normalmente a webcam principal do PC)
webcam = cv2.VideoCapture(0)

# Ajusta a resolução da webcam para 640x480 (boa para desempenho e precisão suficiente)
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Inicializa módulos do MediaPipe
mp_face = mp.solutions.face_mesh      # FaceMesh → detecção de pontos (landmarks) do rosto
mp_drawing = mp.solutions.drawing_utils  # Ferramentas de desenho (se quiser desenhar a malha facial)

# Inicializa comunicação com Arduino
# Porta COM5 (muda conforme o teu computador) a 9600 baud
arduino = serial.Serial('COM5', 9600)

# Cria o objeto FaceMesh, responsável por detectar landmarks faciais
# max_num_faces = 1 → só processa uma face por frame
# min_detection_confidence → confiança mínima para detectar a face
# min_tracking_confidence → confiança mínima para continuar a acompanhar a face detetada
with mp_face.FaceMesh(
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:

    # Loop principal → processa frame a frame da webcam
    while True:
        # Captura um frame da webcam
        control, frame = webcam.read()
        if not control:
            print("Não foi possível capturar frame da webcam.")
            break  # Se não conseguir capturar imagem, sai do loop

        # Converte o frame de BGR (padrão OpenCV) para RGB (padrão MediaPipe)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Processa a imagem RGB para detetar os landmarks faciais
        result = face_mesh.process(rgb)

        # Obtém dimensões da imagem para converter coordenadas normalizadas para pixels
        height, width, channels = frame.shape

        # Se alguma face foi detetada
        if result.multi_face_landmarks:
            # Itera sobre todas as faces detetadas (neste caso, só 1)
            for face_landmarks in result.multi_face_landmarks:

                # Obtém os pontos (landmarks) dos cantos da boca
                # ID 78 → canto direito interno da boca
                # ID 308 → canto esquerdo interno da boca
                right_corner = face_landmarks.landmark[78]
                left_corner = face_landmarks.landmark[308]

                # Converte coordenadas normalizadas (0 a 1) para coordenadas de pixel
                x_right = int(right_corner.x * width)
                y_right = int(right_corner.y * height)
                x_left = int(left_corner.x * width)
                y_left = int(left_corner.y * height)

                # Desenha círculos vermelhos (raio 4) nos cantos da boca para visualização
                cv2.circle(frame, (x_right, y_right), 4, (0, 0, 255), -1)
                cv2.circle(frame, (x_left, y_left), 4, (0, 0, 255), -1)

                # Calcula a distância entre os dois cantos da boca usando teorema de Pitágoras
                distance = math.sqrt((x_right - x_left) ** 2 + (y_right - y_left) ** 2)
                print("Distância entre cantos da boca:", distance)

                # Envia o valor da distância (como string com newline) para o Arduino
                arduino.write(f"{distance}\n".encode('utf-8'))

                # Exemplo de lógica: enviar comando "A" ou "B" baseado na abertura da boca
                # Se a boca estiver mais aberta (distância > 38) envia "A"
                if distance > 37:
                    arduino.write(b"A")
                # Se a boca estiver mais fechada (distância < 36) envia "B"
                elif distance < 35:
                    arduino.write(b"B")

        # Mostra o frame processado numa janela chamada "FaceMesh"
        cv2.imshow("FaceMesh", frame)

        # Lê teclado: sai se pressionar 'q' ou 'ESC' (código 27)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

# Libera os recursos no final
webcam.release()         # Liberta a webcam
cv2.destroyAllWindows()  # Fecha janelas do OpenCV
arduino.close()          # Fecha a comunicação serial com o Arduino
