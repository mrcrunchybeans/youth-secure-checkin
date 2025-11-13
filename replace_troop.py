"""
Script to replace hardcoded "Troop" references with branding variables
"""
import re
from pathlib import Path

def replace_troop_in_file(file_path):
    """Replace 'Troop' with template variable, preserving case"""
    print(f"\nProcessing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    replacements = 0
    
    # Replace "Troop" with {{ branding.group_term }}
    # Only in display contexts, not in data/field names
    patterns = [
        # In text content (but not in HTML attributes like 'name=troop' or 'id=troop')
        (r'<strong>Family:</strong> (\S+) - Troop (\S+)', r'<strong>Family:</strong> \1 - {{ branding.group_term }} \2'),
        (r'<strong>Troop:</strong>', r'<strong>{{ branding.group_term }}:</strong>'),
        (r'>Troop</', r'>{{ branding.group_term }}</'),
    ]
    
    for pattern, replacement in patterns:
        matches = len(re.findall(pattern, content))
        if matches > 0:
            content = re.sub(pattern, replacement, content)
            replacements += matches
            print(f"  Replaced {matches}x: {pattern[:40]}...")
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Saved {replacements} replacements")
        return replacements
    else:
        print(f"  No Troop references to replace")
        return 0

def main():
    templates_dir = Path('templates')
    total_replacements = 0
    
    # Process all HTML files
    for html_file in templates_dir.rglob('*.html'):
        replacements = replace_troop_in_file(html_file)
        total_replacements += replacements
    
    print(f"\n{'='*60}")
    print(f"Total Troop replacements: {total_replacements}")
    print(f"{'='*60}")
    print("\nNote: Database field names ('troop' column) unchanged.")
    print("The 'troop' field will store the group identifier regardless")
    print("of what terminology is displayed to users.")

if __name__ == '__main__':
    main()
