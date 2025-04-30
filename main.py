import cv2
import numpy as np
import os

# ========== SETTINGS ==========
cars_folder = r"D:\Dts Bike\Script\car_images"
rims_raw_folder =r"D:\Dts Bike\Script\cleanpng_images"
rims_transparent_folder = r"D:\Dts Bike\Script\rims"
output_folder = "output"

os.makedirs(rims_transparent_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# ========== FUNCTION 1: Convert rim to transparent ==========
def convert_to_transparent(image_path, save_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Failed to load {image_path}")
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, alpha = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)  # Remove white
    b, g, r = cv2.split(image)
    rgba = [b, g, r, alpha]
    transparent = cv2.merge(rgba)
    cv2.imwrite(save_path, transparent)
    print(f"✅ Saved transparent: {save_path}")

# ========== FUNCTION 2: Detect tyres in car ==========
def detect_tyres(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 7)
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=100,
        param1=100,
        param2=30,
        minRadius=30,
        maxRadius=100
    )
    tyre_coords = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for (x, y, r) in circles[0, :]:
            tyre_coords.append((x, y, r))
    return tyre_coords

# ========== FUNCTION 3: Overlay rim on tyres ==========
def overlay_rim(car_img, rim_img, tyres):
    output = car_img.copy()
    for (x, y, r) in tyres:
        try:
            rim_resized = cv2.resize(rim_img, (2*r, 2*r))

            if rim_resized.shape[2] == 4:
                mask = rim_resized[:, :, 3]
                rim_rgb = rim_resized[:, :, :3]
            else:
                rim_rgb = rim_resized
                mask = np.ones((2*r, 2*r), dtype=np.uint8) * 255
                cv2.circle(mask, (r, r), r, 255, -1)

            for c in range(3):
                output[y-r:y+r, x-r:x+r, c] = (
                    rim_rgb[:, :, c] * (mask / 255.0) +
                    output[y-r:y+r, x-r:x+r, c] * (1.0 - (mask / 255.0))
                )
        except Exception as e:
            print(f"⚠️ Skipped a tyre due to error: {e}")
    return output

# ========== STEP 1: Convert all rims ==========
for rim_file in os.listdir(rims_raw_folder):
    if rim_file.lower().endswith((".jpg", ".jpeg", ".png")):
        input_path = os.path.join(rims_raw_folder, rim_file)
        output_path = os.path.join(rims_transparent_folder, os.path.splitext(rim_file)[0] + ".png")
        convert_to_transparent(input_path, output_path)

# ========== STEP 2: Apply all rims on all cars ==========
rim_files = [f for f in os.listdir(rims_transparent_folder) if f.endswith(".png")]
car_files = [f for f in os.listdir(cars_folder) if f.lower().endswith((".jpg", ".png"))]

for car_file in car_files:
    car_path = os.path.join(cars_folder, car_file)
    car_img = cv2.imread(car_path)
    if car_img is None:
        print(f"❌ Could not read {car_file}")
        continue

    tyres = detect_tyres(car_img)
    if not tyres:
        print(f"⚠️ No tyres found in {car_file}")
        continue

    for rim_file in rim_files:
        rim_path = os.path.join(rims_transparent_folder, rim_file)
        rim_img = cv2.imread(rim_path, cv2.IMREAD_UNCHANGED)
        if rim_img is None:
            print(f"❌ Failed to load rim {rim_file}")
            continue

        result = overlay_rim(car_img, rim_img, tyres)
        save_name = f"{os.path.splitext(car_file)[0]}_{os.path.splitext(rim_file)[0]}.png"
        save_path = os.path.join(output_folder, save_name)
        cv2.imwrite(save_path, result)
        print(f"✅ Saved: {save_path}")
