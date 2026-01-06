# Password Recovery System Implementation

## Overview
A comprehensive password recovery system has been implemented for Youth Secure Check-in. This system provides two recovery methods:
1. **Recovery Codes**: 10 one-time use codes generated during setup
2. **Email Recovery**: Optional email-based recovery (requires SMTP configuration)

## Database Schema

### New Table: `recovery_codes`
```sql
CREATE TABLE IF NOT EXISTS recovery_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_hash TEXT UNIQUE NOT NULL,
    used INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    used_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_recovery_codes_used ON recovery_codes(used);
```

## Core Functions Added (app.py, lines 742-827)

### `generate_recovery_codes()`
- Generates 10 unique recovery codes in format: `XXXXXXXX` (12 random hexadecimal characters)
- Hashes codes using SHA256 before storage
- Stores in database with timestamps
- Returns list of unhashed codes for display to user

**Parameters**: None  
**Returns**: List of 10 code strings

```python
codes = generate_recovery_codes()
# Returns: ['A1B2C3D4E5F6', 'G7H8I9J0K1L2', ...]
```

### `verify_recovery_code(code)`
- Validates provided recovery code
- Checks if code exists and hasn't been used
- Marks code as used upon successful verification
- Returns True if valid, False otherwise

**Parameters**: `code` (string) - The recovery code to verify  
**Returns**: Boolean (True if valid and successfully marked as used)

```python
if verify_recovery_code('A1B2C3D4E5F6'):
    # User can now reset password
```

### `get_recovery_codes_count()`
- Returns count of unused recovery codes
- Helps admin monitor recovery code availability

**Parameters**: None  
**Returns**: Integer (0-10)

```python
unused = get_recovery_codes_count()
# Returns: 3 (meaning 3 codes remain)
```

### `get_recovery_email()` / `set_recovery_email(email)`
- Retrieves or stores the recovery email address
- Email is used for sending temporary recovery codes (if SMTP configured)

**Parameters**: `email` (string, optional) for set function  
**Returns**: String (email address) for get function

```python
current_email = get_recovery_email()
set_recovery_email('admin@example.com')
```

## Routes Added/Modified

### 1. `/forgot-password` (GET/POST)
**Purpose**: Entry point for password recovery  
**Methods**:
- GET: Display recovery method selection (code or email)
- POST: Process recovery method submission

**Features**:
- Tab-based interface for two recovery methods
- Recovery Code method: Direct code entry
- Email method: Verify email and send recovery code (if SMTP configured)
- Validates code immediately for code method
- Sets session flag `can_reset_password` on success

**Template**: `templates/forgot_password.html`

### 2. `/reset-password` (GET/POST)
**Purpose**: Reset password after recovery verification  
**Methods**:
- GET: Display password reset form
- POST: Update password

**Features**:
- Validates session flag (must use recovery first)
- Password validation (min 8 characters)
- Password confirmation matching
- Marks recovery code as used
- Redirects to login after successful reset

**Template**: `templates/reset_password.html`

### 3. `/recovery-codes` (GET)
**Purpose**: Display current recovery codes  
**Authentication**: Requires login (protected by @require_auth)

**Features**:
- Shows all 10 recovery codes (only if `initial_setup=True`)
- Displays count of unused codes
- Download as TXT file functionality
- Print-friendly formatting
- Copy-to-clipboard button for each code
- Integration with admin panel for code regeneration

**Template**: `templates/recovery_codes.html`

### 4. `/admin/regenerate-recovery-codes` (POST)
**Purpose**: Allow admin to generate new recovery codes  
**Authentication**: Requires login

**Features**:
- Clears all old recovery codes from database
- Generates new set of 10 codes
- Redirects to recovery codes display page
- Notifies user of new codes

## Admin Panel Integration

### Updated `/admin/security` route
Added to admin_security() function:
- Retrieves unused codes count
- Displays recovery email address
- Shows SMTP configuration status
- Passes data to template for UI rendering

**New Template Section**: `templates/admin/security.html`
Added "Password Recovery" card with:
- Unused codes display (X/10)
- Last generated date
- "Generate New Recovery Codes" button
- Recovery email input field
- SMTP status indicator
- Email save button

## Setup Flow Modification

### Updated `/setup` route (line 1275-1292)
**Changes**:
1. Calls `generate_recovery_codes()` after password setup
2. Collects optional recovery email from form
3. Stores recovery email if SMTP is configured
4. Redirects to `/recovery-codes?initial_setup=True` instead of login

### Updated `templates/setup.html`
Added recovery email field:
- Optional email input with validation
- Help text explaining purpose
- Shown after admin password fields

## Templates Created

### 1. `templates/forgot_password.html`
- Professional login-style interface
- Tabbed interface for two recovery methods
- Recovery Code tab: Enter code format
- Email tab: Enter email for recovery (only if SMTP configured)
- Link back to login
- Flash message support

### 2. `templates/reset_password.html`
- Centered password reset form
- Password requirements box
- Password and confirm password inputs
- Form validation
- Back link to forgot password

### 3. `templates/recovery_codes.html`
- Display all 10 recovery codes in grid layout
- Code interaction features:
  - Hover to reveal copy button
  - Click to copy to clipboard
  - Inactive styling for used codes
- Information box explaining usage
- Download as TXT button
- Print button (print-friendly styling)
- Admin status section (unused count)
- Links to login or admin settings

## Login Template Update

Updated `templates/login.html`:
- Added "Lost your access code?" link at bottom of login form
- Links to `/forgot-password` page
- Uses branding primary color for link

## Security Considerations

1. **Code Storage**: All recovery codes hashed with SHA256 before database storage
2. **One-Time Use**: Codes marked as used after verification
3. **Session Management**: Password reset only allowed after successful recovery verification
4. **Email Validation**: When using email recovery, user must provide matching email
5. **Temporary Codes**: Email-based recovery codes expire after 10 minutes
6. **SMTP Optional**: Email recovery disabled gracefully if SMTP not configured

## Workflow Examples

### Recovery Code Method
```
1. User visits /forgot-password
2. Selects "Recovery Code" tab
3. Enters one of their TROOP-XXXXXXXX codes
4. System verifies code and marks as used
5. User redirected to /reset-password
6. User enters new password (min 8 chars)
7. Password updated, redirected to login
```

### Email Recovery Method (if SMTP configured)
```
1. User visits /forgot-password
2. Selects "Email Recovery" tab
3. Enters registered email address
4. System generates temporary code and sends via email
5. Temporary code expires in 10 minutes
6. User provides temporary code at /reset-password
7. User enters new password
8. Password updated, redirected to login
```

### Admin Code Regeneration
```
1. Admin visits /admin/security
2. Scrolls to "Password Recovery" section
3. Clicks "Generate New Recovery Codes"
4. Old codes invalidated, new codes created
5. Redirected to /recovery-codes to view codes
6. Can download or print new codes
```

## Configuration

### Required Settings
- Database must be initialized with `recovery_codes` table
- No additional configuration needed for basic code-based recovery

### Optional Settings (for email recovery)
- SMTP server configured in Admin → Email Settings
- Recovery email address provided during setup or in Admin → Security

## Testing Checklist

- [ ] Setup wizard displays recovery email field
- [ ] Recovery codes generated during initial setup
- [ ] Recovery codes display page shows all 10 codes
- [ ] Recovery codes can be downloaded as TXT
- [ ] Recovery codes can be printed
- [ ] Login page shows "Lost your access code?" link
- [ ] /forgot-password displays code and email tabs
- [ ] Code verification works with valid codes
- [ ] Invalid/used codes rejected properly
- [ ] /reset-password requires prior recovery verification
- [ ] Password reset works and redirects to login
- [ ] Admin security page shows codes count
- [ ] Admin can regenerate new codes
- [ ] Email recovery works (if SMTP configured)
- [ ] Email recovery codes expire after 10 minutes
- [ ] Recovery email address can be updated in admin panel

## Dependencies

### New Imports Added
- `import hashlib` (for SHA256 hashing)

### Existing Dependencies Used
- `secrets` (already imported)
- `datetime` (already imported)
- `werkzeug.security.generate_password_hash` (already imported)
- Email functionality via `send_email()` (already exists)

## File Changes Summary

| File | Changes |
|------|---------|
| `app.py` | Added import hashlib, 6 recovery functions, 4 routes, updated admin_security |
| `schema.sql` | Added recovery_codes table |
| `templates/login.html` | Added "Forgot Password" link |
| `templates/setup.html` | Added recovery email input field |
| `templates/admin/security.html` | Added Password Recovery section |
| `templates/forgot_password.html` | NEW - Recovery method selection page |
| `templates/reset_password.html` | NEW - Password reset form |
| `templates/recovery_codes.html` | NEW - Recovery codes display/management |

## Future Enhancements

1. Add rate limiting on password reset attempts
2. Send email notifications when password is reset
3. Add password reset link expiration tracking
4. Implement password history (prevent reuse)
5. Add SMS-based recovery codes option
6. Implement TOTP/authenticator app support
7. Add security questions as additional recovery method
8. Email notification when new recovery codes generated

## Notes

- Recovery codes are shown only once after setup
- Users are encouraged to download/print codes for safe storage
- Admin can regenerate codes anytime from security settings
- Email recovery is optional and requires SMTP setup
- All password recovery is logged (future enhancement)
- Session-based recovery prevents multiple reset attempts per recovery
