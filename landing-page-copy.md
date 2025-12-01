# Youth Secure Check-in - Landing Page Copy

## Hero Section

### Headline
**Secure Check-in Made Simple for Youth Organizations**

### Subheadline
A free, open-source check-in system designed for Trail Life, scouting groups, churches, schools, and youth programs. Self-host for complete control over your data.

### Call-to-Action Buttons
- **Try the Demo** → https://demo.youthcheckin.net/
- **View on GitHub** → https://github.com/mrcrunchybeans/youth-secure-checkin
- **Download Docker** → https://hub.docker.com/r/mrcrunchybeans/youth-secure-checkin

---

## Problem Statement

### "Managing youth check-ins shouldn't be complicated or expensive"

Most check-in systems are:
- ❌ Subscription-based with monthly fees
- ❌ Cloud-only with privacy concerns  
- ❌ Complicated to setup and maintain
- ❌ Limited customization options
- ❌ Vendor lock-in with your data

**There's a better way.**

---

## Solution Overview

### Youth Secure Check-in is different:

✅ **100% Free & Open Source** - No subscriptions, ever  
✅ **Self-Hosted** - Your data stays on your server  
✅ **Easy Setup** - Running in minutes with Docker  
✅ **Fully Customizable** - Your colors, logo, and branding  
✅ **Privacy First** - No tracking, no data collection  
✅ **Battle-Tested** - Used by real troops and organizations

---

## Key Features

### 🚀 Quick Check-in
**Fast family lookup by phone number** - Parents enter the last 4 digits of their phone, select their kids, and they're checked in. Takes less than 10 seconds.

### 👨‍👩‍👧‍👦 Family Management
**Everything in one place** - Store families with multiple kids, authorized adults, emergency contacts, allergies, and special needs. Import hundreds of families from CSV in seconds.

### 🔒 Secure Checkout
**QR codes or printed labels** - Generate unique QR codes for screen sharing or print thermal labels with Brother QL printers. Parents show the code at pickup for secure checkout.

### 📅 Smart Event Tracking
**Auto-import from calendars** - Connect your Google Calendar or Outlook via iCal feed. Events populate automatically, or create them manually in the admin panel.

### 🎨 Your Brand, Your Way
**Complete customization** - Upload your logo, set your colors (primary, secondary, accent), customize group terminology (Troop/Den, Class/Grade, Team, etc.).

### 💾 Backup & Recovery
**Never lose data** - Export everything to JSON and CSV. One-click restore from backup. Complete disaster recovery built-in.

### 📊 Check-in History
**Track attendance** - View complete check-in history with filtering by date, event, and family. Export to CSV for reporting.

### 🐳 Docker Ready
**Deploy anywhere** - Pre-built Docker images available. Runs on any server, Raspberry Pi, NAS, or cloud platform. Single command deployment.

---

## Perfect For

### Trail Life USA
Built by a Trail Life troop, for Trail Life troops. Handles troops, patrols, and Trail Life terminology out of the box.

### Boy Scouts & Girl Scouts
Track dens, patrols, and troops. Manage merit badge events, camping trips, and weekly meetings.

### Churches
Perfect for children's ministry, youth groups, Sunday school, and VBS. Track classes and age groups.

### Schools & After-School Programs
Manage clubs, sports teams, and activities. Track attendance for liability and funding.

### Community Centers
Youth sports, art classes, tutoring programs, and recreational activities.

### Any Youth Organization
Flexible enough for any group that needs secure check-in and attendance tracking.

---

## How It Works

### 1. Deploy in Minutes
```bash
# Create a directory and required folders
mkdir youth-checkin && cd youth-checkin
mkdir -p data uploads

# Download docker-compose.yml
curl -O https://raw.githubusercontent.com/mrcrunchybeans/youth-secure-checkin/master/docker-compose.yml

# Create .env file
echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
echo "DEVELOPER_PASSWORD=your-secure-password" >> .env

# Start the application
docker compose up -d
```
Access at http://localhost:5000 and complete the 4-step setup wizard.

### 2. Import Your Families
Upload a CSV with families and kids, or add them manually. Import from spreadsheets, membership systems, or registration forms.

### 3. Connect Your Calendar
Add your Google Calendar or Outlook iCal URL. Events auto-populate in the check-in dropdown.

### 4. Start Checking In
Parents look up their family, select kids, choose the event, and tap check-in. That's it.

### 5. Secure Checkout
Display QR code on screen or print labels. Parents show code at pickup for secure checkout with timestamps.

---

## Technical Details

### Built With Modern, Reliable Technology
- **Backend**: Flask 3.0 (Python)
- **Database**: SQLite (embedded, zero-config)
- **Frontend**: Bootstrap 5.3 + vanilla JavaScript
- **No external dependencies** for core functionality

### Self-Hosted = Your Control
- Run on your own server, laptop, or Raspberry Pi
- No internet required (except for iCal import)
- All data stored locally in SQLite
- No phone-home, no tracking, no analytics

### Security Features
- **Multi-level authentication**: App password, admin override, developer password
- **Encrypted sessions**: Flask session management with secret key
- **Secure checkout codes**: Unique QR codes or printed labels per kid
- **Authorized adults tracking**: Know who can pick up each child
- **Developer password**: Emergency access via environment variable

### Deployment Options
- **Docker** (recommended): One command deployment
- **Linux server**: systemd service with Nginx reverse proxy
- **Windows**: Run directly with Python
- **Cloud platforms**: Heroku, Railway, Render, Fly.io
- **NAS devices**: Synology, QNAP with Docker support

---

## Demo Access

### Try It Now - No Installation Required

**Demo URL**: https://demo.youthcheckin.net/

**Demo Credentials**:
- **Access Code**: `demo123` or `demo2025`
- **Admin Panel**: Username `demo`, Password `demo123`

**Test Phone Numbers** (for family lookup):
- 555-0101 (Johnson family - 2 kids)
- 555-0102 (Smith family - 1 kid)
- 555-0103 (Williams family - 2 kids)
- 555-0104 (Brown family - 1 kid)
- 555-0105 (Garcia family - 3 kids)
- 555-0106 (Martinez family - 1 kid)
- 555-0107 (Anderson family - 2 kids)
- 555-0108 (Taylor family - 1 kid)

**Note**: Demo data resets every 24 hours automatically.

---

## Installation

### Option 1: Docker Compose (Recommended)

```bash
# Create a directory and required folders
mkdir youth-checkin && cd youth-checkin
mkdir -p data uploads

# Download docker-compose.yml
curl -O https://raw.githubusercontent.com/mrcrunchybeans/youth-secure-checkin/master/docker-compose.yml

# Create .env file with your secrets
echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
echo "DEVELOPER_PASSWORD=your-secure-password" >> .env

# Start the application
docker compose up -d

# Verify it's running
docker compose logs
```

Access at http://localhost:5000

### Option 2: Docker Compose (Custom YAML)

```yaml
services:
  web:
    image: mrcrunchybeans/youth-secure-checkin:latest
    container_name: youth-checkin
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DEVELOPER_PASSWORD=${DEVELOPER_PASSWORD}
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
    restart: unless-stopped
```

**Important:** Create a `.env` file first with your secrets:
```bash
echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
echo "DEVELOPER_PASSWORD=your-secure-password" >> .env
```

Run with: `docker compose up -d`

**Note:** Use `docker compose` (with space), not `docker-compose` (with hyphen).

### Option 3: Python (Direct)

```bash
# Clone repository
git clone https://github.com/mrcrunchybeans/youth-secure-checkin.git
cd youth-secure-checkin

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" > .env
echo "DEVELOPER_PASSWORD=your-secure-password" >> .env

# Run
python app.py
```

Access at http://localhost:5000

---

## Pricing

### Free Forever

This is **100% free and open-source software** under the MIT License.

**What you get**:
- ✅ All features, no limitations
- ✅ Unlimited families and events
- ✅ Unlimited check-ins
- ✅ Complete source code
- ✅ Self-host anywhere
- ✅ Modify and customize
- ✅ Use commercially
- ✅ No attribution required

**What it costs**:
- ❌ No subscription fees
- ❌ No per-user charges
- ❌ No feature paywalls
- ❌ No support contracts required

**Your only costs**:
- Server/hosting (can run on existing hardware)
- Optional: Domain name (~$10/year)
- Optional: SSL certificate (free with Let's Encrypt)

---

## Documentation

### Complete Guides Available

- **[README](https://github.com/mrcrunchybeans/youth-secure-checkin/blob/master/README.md)** - Quick start and overview
- **[Docker Guide](https://github.com/mrcrunchybeans/youth-secure-checkin/blob/master/DOCKER.md)** - Complete containerized deployment
- **[Deployment Guide](https://github.com/mrcrunchybeans/youth-secure-checkin/blob/master/DEPLOYMENT.md)** - Production server setup
- **[Security Guide](https://github.com/mrcrunchybeans/youth-secure-checkin/blob/master/SECURITY.md)** - Best practices and hardening
- **[FAQ](https://github.com/mrcrunchybeans/youth-secure-checkin/blob/master/docs/FAQ.md)** - Common questions answered

---

## Support & Community

### Get Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community help
- **Documentation**: Comprehensive guides and tutorials
- **Demo Instance**: Try before you deploy

### Contributing

This is an open-source project. Contributions welcome!

- Report bugs and request features
- Submit pull requests
- Improve documentation
- Share your deployment stories

---

## Real-World Usage

### Built for Trail Life WI-4603

This system was created by a Trail Life troop leader frustrated with expensive, complicated check-in solutions. After building it for his own troop, he open-sourced it so other youth organizations could benefit.

**What makes it different**:
- Built by someone who uses it weekly
- Designed for actual check-in workflows
- Tested with real families and events
- Refined based on volunteer feedback
- No venture capital, no profit motive
- Just a good tool, shared freely

---

## System Requirements

### Server Requirements
- **OS**: Linux, Windows, macOS, or Docker-capable NAS
- **RAM**: 512 MB minimum (1 GB recommended)
- **Storage**: 100 MB + data storage
- **Python**: 3.10 or higher (if running without Docker)
- **Network**: Local network or internet access

### Supported Browsers
- Chrome, Firefox, Safari, Edge (modern versions)
- Mobile browsers (iOS Safari, Android Chrome)
- Tablets and touch devices supported

### Optional Hardware
- **Label Printer**: Brother QL series (QL-700, QL-800, QL-820NWB)
- **QR Scanner**: Any camera-equipped device or dedicated scanner

---

## Frequently Asked Questions

### Is this really free?
Yes. MIT licensed, no strings attached. Use it forever, modify it, even sell it if you want.

### Do I need to be technical to use this?
Basic computer skills required. If you can install Docker or run Python, you can deploy this. Our guides walk you through everything.

### Can I use this for my school/church/organization?
Absolutely! It's designed to be flexible. Customize the terminology, branding, and workflow to fit your needs.

### What about data privacy?
Your data never leaves your server. No cloud sync, no telemetry, no tracking. You control everything.

### Can I run this on a Raspberry Pi?
Yes! Works great on Raspberry Pi 3 or newer with Docker installed.

### What if I need help?
GitHub Issues and Discussions are monitored. The documentation is comprehensive. The demo lets you try before deploying.

### Can I modify the code?
Yes! MIT license means you can modify anything. Fork it, customize it, make it your own.

### Is there a mobile app?
No separate app needed. The web interface is mobile-responsive and works great on phones and tablets.

### What about HTTPS/SSL?
Production deployment guide includes Let's Encrypt SSL setup with Nginx reverse proxy (free).

### Can multiple people use it simultaneously?
Yes. It's a web app. As many devices as you want can connect at once.

---

## Get Started Today

### 1. Try the Demo
**https://demo.youthcheckin.net/**  
See it in action with pre-populated data. No account needed.

### 2. View the Code
**https://github.com/mrcrunchybeans/youth-secure-checkin**  
Read the docs, check the code, star the repo.

### 3. Deploy Your Own
**https://hub.docker.com/r/mrcrunchybeans/youth-secure-checkin**  
Pull the Docker image and run in minutes.

---

## Footer

### Youth Secure Check-in
A free, open-source check-in system for youth organizations.

**Links**:
- [GitHub Repository](https://github.com/mrcrunchybeans/youth-secure-checkin)
- [Docker Hub](https://hub.docker.com/r/mrcrunchybeans/youth-secure-checkin)
- [Live Demo](https://demo.youthcheckin.net/)
- [Documentation](https://github.com/mrcrunchybeans/youth-secure-checkin/blob/master/README.md)
- [Issue Tracker](https://github.com/mrcrunchybeans/youth-secure-checkin/issues)

**License**: MIT License - Use freely, modify freely, no attribution required.

**Made with ❤️ for youth organizations everywhere**

---

## Social Proof Section (Optional - Add if you have testimonials)

### Used By Organizations Like Yours

> "Saved us $500/year in subscription fees and gives us complete control over our data."  
> — Trail Life Troop Leader

> "Setup took 15 minutes. We were checking in families that same day."  
> — Church Youth Director

> "Finally, a check-in system that doesn't require an IT degree to configure."  
> — After-School Program Coordinator

*(Replace with real testimonials when available)*

---

## Comparison Section (Optional)

### How We Compare

| Feature | Youth Secure Check-in | Typical SaaS Solution |
|---------|----------------------|----------------------|
| **Cost** | $0 forever | $20-100/month |
| **Data Privacy** | Your server only | Their cloud |
| **Customization** | Fully customizable | Limited options |
| **Setup Time** | 5-15 minutes | Hours of training |
| **Vendor Lock-in** | None | Export fees |
| **Internet Required** | No (except iCal) | Yes always |
| **Source Code** | Fully open | Closed/proprietary |
| **Feature Limits** | None | Tiered pricing |

---

## Call-to-Action (Final)

### Ready to Take Control of Your Check-ins?

**Try the demo** → https://demo.youthcheckin.net/  
**View on GitHub** → https://github.com/mrcrunchybeans/youth-secure-checkin  
**Deploy with Docker** → https://hub.docker.com/r/mrcrunchybeans/youth-secure-checkin

**No signup required. No credit card. No commitment. Just download and run.**

---

## SEO Keywords (For Meta Tags)

youth check-in system, trail life check-in, scout check-in software, church check-in, free check-in system, self-hosted check-in, open source attendance, youth organization software, secure checkout, qr code check-in, family check-in, event attendance tracking, docker check-in app, privacy-focused check-in, non-profit check-in solution
