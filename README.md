# Pixel Workbench Project

Standalone scripts to manipulate images and video, including converting animated WEBP files to MP4, merging snapshots, and other one-off utilities. Each tool runs on its own; there is no shared framework.

## Installation

- Use Python 3.12 and an optional virtual environment (`python -m venv .venv` then activate it).
- Install the shared dependencies declared in `pyproject.toml`:

  ```
  pip install -e .
  ```
- If you prefer a global install, run the same command without creating a virtual environment.

## Scripts

### WEBP to video converter
- Converts a single animated WEBP to MP4 while preserving frame timing.
- Run from the repo root or the `scripts/WEB2Video` folder:
  ```
  python scripts/WEB2Video/WEPB_to_video_converter.py
  ```
- A file picker appears; choose the source WEBP. The MP4 is written next to the selected file using the same base name.

### Screen stitcher
- Merges ordered screenshots into one image, keeping identical regions only once.
- Run:
  ```
  python scripts/ScreenStitch.py
  ```
- Select the screenshots in order when prompted. The output `stitch.png` is saved next to the first chosen image; the temporary `stitchtmp/` folder is removed automatically.

## Usage notes

- Scripts are independent; run only what you need.
- Outputs are written alongside your inputs unless otherwise noted.

## License

See `LICENSE` for terms.
