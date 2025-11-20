import cv2
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilenames
import subprocess
import platform
import shutil
import os

if platform.system() == "Windows":
    foldersep = "\\"
else:
    foldersep = "/"

Tk().withdraw()
files = askopenfilenames(title="Choose images")
print("Choose images to compare")

i = 0
imagergbprev = None
leftmost = 1e9
rightmost = 0
topmost = 1e9
bottommost = 0
img_width = None
img_height = None

if not os.path.exists("stitchtmp"):
    os.makedirs("stitchtmp")

# First pass: compute vertical region of change, but keep full width
for file in files:
    img_bgr = cv2.imread(file)
    if img_bgr is None:
        continue

    imagergb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    height, width, _ = imagergb.shape

    if img_width is None:
        img_width = width
        img_height = height

    if i == 1 and imagergbprev is not None:
        print("Performing analysis")

        diff_mask = np.any(imagergb != imagergbprev, axis=2)
        ys, xs = np.where(diff_mask)
        if xs.size > 0 and ys.size > 0:
            # Track where the differences appear
            leftmost = min(leftmost, int(xs.min()))
            rightmost = max(rightmost, int(xs.max()))
            topmost = min(topmost, int(ys.min()))
            bottommost = max(bottommost, int(ys.max()))

            print(
                "Differences at (%d, %d) to (%d, %d)"
                % (leftmost, rightmost, topmost, bottommost)
            )

        # Regardless of where differences are horizontally, keep full width
        leftmost = 0
        rightmost = img_width

    if i > 0 and imagergbprev is not None:
        # If we did not find vertical differences, default to full height
        if bottommost <= topmost or topmost >= 1e8:
            top = 0
            bottom = img_height if img_height is not None else imagergbprev.shape[0]
        else:
            top = int(topmost)
            bottom = int(bottommost)

        # Crop previous image vertically only, horizontal is full width
        crop_prev = imagergbprev[top:bottom, 0:img_width]
        crop_prev_bgr = cv2.cvtColor(crop_prev, cv2.COLOR_RGB2BGR)

        if i == 1:
            idx = 0
        else:
            idx = i - 1

        cv2.imwrite(
            "stitchtmp" + foldersep + "diff" + str(idx) + ".png",
            crop_prev_bgr,
        )

        # If this is the last file, also save current crop
        if i == (len(files) - 1):
            crop_curr = imagergb[top:bottom, 0:img_width]
            crop_curr_bgr = cv2.cvtColor(crop_curr, cv2.COLOR_RGB2BGR)
            cv2.imwrite(
                "stitchtmp" + foldersep + "diff" + str(i) + ".png",
                crop_curr_bgr,
            )

    imagergbprev = imagergb
    i += 1

if img_width is None:
    print("No valid images were selected.")
    shutil.rmtree("stitchtmp")
    raise SystemExit

total = i + 1
i = 0

width_cropped = img_width
fullimage = np.zeros((9999, width_cropped, 3), dtype=np.uint8)

# Placeholder last diff image
placeholder = np.zeros((2000, width_cropped, 3), dtype=np.uint8)
cv2.imwrite(
    "stitchtmp" + foldersep + "diff" + str(total - 1) + ".png",
    placeholder,
)

lineonnew = 0

print("Stitching")
for num in range(0, total):
    if i > 0:
        path1 = "stitchtmp" + foldersep + "diff" + str(i - 1) + ".png"
        path2 = "stitchtmp" + foldersep + "diff" + str(i) + ".png"

        image1_bgr = cv2.imread(path1)
        image2_bgr = cv2.imread(path2)
        if image1_bgr is None or image2_bgr is None:
            i += 1
            continue

        image1rgb = cv2.cvtColor(image1_bgr, cv2.COLOR_BGR2RGB)
        image2rgb = cv2.cvtColor(image2_bgr, cv2.COLOR_BGR2RGB)

        height, width = image1rgb.shape[:2]
        sodone = False

        for line in range(0, height):
            im1 = image1rgb[line : line + 1, 0:width]
            # Compare against first visible line of the next diff image
            if image2rgb.shape[0] > 1:
                im2 = image2rgb[1:2, 0:width]
            else:
                im2 = image2rgb[0:1, 0:width]

            if np.array_equal(im1, im2):
                sodone = True
            else:
                if not sodone:
                    if lineonnew < fullimage.shape[0]:
                        fullimage[lineonnew : lineonnew + 1, 0:width] = im1
                        lineonnew += 1

    i += 1

print("Cropping vertically")

# Only crop vertically, keep full width
mask = np.any(fullimage != 0, axis=2)
row_mask = np.any(mask, axis=1)
ys = np.where(row_mask)[0]

if ys.size > 0:
    top = int(ys.min())
    bottom = int(ys.max()) + 1
    fullimage = fullimage[top:bottom, :]

# Save result next to first selected image
out_dir = os.path.dirname(files[0])

if not os.path.isdir(out_dir):
    os.makedirs(out_dir, exist_ok=True)

out_path = os.path.join(out_dir, "stitch.png")

out_bgr = cv2.cvtColor(fullimage, cv2.COLOR_RGB2BGR)
cv2.imwrite(out_path, out_bgr)

if platform.system() == "Windows":
    subprocess.Popen(r'explorer /select,"' + out_path + '"')
else:
    if platform.system() == "Darwin":
        subprocess.call(["open", "-R", out_path])

shutil.rmtree("stitchtmp")
print("Done!")
