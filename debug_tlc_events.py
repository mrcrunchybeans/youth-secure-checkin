from tlc_client import TrailLifeConnectClient
import os
from dotenv import load_dotenv

load_dotenv()

email = os.getenv('TLC_EMAIL')
password = os.getenv('TLC_PASSWORD')

if not email or not password:
    # print("Please set TLC_EMAIL and TLC_PASSWORD in .env")
    # exit(1)
    pass

# client = TrailLifeConnectClient(email, password)
# if client.login():
    print("Logged in.")
    
    # Try fetching the calendar view events page
    print("Fetching /calendar/view-events...")
    response = client.session.get(f"{client.base_url}/calendar/view-events")
    
    with open("calendar_dump.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved to calendar_dump.html")
    
    # Also try the dashboard which might have upcoming events
    print("Fetching /dashboard...")
    response = client.session.get(f"{client.base_url}/dashboard")
    with open("dashboard_dump.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved to dashboard_dump.html")

if __name__ == "__main__":
    # Allow manual input if env vars fail
    if not email or not password:
        email = input("Enter TLC Email: ")
        import getpass
        password = getpass.getpass("Enter TLC Password: ")
    
    client = TrailLifeConnectClient(email, password)
    if client.login():
        print("Logged in.")
        
        # Try fetching the calendar view events page
        print("Fetching /calendar/view-events...")
        response = client.session.get(f"{client.base_url}/calendar/view-events")
        
        with open("calendar_dump.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved to calendar_dump.html")
        
        # Also try the dashboard which might have upcoming events
        print("Fetching /dashboard...")
        response = client.session.get(f"{client.base_url}/dashboard")
        with open("dashboard_dump.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved to dashboard_dump.html")
    else:
        print("Login failed.")