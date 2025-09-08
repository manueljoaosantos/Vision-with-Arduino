import cv2
import mediapipe as mp
import os
import math
import requests  # <--- mudou de websocket para requests
import time

# 🔇 Silenciar logs do MediaPipe/TFLite
os.environ["GLOG_minloglevel"] = "2"

# Configura IP do NodeMCU
NODEMCU_IP = "192.168.1.142"  # substitui pelo IP do NodeMCU

# Inicializa webcam
webcam = cv2.VideoCapture(0)
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Inicializa MediaPipe FaceMesh
mp_face = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

with mp_face.FaceMesh(
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:

    while True:
        ret, frame = webcam.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb)
        height, width, _ = frame.shape

        if result.multi_face_landmarks:
            for face_landmarks in result.multi_face_landmarks:
                right_corner = face_landmarks.landmark[78]
                left_corner = face_landmarks.landmark[308]
                x_right = int(right_corner.x * width)
                y_right = int(right_corner.y * height)
                x_left = int(left_corner.x * width)
                y_left = int(left_corner.y * height)

                # Calcula distância
                distance = math.sqrt((x_right - x_left) ** 2 + (y_right - y_left) ** 2)
                print("Distância entre cantos da boca:", distance)

                # Envia via HTTP GET para o ESP
                try:
                    r = requests.get(f"http://{NODEMCU_IP}/update", params={"valor": str(distance)}, timeout=0.5)
                    if r.status_code != 200:
                        print("Erro ao enviar para ESP:", r.status_code)
                except requests.exceptions.RequestException as e:
                    print("Falha na comunicação HTTP:", e)

                # Desenho
                cv2.circle(frame, (x_right, y_right), 4, (0, 0, 255), -1)
                cv2.circle(frame, (x_left, y_left), 4, (0, 0, 255), -1)

        cv2.imshow("FaceMesh", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

# Libera recursos
webcam.release()
cv2.destroyAllWindows()
