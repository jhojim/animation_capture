import cv2
import numpy as np
import time
from pyvirtualdisplay import Display
import tensorflow as tf
import queue
import threading

from playwright.sync_api import sync_playwright


def write_combined_frames(output_q, background_cap, end_event):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('result/output.mp4', fourcc, 20.0, (1280, 720))
    total_frames = int(background_cap.get(cv2.CAP_PROP_FRAME_COUNT))

    for _ in range(total_frames):
        try:
            frame, fps = output_q.get(timeout=1)
            ret, background_frame = background_cap.read()

            if ret:
                try:
                    background_frame_gpu = cv2.UMat(background_frame)
                    background_frame_resized_gpu = cv2.resize(background_frame_gpu, (1280, 720))
                    background_frame = background_frame_resized_gpu.get()
                except Exception as e:
                    print(f'Error when resizing: {e}')

                combined_frame = cv2.addWeighted(background_frame, 0.5, frame, 0.5, 0)
                out.write(combined_frame)
            else:
                print("Failed to read frame from background_cap")
                end_event.set()

        except queue.Empty:
            continue

    out.release()


def main():
    print("Initializing...")

    display = Display(visible=0, size=(1280, 720))
    display.start()

    background_cap = cv2.VideoCapture('src/exmpl.mp4')

    frame_q = queue.Queue()
    end_event = threading.Event()

    worker_thread = threading.Thread(target=write_combined_frames, args=(frame_q, background_cap, end_event))
    worker_thread.start()

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

        fps_counter = 0
        fps_start_time = time.time()
        fps = 0

        while not end_event.is_set():
            screenshot = page.locator('.scene.no-select').screenshot(
                type='jpeg',
                quality=100,
            )

            screenshot_array = np.frombuffer(screenshot, np.uint8)
            frame = cv2.imdecode(screenshot_array, cv2.IMREAD_COLOR)

            fps_counter += 1
            if time.time() - fps_start_time > 1:
                fps = fps_counter
                fps_counter = 0
                fps_start_time = time.time()

            cv2.putText(frame, f'FPS: {fps}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            frame_q.put((frame, fps))

    worker_thread.join()

    background_cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
