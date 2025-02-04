from playwright.sync_api import sync_playwright
import cv2
import numpy as np
import time
from pyvirtualdisplay import Display
import tensorflow as tf

import torch


def main():
    print("Initializing...")
    print(torch.cuda.is_available())

    print("Number of GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
    print("Cuda check")

    # Start the virtual display
    display = Display(visible=0, size=(1280, 720))
    display.start()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--use-gl=egl',
                '--enable-gpu-rasterization',
                '--disable-software-rasterization',
                '--ignore-gpu-blocklist',
                '--enable-accelerated-2d-canvas',
                '--disable-gpu-vsync',
                '--enable-native-gpu-memory-buffers',
                '--enable-features=VaapiVideoDecoder',
            ]
        )

        print(browser)

        page = browser.new_page(viewport={'width': 1280, 'height': 720})
        page.goto('https://app.equipe.com/meetings/74298/scoreboards/21')

        print('page.goto')

        cv2.namedWindow('Animation', cv2.WINDOW_NORMAL)

        print('cv2.namedWindow')

        fps_start_time = time.time()
        fps_counter = 0
        fps = 0

        print('try')

        try:
            while True:
                fps_counter += 1

                print('fps_counter')
                print(fps_counter)
                print('fps_counter')

                if time.time() - fps_start_time > 1:
                    fps = fps_counter
                    fps_counter = 0
                    fps_start_time = time.time()

                screenshot = page.locator('.scene.no-select').screenshot(
                    type='jpeg',
                    quality=100,
                )

                screenshot_array = np.frombuffer(screenshot, np.uint8)

                frame = cv2.imdecode(screenshot_array, cv2.IMREAD_COLOR)

                cv2.putText(frame, f'FPS: {fps}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                cv2.imshow('Animation', frame)

                # Save the image instead of showing it
                cv2.imwrite('output.jpg', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                time.sleep(1 / 30)

        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            # Release the display
            display.stop()
            browser.close()


if __name__ == "__main__":
    main()