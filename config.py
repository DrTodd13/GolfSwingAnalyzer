"""
Configuration example for Golf Swing Analyzer.
Edit these values to match your setup.
"""

# Camera Configuration
CAMERA1_ID = 0  # Front-facing camera (typically built-in webcam or USB camera 0)
CAMERA2_ID = 1  # Back-facing camera (typically USB camera 1)

# Output Configuration
OUTPUT_DIR = "output"  # Directory where swing videos will be saved

# Recording Configuration
BUFFER_SECONDS = 3  # Seconds of video to capture BEFORE swing detection
COOLDOWN_SECONDS = 5  # Seconds to wait after a swing before detecting the next one
POST_SWING_SECONDS = 2  # Seconds to record AFTER motion stops

# Motion Detection Configuration
MOTION_THRESHOLD = 500  # Higher = less sensitive, Lower = more sensitive
MIN_MOTION_DURATION = 0.3  # Minimum seconds of sustained motion to trigger recording

# Video Configuration
FPS = 30  # Frames per second for capture and output
RESOLUTION_CAMERA1 = (640, 480)  # (width, height) for camera 1 (front-facing)
RESOLUTION_CAMERA2 = (640, 480)  # (width, height) for camera 2 (back-facing)

# Display Configuration
DISPLAY_LIVE_FEED = True  # Show live camera feed window (press 'q' to quit)
