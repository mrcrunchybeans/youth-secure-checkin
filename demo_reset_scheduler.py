#!/usr/bin/env python3
"""
Demo Reset Scheduler for Youth Secure Check-in
Automatically resets the demo database at specified intervals
"""

import time
import os
import sys
from pathlib import Path
from datetime import datetime
import subprocess

# Configuration
RESET_INTERVAL_HOURS = int(os.getenv('RESET_INTERVAL_HOURS', 24))
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/demo.db')
UPLOAD_PATH = os.getenv('UPLOAD_PATH', 'static/uploads')


def reset_demo_database():
    """Reset the demo database by running the seed script"""
    print(f"[{datetime.now()}] Starting database reset...")
    
    try:
        # Run the seed script
        result = subprocess.run(
            [sys.executable, 'demo_seed.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"[{datetime.now()}] ✓ Database reset successfully!")
            print(result.stdout)
        else:
            print(f"[{datetime.now()}] ✗ Database reset failed!")
            print(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print(f"[{datetime.now()}] ✗ Database reset timed out!")
    except Exception as e:
        print(f"[{datetime.now()}] ✗ Error during reset: {e}")


def clear_uploads():
    """Clear uploaded files (logos, etc.)"""
    try:
        upload_dir = Path(UPLOAD_PATH)
        if upload_dir.exists():
            for file in upload_dir.iterdir():
                if file.is_file():
                    file.unlink()
            print(f"[{datetime.now()}] ✓ Cleared upload directory")
    except Exception as e:
        print(f"[{datetime.now()}] ✗ Error clearing uploads: {e}")


def main():
    """Main scheduler loop"""
    print("=" * 60)
    print("Youth Secure Check-in - Demo Reset Scheduler")
    print(f"Reset interval: {RESET_INTERVAL_HOURS} hours")
    print(f"Database: {DATABASE_PATH}")
    print("=" * 60)
    
    # Initial reset on startup
    reset_demo_database()
    clear_uploads()
    
    # Calculate seconds to wait
    sleep_seconds = RESET_INTERVAL_HOURS * 3600
    
    # Main loop
    while True:
        next_reset = datetime.now().timestamp() + sleep_seconds
        next_reset_str = datetime.fromtimestamp(next_reset).strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{datetime.now()}] Next reset scheduled for: {next_reset_str}")
        
        # Sleep until next reset
        time.sleep(sleep_seconds)
        
        # Perform reset
        reset_demo_database()
        clear_uploads()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Scheduler stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[{datetime.now()}] Fatal error: {e}")
        sys.exit(1)
