import cv2
import time
import numpy as np
import HandTrackingModule as htm
from tkinter import *
from PIL import Image, ImageTk
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


def main_program(video_label):
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
    volRange = volume.GetVolumeRange() # phạm vi âm lượng
    minVol = volRange[0]    # lấy giá trị max và min 
    maxVol = volRange[1]
    vol = 0
    volBar = 400
    volPer = 0
    colorVol = (255, 0, 0)

    def update_frame():
        nonlocal volBar, volPer, colorVol, pTime
        success, img = cap.read()
        if not success:
            return

        img = detector.findHands(img) # tìm bàn tay
        lmList, bbox = detector.findPosition(img, draw=True)# đẩy ra các vị trí điểm bàn tay

        if len(lmList) != 0:  # bắt bàn tay có giá trị, giấu tay đi thì giá trị rỗng
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
            if 250 < area < 1000:
                length, img, lineInfo = detector.findDistance(4, 8, img)

                volBar = np.interp(length, [10, 250], [400, 150])
                volPer = np.interp(length, [10, 250], [0, 100])
                volPer = round(volPer)

                fingers = detector.fingersUp()
                if not fingers[4]:
                    volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                    colorVol = (0, 255, 0)
                else:
                    colorVol = (255, 0, 0)

        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
        cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
        cv2.putText(img, f'Vol Set: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX, 1, colorVol, 3)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)

        video_label.imgtk = img_tk
        video_label.configure(image=img_tk)
        video_label.after(10, update_frame)
       
   
    update_frame()
    
def show_video_label():
    video_label.place(x=250, y=100)  # Hiển thị video label
    btn_exit.place(x=550, y=600)  # Hiển thị nút EXIT
    main_program(video_label)  # Bắt đầu chương trình chính
    btn_start.place_forget() 
    
def exit_program():
    video_label.place_forget()  # Ẩn video label
    bg_label.place(x=0, y=0)    # Hiển thị background label
    btn_start.place(x=550, y=600)  # Hiển thị nút START
    btn_exit.place_forget() 

frm = Tk()
frm.geometry("1202x669")
bg_img = ImageTk.PhotoImage(file='background.png')
bg_label = Label(frm, image=bg_img)
bg_label.place(x=0, y=0)
frm.title("Image Processing Project")

video_label = Label(frm)
video_label.place(x=250, y=100)  

btn_start = Button(frm, text="START", font=("Consolas", 14, "bold"),
                   bg="yellow", fg="black", command=show_video_label)
btn_start.place(x=550, y=600)

btn_exit = Button(frm, text="EXIT", font=("Consolas", 14, "bold"),
                   bg="red", fg="black", command=exit_program)

#btn_exit.place(x=550, y=600)

frm.mainloop()