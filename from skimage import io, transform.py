from skimage import io,transform
import numpy as np

car = io.imread(r"D:\Dts Bike\Car Img\black-sedan-car-isolated-white-vector\67358.jpg")
rim = io.imread(r"D:\Dts Bike\Rim\sleek-black-alloy-.jpg")

rim_resized = transform.resize(rim, (120, 120), anti_aliasing=True)

# Convert to same data type
rim_resized = (rim_resized * 255).astype(np.uint8)

# Define region to place rim
x, y = 300, 400
car[y:y+120, x:x+120] = rim_resized

io.imsave("car_with_rim_skimage.jpg", car)
