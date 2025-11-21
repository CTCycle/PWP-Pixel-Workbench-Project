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
        print("Analyzing screenshots")

        diff_mask = np.any(imagergb != imagergbprev, axis=2)
        ys, xs = np.where(diff_mask)
        if xs.size > 0 and ys.size > 0:
            # Track where the differences appear
            leftmost = min(leftmost, int(xs.min()))
            rightmost = max(rightmost, int(xs.max()))
            topmost = min(topmost, int(ys.min()))
            bottommost = max(bottommost, int(ys.max()))

            print(
                "Differences from (%d, %d) to (%d, %d)"
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

print("Merging together")
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

# Only crop vertically, keep full width
mask = np.any(fullimage != 0, axis=2)
row_mask = np.any(mask, axis=1)
ys = np.where(row_mask)[0]

if ys.size > 0:
    top = int(ys.min())
    bottom = int(ys.max()) + 1
    fullimage = fullimage[top:bottom, :]

# Restore identical regions above and below the diff region
# Use the first original image as the source of identical content
if (
    img_height is not None
    and not (bottommost <= topmost or topmost >= 1e8)
    and len(files) > 0
):
    first_bgr = cv2.imread(files[0])
    if first_bgr is not None:
        first_rgb = cv2.cvtColor(first_bgr, cv2.COLOR_BGR2RGB)

        # Clamp diff boundaries to valid image range
        top_diff = max(0, min(int(topmost), img_height))
        bottom_diff = max(top_diff, min(int(bottommost), img_height))

        # Top unchanged region: rows [0, top_diff)
        top_part = first_rgb[0:top_diff, 0:img_width]

        # Bottom unchanged region: rows [bottom_diff, img_height)
        bottom_part = first_rgb[bottom_diff:img_height, 0:img_width]

        final_height = (
            top_part.shape[0] + fullimage.shape[0] + bottom_part.shape[0]
        )
        finalimage = np.zeros((final_height, img_width, 3), dtype=np.uint8)

        cur = 0
        if top_part.size > 0:
            h_top = top_part.shape[0]
            finalimage[cur : cur + h_top, 0:img_width] = top_part
            cur += h_top

        if fullimage.size > 0:
            h_diff = fullimage.shape[0]
            finalimage[cur : cur + h_diff, 0:img_width] = fullimage
            cur += h_diff

        if bottom_part.size > 0:
            h_bottom = bottom_part.shape[0]
            finalimage[cur : cur + h_bottom, 0:img_width] = bottom_part

        fullimage = finalimage

# Save result next to first selected image
out_dir = os.path.dirname(files[0]) # type: ignore

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
print("Your screenshots have been merged!")
