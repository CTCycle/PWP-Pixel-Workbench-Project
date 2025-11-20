# Pixel Workbench Project

A collection of small, task focused scripts for manipulating image and video assets. The repository is not a unified framework, it is a set of independent utilities. Each directory contains its own logic, requirements, and documentation. This top level file only describes the overall structure.

## Contents

### 1. Screenshots_wizard
A Python script for merging screenshots into a single composed output.
Files include:
- merge_screenshots.py
- README.md
- LICENSE

Functionality is limited to image merging. No broader workflow is provided.

### 2. WEPB_to_video_converter
A converter for producing a video file from a collection of WEBP images.
Files include:
- WEPB_to_video_converter.py
- requirements.txt
- README.md
- directories webp and video for input and output staging

Actual video encoding behavior depends on the libraries listed in requirements.txt. Consult the component specific README for precise usage.

## Installation

There is no shared dependency set. Install requirements only for the tool you want to run.

Example:

\`\`\`
cd WEPB_to_video_converter
pip install -r requirements.txt
\`\`\`

If the Screenshots_wizard tool has dependencies, they are documented in its own README.

## Usage

Run scripts directly from their respective directories. Inputs and outputs must follow the conventions defined inside each tool.

Examples:

Screenshots_wizard/merge_screenshots.py
WEPB_to_video_converter/WEPB_to_video_converter.py


No orchestration or entrypoint exists at the project root. Each tool performs one operation and then exits.

## Licensing

Each directory contains its own license file. Licenses are not consolidated at the project root. Review them before redistribution or integration.

## Scope

The repository is intended as a simple workspace for small media utilities. It is not designed for scalability, plugin systems, or deep extensibility. Additional scripts can be added in separate directories as long as they are self contained and documented.
