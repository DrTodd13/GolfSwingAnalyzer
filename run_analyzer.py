#!/usr/bin/env python3
"""
Example script to run the Golf Swing Analyzer with custom configuration.
"""

from golf_swing_analyzer import GolfSwingAnalyzer
import config


def main():
    """Run the analyzer with configuration from config.py"""
    print("Starting Golf Swing Analyzer...")
    print(f"Front camera: {config.CAMERA1_ID}")
    print(f"Back camera: {config.CAMERA2_ID}")
    print(f"Output directory: {config.OUTPUT_DIR}")
    print()
    
    analyzer = GolfSwingAnalyzer(
        camera1_id=config.CAMERA1_ID,
        camera2_id=config.CAMERA2_ID,
        output_dir=config.OUTPUT_DIR,
        buffer_seconds=config.BUFFER_SECONDS,
        cooldown_seconds=config.COOLDOWN_SECONDS,
        motion_threshold=config.MOTION_THRESHOLD,
        fps=config.FPS,
        resolution=config.RESOLUTION
    )
    
    try:
        analyzer.run(display=config.DISPLAY_LIVE_FEED)
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
