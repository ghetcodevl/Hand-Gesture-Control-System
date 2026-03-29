import mediapipe as mp
import cv2
import time
import math
class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            model_complexity=1,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):

        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        return lmList

    def fingersUp(self):
        fingers = []

        # Kiểm tra có lmList chưa
        if not hasattr(self, "lmList") or len(self.lmList) != 21:
            return []

        # Ngón cái (so trục X)
        if self.lmList[4][1] > self.lmList[3][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 ngón còn lại (so trục Y)
        tipIds = [8, 12, 16, 20]

        for id in tipIds:
            if self.lmList[id][2] < self.lmList[id - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def apply_zoom(self, img, zoom):
        h, w = img.shape[:2]

        if zoom <= 1:
            return img

        new_w = int(w / zoom)
        new_h = int(h / zoom)

        x1 = max((w - new_w) // 2, 0)
        y1 = max((h - new_h) // 2, 0)

        cropped = img[y1:y1 + new_h, x1:x1 + new_w]

        if cropped.size == 0:
            return img

        return cv2.resize(cropped, (w, h))

    def one_hand_pinch_zoom(self, img, zoom, prevDistance):
        lmList = self.findPosition(img, handNo=0,  draw=False)

        if len(lmList) == 21:
            x1, y1 = lmList[4][1], lmList[4][2]  # ngón cái
            x2, y2 = lmList[8][1], lmList[8][2]  # ngón trỏ

            distance = math.hypot(x2 - x1, y2 - y1)

            cv2.circle(img, (x1, y1), 8, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 8, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)

            if prevDistance is not None:
                diff = distance - prevDistance
                zoom += diff * 0.004
                zoom = max(1.0, min(3.5, zoom))

            prevDistance = distance
        else:
            prevDistance = None

        return img, zoom, prevDistance

    def two_hand_zoom(self, img, zoom, prevDistance):
        if self.results.multi_hand_landmarks and len(self.results.multi_hand_landmarks) == 2:

            h, w, c = img.shape
            centers = []

            for handLms in self.results.multi_hand_landmarks:
                cx = int(handLms.landmark[9].x * w)
                cy = int(handLms.landmark[9].y * h)
                centers.append((cx, cy))
                cv2.circle(img, (cx, cy), 8, (0, 255, 0), cv2.FILLED)

            (x1, y1), (x2, y2) = centers
            distance = math.hypot(x2 - x1, y2 - y1)

            if prevDistance is not None:
                diff = distance - prevDistance
                zoom += diff * 0.003
                zoom = max(1.0, min(3.5, zoom))

            prevDistance = distance
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

        else:
            prevDistance = None

        return img, zoom, prevDistance
def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(1)
    detector = handDetector()
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) != 0:
            print(lmList[4])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()