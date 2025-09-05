import cv2
import os

# 🔇 Silenciar logs do MediaPipe/TFLite
# 0 = mostrar todos os logs, 1 = INFO, 2 = WARNING, 3 = ERROR
os.environ["GLOG_minloglevel"] = "2"

import mediapipe as mp  # Biblioteca para detecção de face, mãos, pose, etc.

# Inicializa a webcam (0 = primeira câmera conectada)
webcam = cv2.VideoCapture(0)

# Define a resolução da webcam (640x480) para melhorar FPS e desempenho
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Inicializa módulos do MediaPipe
mp_face = mp.solutions.face_mesh       # FaceMesh: detecção de landmarks faciais
mp_drawing = mp.solutions.drawing_utils  # Utilitários para desenhar landmarks e conexões

# Cria o objeto FaceMesh com configurações
with mp_face.FaceMesh(
    max_num_faces=1,                  # Número máximo de faces a detectar
    min_detection_confidence=0.5,     # Confiança mínima para detecção
    min_tracking_confidence=0.5       # Confiança mínima para tracking
) as face_mesh:

    # Loop principal para capturar frames da webcam
    while True:
        control, frame = webcam.read()  # Lê frame da webcam
        if not control:
            print("Não foi possível capturar frame da webcam.")
            break

        # Converte o frame BGR (OpenCV) para RGB (MediaPipe requer RGB)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Processa o frame para detectar landmarks faciais
        result = face_mesh.process(rgb)

        # Se alguma face foi detectada
        if result.multi_face_landmarks:
            for face_landmarks in result.multi_face_landmarks:
                # Desenha landmarks e conexões no frame
                mp_drawing.draw_landmarks(
                    frame,
                    face_landmarks,
                    mp_face.FACEMESH_CONTOURS,  # Desenha contornos principais do rosto
                    landmark_drawing_spec=mp_drawing.DrawingSpec(
                        color=(0, 255, 255),      # Cor dos pontos (amarelo-ciano)
                        thickness=1,               # Espessura dos pontos
                        circle_radius=1            # Tamanho dos círculos
                    ),
                    connection_drawing_spec=mp_drawing.DrawingSpec(
                        color=(255, 0, 255),      # Cor das conexões (magenta)
                        thickness=1               # Espessura das linhas
                    )
                )

        # Mostra o frame resultante em uma janela chamada "FaceMesh"
        cv2.imshow("FaceMesh", frame)

        # Espera 1ms por tecla; sai se 'q' ou 'ESC' forem pressionadas
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 27 = ESC
            break

# Libera a webcam e fecha todas as janelas abertas
webcam.release()
cv2.destroyAllWindows()
