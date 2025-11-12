# Label Printing & Checkout Code Feature

This feature adds secure checkout verification using printed labels with unique codes.

## Overview

When enabled, this feature:
1. Generates a unique 5-digit code for each check-in
2. Automatically prints a label with the child's name, event details, and checkout code
3. Requires the parent to enter the code to check out their child
4. Provides admin override capability for special circumstances
5. **Prints on the client machine** (where the browser is running), not the server

## Architecture

The label printing uses **client-side JavaScript** with DYMO's Label Framework:
- Server generates checkout codes and sends label data to browser
- Browser JavaScript automatically prints to locally connected DYMO printer
- Works through Cloudflare tunnels and remote connections
- No server-side printer configuration needed

## Setup

### 1. Run Migrations

```bash
cd /var/www/troop_checkin
python3 migrate_add_checkout_code.py
python3 migrate_add_label_settings.py
```

### 2. Install DYMO Software (On Check-in Kiosk/Computer)

**Important**: Install DYMO software on the computer where labels will print (NOT the server).

#### Windows
1. Download **DYMO Connect** from: https://www.dymo.com/support
2. Install and run DYMO Connect
3. Connect your DYMO LabelWriter printer via USB
4. Verify printer shows up in DYMO Connect

#### Mac
1. Download **DYMO Connect** for Mac from: https://www.dymo.com/support
2. Install and grant necessary permissions
3. Connect DYMO LabelWriter via USB

#### Linux (Ubuntu/Debian)
```bash
# Download DYMO Label software
wget https://download.dymo.com/dymo/Software/Linux/dymo-cups-drivers-1.4.0.tar.gz
tar -xzf dymo-cups-drivers-1.4.0.tar.gz
cd dymo-cups-drivers-1.4.0.5
sudo ./configure && sudo make && sudo make install

# Or use the web service approach (recommended)
# DYMO Connect runs as a local web service on port 41951
```

### 3. Configure in Admin Settings

1. Go to Admin → Settings
2. Scroll to "Label Printing & Checkout Codes"
3. Check "Require checkout codes"
4. Select printer type: **DYMO** (recommended)
5. Set label dimensions (default: 2.0" x 1.0" for DYMO 30252 labels)
6. Click "Update Label Settings"

### 4. Test Printing

The first time you check in with the feature enabled:
- A code will be generated
- The system will attempt to print a label
- Check console logs for any printing errors
- A test image is saved to `/tmp/test_label.png` for debugging

## Hardware Requirements

### DYMO Label Printers
- Supported: DYMO LabelWriter series
- Connection: USB
- Label size: Configurable (default 2" x 1")
- Requires: `pyusb` and `python-escpos` packages

### Brother QL Series
- Supported: Brother QL-500, QL-700, QL-800, etc.
- Connection: USB or Network
- Label size: Configurable
- Requires: `brother-ql` package

## Usage

### For Staff

1. **Check-In**: 
   - Parent provides phone number
   - Select kids to check in
   - Labels print automatically with unique codes
   - Give labels to parents

2. **Check-Out**:
   - Click "Check Out" button
   - System prompts for checkout code
   - Parent enters code from label
   - If correct, child is checked out
   - If incorrect, error message is shown

3. **Admin Override**:
   - If parent lost their label
   - Staff can use admin credentials to bypass code requirement
   - Click "Check Out" and select "Admin Override" when prompted

### For Parents

1. Receive printed label at check-in with:
   - Child's name
   - Event name and date
   - Check-in time
   - 5-digit checkout code

2. Keep label safe

3. At check-out, provide the 5-digit code from the label

## Security Features

- **Unique codes per event**: Codes are only unique within an event (can reuse across different events)
- **Admin override**: Staff with admin credentials can bypass code requirement
- **Code verification**: System prevents checkout without correct code
- **Label security**: Only printed, never displayed on screen

## Troubleshooting

### Labels aren't printing

1. Check printer connection:
   ```bash
   lsusb  # Should show your printer
   ```

2. Check printer permissions:
   ```bash
   sudo usermod -a -G lp troop
   ```

3. Check logs:
   ```bash
   sudo journalctl -u troop_checkin -n 50
   ```

4. Test label generation:
   ```bash
   cd /var/www/troop_checkin
   python3 label_printer.py
   # Check /tmp/test_label.png
   ```

### Code verification failing

1. Ensure migrations were run
2. Check database:
   ```bash
   sqlite3 checkin.db "SELECT checkout_code FROM checkins WHERE checkout_time IS NULL LIMIT 5;"
   ```

3. Verify setting is enabled:
   ```bash
   sqlite3 checkin.db "SELECT value FROM settings WHERE key='require_checkout_code';"
   ```

### Performance issues

- Label printing happens synchronously during check-in
- For high-traffic events, consider disabling the feature
- Or implement background printing (future enhancement)

## Disabling the Feature

1. Go to Admin → Settings
2. Uncheck "Require checkout codes"
3. Click "Update Label Settings"

Check-ins will work normally without codes. Existing codes in the database are preserved but not required.

## Database Schema

### checkins table
- `checkout_code TEXT`: 5-digit code for verification (NULL if feature disabled)

### settings table
- `require_checkout_code`: 'true' or 'false'
- `label_printer_type`: 'dymo' or 'brother'
- `label_width`: Width in inches (e.g., '2.0')
- `label_height`: Height in inches (e.g., '1.0')

## Future Enhancements

- QR code support
- SMS code delivery
- Background label printing
- Batch label printing
- Custom label templates
- Email code option
- Parent portal for code retrieval
