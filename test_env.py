import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Check what's loaded
dev_password = os.getenv('DEVELOPER_PASSWORD', None)
secret_key = os.getenv('SECRET_KEY', None)

print("=" * 50)
print("Environment Variables Check:")
print("=" * 50)
print(f"DEVELOPER_PASSWORD loaded: {dev_password is not None}")
if dev_password:
    print(f"DEVELOPER_PASSWORD value: '{dev_password}'")
    print(f"DEVELOPER_PASSWORD length: {len(dev_password)}")
    print(f"DEVELOPER_PASSWORD repr: {repr(dev_password)}")
else:
    print("DEVELOPER_PASSWORD is None or empty")

print(f"\nSECRET_KEY loaded: {secret_key is not None}")
if secret_key:
    print(f"SECRET_KEY length: {len(secret_key)}")
print("=" * 50)
