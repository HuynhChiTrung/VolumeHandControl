import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from tkinter import *  
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def main_program() :
    ################################
    wCam, hCam = 640, 480
    ################################

    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    pTime = 0

    detector = htm.handDetector(detectionCon=0.7) # độ tin cậy phát hiện bàn tay 0.7

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    # volume.GetMute()
    # volume.GetMasterVolumeLevel()
    volRange = volume.GetVolumeRange() # phạm vi âm lượng
    minVol = volRange[0]    # lấy giá trị max và min 
    maxVol = volRange[1]
    vol = 0
    volBar = 400
    volPer = 0
    colorVol = (255, 0, 0)
    while True:
        success, img = cap.read()
        img = detector.findHands(img) # tìm bàn tay
        lmList, bbox = detector.findPosition(img, draw=True)# đẩy ra các vị trí điểm bàn tay
        # sử dụng lmList để có diểm bàn tay mới bắt đầu làm 
        if len(lmList) != 0:  # bắt bàn tay có giá trị, giấu tay đi thì giá trị rỗng
            # print(lmList[4], lmList[8])

        # Filter based on size
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
            # print(area)
            if 250 < area < 1000:

                # Find Distance between index and Thumb
                length, img, lineInfo = detector.findDistance(4, 8, img)
                # print(length)

                # Convert Volume
                volBar = np.interp(length, [10, 250], [400, 150])
                volPer = np.interp(length, [10, 250], [0, 100])

                # Reduce Resolution to make it smoother
                smoothness = 1
                volPer = smoothness * round(volPer / smoothness)

                # Check fingers up
                fingers = detector.fingersUp()
                # print(fingers)

                # If pinky is down set volume
                if not fingers[4]:
                    volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                    colorVol = (0, 255, 0)
                else:
                    colorVol = (255, 0, 0)

        # vẽ thanh âm lượng tượng trưng khi run
        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)  # hình chữ nhật (điểm bắt đầu - kết thúc) - màu - độ dày 
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
        # show % volume
        cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                    1, (255, 0, 0), 3)
        cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
        cv2.putText(img, f'Vol Set: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX,
                    1, colorVol, 3)

        # định dạng chữ fps trên màn hình video
        cTime = time.time() # trả về số giây, vào thời điểm bắt đầu thời gian
        fps = 1 / (cTime - pTime) # tính fps Frames per second - chỉ số khung hình trên mỗi giây
        pTime = cTime
        # show fps lên màn hình
        cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                    1, (255, 0, 0), 3)

        cv2.imshow("Img", img)
        # Chờ 1ms và kiểm tra phím nhấn
        key = cv2.waitKey(1)

        # Nếu phím 'q' được nhấn, thoát khỏi vòng lặp
        if key == ord('q'):
            break

    # Giải phóng tài nguyên và đóng cửa sổ
    cap.release()
    cv2.destroyAllWindows()

frm = Tk()
frm.geometry("1202x669")
bg = PhotoImage(file = r'background.png')
label1 = Label(frm, image = bg)
label1.place(x = 0, y = 0)
frm.title("Image Processing Project")
btn_Start = Button(frm, text="START PROGRAM", font=("Consolas",14,"bold"),bg="yellow",fg="black",command=main_program)
btn_Start.place(x=500,y=500)
frm.mainloop()