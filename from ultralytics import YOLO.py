from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")
img = cv2.imread("car.jpg")

results = model(img)

for r in results:
    for box in r.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        if box.cls[0] == 3:  # If 'car wheel' class
            # Paste your rim here
            rim = cv2.imread("rim.png")
            rim_resized = cv2.resize(rim, (x2 - x1, y2 - y1))
            img[y1:y2, x1:x2] = rim_resized

cv2.imwrite("car_with_rim_yolo.jpg", img)
