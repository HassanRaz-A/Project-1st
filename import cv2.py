import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

# Global variables
click_x, click_y = -1, -1
car_img = None
rim_img = None

def select_images():
    """Open file dialogs to select car and rim images"""
    root = tk.Tk()
    root.withdraw()
    
    # Select car image
    car_path = filedialog.askopenfilename(title="Select Car Image", filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not car_path:
        print("No car image selected!")
        exit()
    
    # Select rim image
    rim_path = filedialog.askopenfilename(title="Select Rim Image", filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not rim_path:
        print("No rim image selected!")
        exit()
    
    return car_path, rim_path

def mouse_callback(event, x, y, flags, param):
    """Handle mouse clicks for position selection"""
    global click_x, click_y
    if event == cv2.EVENT_LBUTTONDOWN:
        click_x, click_y = x, y
        print(f"Selected position: ({x}, {y})")

def main():
    global car_img, rim_img, click_x, click_y
    
    # Select images through dialog
    car_path, rim_path = select_images()
    
    # Load images
    car_img = cv2.imread(car_path)
    rim_img = cv2.imread(rim_path, cv2.IMREAD_UNCHANGED)
    
    # Check if images loaded properly
    if car_img is None or rim_img is None:
        print("Error loading images!")
        exit()
    
    # Get rim size from user
    rim_size = int(input("Enter rim size in pixels (recommended 100-200): "))
    
    # Create window for position selection
    cv2.namedWindow("Select Rim Position")
    cv2.setMouseCallback("Select Rim Position", mouse_callback)
    
    # Display instructions
    print("\nINSTRUCTIONS:")
    print("1. Click where you want to place the rim center")
    print("2. Press any key when done")
    
    # Display car image and wait for click
    while True:
        cv2.imshow("Select Rim Position", car_img)
        key = cv2.waitKey(1) & 0xFF
        if key != 255 or click_x != -1:
            break
    
    cv2.destroyAllWindows()
    
    # Resize rim
    rim_resized = cv2.resize(rim_img, (rim_size, rim_size))
    
    # Calculate placement area (center to top-left conversion)
    y_start = click_y - rim_size//2
    x_start = click_x - rim_size//2
    
    # Ensure placement stays within image boundaries
    y_start = max(0, y_start)
    x_start = max(0, x_start)
    y_end = min(car_img.shape[0], y_start + rim_size)
    x_end = min(car_img.shape[1], x_start + rim_size)
    
    # Adjust rim size if near edges
    actual_height = y_end - y_start
    actual_width = x_end - x_start
    rim_final = cv2.resize(rim_resized, (actual_width, actual_height))
    
    # Alpha blending for transparent PNGs
    if rim_final.shape[2] == 4:
        alpha = rim_final[:, :, 3] / 255.0
        for c in range(3):
            car_img[y_start:y_end, x_start:x_end, c] = \
                car_img[y_start:y_end, x_start:x_end, c] * (1 - alpha) + \
                rim_final[:, :, c] * alpha
    else:
        car_img[y_start:y_end, x_start:x_end] = rim_final
    
    # Show and save result
    cv2.imshow("Final Result", car_img)
    cv2.waitKey(0)
    output_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
    if output_path:
        cv2.imwrite(output_path, car_img)
        print(f"Image saved to: {output_path}")
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()