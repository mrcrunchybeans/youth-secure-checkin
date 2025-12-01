# Website Copy for YouthCheckIn Landing Page

## Hero Section

### Main Headline
**Secure Check-in Made Simple for Youth Organizations**

### Subheadline
A free, open-source check-in system designed for Trail Life, scouting groups, churches, schools, and youth programs. Self-host for complete control over your data.

### Hero Description
Fast family lookup by phone number, QR code checkout, and Brother QL thermal label printing. Deploy in minutes with Docker, customize your branding, import families from CSV, and connect your calendar for automatic event population.

### Call-to-Action Buttons
- **Try the Live Demo** → https://darkorchid-alpaca-670675.hostingersite.com/
- **Download Free (GitHub)** → https://github.com/mrcrunchybeans/youth-secure-checkin
- **View on Docker Hub** → https://hub.docker.com/r/mrcrunchybeans/youth-secure-checkin

---

## Problem Statement Section

### Headline
**Managing youth check-ins shouldn't be complicated or expensive**

### The Problem
Most check-in systems are:
- ❌ Subscription-based with monthly fees ($20-100/month)
- ❌ Cloud-only with privacy concerns about your family data
- ❌ Complicated to setup and maintain
- ❌ Limited customization options
- ❌ Vendor lock-in with your attendance data

### The Solution
**YouthCheckIn is different:**
- ✅ **100% Free & Open Source** - No subscriptions, ever (MIT License)
- ✅ **Self-Hosted** - Your data stays on your server, complete privacy
- ✅ **Easy Setup** - Running in minutes with Docker
- ✅ **Fully Customizable** - Your colors, logo, and terminology
- ✅ **Privacy First** - No tracking, no data collection, no phone-home
- ✅ **Battle-Tested** - Built by a Trail Life troop leader, used by real organizations

---

## Key Features Section

### Section Headline
**Key Features That Make Check-in Easy**

### Feature 1: 🚀 Quick Check-in
**Fast family lookup by phone number** - Parents enter the last 4 digits of their phone, select their kids from the list, choose the event, and tap check-in. Takes less than 10 seconds per family.

### Feature 2: 👨‍👩‍👧‍👦 Family Management
**Everything in one place** - Store families with multiple kids, authorized pickup adults, emergency contacts, allergies, and special needs notes. Import hundreds of families from CSV in seconds with flexible column name support.

### Feature 3: 🔒 Secure Checkout
**QR codes or printed labels** - Generate unique QR codes for screen sharing or print thermal labels with Brother QL (QL-700, QL-800, QL-820NWB) or Dymo LabelWriter printers. Parents show the code at pickup for secure checkout with timestamps.

### Feature 4: 📅 Smart Event Tracking
**Auto-import from calendars** - Connect your Google Calendar or Outlook via iCal feed URL. Events populate automatically in the check-in dropdown, or create them manually in the admin panel. Configure date range from ±1 to ±12 months.

### Feature 5: 🎨 Your Brand, Your Way
**Complete customization** - Upload your logo (PNG, JPG, SVG), set your colors (primary, secondary, accent), customize group terminology (Troop/Den, Class/Grade, Team, etc.). Add your organization name and details.

### Feature 6: 💾 Backup & Recovery
**Never lose data** - Export everything to JSON and CSV. One-click restore from backup files. Complete disaster recovery workflow built-in. Export family data, check-in history, and all settings.

### Feature 7: 📊 Check-in History
**Track attendance** - View complete check-in history with filtering by date, event, and family. See who's currently checked in, who's been picked up, and who still needs follow-up. Export to CSV for reporting and analysis.

### Feature 8: 🐳 Docker Ready
**Deploy anywhere** - Pre-built Docker images available on Docker Hub. Runs on any server, Raspberry Pi 3+, NAS (Synology/QNAP), VPS, or cloud platform. Single command deployment with docker-compose.

---

## Perfect For Section

### Section Headline
**Perfect for Trail Life, Scouts, Churches & Schools**

### Trail Life USA & Scouting
Built by a Trail Life troop, for Trail Life troops. Handles troops, patrols, dens, and Trail Life terminology out of the box. Perfect for Boy Scouts, Girl Scouts, weekly meetings, camping trips, and merit badge events.

### Churches & Youth Groups
Perfect for children's ministry, youth groups, Sunday school, VBS (Vacation Bible School), Wednesday night programs, and special events. Track classes and age groups easily.

### Schools & After-School Programs
Manage clubs, sports teams, art classes, tutoring programs, and recreational activities. Track attendance for liability and funding requirements.

### Community Centers & Any Youth Organization
Youth sports leagues, community programs, daycare facilities, summer camps. Flexible enough for any group that needs secure check-in and attendance tracking.

---

## How It Works Section

### Section Headline
**How It Works - Get Started in 5 Simple Steps**

### Step 1: Deploy in Minutes
```bash
docker pull mrcrunchybeans/youth-secure-checkin:latest
docker-compose up -d
```
Access at http://localhost:5000 and complete the 4-step setup wizard (organization details, colors, access code, event settings).

### Step 2: Import Your Families
Upload a CSV with families and kids, or add them manually one at a time. Import from spreadsheets, membership systems, or registration forms. Flexible column name matching (phone, phone_number, mobile all work).

### Step 3: Connect Your Calendar
Add your Google Calendar or Outlook iCal URL in the admin panel. Events automatically populate in the check-in dropdown. Or create events manually if you prefer.

### Step 4: Start Checking In
Parents look up their family by last 4 digits of phone, select their kids from the list, choose the event, and tap check-in. Status updates in real-time.

### Step 5: Secure Checkout
Display QR code on screen or print thermal labels. Parents show code at pickup for secure checkout with automatic timestamps. Verify authorized adults can pick up each child.

---

## Live Demo Section

### Section Headline
**Try the Demo - No Installation Required**

### Demo Access Information
**Demo URL:** https://darkorchid-alpaca-670675.hostingersite.com/

**Three Levels of Access:**

1. **Check-in Page** (parent/volunteer view):
   - Enter access code: `demo123` or `demo2025` (either works)
   - This is what parents use to check in their kids

2. **Admin Panel** (manage families, events, history):
   - Click "Admin" link at bottom of page
   - Enter admin password: `demo123`
   - Manage families, events, branding, and view check-in history

3. **Developer Settings** (email configuration, advanced settings):
   - Inside Admin Panel, go to Security or Email Settings
   - Click "Unlock" and enter developer password: `demo2025`
   - Configure SMTP/email settings and override password (advanced features)

**Test Phone Numbers** (for family lookup on check-in page):
- **555-0101** - Johnson family (2 kids: Emily and Michael)
- **555-0102** - Smith family (1 kid: Sarah)
- **555-0103** - Williams family (2 kids: David and Jessica)
- **555-0104** - Brown family (1 kid: James)
- **555-0105** - Garcia family (3 kids: Sofia, Carlos, Isabella)
- **555-0106** - Martinez family (1 kid: Emma)
- **555-0107** - Anderson family (2 kids: Olivia and Noah)
- **555-0108** - Taylor family (1 kid: Ava)

**What's Pre-Loaded:**
- 8 families with realistic data
- 15 scouts/kids with various notes (allergies, special needs)
- 6 events (past meetings, camping trip, upcoming activities)
- Check-in history for past events with realistic timestamps
- Pre-configured settings for Demo Troop 4603

**Note:** Demo data automatically resets every 24 hours to keep it fresh for new users.

---

## Technical Details Section

### Section Headline
**Built With Modern, Reliable Technology**

### Tech Stack
- **Backend:** Flask 3.0 (Python web framework)
- **Database:** SQLite (embedded, zero-configuration required)
- **Frontend:** Bootstrap 5.3 + vanilla JavaScript (no complex frameworks)
- **QR Codes:** qrcode library with Pillow for image generation
- **Label Printing:** Brother QL series and Dymo LabelWriter printer support
- **Calendar Import:** icalendar library + pytz for timezone handling
- **CSV Processing:** Native Python csv module
- **Production Server:** Gunicorn WSGI server

### Why Self-Hosting Matters
- **Complete Control:** Run on your own server, laptop, or Raspberry Pi
- **Privacy First:** No internet required (except for optional iCal import)
- **All Data Local:** Everything stored locally in SQLite database
- **No Tracking:** No phone-home, no analytics, no external dependencies
- **Offline Capable:** Works on local network without internet

### Security Features
- **Multi-level authentication:** App password, admin override code, developer password
- **Encrypted sessions:** Flask session management with configurable secret key
- **Secure checkout codes:** Unique QR codes or printed labels per child per event
- **Authorized adults tracking:** Database of who can pick up each child
- **Developer password:** Emergency access via environment variable (.env file)
- **Password hashing:** PBKDF2 SHA256 for admin password storage

---

## Installation & Deployment Section

### Section Headline
**Three Ways to Deploy**

### Option 1: Docker (Recommended)
```bash
# Pull the latest image
docker pull mrcrunchybeans/youth-secure-checkin:latest

# Run with docker-compose
docker-compose up -d

# Access at http://localhost:5000
```

**Advantages:** One command deployment, automatic updates, isolated environment, works everywhere Docker runs.

### Option 2: Docker Compose (Full Stack)
```yaml
version: '3.8'
services:
  web:
    image: mrcrunchybeans/youth-secure-checkin:latest
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=your-secret-key-here
      - DEVELOPER_PASSWORD=your-dev-password
    volumes:
      - ./data:/app/data
      - ./uploads:/app/static/uploads
    restart: unless-stopped
```

### Option 3: Python (Direct Installation)
```bash
# Clone repository
git clone https://github.com/mrcrunchybeans/youth-secure-checkin.git
cd youth-secure-checkin

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" > .env
echo "DEVELOPER_PASSWORD=your-secure-password" >> .env

# Run application
python app.py
```

### System Requirements
**Minimum:**
- 512 MB RAM
- 100 MB storage (plus data)
- Python 3.10+ (if not using Docker)
- Any modern web browser

**Recommended:**
- 1 GB RAM
- 1 GB storage
- Docker 20+ with Docker Compose
- Nginx reverse proxy for production
- Let's Encrypt SSL certificate (free)

**Works Great On:**
- Raspberry Pi 3 or newer
- Cheap VPS (DigitalOcean, Linode, Vultr - $5-10/month)
- Proxmox LXC containers
- Synology/QNAP NAS with Docker
- Home lab servers or Intel NUCs
- Cloud platforms (Heroku, Railway, Render, Fly.io)

---

## Pricing Section

### Section Headline
**Free Forever - Really**

### Open Source (Self-Hosted)
**$0/month - Always Free**

This is 100% free and open-source software under the MIT License.

**What you get:**
- ✅ All features, no limitations or paywalls
- ✅ Unlimited families, kids, and events
- ✅ Unlimited check-ins and devices
- ✅ Complete source code access
- ✅ Self-host anywhere (your choice of server)
- ✅ Modify and customize freely
- ✅ Use commercially without restrictions
- ✅ No attribution required

**What it costs:**
- ❌ No subscription fees ever
- ❌ No per-user charges
- ❌ No feature limits based on tier
- ❌ No support contracts required

**Your only costs:**
- Server/hosting (can run on existing hardware you already own)
- Optional: Domain name (~$10/year)
- Optional: SSL certificate (free with Let's Encrypt)

### Managed Hosting (Optional)
**$10/month or $100/year**

For organizations that want a hands-off, turnkey solution.

**Includes:**
- Fully hosted YouthCheckIn instance on our servers
- Custom domain name setup*
- Unlimited events, kids, and devices
- Automatic software updates
- Daily backups with retention
- Zero maintenance required
- Email support (48-72 hour response time)
- 99.9% uptime SLA

**Optional Support Package: +$5/month**
- Priority email support (12-24 hour response)
- Onboarding call to help setup
- Help setting up rooms, events, families
- Assistance with data migration/import
- Troubleshooting and training support

**Supporter Tier: $20/month**
Same features—just a way for churches to support development and sponsor other ministries.

### Fair-Use Policy
YouthCheckIn does not limit the number of kids, events, or devices. To keep the service reliable for all hosted customers, we may reach out if usage becomes extremely high (e.g., hundreds of check-ins per hour or automated/bot usage). In the rare event this happens, we'll work with you to find a solution, including a dedicated instance if needed. We exist to support your ministry—not limit it.

---

## Why Organizations Trust YouthCheckIn

### 🔍 Transparent
Open source code on GitHub. No hidden features, no tricks, no vendor lock-in. You can read every line of code and verify exactly what it does.

### 🧭 Simple
Check-in takes 10 seconds per family. Volunteers can be trained in minutes. Clean interface works on phones, tablets, and laptops. No complex configuration required.

### 🛡️ Safe
Built carefully to help ensure the right person picks up the right child. Unique checkout codes, authorized adult tracking, timestamps for accountability.

### 💻 Self-Host Friendly
One-command Docker deployment. Runs effortlessly on Raspberry Pi 3+, NAS devices, VPS servers, or home lab environments. Python 3.10+ also supported.

### 🎨 Customizable
Upload your logo, set your brand colors, customize terminology for your organization type (troops, classes, teams, etc.). Make it yours.

### 📦 Export Everything
Your data is never locked in. Export to CSV and JSON anytime. Complete backup and restore workflow. Move to another system if you want (but you won't want to).

---

## Origin Story Section

### Section Headline
**Built for Trail Life WI-4603 by a Troop Leader**

### The Story
This system was created by a Trail Life troop leader who was frustrated with expensive, complicated check-in solutions that cost $50-100/month and required complex training. After building it for his own troop's weekly meetings and camping trips, he realized other youth organizations faced the same problems.

Instead of starting a company and charging for it, he open-sourced the entire project so any Trail Life troop, Boy Scout den, church youth group, or after-school program could use it for free. Forever.

**What makes it different:**
- Built by someone who uses it every week
- Designed for actual check-in workflows (not theoretical ones)
- Tested with real families and real events
- Refined based on volunteer feedback
- No venture capital, no profit motive
- Just a good tool, shared freely

---

## FAQ Section

### Is the open-source version really free forever?
Yes. MIT licensed, no strings attached. The code belongs to the community. Use it forever, modify it however you want, even sell it if you wish. Hosting is simply optional for organizations that want a turnkey solution without managing servers.

### Do you store any children's data?
Not on the self-hosted open-source version—everything stays on YOUR server. For managed hosting customers, we store only what your organization enters, securely encrypted, with daily backups. We never sell or share data. Export everything anytime.

### Can we export our data?
Always, anytime. Export families to CSV, check-in history to CSV, and complete configuration to JSON. Your data is never locked in. Complete backup/restore workflow built-in.

### Do we need special hardware?
**To use the system:** Any device with a web browser—phone, tablet, laptop, or desktop computer.

**To self-host:** Any Docker-capable device (Raspberry Pi 3+, NAS, VPS, home server) or Python 3.10+ on Linux/Windows/Mac.

**Optional:** Brother QL series thermal printer for label printing (QL-700, QL-800, QL-820NWB models supported).

### What if our organization grows?
There are no caps or limits on families, kids, events, or devices. Growth is never penalized. The system scales from 10 kids to 500+ kids without additional cost or configuration.

### How long does setup take?
**Self-hosted Docker:** 5-15 minutes from first command to checking in your first family.
**Self-hosted Python:** 20-30 minutes including environment setup.
**Managed hosting:** We set it up for you, usually same business day.

### Can multiple devices use it simultaneously?
Yes. It's a web application. As many devices as you want can connect at once—check-in kiosk, admin tablet, leader's phone, all simultaneously.

### Does it work offline?
Mostly yes. Once deployed, it works on your local network without internet. The only internet-required feature is iCal calendar import. Everything else (check-in, checkout, admin) works offline.

### What about HTTPS/SSL?
Production deployment guide includes complete Let's Encrypt SSL setup with Nginx reverse proxy (free). Or use Cloudflare tunnels for zero-config HTTPS.

### Is there a mobile app?
No separate app needed. The web interface is fully mobile-responsive and works great on phones and tablets. Add to home screen for app-like experience.

### Can we customize the code?
Yes! MIT license means you can modify anything. Fork it, customize it, make it your own. Many organizations add custom features specific to their needs.

---

## Support & Community Section

### Section Headline
**Get Help & Contribute**

### Community Support
- **GitHub Issues:** Bug reports and feature requests → github.com/mrcrunchybeans/youth-secure-checkin/issues
- **GitHub Discussions:** Questions and community help → github.com/mrcrunchybeans/youth-secure-checkin/discussions
- **Documentation:** Comprehensive guides and tutorials included in repo
- **Live Demo:** Try before you deploy → darkorchid-alpaca-670675.hostingersite.com

### Contributing
This is an open-source project. Contributions welcome!
- Report bugs and request features
- Submit pull requests with improvements
- Improve documentation
- Share your deployment stories
- Help other users in discussions

### Documentation Included
- **README.md** - Quick start and overview
- **DOCKER.md** - Complete containerized deployment guide
- **DEPLOYMENT.md** - Production server setup instructions  
- **SECURITY.md** - Best practices and security hardening
- **FAQ.md** - Frequently asked questions answered
- **CLOUD_BACKUP_SETUP.md** - Google Drive backup integration

---

## Call-to-Action (Final)

### Section Headline
**Ready to Take Control of Your Check-ins?**

### Primary CTA
**Try the Live Demo** → https://darkorchid-alpaca-670675.hostingersite.com/  
See it in action with pre-populated data. No account needed. No credit card. Just try it.

### Secondary CTAs
**Download from GitHub** → https://github.com/mrcrunchybeans/youth-secure-checkin  
Read the docs, check the code, star the repo, fork it.

**Pull Docker Image** → https://hub.docker.com/r/mrcrunchybeans/youth-secure-checkin  
Pull the image and run in minutes. Production-ready containers.

**Contact About Hosting** → [Your contact method]  
Want us to host it for you? Let's talk about managed hosting options.

---

## Footer Content

### Tagline
**YouthCheckIn** - Secure check-in made simple for youth organizations.

### Quick Links
- [GitHub Repository](https://github.com/mrcrunchybeans/youth-secure-checkin)
- [Docker Hub](https://hub.docker.com/r/mrcrunchybeans/youth-secure-checkin)
- [Live Demo](https://darkorchid-alpaca-670675.hostingersite.com/)
- [Documentation](https://github.com/mrcrunchybeans/youth-secure-checkin/blob/master/README.md)
- [Issue Tracker](https://github.com/mrcrunchybeans/youth-secure-checkin/issues)
- [Community Discussions](https://github.com/mrcrunchybeans/youth-secure-checkin/discussions)

### Legal
**License:** MIT License - Use freely, modify freely, no attribution required.

**Made with ❤️ for youth organizations everywhere**

Open-source forever. Hosting optional.

© 2025 YouthCheckIn

---

## SEO Keywords for Meta Tags

youth check-in system, trail life check-in, scout check-in software, church check-in, free check-in system, self-hosted check-in, open source attendance, youth organization software, secure checkout, qr code check-in, family check-in, event attendance tracking, docker check-in app, privacy-focused check-in, non-profit check-in solution, boy scouts check-in, girl scouts check-in, children's ministry check-in, youth group check-in, after school program check-in

---

## Meta Description for SEO
Free, open-source check-in system for Trail Life, scouts, churches, schools & youth programs. Fast phone lookup, QR code checkout, self-hosted for complete privacy. Deploy in minutes with Docker.

---

## Social Media Sharing Text

### Twitter/X Post
🎯 Built a free, open-source check-in system for youth organizations!

✅ Fast phone lookup (10 sec check-in)
✅ QR code checkout
✅ Self-hosted (your data, your control)
✅ Docker deployment in minutes

Built for Trail Life, perfect for any youth program.

Try the demo → [link]

### Facebook/LinkedIn Post
I'm excited to share YouthCheckIn - a completely free, open-source check-in system I built for youth organizations like Trail Life, scouts, churches, and schools.

Why I built it:
Our troop was spending $100/month on complicated check-in software. I knew there had to be a better way.

What makes it different:
• 100% free forever (MIT license)
• Self-hosted for complete privacy
• Fast check-in (10 seconds per family)
• QR codes or thermal label printing
• Works on phones, tablets, laptops
• Deploy in minutes with Docker

Perfect for:
• Trail Life & scouting groups
• Church children's ministry
• After-school programs
• Sports teams and clubs
• Any youth organization

Try the live demo (no account needed): [demo link]
Download on GitHub: [github link]
Pull Docker image: [docker hub link]

Built by a troop leader, for troop leaders. Shared freely with everyone.

#YouthMinistry #OpenSource #TrailLife #Scouting #ChildrensMinistry #Docker
