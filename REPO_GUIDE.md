# Repository Documentation Guide

## Primary User Documentation

### Getting Started
- **README.md** - Main project overview, quick start, features
- **DOCKER_QUICKSTART.md** - Fast Docker deployment (5 minutes)
- **DOCKER.md** - Complete Docker deployment guide with all options
- **SECURITY.md** - Security best practices and configuration

### Deployment Guides
- **docker-compose.yml** - Production deployment configuration
- **docker-compose.demo.yml** - Demo/Portainer deployment configuration
- **DEPLOYMENT_CHECKLIST.md** - Production deployment checklist
- **Dockerfile** - Container build instructions

### Demo System
- **DOCKER_DEMO_README.md** - Demo mode documentation
- **DEMO_REFERENCE.md** - Quick reference for demo credentials
- **demo_seed.py** - Demo data seeding script
- **demo_reset_scheduler.py** - Auto-reset scheduler for demo mode
- **test_demo.py** - Demo validation tests

### Cloud Backup
- **CLOUD_BACKUP_SETUP_SECURE.md** - Complete cloud backup setup guide (Google Drive, Dropbox, OneDrive)
- **cloud_backup.py** - Cloud backup implementation

### Additional Documentation
- **CHANGELOG.md** - Version history and changes
- **CONTRIBUTING.md** - How to contribute to the project
- **LICENSE** - MIT License
- **docs/** - FAQ, Wiki, and images
- **WEBSITE_COPY.md** - Landing page copy for marketing site

### Build Scripts
- **build_demo.ps1** - PowerShell script to build demo (Windows)
- **build_demo.sh** - Bash script to build demo (Linux/Mac)

## Application Files

### Core Application
- **app.py** - Main Flask application (3700+ lines)
- **wsgi.py** - WSGI entry point for production
- **requirements.txt** - Python dependencies
- **requirements_label_printing.txt** - Optional label printer dependencies
- **schema.sql** - Database schema
- **__init__.py** - Python package marker

### Label Printing
- **label_printer.py** - Brother QL printer integration

### Static Assets
- **static/** - CSS, JavaScript, favicon, uploaded logos
- **templates/** - HTML templates (Jinja2)

### Testing
- **tests/test_app.py** - Application tests
- **test_demo.py** - Demo mode validation

## Configuration Files

- **.env.example** - Example environment variables
- **.env.docker** - Docker-specific environment template
- **.gitignore** - Git ignore rules
- **.dockerignore** - Docker ignore rules
- **Procfile** - Heroku/PaaS deployment configuration

## Not Tracked in Git

The following are excluded via .gitignore:

- **.env** - Your local environment variables (SECRET_KEY, DEVELOPER_PASSWORD)
- **data/** - SQLite database and data files
- **uploads/** - User-uploaded files (logos, etc.)
- **local-scripts/** - Personal development scripts
- **local-dev-files/** - Personal development files
- **landingpage.html** - WordPress landing page
- **landing-page-copy.md** - Landing page draft copy
- **WEBSITE_COPY.md** - Landing page final copy

## Documentation Organization

### Essential for All Users
1. README.md - Start here
2. DOCKER_QUICKSTART.md - Fastest way to deploy
3. SECURITY.md - Security configuration

### For Production Deployment
1. DOCKER.md - Full deployment guide
2. DEPLOYMENT_CHECKLIST.md - Deployment steps
3. docker-compose.yml - Production config

### For Demo/Testing
1. DOCKER_DEMO_README.md - Demo setup
2. docker-compose.demo.yml - Demo config
3. DEMO_REFERENCE.md - Demo credentials

### For Cloud Backup
1. CLOUD_BACKUP_SETUP_SECURE.md - Complete setup guide

### For Contributors
1. CONTRIBUTING.md - Contribution guidelines
2. CHANGELOG.md - Version history
3. docs/ - Additional documentation

## Recent Cleanup (Nov 2025)

Removed redundant documentation to streamline the repository:
- ❌ DOCKER_QUICK_START.md (duplicate)
- ❌ CLOUD_BACKUP_IMPLEMENTATION.md (technical internals)
- ❌ CLOUD_BACKUP_QUICKREF.md (redundant)
- ❌ CLOUD_BACKUP_SETUP.md (superseded by SECURE version)
- ❌ DOCKER_DEMO_IMPLEMENTATION.md (technical internals)
- ❌ SECURE_CREDENTIALS_SUMMARY.md (internal dev notes)

## Quick Reference

**New users?** → README.md → DOCKER_QUICKSTART.md  
**Production deployment?** → DOCKER.md → DEPLOYMENT_CHECKLIST.md  
**Demo mode?** → DOCKER_DEMO_README.md  
**Cloud backup?** → CLOUD_BACKUP_SETUP_SECURE.md  
**Security?** → SECURITY.md  
**Contributing?** → CONTRIBUTING.md
