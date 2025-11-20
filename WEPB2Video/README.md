# WebP-to-MP4 Converter

Convert animated .webp files in bulk to .mp4, preserving original animation speed and quality as much as possible—using just Python, Pillow, and OpenCV.

## Features
**Batch conversion:** Converts all .webp files in a folder with a single command.

**Animation timing preserved:** Matches each frame’s original display duration for smooth, natural playback in the output .mp4.

**Simple usage:** No external binaries or complicated setup.

## Installation 
Install dependencies using the following command and place your .webp files into the webp folder.

`pip install -r requirements.txt`

To run the script:

`python WEPB_to_video_converter.py`

Converted .mp4 files will appear in the video folder.

## Notes
The script uses a default output framerate of 50 FPS to closely match original frame durations. You can adjust this value in the script (out_fps). Image quality is preserved as much as possible, but some minor compression may occur due to MP4 encoding. Only animated WebP files will produce multi-frame MP4s; static WebPs will become single-frame videos.

## License
This project is licensed under the terms of the MIT license. See the LICENSE file for details.