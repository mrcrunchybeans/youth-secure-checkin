import os
import getpass
from tlc_client import TrailLifeConnectClient

def main():
    print("Trail Life Connect Connection Tester")
    print("------------------------------------")
    
    email = input("Enter your Email: ")
    password = getpass.getpass("Enter your Password: ")
    
    client = TrailLifeConnectClient(email, password)
    
    print("\nAttempting to login...")
    if client.login():
        print("Login Successful!")
        
        print("\nFetching upcoming events...")
        events = client.get_upcoming_events()
        
        if events:
            print(f"Found {len(events)} events:")
            for i, event in enumerate(events):
                print(f"{i+1}. {event['name']} (ID: {event['id']})")
            
            choice = input("\nEnter the number of an event to fetch its roster (or 0 to exit): ")
            if choice.isdigit() and int(choice) > 0 and int(choice) <= len(events):
                selected_event = events[int(choice)-1]
                print(f"\nFetching roster for '{selected_event['name']}'...")
                roster = client.get_event_roster(selected_event['id'])
                
                print(f"Found {len(roster)} members in roster:")
                for name, uid in list(roster.items())[:5]: # Show first 5
                    print(f" - {name}: {uid}")
                if len(roster) > 5:
                    print(f" ... and {len(roster)-5} more.")
                    
                print("\n(Note: No attendance will be changed in this test)")
        else:
            print("No events found. The HTML parsing logic might need adjustment.")
            
    else:
        print("Login Failed.")

if __name__ == "__main__":
    main()
