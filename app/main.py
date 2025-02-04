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

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('result/output.mp4', fourcc, 20.0, (1280, 720))

    # Initialize video capture
    background_cap = cv2.VideoCapture('src/exmpl.mp4')

    if background_cap.isOpened():
        print("File opened successfully")
        num_frames = int(background_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f'Success: Video file opened. It contains {num_frames} frames')
        print(background_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(background_cap.get(cv2.CAP_PROP_FPS))
        print(background_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        print(background_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Setting to capture the first frame
        background_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        ret, frame = background_cap.read()

        if not ret:
            print('Failed to read frame from background_cap')

    else:
        print("Error opening file")

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

        page = browser.new_page(viewport={'width': 1280, 'height': 720})
        page.goto('https://app.equipe.com/meetings/74298/scoreboards/21')

        print('page.goto')

        cv2.namedWindow('Animation', cv2.WINDOW_NORMAL)

        print('cv2.namedWindow')

        fps_start_time = time.time()
        fps_counter = 0
        fps = 0

        start_time = time.time()
        max_duration = 20  # seconds

        print('try')

        try:
            while True:
                fps_counter += 1

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

                # # Write the frame to the output video
                # out.write(frame)
                #
                # # Display result
                # cv2.imshow("Animation", frame)

                # cv2.imshow('Animation', frame)
                #
                # # Save the image instead of showing it
                # cv2.imwrite('result/output.jpg', frame)

                # # Read the current frame from the background video
                # _, background_frame = background_cap.read()
                #
                # # # Resize the background frame to match the screenshot array frame
                # # background_frame = cv2.resize(background_frame, (frame.shape[1], frame.shape[0]))
                #
                # if background_frame is not None:
                #     # Resize the background frame to match the screenshot array frame
                #     # background_frame = cv2.resize(background_frame, (frame.shape[1], frame.shape[0]))
                #     background_frame = cv2.resize(background_frame, (1280, 720))
                # else:
                #     print("Failed to read frame from background_cap")
                #     break  # or continue

                # Read the current frame from the background video
                ret, background_frame = background_cap.read()
                if ret:
                    try:
                        background_frame = cv2.resize(background_frame, (1280, 720))
                    except Exception as e:
                        print(f'Error when resizing: {e}')
                else:
                    print("Failed to read frame from background_cap")
                    break  # or continue

                # Combine the two frames (note: you might want to adjust the alpha and beta values according to your needs, this is just doing a simple blending)
                combined_frame = cv2.addWeighted(background_frame, 0.5, frame, 0.5, 0)

                # Write the combined frame to the output video
                out.write(combined_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                if time.time() - start_time > max_duration:
                    break

                # time.sleep(1 / 30)

        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            # Release the display
            display.stop()
            browser.close()

            background_cap.release()
            out.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
