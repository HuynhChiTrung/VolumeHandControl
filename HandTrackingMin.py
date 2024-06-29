import cv2
import mediapipe as mp
import time
# FILE BẮT 2 TAY TỪ CAM DO CHƯA CHỈNH ĐỂ TEST VÀ LÀM 
# 1 webcam id mặc định 0 còn 2 thì chưa biết (1-2 tùy chỉnh cam bật)
cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0

# bắt cam 
while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    # print(results.multi_hand_landmarks)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                print(id, cx, cy)
                # if id == 4:
                cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    # viết ra FPS hiển thị trên màn hình chạy
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    # định dạng chữ fps trên màn hình     
    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 255), 3)

    cv2.imshow("Image", img)
     # Chờ 1ms và kiểm tra phím nhấn
    key = cv2.waitKey(1)

    # Nếu phím 'q' được nhấn, thoát khỏi vòng lặp
    if key == ord('q'):
        break

# Giải phóng tài nguyên và đóng cửa sổ
cap.release()
cv2.destroyAllWindows()