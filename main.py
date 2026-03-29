import cv2
import mediapipe as mp
import pyautogui
import hand as htm
import math
import time
import decor
from draw_mode import DrawMode


mode = 0
cooldown = 0
currentGesture = None
modeGestureCounter = 0
requiredFrames = 12   # phải giữ 12 frame mới đổi mode



#set độ rộng của Frame
wScr, hScr = pyautogui.size()
wWin = int(wScr * 0.7)
hWin = int(hScr * 0.7)
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Image", wWin, hWin)


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
detector = htm.handDetector(detectionCon=0.55)

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

zoom = 1.0
minZoom = 1.0
maxZoom = 3.0
mode = 0
cooldown = 0
prevX, prevY = 0, 0
smoothening = 5
prevDistance = None
prevPinchDistance = None
prevTwoHandDistance = None
screenW, screenH = pyautogui.size()

pTime = 0
#Vẽ
drawColor = (255, 0, 255)
brushThickness = 8
eraserThickness = 40
xp, yp = 0, 0
canvas = None
hCam, wCam = 480, 640  # hoặc lấy từ frame
drawMode = None

while True:
    #Lấy FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if cTime != pTime else 0
    pTime = cTime
    success, img = cap.read()
    img = cv2.flip(img, 1)
    if canvas is None:
        canvas = img.copy() * 0

    #Tìm tay
    img = detector.findHands(img)



    hCam, wCam = img.shape[:2]
    if drawMode is None:
        drawMode = DrawMode(wCam, hCam)



    if detector.results and detector.results.multi_hand_landmarks:
        lmList = detector.findPosition(img, draw=False)
        detector.lmList = lmList
        print(lmList)
        if len(lmList) == 21:
            fingers = detector.fingersUp()

            if fingers == currentGesture:
                gestureCounter += 1
            else:
                currentGesture = fingers
                gestureCounter = 1

                # ===== THOÁT MODE (nắm tay giữ lâu) =====
            if fingers == [0, 0, 0, 0, 0] and gestureCounter > 20:
                mode = 0
                cooldown = 20

                # ===== CHỈ CHO ĐỔI MODE KHI ĐANG Ở MODE 0 =====
            if mode == 0 and cooldown == 0:

                if fingers == [1, 0, 0, 0, 0] and gestureCounter > requiredFrames:
                    mode = 0
                    cooldown = 25

                elif fingers == [0, 1, 1, 0, 0] and gestureCounter > requiredFrames:
                    mode = 1
                    cooldown = 25

                elif fingers == [0, 1, 1, 1, 0] and gestureCounter > requiredFrames:
                    mode = 2
                    cooldown = 25

                elif fingers == [1, 1, 1, 1, 1] and gestureCounter > requiredFrames:
                    mode = 3
                    cooldown = 25
    if cooldown > 0:
        cooldown -= 1
    if mode == 0:
        # Nếu có 2 tay → ưu tiên zoom 2 tay
        if detector.results.multi_hand_landmarks and len(detector.results.multi_hand_landmarks) == 2:
            img, zoom, prevTwoHandDistance = detector.two_hand_zoom(
                img, zoom, prevTwoHandDistance)
            prevPinchDistance = None

        # Nếu chỉ có 1 tay → dùng pinch
        else:
            img, zoom, prevPinchDistance = detector.one_hand_pinch_zoom(
                img, zoom, prevPinchDistance)
            prevTwoHandDistance = None

        img = detector.apply_zoom(img, zoom)
    elif mode == 1:


        hCam, wCam = img.shape[:2]  # kích thước camera
        wScr, hScr = pyautogui.size()  # kích thước màn hình

        if detector.results and detector.results.multi_hand_landmarks:

            lmList = detector.findPosition(img, draw=False)
            detector.lmList = lmList

            if len(lmList) == 21:

                fingers = detector.fingersUp()

                # Lấy đầu ngón trỏ
                x1, y1 = lmList[8][1], lmList[8][2]

                # ===== CHUYỂN TỌA ĐỘ =====
                xScreen = x1 * wScr / wCam
                yScreen = y1 * hScr / hCam

                # ===== LÀM MƯỢT =====
                currX = prevX + (xScreen - prevX) / smoothening
                currY = prevY + (yScreen - prevY) / smoothening

                # ===== DI CHUYỂN =====
                if fingers == [0, 1, 0, 0, 0]:
                    pyautogui.moveTo(currX, currY)

                prevX, prevY = currX, currY

                # ===== CLICK BẰNG PINCH =====
                xThumb, yThumb = lmList[4][1], lmList[4][2]
                distance = math.hypot(x1 - xThumb, y1 - yThumb)

                if distance < 25:
                    pyautogui.click()
                    time.sleep(0.2)

    elif mode == 2:
        pass

    elif mode == 3:
        img = drawMode.update(img, detector)




    #Vẽ
    imgGray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, canvas)
    #Hiễn decor
    img = decor.draw_hud(img, mode, zoom, fps)
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break


cap.release()
cv2.destroyAllWindows()