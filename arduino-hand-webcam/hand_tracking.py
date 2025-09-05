import cv2
import os

# 🔇 Silenciar logs do MediaPipe/TFLite
# 0 = mostra todos os logs, 1 = INFO, 2 = WARNING, 3 = ERROR
os.environ["GLOG_minloglevel"] = "2"

import mediapipe as mp  # Biblioteca para visão computacional (face, mãos, pose, etc.)

# Inicializa a webcam (0 = primeira câmera conectada)
webcam = cv2.VideoCapture(0)

# Define a resolução da webcam para 640x480 (boa relação entre desempenho e qualidade)
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Inicializa módulos do MediaPipe
mp_hands = mp.solutions.hands         # Hands → detecção de landmarks da mão
mp_drawing = mp.solutions.drawing_utils  # Ferramentas para desenhar landmarks e conexões

# Cria o objeto Hands com configurações
with mp_hands.Hands(
    max_num_hands=2,                 # Número máximo de mãos a detectar
    min_detection_confidence=0.5,    # Confiança mínima para detectar a mão
    min_tracking_confidence=0.5      # Confiança mínima para acompanhar a mão
) as hands:

    # Loop principal para capturar frames da webcam
    while True:
        control, frame = webcam.read()  # Lê um frame da webcam
        if not control:
            print("Não foi possível capturar frame da webcam.")
            break

        # Converte o frame BGR (OpenCV) para RGB (MediaPipe usa RGB)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Processa o frame para detectar landmarks da mão
        result = hands.process(rgb)

        # Se alguma mão foi detectada
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Desenha landmarks e conexões no frame
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,  # Desenha conexões principais da mão
                    landmark_drawing_spec=mp_drawing.DrawingSpec(
                        color=(0, 255, 255),    # Cor dos pontos (amarelo-ciano)
                        thickness=1,            # Espessura dos pontos
                        circle_radius=3         # Tamanho dos círculos
                    ),
                    connection_drawing_spec=mp_drawing.DrawingSpec(
                        color=(255, 0, 255),    # Cor das conexões (magenta)
                        thickness=2             # Espessura das linhas
                    )
                )

        # Mostra o frame resultante em uma janela chamada "Hands"
        cv2.imshow("Hands", frame)

        # Espera 1ms por tecla; sai se 'q' ou 'ESC' forem pressionadas
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 27 = ESC
            break

# Libera a webcam e fecha todas as janelas abertas
webcam.release()
cv2.destroyAllWindows()
