import cv2
import mediapipe as mp
import math
import requests

NODEMCU_IP = "192.168.1.142"  # IP do NodeMCU

# Inicializa MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    hand_value = 0
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Contagem de dedos abertos (simplificado)
            tips = [4, 8, 12, 16, 20]  # IDs das pontas dos dedos
            open_count = 0
            for tip in tips:
                if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip-2].y:
                    open_count += 1
            hand_value = int(open_count * q20)  # Converte para 0-100

    # Envia para NodeMCU via HTTP
    try:
        requests.get(f"http://{NODEMCU_IP}/update?valor={hand_value}", timeout=0.2)
    except:
        pass

    cv2.imshow("Hands", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
