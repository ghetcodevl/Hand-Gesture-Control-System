import cv2

class DrawMode:

    def __init__(self, width, height):
        self.canvas = None
        self.xp, self.yp = 0, 0
        self.brushThickness = 15
        self.eraserThickness = 50
        self.sidebarWidth = 100
        self.colorList = [
            (255, 0, 255),
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (0, 0, 0)
        ]

        self.boxSize = 80
        self.drawColor = self.colorList[0]

        self.width = width
        self.height = height

    def init_canvas(self, img):
        if self.canvas is None:
            self.canvas = img.copy() * 0

    def draw_palette(self, img):

        cv2.rectangle(img, (0, 0),
                      (self.sidebarWidth, self.height),
                      (40, 40, 40), cv2.FILLED)

        boxHeight = 80

        totalHeight = len(self.colorList) * boxHeight
        startY = self.height - totalHeight  # 👈 bắt đầu từ dưới

        for i, color in enumerate(self.colorList):

            y1 = startY + i * boxHeight
            y2 = y1 + boxHeight

            cv2.rectangle(img,
                          (0, y1),
                          (self.sidebarWidth, y2),
                          color,
                          cv2.FILLED)

            if color == self.drawColor:
                cv2.rectangle(img,
                              (0, y1),
                              (self.sidebarWidth, y2),
                              (255, 255, 255),
                              3)

            if color == (0, 0, 0):
                cv2.putText(img, "E",
                            (30, y1 + 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (255, 255, 255), 2)

    def update(self, img, detector):

        self.init_canvas(img)
        self.draw_palette(img)

        if detector.results and detector.results.multi_hand_landmarks:

            lmList = detector.findPosition(img, draw=False)
            detector.lmList = lmList

            if len(lmList) == 21:

                fingers = detector.fingersUp()
                x1, y1 = lmList[8][1], lmList[8][2]

                boxHeight = 80
                totalHeight = len(self.colorList) * boxHeight
                startY = self.height - totalHeight

                # Chọn màu
                if fingers == [0, 1, 1, 0, 0] and x1 < self.sidebarWidth and y1 > startY:
                    index = (y1 - startY) // boxHeight



                    if index < len(self.colorList):
                        self.drawColor = self.colorList[index]

                    self.xp, self.yp = 0, 0

                # Vẽ
                elif fingers == [0,1,0,0,0]:

                    if self.xp == 0 and self.yp == 0:
                        self.xp, self.yp = x1, y1

                    thickness = self.brushThickness
                    if self.drawColor == (0,0,0):
                        thickness = self.eraserThickness

                    cv2.line(self.canvas,
                             (self.xp,self.yp),
                             (x1,y1),
                             self.drawColor,
                             thickness)

                    self.xp, self.yp = x1, y1
                # ===== CLEAR KHI 5 NGÓN KHÉP =====
                elif fingers == [1, 1, 1, 1, 1]:

                    # Lấy đầu các ngón
                    x8, y8 = lmList[8][1], lmList[8][2]
                    x12, y12 = lmList[12][1], lmList[12][2]
                    x16, y16 = lmList[16][1], lmList[16][2]
                    x20, y20 = lmList[20][1], lmList[20][2]

                    # Tính khoảng cách giữa các ngón
                    d1 = abs(x8 - x12)
                    d2 = abs(x12 - x16)
                    d3 = abs(x16 - x20)

                    # Nếu các ngón sát nhau
                    if d1 < 20 and d2 < 20 and d3 < 20:
                        self.canvas = img.copy() * 0
                        self.xp, self.yp = 0, 0
                # Clear
                elif fingers == [1,1,1,1,1]:

                    self.xp, self.yp = 0, 0



        img = cv2.addWeighted(img, 1, self.canvas, 1, 0)

        return img

