import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

import cv2
import numpy as np
from PIL import Image


###############################################################################
def webp_to_mp4_preserve_fps(webp_path, mp4_path, out_fps=50):
    img = Image.open(webp_path)
    frames = []
    durations = []
    try:
        while True:
            frames.append(np.array(img.convert('RGB')))
            # default frame duration is at 100 ms if not specified
            durations.append(img.info.get('duration', 100))
            img.seek(img.tell() + 1)
    except EOFError:
        pass

    if not frames:
        print(f"No frames found in {webp_path}. Skipping.")
        return

    # Build video frames according to durations
    video_frames = []
    for i, frame in enumerate(frames):
        duration = durations[i] / 1000  # duration in seconds
        count = max(1, int(round(duration * out_fps)))
        for _ in range(count):
            video_frames.append(frame)

    height, width, _ = video_frames[0].shape
    fourcc =  cv2.VideoWriter.fourcc(*'mp4v')
    video = cv2.VideoWriter(mp4_path, fourcc, out_fps, (width, height))
    for frame in video_frames:
        video.write(frame[..., ::-1])
    video.release()
    print(f"Converted {webp_path} -> {mp4_path} | Out FPS: {out_fps}")


###############################################################################
if __name__ == '__main__':
    root = Tk()
    root.withdraw()
    webp_path = askopenfilename(
        title='Choose a WEBP file',
        filetypes=[('WEBP files', '*.webp')],
    )
    root.destroy()

    if not webp_path:
        print('No WEBP file selected. Exiting.')
        raise SystemExit

    mp4_path = os.path.splitext(webp_path)[0] + '.mp4'
    webp_to_mp4_preserve_fps(webp_path, mp4_path)
