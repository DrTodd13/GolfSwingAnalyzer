# Golf Swing Analyzer

A Python application that uses OpenCV to monitor two cameras (one facing a golfer and another behind the golfer) and automatically creates side-by-side video clips of detected golf swings.

## Features

- **Dual Camera Monitoring**: Simultaneously captures video from two cameras
- **Automatic Swing Detection**: Uses motion detection to identify when a golf swing occurs
- **Pre-Swing Buffer**: Captures video from before the swing starts (configurable buffer)
- **Side-by-Side Output**: Combines both camera feeds into a single video with front and back views
- **Automatic Clipping**: Saves only the swing portion, from start to finish
- **Live Preview**: Optional live display of camera feeds with recording status
- **Configurable Settings**: Adjust sensitivity, timing, resolution, and more

## Requirements

- Python 3.7 or higher
- Two cameras (built-in webcam + USB camera, or two USB cameras)
- OpenCV and NumPy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/DrTodd13/GolfSwingAnalyzer.git
cd GolfSwingAnalyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

Run the analyzer with default settings:
```bash
python golf_swing_analyzer.py
```

### Using Custom Configuration

1. Edit the `config.py` file to match your camera setup and preferences
2. Run the analyzer:
```bash
python run_analyzer.py
```

### Configuration Options

Edit `config.py` to customize:

- **Camera IDs**: Set which cameras to use (typically 0 and 1)
- **Motion Threshold**: Adjust sensitivity for swing detection
- **Buffer Duration**: How many seconds before the swing to include
- **Cooldown Period**: Time to wait between detecting swings
- **Video Resolution**: Camera capture resolution (can be set independently for each camera)
- **FPS**: Frames per second for capture and output

### Controls

- Press `q` to quit the application
- Videos are automatically saved to the `output/` directory

## How It Works

1. **Continuous Monitoring**: The system continuously monitors both cameras
2. **Circular Buffer**: Maintains a rolling buffer of recent frames (default 3 seconds)
3. **Motion Detection**: Detects significant motion using frame differencing
4. **Swing Identification**: When sustained motion is detected, begins recording
5. **Automatic Stop**: Stops recording a few seconds after motion ceases
6. **Video Creation**: Combines frames from both cameras side-by-side
7. **Save Output**: Exports the clip with a timestamp filename

## Output

Videos are saved in the `output/` directory with filenames like:
- `swing_20231226_143022.mp4`

Each video contains:
- Frames from before the swing started (from buffer)
- The entire swing motion
- A few seconds after the swing completes
- Both camera views side-by-side

## Troubleshooting

### Camera Not Found
- Check camera IDs with your system (may need to try 0, 1, 2, etc.)
- Ensure cameras are connected and not in use by another application
- On Linux, you may need appropriate permissions for `/dev/video*`

### No Swings Detected
- Adjust `MOTION_THRESHOLD` in config.py (lower = more sensitive)
- Adjust `MIN_MOTION_DURATION` to require less sustained motion
- Ensure adequate lighting and camera positioning

### Poor Performance
- Reduce `RESOLUTION` in config.py
- Lower `FPS` setting
- Close other applications using the camera

## Project Structure

```
GolfSwingAnalyzer/
├── golf_swing_analyzer.py  # Main application class
├── config.py               # Configuration settings
├── run_analyzer.py         # Example runner script
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── output/                # Generated video clips (created automatically)
```

## Technical Details

- **Motion Detection**: Uses frame differencing with Gaussian blur and thresholding
- **Video Format**: MP4 with H.264 codec (compatible with most players)
- **Frame Synchronization**: Ensures both cameras are synchronized frame-by-frame
- **Buffer Management**: Efficient circular buffer using Python deque

## License

This project is open source. See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.