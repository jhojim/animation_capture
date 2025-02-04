from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import cv2
from PIL import Image
import numpy as np
import time
from io import BytesIO

# Use webdriver_manager to download and setup ChromeDriver
webdriver_service = Service(ChromeDriverManager().install())

# Setup Chrome options
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1280,720")

# Use Chrome webdriver, use options and webdriver_service
driver = webdriver.Chrome(service=webdriver_service, options=options)
driver.set_window_size(1280, 720)

driver.get('https://app.equipe.com/meetings/74298/scoreboards/21')

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('result/output.mp4', fourcc, 20.0, (1280, 720))

start_time = time.time()
max_duration = 60  # seconds

# Initialize video capture
cap = cv2.VideoCapture('src/exmpl.mp4')

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.scene.no-select'))
    )
except:
    print("Element with the selector '.scene.no-select' could not be found")
    driver.quit()


while time.time() - start_time < max_duration:
    # Get the current screenshot
    png_image = element.screenshot_as_png
    img = Image.open(BytesIO(png_image))

    # Convert to RGBA
    img = img.convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        # change all white (also shades of whites)
        # pixels to transparent
        if item[0] in list(range(200, 256)):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)

    # Resize image
    img = img.resize((1280, 720), Image.LANCZOS)

    # Convert image to numpy array and adjust colors
    screenshot_frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)

    # Create mask for transparent pixels in screenshot frame
    mask = screenshot_frame[:, :, 3] > 0

    # Get the current frame from the exmpl.mp4 video
    ret, video_frame = cap.read()
    if not ret:
        break  # Exit the loop if no more frames

    # Resize the video frame
    video_frame = cv2.resize(video_frame, (1280, 720))

    # Add screenshot frame on top of the video frame
    video_frame[mask] = screenshot_frame[:, :, :3][mask]

    # Write the frame to the output video
    out.write(video_frame)

# while cap.isOpened():
#     # Get the current screenshot
#     png_image = element.screenshot_as_png
#     img = Image.open(BytesIO(png_image))
#
#     # Convert to RGBA
#     img = img.convert("RGBA")
#     datas = img.getdata()
#
#     new_data = []
#     for item in datas:
#         # change all white (also shades of whites)
#         # pixels to transparent
#         if item[0] in list(range(200, 256)):
#             new_data.append((255, 255, 255, 0))
#         else:
#             new_data.append(item)
#
#     img.putdata(new_data)
#
#     # Resize image
#     img = img.resize((1280, 720), Image.LANCZOS)
#
#     # Convert image to numpy array and adjust colors
#     screenshot_frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)
#
#     # Create mask for transparent pixels in screenshot frame
#     mask = screenshot_frame[:, :, 3] > 0
#
#     # Get the current frame from the exmpl.mp4 video
#     ret, video_frame = cap.read()
#     if not ret:
#         break  # Exit the loop if no more frames
#
#     # Resize the video frame
#     video_frame = cv2.resize(video_frame, (1280, 720))
#
#     # Add screenshot frame on top of the video frame
#     video_frame[mask] = screenshot_frame[:, :, :3][mask]
#
#     # Write the frame to the output video
#     out.write(video_frame)
#
#     # If you want to slow down the frames, uncomment the line below
#     # time.sleep(1 / 20)

# while time.time() - start_time < max_duration:
#     png_image = element.screenshot_as_png
#     img = Image.open(BytesIO(png_image))
#
#     # Convert to RGBA
#     img = img.convert("RGBA")
#     datas = img.getdata()
#
#     new_data = []
#     for item in datas:
#         # change all white (also shades of whites)
#         # pixels to transparent
#         if item[0] in list(range(200, 256)):
#             new_data.append((255, 255, 255, 0))
#         else:
#             new_data.append(item)
#
#     img.putdata(new_data)
#
#     # Resize image
#     img = img.resize((1280, 720), Image.LANCZOS)
#
#     screenshot_frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)
#
#     # Create mask for non-transparent pixels
#     mask = screenshot_frame[:, :, 3] > 0
#
#     # Read a frame from exmpl.mp4 video
#     ret, video_frame = cap.read()
#     if not ret:
#         print("Couldn't retrieve frame from exmpl.mp4, exiting.")
#         break
#
#     # Resize the video frame to match the screenshot frame
#     video_frame = cv2.resize(video_frame, (1280, 720))
#
#     # Overlay screenshot onto video frame
#     video_frame[mask] = screenshot_frame[:, :, :3][mask]
#
#     # Write the overlay frame to the output video
#     out.write(video_frame)
#
#     time.sleep(1 / 20)

driver.quit()

# Release the video capture and video writer
cap.release()
out.release()
