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
