import cv2
import os
import mediapipe as mp
import math
import requests

# 🔇 Silenciar logs do MediaPipe/TFLite
os.environ["GLOG_minloglevel"] = "2"

# Configura IP do NodeMCU
NODEMCU_IP = "192.168.1.142"  # substitui pelo IP do NodeMCU
NODEMCU_PORT = 80

# Inicializa webcam
webcam = cv2.VideoCapture(0)
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Inicializa MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Índices dos landmarks para cada dedo
TIP_IDS = [4, 8, 12, 16, 20]   # polegar, indicador, médio, anelar, mindinho
PIP_IDS = [3, 6, 10, 14, 18]   # junta intermediária para comparação

# Cria o objeto Hands
with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:

    while True:
        ret, frame = webcam.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        fingers_state = []  # vai guardar 0 = fechado, 1 = aberto

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Desenha landmarks
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                landmarks = hand_landmarks.landmark

                # Detecta se cada dedo está aberto
                for tip_id, pip_id in zip(TIP_IDS, PIP_IDS):
                    tip_y = landmarks[tip_id].y
                    pip_y = landmarks[pip_id].y
                    # Para polegar, usa eixo x
                    if tip_id == 4:
                        tip_x = landmarks[tip_id].x
                        pip_x = landmarks[pip_id].x
                        fingers_state.append(1 if tip_x < pip_x else 0)
                    else:
                        fingers_state.append(1 if tip_y < pip_y else 0)

        # Converte para string tipo "10101" e envia para Arduino
        if fingers_state:
            state_str = ''.join(map(str, fingers_state))
            try:
                requests.get(f"http://{NODEMCU_IP}/update?valor={state_str}")
            except:
                pass
            print("Dedos:", state_str)

        cv2.imshow("Hands", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

webcam.release()
cv2.destroyAllWindows()
