import cv2

webcam=cv2.VideoCapture(0)

while (True):
    control,frame=webcam.read()
    cv2.imshow("Result",frame)

    if(cv2.waitKey(1) & 0xFF == ord('q')):
        break
