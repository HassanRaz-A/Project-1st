import cv2
import numpy as np
import os
from tkinter import filedialog, Tk, Button, Label, Scale, HORIZONTAL
from PIL import Image, ImageTk

# === FOLDERS ===
rim_folder = r"D:\Dts Bike\Script\rims"
rim_images = []
rim_index = 0

# === GLOBAL VARIABLES ===
car_img = None
rim_img = None
tyre_positions = []
adjusted_positions = []
rim_scale = 0.65  # default scale
canvas_img = None
window = None
label = None
selected_rim_idx = -1  # For manual dragging

# === LOAD RIM IMAGES ===
def load_rims():
    global rim_images
    if not os.path.exists(rim_folder):
        os.makedirs(rim_folder)
    for file in os.listdir(rim_folder):
        if file.lower().endswith(".png"):
            img = cv2.imread(os.path.join(rim_folder, file), cv2.IMREAD_UNCHANGED)
            if img is not None:
                rim_images.append((file, img))
    if rim_images:
        print(f"✅ Loaded {len(rim_images)} rims.")

# === DETECT TYRES ===
def detect_tyres(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 7)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100,
                               param1=100, param2=30, minRadius=30, maxRadius=100)
    coords = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for (x, y, r) in circles[0, :]:
            coords.append([x, y, r])
    return coords

# === OVERLAY RIM WITH ADJUSTMENTS ===
def overlay_rim(image, rim, positions):
    output = image.copy()
    for idx, (x, y, r) in enumerate(positions):
        try:
            rim_radius = int(r * rim_scale)
            rim_resized = cv2.resize(rim, (2 * rim_radius, 2 * rim_radius))

            if rim_resized.shape[2] == 4:
                mask = rim_resized[:, :, 3]
                rim_rgb = rim_resized[:, :, :3]
            else:
                rim_rgb = rim_resized
                mask = np.ones((2 * rim_radius, 2 * rim_radius), dtype=np.uint8) * 255
                cv2.circle(mask, (rim_radius, rim_radius), rim_radius, 255, -1)

            y1, y2 = y - rim_radius, y + rim_radius
            x1, x2 = x - rim_radius, x + rim_radius

            if y1 < 0 or y2 > output.shape[0] or x1 < 0 or x2 > output.shape[1]:
                continue

            for c in range(3):
                output[y1:y2, x1:x2, c] = (
                    rim_rgb[:, :, c] * (mask / 255.0) +
                    output[y1:y2, x1:x2, c] * (1.0 - (mask / 255.0))
                )
        except Exception as e:
            print(f"⚠️ Error overlaying rim at index {idx}: {e}")
    return output

# === UPDATE DISPLAY ===
def update_display():
    global canvas_img, car_img, rim_img, label
    if car_img is None or rim_img is None:
        return
    preview = overlay_rim(car_img.copy(), rim_img, adjusted_positions)
    rgb = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    canvas_img = ImageTk.PhotoImage(image=pil_img)
    label.configure(image=canvas_img)
    label.image = canvas_img

# === LOAD CAR IMAGE ===
def load_car():
    global car_img, tyre_positions, adjusted_positions
    file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png")])
    if file_path:
        car_img = cv2.imread(file_path)
        tyre_positions = detect_tyres(car_img)
        adjusted_positions.clear()
        adjusted_positions.extend([list(pos) for pos in tyre_positions])
        update_display()

# === NEXT / PREV RIM ===
def next_rim():
    global rim_index, rim_img
    if rim_images:
        rim_index = (rim_index + 1) % len(rim_images)
        rim_img = rim_images[rim_index][1]
        update_display()

def prev_rim():
    global rim_index, rim_img
    if rim_images:
        rim_index = (rim_index - 1) % len(rim_images)
        rim_img = rim_images[rim_index][1]
        update_display()

# === SAVE FINAL IMAGE ===
def save_output():
    if car_img is not None and rim_img is not None:
        result = overlay_rim(car_img, rim_img, adjusted_positions)
        save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png")])
        if save_path:
            cv2.imwrite(save_path, result)
            print(f"✅ Image saved to: {save_path}")

# === RIM SCALE SLIDER ===
def scale_changed(val):
    global rim_scale
    rim_scale = float(val) / 100.0
    update_display()

# === MOUSE DRAG FOR POSITIONING ===
def on_mouse_drag(event):
    global selected_rim_idx
    if selected_rim_idx != -1 and adjusted_positions:
        adjusted_positions[selected_rim_idx][0] = event.x
        adjusted_positions[selected_rim_idx][1] = event.y
        update_display()

def on_mouse_click(event):
    global selected_rim_idx
    min_dist = float('inf')
    selected_rim_idx = -1
    for i, (x, y, _) in enumerate(adjusted_positions):
        dist = (x - event.x)**2 + (y - event.y)**2
        if dist < min_dist and dist < 10000:  # within ~100px
            min_dist = dist
            selected_rim_idx = i

# === MAIN GUI ===
def main_gui():
    global window, label
    load_rims()

    window = Tk()
    window.title("🔧 2D Rim Fitter (Drag + Resize)")
    window.geometry("950x700")

    Button(window, text="📷 Load Car", command=load_car).pack()
    Button(window, text="⏪ Prev Rim", command=prev_rim).pack()
    Button(window, text="Next Rim ⏩", command=next_rim).pack()
    Button(window, text="💾 Save Image", command=save_output).pack()

    Label(window, text="🛞 Rim Size (%)").pack()
    scale = Scale(window, from_=40, to=100, orient=HORIZONTAL, command=scale_changed)
    scale.set(int(rim_scale * 100))
    scale.pack()

    label = Label(window)
    label.pack()
    label.bind("<Button-1>", on_mouse_click)
    label.bind("<B1-Motion>", on_mouse_drag)

    window.mainloop()

# === LAUNCH ===
if __name__ == "__main__":
    main_gui()
