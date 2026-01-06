# Release Notes - v1.0.3

## Date: January 5, 2026

## New Features

### 🔐 Comprehensive Password Recovery System

A complete password recovery system has been implemented to help administrators recover access to their accounts without losing data. The system provides two complementary recovery methods:

#### Recovery Code Method
- **10 one-time use recovery codes** generated automatically during initial setup
- Codes are **12-character hexadecimal strings** (e.g., `A1B2C3D4E5F6`)
- Codes are **hashed with SHA256** before storage (not stored in plaintext)
- Each code can only be used **once** to reset the password
- Recovery codes are **universal** - work for any organization type (troops, churches, schools, teams, etc.)

#### Email Recovery Method
- Optional **email-based password recovery** for convenience
- Requires SMTP to be configured in Admin → Email Settings
- Temporary recovery codes are sent via email with **10-minute expiration**
- Email address is configurable in Admin → Security settings

#### Features
- **Secure password reset** with minimum 8-character requirement
- **Session-based protection** - password reset requires prior recovery verification
- **Admin control panel** for managing recovery codes and recovery email
- **Code regeneration** - admins can generate new codes anytime (invalidates old codes)
- **Code status tracking** - shows count of unused codes remaining (0-10)
- **Download/Print codes** - users can securely save recovery codes as PDF or text file
- **Responsive interface** - works on desktop, tablet, and mobile devices

### User Experience Improvements

#### For First-Time Users
1. Setup wizard now includes optional recovery email field
2. After setup, recovery codes are displayed with options to:
   - Print codes for safe storage
   - Download as TXT file
   - Copy individual codes to clipboard

#### For Existing Users Who Lost Password
1. Click "Lost your access code?" link on login page
2. Choose recovery method:
   - **Recovery Code**: Enter one of the 10 saved codes
   - **Email Recovery**: Request temporary code via email (if SMTP configured)
3. Verify recovery method
4. Create new password
5. Log back in

#### For Administrators
1. View unused recovery codes count in Admin → Security
2. Update recovery email address
3. Generate new recovery codes (invalidates old ones)
4. View complete list of current codes

## Technical Details

### Database Changes
- **New table**: `recovery_codes` 
  - Stores hashed recovery codes
  - Tracks usage status (used/unused)
  - Records timestamps for created and used dates
  - Indexed for performance

### New Routes
- `GET/POST /forgot-password` - Recovery method selection and code/email entry
- `GET/POST /reset-password` - Password reset form (after recovery verification)
- `GET /recovery-codes` - Display recovery codes
- `POST /admin/regenerate-recovery-codes` - Generate new codes

### New Templates
- `templates/forgot_password.html` - Recovery method selection
- `templates/reset_password.html` - Password reset form
- `templates/recovery_codes.html` - Display and manage codes

### Modified Templates
- `templates/login.html` - Added "Lost your access code?" link
- `templates/setup.html` - Added recovery email field
- `templates/admin/security.html` - Added password recovery management section

### New Utility Functions
- `generate_recovery_codes()` - Create 10 new recovery codes
- `verify_recovery_code(code)` - Validate code and mark as used
- `get_recovery_codes_count()` - Get count of unused codes
- `get_recovery_email()` / `set_recovery_email(email)` - Manage recovery email

## Security Enhancements

✅ **Code Security**
- Recovery codes hashed with SHA256 before storage
- One-time use enforcement in database
- No codes stored in plaintext

✅ **Password Security**
- Passwords hashed with pbkdf2:sha256
- Minimum 8-character requirement
- Password confirmation validation
- Automatic session clearing after reset

✅ **Session Security**
- Password reset requires prior recovery verification
- Session flags prevent unauthorized resets
- Email recovery codes expire after 10 minutes

✅ **Optional Features**
- Email recovery only works if SMTP is configured
- Recovery email is optional
- Graceful fallback if email service unavailable

## Compatibility

✅ **Backward Compatible**
- Existing installations continue to work without changes
- Recovery feature is opt-in for existing users
- All existing password functionality preserved

✅ **Organization Types**
- Generic recovery code format (no organization-specific prefixes)
- Works for troops, churches, schools, teams, groups, and any other organization

## Breaking Changes

❌ **None** - This release is fully backward compatible

## Migration Notes

### For New Installations
- Recovery codes are automatically generated during setup
- Recovery email field is optional during setup
- No manual migration needed

### For Existing Installations
1. Apply database schema changes (recovery_codes table created automatically)
2. Deploy updated code
3. Existing users can:
   - Use "Lost your access code?" link if they forget password
   - Regenerate recovery codes from Admin → Security panel
   - Set recovery email in Admin → Security panel

### Installation Steps
1. Pull latest code from GitHub
2. Restart application (database schema auto-creates if needed)
3. Test recovery flow: 
   - Visit `/forgot-password`
   - Verify both recovery methods appear correctly
   - Test password reset with recovery code

## Documentation

Three comprehensive documentation files have been included:

1. **PASSWORD_RECOVERY_IMPLEMENTATION.md**
   - Complete implementation details
   - Database schema
   - All routes and functions
   - Configuration options

2. **PASSWORD_RECOVERY_QUICK_REFERENCE.md**
   - Quick reference guide
   - System architecture diagrams
   - User flow examples
   - Troubleshooting guide

3. **PASSWORD_RECOVERY_COMPLETE.md**
   - Full implementation summary
   - Code examples
   - Testing checklist
   - Deployment instructions

## Testing

The password recovery system has been tested for:

✅ Recovery code generation (correct format, hashing)
✅ Code verification (valid/invalid codes, one-time use)
✅ Password reset (minimum length, confirmation matching)
✅ Email recovery (sends emails, codes expire correctly)
✅ Admin management (code count tracking, regeneration)
✅ Session security (must verify recovery before reset)
✅ Mobile responsiveness (works on all device sizes)

## Known Issues

None at this time.

## Future Enhancements

Planned for future releases:
- Rate limiting on password reset attempts
- Password reset audit logging
- Security questions as alternative recovery
- SMS-based recovery codes
- TOTP/authenticator app support
- Hardware key/FIDO2 support

## Contributors

This release implements the password recovery system requested by users who needed a secure way to regain access if they forget their admin password.

## Installation & Upgrade

### New Installation
Password recovery is enabled automatically during setup.

### Upgrade from Previous Version
1. Pull latest code
2. Restart application
3. Recovery codes table auto-creates if needed
4. No data loss or downtime required

## Support

For questions or issues with the password recovery system:
1. Check PASSWORD_RECOVERY_QUICK_REFERENCE.md for troubleshooting
2. Review PASSWORD_RECOVERY_IMPLEMENTATION.md for technical details
3. Visit Admin → Security for configuration options

## Summary

This release adds enterprise-grade password recovery capabilities to Youth Secure Check-in, ensuring that administrators never permanently lose access to their accounts. The system balances security (hashed codes, one-time use, encryption) with usability (multiple recovery methods, simple interface, clear instructions).
