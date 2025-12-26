"""
Golf Swing Analyzer
Main module for detecting and recording golf swings from dual camera setup.
"""

import cv2
import numpy as np
from collections import deque
from datetime import datetime
import os
import time


class GolfSwingAnalyzer:
    """
    Monitors two cameras and detects golf swings.
    When a swing is detected, creates a side-by-side video clip.
    """
    
    def __init__(self, camera1_id=0, camera2_id=1, output_dir="output", 
                 buffer_seconds=5, cooldown_seconds=3, motion_threshold=500,
                 fps=30, resolution=(640, 480)):
        """
        Initialize the Golf Swing Analyzer.
        
        Args:
            camera1_id: ID of the first camera (front view)
            camera2_id: ID of the second camera (back view)
            output_dir: Directory to save video clips
            buffer_seconds: Seconds of video to keep in buffer before swing detection
            cooldown_seconds: Seconds to wait after detecting a swing before detecting next
            motion_threshold: Threshold for motion detection (lower = more sensitive)
            fps: Frames per second for capture and output
            resolution: Tuple of (width, height) for camera resolution
        """
        self.camera1_id = camera1_id
        self.camera2_id = camera2_id
        self.output_dir = output_dir
        self.buffer_seconds = buffer_seconds
        self.cooldown_seconds = cooldown_seconds
        self.motion_threshold = motion_threshold
        self.fps = fps
        self.resolution = resolution
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize cameras
        self.cap1 = None
        self.cap2 = None
        
        # Frame buffers (circular buffer to store frames before swing)
        buffer_size = int(buffer_seconds * fps)
        self.buffer1 = deque(maxlen=buffer_size)
        self.buffer2 = deque(maxlen=buffer_size)
        
        # State tracking
        self.is_recording = False
        self.recording_frames1 = []
        self.recording_frames2 = []
        self.last_swing_time = 0
        
        # Motion detection
        self.prev_frame1 = None
        self.prev_frame2 = None
        self.motion_start_time = None
        self.motion_detected = False
        self.frames_since_motion = 0
        self.min_motion_duration = 0.3  # Minimum duration of motion to consider it a swing
        self.post_motion_frames = int(fps * 2)  # Record for 2 seconds after motion stops
        
    def initialize_cameras(self):
        """Initialize both cameras with proper settings."""
        self.cap1 = cv2.VideoCapture(self.camera1_id)
        self.cap2 = cv2.VideoCapture(self.camera2_id)
        
        # Set camera properties
        for cap in [self.cap1, self.cap2]:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        # Verify cameras are opened
        if not self.cap1.isOpened():
            raise RuntimeError(f"Cannot open camera {self.camera1_id}")
        if not self.cap2.isOpened():
            raise RuntimeError(f"Cannot open camera {self.camera2_id}")
        
        print(f"Cameras initialized: {self.camera1_id} and {self.camera2_id}")
        
    def detect_motion(self, frame, prev_frame):
        """
        Detect motion between current frame and previous frame.
        
        Args:
            frame: Current frame
            prev_frame: Previous frame
            
        Returns:
            bool: True if significant motion detected
        """
        if prev_frame is None:
            return False
        
        # Convert frames to grayscale
        gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
        gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)
        
        # Compute absolute difference
        frame_diff = cv2.absdiff(gray1, gray2)
        
        # Apply threshold
        _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
        
        # Calculate motion score
        motion_score = np.sum(thresh)
        
        return motion_score > self.motion_threshold * 255
    
    def combine_frames_side_by_side(self, frame1, frame2):
        """
        Combine two frames side by side.
        
        Args:
            frame1: First frame (left)
            frame2: Second frame (right)
            
        Returns:
            Combined frame
        """
        # Ensure frames are the same height
        h1, w1 = frame1.shape[:2]
        h2, w2 = frame2.shape[:2]
        
        if h1 != h2:
            # Resize to match height
            target_height = min(h1, h2)
            frame1 = cv2.resize(frame1, (int(w1 * target_height / h1), target_height))
            frame2 = cv2.resize(frame2, (int(w2 * target_height / h2), target_height))
        
        # Concatenate horizontally
        combined = np.hstack((frame1, frame2))
        return combined
    
    def save_swing_video(self):
        """Save the recorded swing as a video file."""
        if not self.recording_frames1 or not self.recording_frames2:
            print("No frames to save")
            return
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_dir, f"swing_{timestamp}.mp4")
        
        # Get frame dimensions
        sample_frame = self.combine_frames_side_by_side(
            self.recording_frames1[0], 
            self.recording_frames2[0]
        )
        height, width = sample_frame.shape[:2]
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (width, height))
        
        # Write frames
        for frame1, frame2 in zip(self.recording_frames1, self.recording_frames2):
            combined = self.combine_frames_side_by_side(frame1, frame2)
            out.write(combined)
        
        out.release()
        
        duration = len(self.recording_frames1) / self.fps
        print(f"Saved swing video: {output_path} ({duration:.2f} seconds, {len(self.recording_frames1)} frames)")
        
    def process_frame(self):
        """Process a single frame from both cameras."""
        # Read frames
        ret1, frame1 = self.cap1.read()
        ret2, frame2 = self.cap2.read()
        
        if not ret1 or not ret2:
            print("Failed to read from cameras")
            return False
        
        # Detect motion in both cameras
        motion1 = self.detect_motion(frame1, self.prev_frame1)
        motion2 = self.detect_motion(frame2, self.prev_frame2)
        motion = motion1 or motion2
        
        current_time = time.time()
        
        # Check if we're in cooldown period after a recent swing
        in_cooldown = (current_time - self.last_swing_time) < self.cooldown_seconds
        
        if not self.is_recording:
            # Always add frames to circular buffer
            self.buffer1.append(frame1.copy())
            self.buffer2.append(frame2.copy())
            
            # Check for start of motion (potential swing)
            if motion and not in_cooldown:
                if self.motion_start_time is None:
                    self.motion_start_time = current_time
                elif (current_time - self.motion_start_time) >= self.min_motion_duration:
                    # Motion has been sustained long enough, start recording
                    print("Swing detected! Starting recording...")
                    self.is_recording = True
                    self.motion_detected = True
                    self.frames_since_motion = 0
                    
                    # Initialize recording with buffered frames
                    self.recording_frames1 = list(self.buffer1)
                    self.recording_frames2 = list(self.buffer2)
            else:
                # Reset motion start time if motion stops
                if not motion:
                    self.motion_start_time = None
        else:
            # Currently recording
            self.recording_frames1.append(frame1.copy())
            self.recording_frames2.append(frame2.copy())
            
            if motion:
                self.frames_since_motion = 0
            else:
                self.frames_since_motion += 1
            
            # Stop recording if motion has stopped for enough frames
            if self.frames_since_motion >= self.post_motion_frames:
                print(f"Swing complete! Recorded {len(self.recording_frames1)} frames")
                self.save_swing_video()
                
                # Reset state
                self.is_recording = False
                self.motion_detected = False
                self.frames_since_motion = 0
                self.motion_start_time = None
                self.recording_frames1 = []
                self.recording_frames2 = []
                self.last_swing_time = current_time
        
        # Update previous frames
        self.prev_frame1 = frame1
        self.prev_frame2 = frame2
        
        return True
    
    def run(self, display=True):
        """
        Run the golf swing analyzer.
        
        Args:
            display: If True, display live camera feeds
        """
        try:
            self.initialize_cameras()
            print("Golf Swing Analyzer started. Press 'q' to quit.")
            print(f"Monitoring cameras {self.camera1_id} and {self.camera2_id}...")
            print(f"Output directory: {self.output_dir}")
            
            while True:
                success = self.process_frame()
                if not success:
                    break
                
                # Display live feed if requested
                if display:
                    ret1, display_frame1 = self.cap1.read()
                    ret2, display_frame2 = self.cap2.read()
                    
                    if ret1 and ret2:
                        # Create display frame
                        display_frame = self.combine_frames_side_by_side(display_frame1, display_frame2)
                        
                        # Add status text
                        status = "RECORDING" if self.is_recording else "MONITORING"
                        color = (0, 0, 255) if self.is_recording else (0, 255, 0)
                        cv2.putText(display_frame, status, (10, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                        
                        cv2.imshow("Golf Swing Analyzer", display_frame)
                    
                    # Check for quit key
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("Quitting...")
                        break
                else:
                    # Small delay when not displaying
                    time.sleep(1.0 / self.fps)
                    
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Release resources."""
        if self.cap1 is not None:
            self.cap1.release()
        if self.cap2 is not None:
            self.cap2.release()
        cv2.destroyAllWindows()
        print("Cameras released and windows closed.")


def main():
    """Main entry point for the application."""
    # Configuration
    analyzer = GolfSwingAnalyzer(
        camera1_id=0,           # Front camera
        camera2_id=1,           # Back camera
        output_dir="output",    # Output directory for videos
        buffer_seconds=3,       # Keep 3 seconds of video before swing
        cooldown_seconds=5,     # Wait 5 seconds between swing detections
        motion_threshold=500,   # Motion detection sensitivity
        fps=30,                 # Frames per second
        resolution=(640, 480)   # Camera resolution
    )
    
    try:
        analyzer.run(display=True)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
