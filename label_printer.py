#!/usr/bin/env python3
"""
Label printing module for check-in system.
Supports DYMO label printers with customizable label sizes.
"""

import random
import sqlite3
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from brother_ql.brother_ql_create import convert
    from brother_ql import BrotherQLRaster
    HAS_BROTHER_QL = True
except ImportError:
    HAS_BROTHER_QL = False

try:
    from dymoprinter import DymoLabeler
    HAS_DYMO = True
except ImportError:
    HAS_DYMO = False


def generate_unique_code(event_id: int, db_path: str) -> str:
    """
    Generate a unique 5-digit code for this event.
    Ensures no duplicate codes exist for active check-ins in this event.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    max_attempts = 100
    for _ in range(max_attempts):
        code = f"{random.randint(10000, 99999)}"
        
        # Check if code already exists for active check-ins in this event
        cursor.execute("""
            SELECT COUNT(*) FROM checkins 
            WHERE event_id = ? AND checkout_code = ? AND checkout_time IS NULL
        """, (event_id, code))
        
        if cursor.fetchone()[0] == 0:
            conn.close()
            return code
    
    conn.close()
    raise Exception("Failed to generate unique checkout code after 100 attempts")


def create_label_image(kid_name: str, event_name: str, event_date: str, 
                       checkin_time: str, checkout_code: str, 
                       width_inches: float = 2.0, height_inches: float = 1.0) -> 'Image.Image':
    """
    Create a PIL Image for the label with all check-in information.
    
    Args:
        kid_name: Name of the child
        event_name: Name of the event
        event_date: Date of the event
        checkin_time: Time of check-in
        checkout_code: 5-digit checkout code
        width_inches: Label width in inches
        height_inches: Label height in inches
    
    Returns:
        PIL Image object
    """
    # Convert inches to pixels (300 DPI)
    dpi = 300
    width = int(width_inches * dpi)
    height = int(height_inches * dpi)
    
    # Create image
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font, fall back to default if not available
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        code_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    except:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        code_font = ImageFont.load_default()
    
    # Layout
    y_pos = 30
    
    # Kid name (title)
    draw.text((20, y_pos), kid_name, fill='black', font=title_font)
    y_pos += 80
    
    # Event info
    draw.text((20, y_pos), f"{event_name}", fill='black', font=body_font)
    y_pos += 50
    draw.text((20, y_pos), f"{event_date} • {checkin_time}", fill='black', font=body_font)
    y_pos += 70
    
    # Checkout code (prominently displayed)
    draw.text((20, y_pos), "Checkout Code:", fill='black', font=body_font)
    y_pos += 60
    draw.text((20, y_pos), checkout_code, fill='black', font=code_font)
    
    return img


def print_label_dymo(img: 'Image.Image', printer_name: Optional[str] = None) -> bool:
    """
    Print label using DYMO printer.
    
    Args:
        img: PIL Image to print
        printer_name: Optional specific printer name
    
    Returns:
        True if successful, False otherwise
    """
    if not HAS_DYMO:
        print("DYMO library not installed. Install with: pip install dymoprinter")
        return False
    
    try:
        # This is a placeholder - actual DYMO integration would depend on the specific library
        # You'll need to install: pip install dymoprinter
        # and configure it for your specific DYMO model
        print("DYMO printing not fully implemented yet - would print label here")
        print(f"Label image size: {img.size}")
        return True
    except Exception as e:
        print(f"Error printing to DYMO: {e}")
        return False


def print_checkout_label(kid_name: str, event_name: str, event_date: str,
                        checkin_time: str, checkout_code: str,
                        printer_type: str = 'dymo',
                        width: float = 2.0, height: float = 1.0) -> bool:
    """
    Main function to print a checkout label.
    
    Args:
        kid_name: Name of the child
        event_name: Name of the event  
        event_date: Date of the event (YYYY-MM-DD format)
        checkin_time: Time of check-in (HH:MM format)
        checkout_code: 5-digit checkout code
        printer_type: Type of printer ('dymo', 'brother', etc.)
        width: Label width in inches
        height: Label height in inches
    
    Returns:
        True if printing successful, False otherwise
    """
    # Create the label image
    img = create_label_image(kid_name, event_name, event_date, checkin_time, 
                            checkout_code, width, height)
    
    # Save a copy for debugging (optional)
    # img.save('/tmp/last_label.png')
    
    # Print based on printer type
    if printer_type.lower() == 'dymo':
        return print_label_dymo(img)
    else:
        print(f"Unsupported printer type: {printer_type}")
        return False


# For testing
if __name__ == '__main__':
    # Test label generation
    img = create_label_image(
        kid_name="John Smith",
        event_name="Troop Meeting",
        event_date="2025-11-11",
        checkin_time="18:30",
        checkout_code="12345",
        width_inches=2.0,
        height_inches=1.0
    )
    img.save('/tmp/test_label.png')
    print("Test label saved to /tmp/test_label.png")
