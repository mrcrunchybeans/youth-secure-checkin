# Kid Notes Feature

## Overview

Added a notes/comments field to each kid's profile that allows staff to record important information such as:
- Special dietary restrictions (allergies, vegetarian, etc.)
- Special needs or accommodations
- Medical information
- Any other relevant notes

## Features

### Admin Interface
- **Edit Family**: Each kid now has a text area below their name field for notes
- **Add Family**: New kids can have notes added during family creation
- Notes are optional and can be left blank

### Check-in Display
- **Info Icon (ℹ️)**: Kids with notes show a blue info badge next to their name
- **Hover Tooltip**: Hovering over the icon displays the full note content
- **Works on Both Views**: Available on the main index page and kiosk mode

## Database Changes

### Schema Update
Added `notes` column to the `kids` table:
```sql
ALTER TABLE kids ADD COLUMN notes TEXT
```

### Migration
Run the migration script to update existing databases:
```bash
python migrate_add_kid_notes.py
```

## User Experience

1. **Adding Notes**: 
   - Go to Admin > Families > Edit Family
   - Enter notes in the text area below each kid's name
   - Notes support multiple lines

2. **Viewing Notes**:
   - When a kid with notes is checked in, an ℹ️ icon appears next to their name
   - Hover over or tap the icon to see the full note
   - Works on both desktop and mobile devices

## Technical Details

### Files Modified
- `schema.sql` - Added notes column to kids table
- `app.py` - Updated routes to handle kid notes (admin_edit_family, admin_add_family, index, kiosk)
- `templates/admin/edit_family.html` - Added textarea fields for notes
- `templates/admin/add_family.html` - Added textarea fields for notes
- `templates/index.html` - Display notes icon with Bootstrap tooltip
- `templates/kiosk.html` - Display notes icon with Bootstrap tooltip

### Database Field
- **Column**: `kids.notes`
- **Type**: TEXT
- **Nullable**: Yes (NULL when no notes)

### Display Logic
- Notes are only shown if they contain content
- Empty or NULL notes don't display an icon
- Uses Bootstrap 5 tooltips for consistent UX
- HTML content is preserved (line breaks are converted to `<br>` tags)

## Backward Compatibility

- Fully backward compatible with existing data
- Kids without notes continue to display normally
- No breaking changes to existing functionality
- The notes field is optional and defaults to NULL

## Future Enhancements (Optional)

Potential improvements could include:
- Rich text formatting for notes
- Color-coding or categories (dietary, medical, behavioral, etc.)
- Note history/audit trail
- Alerts or warnings for critical information
- Printable reports including notes
