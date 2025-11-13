# Export Features Documentation

## Overview
The check-in system now supports exporting both family data and configuration backups, making it easy to backup, migrate, or audit your data.

## Features

### 1. Family List Export
**Location:** Admin Panel → Families → "Export to CSV" button

**What it exports:**
- All families with their adults and children
- Phone numbers (last 4 digits)
- Group/troop assignments
- Authorized adults for pickup
- Special notes for children
- All data in standard CSV format

**File format:** `families_export_YYYYMMDD_HHMMSS.csv`

**Columns exported:**
1. Last Name
2. First Name
3. Youth (Y = child, blank = adult)
4. Mobile Phone
5. Address Line 1
6. Authorized Adults
7. Notes
8. Group ID

**Use cases:**
- Backup family data before major changes
- Export to share with other systems
- Create reports for organization leadership
- Migrate to another check-in system

### 2. Configuration Backup Export
**Location:** Admin Panel → Security Settings → "Export Backup" button

**What it exports:**
- Organization branding (name, type, group term, colors)
- Logo and favicon filenames
- Security codes (app password, admin override, checkout codes)
- Event date range settings
- Label printing settings
- All configuration in JSON format

**File format:** `configuration_backup_YYYYMMDD_HHMMSS.json`

**Metadata included:**
- Export date/time
- App version
- Complete settings database

**Use cases:**
- Backup configuration before making changes
- Document current setup for auditing
- Migrate settings to another server
- Restore after system issues

## Usage Examples

### Exporting Family Data
1. Log in to admin panel
2. Navigate to "Families"
3. Click "Export to CSV"
4. File downloads automatically
5. Open in Excel, Google Sheets, or any CSV editor

### Exporting Configuration
1. Log in to admin panel
2. Navigate to "Security Settings"
3. Click "Export Backup" button
4. JSON file downloads automatically
5. Store in secure location for disaster recovery

### Restoring Configuration
1. Log in to admin panel
2. Navigate to "Security Settings"
3. Click "Restore Backup" button
4. A modal dialog will appear with warnings
5. Click "Choose File" and select your backup JSON file
6. Review the warning about overwriting current settings
7. Click "Restore Backup" to complete the import
8. System will confirm successful restoration
9. Review settings and restart application if needed

**Important:** Always export a current backup before restoring to have a rollback option.

## Import/Export Round Trip

The CSV export format is compatible with the CSV import format:

**Export → Edit → Import workflow:**
1. Export families to CSV
2. Edit in spreadsheet program
3. Save changes
4. Import updated CSV
5. System validates and imports changes

**Important notes:**
- Export uses same column names as import
- Both support optional "Authorized Adults" and "Notes" columns
- Family grouping maintained via Last Name and Address
- Phone numbers standardized to last 4 digits

## Security Considerations

### Configuration Backups
- **Contains sensitive data:** Access codes, passwords (except developer password)
- **Store securely:** Use encrypted storage or secure password manager
- **Regular backups:** Schedule exports before major changes
- **Version control:** Keep timestamped backups for rollback capability

### Family Data
- **Contains PII:** Phone numbers, names, notes may include sensitive info
- **Access control:** Only admin users can export
- **Data retention:** Follow your organization's privacy policies
- **Encryption:** Consider encrypting exports if storing long-term

## Technical Details

### CSV Export Implementation
- Uses Python's native `csv` module
- Character encoding: UTF-8
- Line endings: Standard for platform
- Quotes: Applied to fields with commas or special characters
- Headers: Always included in first row

### JSON Export Implementation
- Pretty-printed with 2-space indentation
- ISO 8601 timestamps
- Excludes developer password (environment-only)
- Includes app version for compatibility checking

### JSON Import Implementation
- Validates JSON structure before importing
- Supports INSERT OR REPLACE for all settings
- Skips empty/null values
- Provides detailed feedback on import success
- Shows count of imported settings
- Includes safety warnings before restoration

### File Naming
Both exports use timestamps to prevent overwrites:
- Format: `YYYYMMDD_HHMMSS` (e.g., `20240115_143022`)
- Ensures unique filenames for each export
- Easy to sort chronologically

## Future Enhancements

Potential additions for future versions:
- [x] Configuration import/restore functionality
- [ ] Scheduled automatic backups
- [ ] Export event history with check-in/check-out data
- [ ] Excel (.xlsx) export format option
- [ ] Encrypted backup option
- [ ] Cloud storage integration (Google Drive, Dropbox, etc.)
- [ ] Email backup reports

## Version History

**v1.0 (Current)**
- Initial CSV family export
- JSON configuration backup export
- Export buttons in admin UI
- Timestamped filenames
