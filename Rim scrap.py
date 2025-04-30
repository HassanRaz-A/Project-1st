from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import os
import time

# Setup headless Chrome browser
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)

# Your target URL
url = "https://www.istockphoto.com/search/more-like-this/157382327?assettype=image"
driver.get(url)
time.sleep(5)  # Wait for JS to load content

# Scroll down to trigger lazy-load
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(3)

# Create folder
os.makedirs("rim_images", exist_ok=True)

# Find all <img> in target structure
images = driver.find_elements(By.CSS_SELECTOR, 'div.kTsQchCkt1PlV7LGmtQA article.h7bO_HMReSDi_Svmpt9y img')

# Download each image
for i, img in enumerate(images):
    src = img.get_attribute("src")
    if src and "media.istockphoto.com" in src:
        try:
            ext = src.split('.')[-1].split('?')[0]
            img_data = requests.get(src, timeout=10).content
            file_name = f"rim_{i+1}.{ext}"
            with open(file_name, "wb") as f:
                f.write(img_data)
            print(f"✅ Downloaded: {file_name}")
        except Exception as e:
            print(f"❌ Failed to download {src}: {e}")

driver.quit()
print("✅ All done!")
