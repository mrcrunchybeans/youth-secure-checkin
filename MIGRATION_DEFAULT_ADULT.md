# Default Adult Feature Migration Guide

## What's New

The troop check-in system now supports setting a **default adult** for each family. When a family checks in at the kiosk, the default adult will be automatically pre-selected in the dropdown, making the check-in process faster and more convenient.

## Changes Made

### 1. Database Schema Update
- Added `default_adult_id` column to the `families` table
- This column references an adult in the `adults` table for each family

### 2. Admin Interface Updates
- **Edit Family Page**: Radio buttons now appear next to each adult name, allowing you to select which adult should be the default
- **Add Family Page**: When adding a new family, you can select the default adult using radio buttons
- The first adult is selected by default when creating a new family

### 3. Check-in Kiosk
- When a family enters their phone number, the default adult (if set) will be automatically selected in the dropdown
- If no default is set, the first adult in the list will be selected (previous behavior)

## Migration Instructions

### For Existing Databases

If you have an existing `checkin.db` database, you need to run the migration script to add the new column:

```bash
python migrate_add_default_adult.py
```

This script will:
- Check if the `default_adult_id` column already exists
- Add the column if it doesn't exist
- Report success or if migration is not needed

### For New Installations

No migration is needed - the updated `schema.sql` already includes the `default_adult_id` column.

## How to Use

### Setting a Default Adult

1. Go to **Admin** > **Families**
2. Click **Edit** on any family
3. You'll see radio buttons next to each adult's name
4. Select the radio button for the adult you want as the default
5. Click **Update Family**

### Check-in Behavior

- When a family checks in at the kiosk, the default adult will be pre-selected
- Users can still change the selection if needed
- If no default is set, the first adult is selected (backward compatible)

## Technical Details

### Database Schema
```sql
ALTER TABLE families 
ADD COLUMN default_adult_id INTEGER 
REFERENCES adults(id) ON DELETE SET NULL;
```

### API Changes
The `/checkin_last4` endpoint now returns:
```json
{
  "family_id": 1,
  "phone": "1234567890",
  "troop": "123",
  "default_adult_id": 5,
  "adults": [...],
  "kids": [...]
}
```

## Backward Compatibility

This feature is fully backward compatible:
- Existing families without a default adult will continue to work
- The first adult is selected if no default is specified
- No data loss or breaking changes

## Rollback

If you need to rollback this feature, you can remove the column:

```sql
-- Note: SQLite doesn't support DROP COLUMN directly
-- You would need to recreate the table without the column
-- This is not recommended unless absolutely necessary
```
