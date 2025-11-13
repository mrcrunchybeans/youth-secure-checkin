# Trail Life Troop Check-in System

A Flask-based check-in system for Trail Life troops with QR code checkout, label printing, and family management.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and configure your secrets:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `SECRET_KEY` - Flask session encryption key (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `DEVELOPER_PASSWORD` - Backup admin password for override features

**Important:** Never commit `.env` to version control! It's already in `.gitignore`.

### 3. Initialize Database

```bash
python -c "from app import init_db; init_db()"
```

### 4. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` to access the check-in system.

## Security

- The `.env` file contains sensitive credentials and should never be committed to Git
- `.env.example` is provided as a template (safe to commit)
- Developer password provides backup admin access and unlocks sensitive override settings
- Keep your `SECRET_KEY` secure - it encrypts session data

## Features

- Family and kid management
- Event check-in/checkout
- QR code sharing for checkout
- Label printing (Dymo/Brother support)
- Admin override codes
- Check-in history and reporting
