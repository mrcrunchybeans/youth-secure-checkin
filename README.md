# Youth Secure Check-in

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.0](https://img.shields.io/badge/flask-3.0-green.svg)](https://flask.palletsprojects.com/)

A secure, flexible check-in/check-out system for youth organizations including Trail Life, scouting groups, churches, schools, and community programs. Features family management, event tracking, QR code checkout, label printing, and comprehensive security controls.

![Check-in Interface](docs/images/checkin-screenshot.png)

## 🌟 Key Features

### ✅ Check-in Management
- **Quick Check-in**: Fast family lookup by phone number (last 4 digits)
- **Event Selection**: Auto-populated from iCal feeds or manual entry
- **Kid Selection**: Multi-kid check-in with one tap
- **Status Tracking**: Real-time check-in/check-out status with timestamps
- **History View**: Complete check-in history with filtering

### 🔒 Security & Access Control
- **Multiple Authentication Levels**: App password, admin override, developer password
- **Checkout Codes**: QR codes or printed labels for secure pickup
- **Authorized Adults**: Track who can pick up each child
- **Developer Password**: Backup access via environment variable
- **Session Security**: Encrypted session management

### 👨‍👩‍👧‍👦 Family Management
- **Family Records**: Store families with adults and children
- **Group Assignment**: Organize by troop/den/class/group
- **CSV Import/Export**: Bulk import families, export for backup
- **Flexible Import**: Supports multiple CSV column name variations
- **Notes Field**: Track allergies, special needs, emergency info

### 🎨 Customizable Branding
- **Organization Details**: Name, type, group terminology
- **Color Schemes**: Primary, secondary, and accent colors
- **Logo Upload**: PNG, JPG, or SVG logos (auto-sized)
- **Favicon Support**: Custom browser tab icons
- **Setup Wizard**: First-run configuration guide

### 🎫 Checkout Options
- **QR Codes**: Display on screen for mobile scanning
- **Label Printing**: Brother QL series thermal printers
- **Dual Mode**: Support both QR and labels simultaneously
- **Custom Labels**: Three-line configurable text

### 📊 Event Management
- **iCal Import**: Auto-import from Google Calendar, Outlook, etc.
- **Manual Entry**: Create events directly in the system
- **Date Range Control**: Configurable event dropdown (±1 to ±12 months)
- **Event History**: Track attendance across events

### 💾 Backup & Restore
- **Configuration Export**: JSON backup of all settings
- **Configuration Import**: Restore settings from backup
- **Family Export**: CSV export of all family data
- **Disaster Recovery**: Complete backup/restore workflow

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git (for cloning the repository)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mrcrunchybeans/youth-secure-checkin.git
   cd youth-secure-checkin
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env and set:
   # SECRET_KEY - Generate with: python -c "import secrets; print(secrets.token_hex(32))"
   # DEVELOPER_PASSWORD - Set a secure backup admin password
   ```

5. **Initialize database**
   ```bash
   python -c "from app import init_db; init_db()"
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the system**
   - Open browser to `http://localhost:5000`
   - Complete the setup wizard
   - Start checking in families!

## 📖 Documentation

- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment instructions
- **[Security Guide](SECURITY.md)** - Security best practices and configuration
- **[Export Features](EXPORT_FEATURES.md)** - Backup and restore documentation
- **[FAQ](docs/FAQ.md)** - Frequently asked questions
- **[Wiki](../../wiki)** - Detailed guides and tutorials

## 🎯 Use Cases

This system is perfect for:
- **Trail Life USA** troops and outposts
- **Scouting organizations** (BSA, Girl Scouts, etc.)
- **Churches** (children's ministry, youth groups)
- **Schools** (after-school programs, clubs)
- **Community centers** (sports teams, activities)
- **Childcare facilities** (daycare, preschool)
- **Any organization** tracking youth attendance

## 🔧 Configuration

### First-Time Setup Wizard
On first run, you'll complete a 4-step setup wizard:
1. **Organization Details**: Name, type, group terminology
2. **Color Scheme**: Primary, secondary, accent colors
3. **Access Code**: Set the main login password
4. **Event Settings**: Configure event date range

### Admin Panel
Access comprehensive settings at `/admin`:
- **Families**: Add, edit, import, export family records
- **Events**: Import from iCal or create manually
- **Security**: Access codes, checkout codes, label settings
- **Branding**: Logo, favicon, colors, organization details
- **Backup & Restore**: Export/import configuration

## 📸 Screenshots

<details>
<summary>Click to view screenshots</summary>

### Check-in Interface
![Check-in](docs/images/checkin.png)

### Admin Panel
![Admin Panel](docs/images/admin-panel.png)

### Family Management
![Families](docs/images/families.png)

### Security Settings
![Security](docs/images/security.png)

### Branding Customization
![Branding](docs/images/branding.png)

</details>

## 🛠️ Technology Stack

- **Backend**: Flask 3.0 (Python web framework)
- **Database**: SQLite (embedded, zero-config)
- **Frontend**: Bootstrap 5.3 + vanilla JavaScript
- **QR Codes**: qrcode library with Pillow
- **Label Printing**: Brother QL series support
- **Calendar Import**: icalendar + pytz
- **CSV Processing**: Native Python csv module

## 📋 Requirements

See [requirements.txt](requirements.txt) for full dependency list:
- Flask==3.0.0
- icalendar==5.0.11
- requests==2.31.0
- qrcode==7.4.2
- Pillow==10.1.0
- python-dotenv==1.0.0
- gunicorn==21.2.0 (for production)

## 🐳 Deployment Options

### Option 1: Linux Server (Recommended)
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions:
- Ubuntu/Debian with systemd
- Nginx reverse proxy
- Gunicorn WSGI server
- SSL/TLS with Let's Encrypt

### Option 2: Docker (Coming Soon)
```bash
docker-compose up -d
```

### Option 3: Platform as a Service
- Heroku (use Procfile included)
- Railway
- Render
- Fly.io

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for Trail Life WI-4603, adapted for universal use
- Bootstrap for the responsive UI framework
- Flask community for excellent documentation
- All contributors and users providing feedback

## 💬 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Wiki**: [Project Wiki](../../wiki)
---

**Made with ❤️ for youth organizations everywhere**
- Event check-in/checkout
- QR code sharing for checkout
- Label printing (Dymo/Brother support)
- Admin override codes
- Check-in history and reporting
