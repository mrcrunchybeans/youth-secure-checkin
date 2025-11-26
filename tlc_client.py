import requests
from bs4 import BeautifulSoup
import logging
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrailLifeConnectClient:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.base_url = "https://www.traillifeconnect.com"
        self.csrf_token = None
        
        # Common headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': self.base_url,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })

    def _extract_csrf_token(self, soup):
        """Extracts CSRF token from meta tag or form input."""
        # Try meta tag first (common in Yii/Laravel)
        token = soup.find('meta', {'name': 'csrf-token'})
        if token:
            return token['content']
        
        # Try form input
        token_input = soup.find('input', {'name': '_csrf'}) or soup.find('input', {'name': '_token'}) or soup.find('input', {'name': 'YII_CSRF_TOKEN'})
        if token_input:
            return token_input['value']
            
        return None

    def login(self):
        """
        Logs into Trail Life Connect.
        """
        login_url = f"{self.base_url}/login"
        
        # 1. Get the login page to fetch cookies and CSRF token
        logger.info("Fetching login page...")
        response = self.session.get(login_url)
        if response.status_code != 200:
            logger.error("Failed to load login page")
            return False

        soup = BeautifulSoup(response.text, 'html.parser')
        self.csrf_token = self._extract_csrf_token(soup)
        
        if self.csrf_token:
            logger.info("Found CSRF token.")
            # Set the token in headers for future AJAX requests
            self.session.headers.update({'x-csrf-token': self.csrf_token})
        else:
            logger.warning("Could not find CSRF token on login page. Login might fail.")

        # Prepare payload - field names might need adjustment based on actual form
        # Common names: 'LoginForm[email]', 'email', 'username'
        # Based on typical Yii forms, it might be nested like LoginForm[username]
        # But for now we'll try simple names or look for inputs
        
        payload = {}
        
        # Try to find the actual input names
        email_input = soup.find('input', {'type': 'email'}) or soup.find('input', {'type': 'text', 'name': re.compile(r'email|user', re.I)})
        password_input = soup.find('input', {'type': 'password'})
        
        email_field = email_input['name'] if email_input else 'email'
        password_field = password_input['name'] if password_input else 'password'
        
        payload[email_field] = self.email
        payload[password_field] = self.password
        
        # Add CSRF token to body if it was found in a form input
        csrf_input = soup.find('input', {'name': '_csrf'}) or soup.find('input', {'name': '_token'})
        if csrf_input:
            payload[csrf_input['name']] = csrf_input['value']
        elif self.csrf_token:
             # Fallback for some frameworks
            payload['_csrf'] = self.csrf_token

        # 2. Post credentials
        logger.info(f"Posting credentials to {login_url}...")
        post_response = self.session.post(login_url, data=payload)
        
        # Check for success
        if "dashboard" in post_response.url or "Logout" in post_response.text:
            logger.info("Login successful!")
            # Update CSRF token from dashboard if it changed
            soup = BeautifulSoup(post_response.text, 'html.parser')
            new_token = self._extract_csrf_token(soup)
            if new_token:
                self.csrf_token = new_token
                self.session.headers.update({'x-csrf-token': self.csrf_token})
            return True
        else:
            logger.error("Login failed. Check credentials or field names.")
            return False

    def get_upcoming_events(self):
        """
        Scrapes the calendar events page to find upcoming events.
        Returns a list of dicts: {'id': '...', 'name': '...', 'date': '...'}
        """
        url = f"{self.base_url}/calendar/view-events"
        logger.info(f"Fetching events from {url}...")
        response = self.session.get(url)
        
        if response.status_code != 200:
            logger.error("Failed to fetch calendar events page")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        events = []
        
        # Find the grid view table rows
        # Rows have data-key attribute which is the event ID
        rows = soup.find_all('tr', attrs={'data-key': True})
        
        for row in rows:
            event_id = row['data-key']
            
            # Find date (usually data-col-seq="2")
            date_cell = row.find('td', attrs={'data-col-seq': '2'})
            event_date = date_cell.get_text(strip=True) if date_cell else "Unknown Date"
            
            # Find title (usually data-col-seq="3")
            title_cell = row.find('td', attrs={'data-col-seq': '3'})
            event_name = title_cell.get_text(strip=True) if title_cell else "Unknown Event"
            
            # Combine date and name for display
            display_name = f"{event_name} ({event_date})"
            
            events.append({
                'id': event_id,
                'name': display_name,
                'date': event_date,
                'title': event_name
            })
            
        logger.info(f"Found {len(events)} events.")
        return events

    def get_event_roster(self, event_id):
        """
        Fetches the list of users for a specific event.
        Returns a dict mapping Name -> UserID.
        """
        url = f"{self.base_url}/calendar/attendance-user-list"
        
        # Payload based on user logs
        payload = {
            'patrol': '',
            'eventId': event_id,
            'sortBy': 'level',
            'rsvpOnly': 'false',
            'lockAttended': 'true'
        }
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        
        logger.info(f"Fetching roster for event {event_id}...")
        response = self.session.post(url, data=payload, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch roster: {response.status_code}")
            return {}

        # DEBUG: Save HTML to file for inspection
        try:
            with open("roster_dump.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            logger.info("Saved roster HTML to roster_dump.html for debugging.")
        except Exception as e:
            logger.warning(f"Could not save debug HTML: {e}")

        # The response is HTML snippets of users
        soup = BeautifulSoup(response.text, 'html.parser')
        roster = {}
        
        # Strategy: Look for divs with class 'user-row' and 'data-user' attribute
        # Example: <div data-user="uz8h3zpncocu" class="user-row">...<a ...>Clinton, Josiah</a>...</div>
        
        user_rows = soup.find_all(class_='user-row')
        for row in user_rows:
            user_id = row.get('data-user')
            if user_id:
                # Try to find the name in an anchor tag
                link = row.find('a')
                if link:
                    name = link.get_text(strip=True)
                    # Format name to be "First Last" if it is "Last, First"
                    if ',' in name:
                        parts = name.split(',')
                        if len(parts) == 2:
                            name = f"{parts[1].strip()} {parts[0].strip()}"
                    
                    roster[name] = user_id
                else:
                    # Fallback to image alt text
                    img = row.find('img')
                    if img and img.get('alt'):
                        name = img.get('alt')
                        if ',' in name:
                            parts = name.split(',')
                            if len(parts) == 2:
                                name = f"{parts[1].strip()} {parts[0].strip()}"
                        roster[name] = user_id

        logger.info(f"Found {len(roster)} members in roster.")
        return roster

    def mark_attendance(self, event_id, tlc_user_id, present=True):
        """
        Toggles attendance for a specific user and event.
        """
        url = f"{self.base_url}/calendar/toggle-attendance"
        
        # Payload based on user logs
        payload = {
            'userId': tlc_user_id,
            'eventId': event_id,
            'value': '1' if present else '0', # Assuming 1 is present
            'use_lesson_plans': '1'
        }
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        
        logger.info(f"Marking user {tlc_user_id} as {'present' if present else 'absent'} for event {event_id}...")
        response = self.session.post(url, data=payload, headers=headers)
        
        if response.status_code == 200:
            logger.info("Success.")
            return True
        else:
            logger.error(f"Failed: {response.status_code} - {response.text}")
            return False

