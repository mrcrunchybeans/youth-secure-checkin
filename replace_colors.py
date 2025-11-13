"""
Script to replace hardcoded colors with branding variables in templates
"""
import re
from pathlib import Path

# Color mappings
COLOR_MAP = {
    '#79060d': '{{ branding.primary_color }}',
    '#8d0710': '{{ branding.primary_color }}',  # Darker variant, use same
    '#003b59': '{{ branding.secondary_color }}',
    '#004a6e': '{{ branding.secondary_color }}',  # Lighter variant
    '#4a582d': '{{ branding.accent_color }}',
}

def replace_colors_in_file(file_path):
    """Replace hardcoded colors with template variables"""
    print(f"\nProcessing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    replacements = 0
    
    for old_color, new_color in COLOR_MAP.items():
        # Case-insensitive replacement
        pattern = re.compile(re.escape(old_color), re.IGNORECASE)
        matches = len(pattern.findall(content))
        if matches > 0:
            content = pattern.sub(new_color, content)
            replacements += matches
            print(f"  Replaced {matches}x: {old_color} → {new_color}")
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Saved {replacements} replacements")
        return replacements
    else:
        print(f"  No changes needed")
        return 0

def main():
    templates_dir = Path('templates')
    total_replacements = 0
    
    # Process all HTML files
    for html_file in templates_dir.rglob('*.html'):
        if 'admin/settings.html' in str(html_file):
            print(f"\nSkipping {html_file} (already updated manually)")
            continue
        if 'login.html' in str(html_file):
            print(f"\nSkipping {html_file} (already updated manually)")
            continue
            
        replacements = replace_colors_in_file(html_file)
        total_replacements += replacements
    
    print(f"\n{'='*60}")
    print(f"Total replacements: {total_replacements}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
