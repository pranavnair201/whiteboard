import cv2
import numpy as np
import os
from PIL import Image

# Load video
video_path = "doc_veo.mp4"
cap = cv2.VideoCapture(video_path)

# Create output folder for frames
os.makedirs("frames", exist_ok=True)

frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define black range and create mask
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])
    mask = cv2.inRange(hsv, lower_black, upper_black)

    # Invert mask
    mask_inv = cv2.bitwise_not(mask)

    # Convert mask to 4-channel (RGBA)
    b, g, r = cv2.split(frame)
    alpha = mask_inv  # Make detected black pixels transparent
    rgba = cv2.merge([b, g, r, alpha])

    # Save frame as PNG with transparency
    cv2.imwrite(f"frames/frame_{frame_count:04d}.png", rgba)

    frame_count += 1

cap.release()
cv2.destroyAllWindows()

import subprocess
ffmpeg_cmd = [
    "ffmpeg",
    "-framerate", "30",
    "-i", "frames/frame_%04d.png",
    "-c:v", "libvpx-vp9",
    "-pix_fmt", "yuva420p",
    "output.webm"
]

subprocess.run(ffmpeg_cmd)