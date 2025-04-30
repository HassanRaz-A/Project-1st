from PIL import Image

car = Image.open(r"D:\Dts Bike\Car Img\black-sedan-car-isolated-white-vector\67358.jpg").convert("RGBA")
rim = Image.open("D:\Dts Bike\Rim\sleek-black-alloy-.jpg").convert("RGBA")
rim = rim.resize((120, 120))

# Position to paste
position = (300, 400)
car.paste(rim, position, rim)  # 3rd arg is mask for transparency

car.save("D:\Dts Bike\Rim\new sleek-black-alloy-.jpg")
