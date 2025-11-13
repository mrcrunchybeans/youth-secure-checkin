from app import app

print("Checking for unlock_override route...")
routes = [str(rule) for rule in app.url_map.iter_rules()]
unlock_routes = [r for r in routes if 'unlock' in r]
print(f"Found routes with 'unlock': {unlock_routes}")

print("\nChecking DEVELOPER_PASSWORD...")
from app import DEVELOPER_PASSWORD
print(f"DEVELOPER_PASSWORD is None: {DEVELOPER_PASSWORD is None}")
if DEVELOPER_PASSWORD:
    print(f"DEVELOPER_PASSWORD length: {len(DEVELOPER_PASSWORD)}")
    print(f"DEVELOPER_PASSWORD value: '{DEVELOPER_PASSWORD}'")
