import cv2
def draw_hud(img, mode, zoom, fps):

    h, w = img.shape[:2]

    # ====== Thanh nền trên ======
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (w, 90), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)

    # ====== Hiển thị MODE ======
    mode_names = ["HOME", "MOUSE", "PLAY", "DRAW"]
    cv2.putText(img, f"MODE: {mode_names[mode]}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2, (0, 150, 150), 3)

    # ====== FPS ======
    cv2.putText(img, f"FPS: {int(fps)}",
                (w - 200, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 150, 0), 2)

    # ====== Zoom Bar ======
    bar_length = 300
    bar_height = 20
    zoom_percent = min(max((zoom - 1) / 2.5, 0), 1)

    cv2.rectangle(img,
                  (30, 70),
                  (30 + bar_length, 70 + bar_height),
                  (100, 100, 100), 2)

    cv2.rectangle(img,
                  (30, 70),
                  (30 + int(bar_length * zoom_percent), 70 + bar_height),
                  (0, 255, 255), -1)

    return img