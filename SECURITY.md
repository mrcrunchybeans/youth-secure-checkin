# Trail Life Check-in System - Security Configuration

## Developer Password

A hard-coded developer password is set in `app.py` to ensure administrative access is always available:

```python
DEVELOPER_PASSWORD = 'dev2024secure'
```

**⚠️ IMPORTANT: Change this password before deploying to production!**

### How the Security System Works

1. **User Access Code**: Configurable through the Admin → Settings page. This is the password users will enter to access the system.

2. **Developer Password**: Hard-coded in `app.py`. This password always works, even if users change the access code.

### First Time Setup

1. Start the application: `python app.py`
2. Navigate to the login page
3. Enter the default access code: `changeme` OR the developer password from your `.env` file
4. **IMPORTANT**: Immediately go to Admin → Settings to change the access code to something secure
5. Also change the developer password in your `.env` file

### Changing the Developer Password

Edit `app.py` and update this line:

```python
DEVELOPER_PASSWORD = 'your-secure-password-here'
```

### Security Best Practices

- Change the developer password to something unique
- Share the user access code with authorized troop members only
- Update the access code periodically
- Keep the developer password private (for administrators only)
- Use the developer password only as a backup/recovery method
