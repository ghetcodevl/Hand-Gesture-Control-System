import cv2

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print("Camera index:", i)
        cap.release()



import cv2

capLaptop = cv2.VideoCapture(0, cv2.CAP_DSHOW)
capPhone  = cv2.VideoCapture(2, cv2.CAP_DSHOW)

while True:
    ret1, img1 = capLaptop.read()
    ret2, img2 = capPhone.read()

    if ret1:
        cv2.imshow("Laptop Cam", img1)
    if ret2:
        cv2.imshow("Phone Cam", img2)

    if cv2.waitKey(1) & 0xFF == 27:
        break

capLaptop.release()
capPhone.release()
cv2.destroyAllWindows()