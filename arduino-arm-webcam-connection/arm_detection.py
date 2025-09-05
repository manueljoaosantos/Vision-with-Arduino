import cv2             # OpenCV → processamento de imagem e acesso à webcam
import mediapipe as mp # MediaPipe → detecção de landmarks do corpo (Pose)
import serial          # PySerial → comunicação entre Python e Arduino
import os              # OS → manipulação de variáveis de ambiente
import math            # Math → funções matemáticas (ex.: sqrt)

# 🔇 Silenciar logs do MediaPipe/TFLite
# 0 = mostra todos os logs, 1 = INFO, 2 = WARNING, 3 = ERROR
os.environ["GLOG_minloglevel"] = "2"

# Inicializa a webcam
# 0 → primeira câmera conectada
webcam = cv2.VideoCapture(0)
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Inicializa módulos do MediaPipe
mp_pose = mp.solutions.pose  # Pose → detecção de landmarks do corpo

# Inicializa comunicação com Arduino
# Porta COM5 (alterar conforme o computador) a 9600 baud
arduino = serial.Serial('COM5', 9600)

# Função para enviar sinais ao Arduino com base na distância
def send_signal_to_arduino(distance):
    if 0 < distance <= 250:
        arduino.write(b'A')
    elif 250 < distance <= 450:
        arduino.write(b'B')
    elif distance > 450:
        arduino.write(b'C')

# Cria o objeto Pose com configurações
with mp_pose.Pose(
    static_image_mode=False,        # False → modo vídeo
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as pose:
    while True:
        # Captura um frame da webcam
        control, frame = webcam.read()
        if not control:
            print("Não foi possível capturar frame da webcam.")
            break

        # Converte BGR → RGB para MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Processa o frame para detectar landmarks
        result = pose.process(rgb)

        # Obtém dimensões da imagem
        height, width, channels = frame.shape

        # Se algum corpo foi detectado
        if result.pose_landmarks:
            # Pega landmarks do braço
            wrist = result.pose_landmarks.landmark[16]
            elbow = result.pose_landmarks.landmark[14]
            shoulder = result.pose_landmarks.landmark[12]

            # Converte coordenadas normalizadas para pixels
            x_wrist, y_wrist = int(wrist.x * width), int(wrist.y * height)
            x_elbow, y_elbow = int(elbow.x * width), int(elbow.y * height)
            x_shoulder, y_shoulder = int(shoulder.x * width), int(shoulder.y * height)

            # Desenha círculos nos pontos
            cv2.circle(frame, (x_wrist, y_wrist), 20, (0, 0, 255), -1)
            cv2.circle(frame, (x_elbow, y_elbow), 20, (0, 0, 255), -1)
            cv2.circle(frame, (x_shoulder, y_shoulder), 20, (0, 0, 255), -1)

            # Desenha linhas entre os pontos (braço)
            cv2.line(frame, (x_wrist, y_wrist), (x_elbow, y_elbow), (0, 0, 255), 2)
            cv2.line(frame, (x_elbow, y_elbow), (x_shoulder, y_shoulder), (0, 0, 255), 2)

            # Calcula distância entre punho e ombro (aproximação do comprimento do braço)
            distance = math.sqrt((x_shoulder - x_wrist) ** 2 + (y_shoulder - y_wrist) ** 2)
            print("Distância:", distance)

            # Envia sinal ao Arduino
            send_signal_to_arduino(distance)

        # Mostra frame
        cv2.imshow("Pose Detection", frame)

        # Sai com 'q' ou ESC
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

# Liberta recursos
webcam.release()
cv2.destroyAllWindows()
arduino.close()
