import requests
from bs4 import BeautifulSoup
import os

# URL of the target webpage
url = "https://www.istockphoto.com/search/2/image?utm_campaign=srp_photos_bottom&utm_content=https%3A%2F%2Funsplash.com%2Fs%2Fphotos%2Fcar-rim&utm_medium=affiliate&utm_source=unsplash&utm_term=car+rim%3A%3A%3A&alloweduse=availableforalluses&excludenudity=true&mediatype=photography&phrase=car+rim&sort=best"

# Send GET request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}
response = requests.get(url, headers=headers)

# Check for success
if response.status_code != 200:
    print(f"Failed to load page: {response.status_code}")
    exit()

# Parse the HTML
soup = BeautifulSoup(response.text, 'html.parser')
list_items = soup.find_all('li', class_='list-item')

# Extract image URLs
image_urls = []
for item in list_items:
    link_tag = item.find('link', itemprop='contentUrl')
    if link_tag and link_tag.get('href'):
        image_urls.append(link_tag['href'])

# Create folder to save images
folder = 'downloaded_car_rim_images'
os.makedirs(folder, exist_ok=True)

# Download images
for i, url in enumerate(image_urls, 1):
    try:
        ext = url.split('.')[-1].split('?')[0]
        filename = os.path.join(folder, f"car_image_{i}.{ext}")
        img_data = requests.get(url).content
        with open(filename, 'wb') as f:
            f.write(img_data)
        print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
