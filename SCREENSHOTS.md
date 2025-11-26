# Screenshot & Marketing Deployment

This configuration is designed to create a "clean" instance of the application populated with realistic dummy data ("Troop 101") but without any "Demo Mode" banners or indicators. This is ideal for taking screenshots for the website, GitHub, or social media.

## Features

- **Realistic Data**: Pre-populated with "Troop 101", families, kids, and events.
- **No Demo Banners**: Looks like a production instance.
- **Auto-Reset**: Resets data every 24 hours to keep dates relative to "today".
- **Secure-ish**: Uses a separate database (`screenshots.db`) and volume.

## Deployment

1. **Copy Files to Server**:
   Ensure the following files are on your server:
   - `docker-compose.screenshots.yml`
   - `screenshot_seed.py`
   - `screenshot_reset_scheduler.py`

2. **Start the Service**:
   ```bash
   docker-compose -f docker-compose.screenshots.yml up -d
   ```

3. **Access**:
   - URL: `http://your-server-ip:5000`
   - Admin Password: `demo123`
   - App Password: `demo123`

## Customization

To change the seeded data (e.g., troop name, specific scenarios), edit `screenshot_seed.py` before starting the container.

## Resetting Data

The data automatically resets every 24 hours. To force a reset immediately:

```bash
docker-compose -f docker-compose.screenshots.yml restart screenshot-reset
```
Or manually run the seed script inside the container:
```bash
docker exec -it youth-checkin-screenshots python screenshot_seed.py
```

## Recommended Screenshot List

Here is a checklist of screenshots to capture for your marketing materials, documentation, and GitHub repository.

### 1. The "Hero" Shots (Main Features)
- **Kiosk - Main Screen**: The clean, welcoming interface on a tablet/desktop. Shows the keypad and "Currently Checked In" list.
- **Kiosk - Family Selection**: The modal that appears after entering a phone number, showing adults and kids to select.
- **Mobile Check-in**: The interface on a mobile phone (use browser dev tools to simulate iPhone/Pixel) to show responsiveness.

### 2. Security & Safety
- **QR Code Checkout**: The modal showing the unique checkout QR code after a successful check-in.
- **Checkout Verification**: The screen asking for a checkout code (simulating a secure pickup).
- **Authorized Adults**: Tooltip or view showing who is authorized to pick up a child.

### 3. Admin Dashboard & Management
- **Admin Dashboard**: The main overview showing active events, attendance stats, and quick actions.
- **Event Management**: The list of events showing past and upcoming meetings.
- **Family Management**: The family list view, showing how easy it is to manage roster.
- **Family Detail View**: Editing a specific family, showing parents, kids, and medical notes.

### 4. Customization & Branding
- **Branding Settings**: The admin page where you set colors and logos, showing the white-label capabilities.
- **Dark Mode**: If applicable, or just the contrast of the UI.

### 5. Workflow Action Shots
- **Check-in Success**: The green success message/alert after checking in.
- **History/Reporting**: The attendance history view for a specific event or child.

### Tips for Great Screenshots
- **Hide Browser UI**: Press F11 for fullscreen or use browser developer tools "Capture screenshot" command.
- **Consistent Window Size**: Use a fixed resolution (e.g., 1280x800 for desktop, 375x812 for mobile) for all shots.
- **Clean Data**: The `screenshot_seed.py` script already provides clean "Troop 101" data, so you don't need to blur anything out.
