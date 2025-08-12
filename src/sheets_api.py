import os
import json
from datetime import datetime
from typing import List, Dict, Optional

try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("Google API libraries not installed. Google Sheets integration disabled.")

class SheetsAPI:
    """Handle Google Sheets API operations for mood tracking data"""
    
    # Scopes for Google Sheets API
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, spreadsheet_id: str = None, credentials_path: str = 'credentials.json'):
        self.spreadsheet_id = spreadsheet_id or os.getenv('GOOGLE_SHEETS_ID')
        self.credentials_path = credentials_path
        self.service = None
        self.creds = None
        
        if not GOOGLE_API_AVAILABLE:
            print("Google Sheets API not available. Install required packages.")
            return
            
        if self.spreadsheet_id:
            self._authenticate()
    
    def _authenticate(self) -> bool:
        """Authenticate with Google Sheets API"""
        if not GOOGLE_API_AVAILABLE:
            return False
            
        token_path = 'token.json'
        
        # Load existing credentials if available
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        # If no valid credentials, prompt for authorization
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    return False
            else:
                if not os.path.exists(self.credentials_path):
                    print(f"Credentials file {self.credentials_path} not found.")
                    print("Please follow the setup instructions to create credentials.json")
                    return False
                    
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error during authentication: {e}")
                    return False
            
            # Save the credentials for next run
            with open(token_path, 'w') as token:
                token.write(self.creds.to_json())
        
        try:
            self.service = build('sheets', 'v4', credentials=self.creds)
            return True
        except Exception as e:
            print(f"Error building service: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if API is properly connected"""
        return self.service is not None and GOOGLE_API_AVAILABLE
    
    def create_mood_sheet(self, sheet_name: str = "MoodTracker") -> bool:
        """Create a new sheet for mood tracking with headers"""
        if not self.is_connected():
            return False
            
        try:
            # Create new sheet
            body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id, body=body).execute()
            
            # Add headers
            headers = [
                'Timestamp', 'Date', 'Time', 'Mood Score', 'Stress Level',
                'Energy Level', 'Sleep Hours', 'Notes', 'Tags'
            ]
            
            range_name = f"{sheet_name}!A1:I1"
            body = {
                'values': [headers]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"Created sheet '{sheet_name}' with headers")
            return True
            
        except Exception as e:
            print(f"Error creating sheet: {e}")
            return False
    
    def add_mood_entry(self, mood_entry, sheet_name: str = "MoodTracker") -> bool:
        """Add a single mood entry to the sheet"""
        if not self.is_connected():
            return False
            
        try:
            # Convert mood entry to row data
            timestamp = mood_entry.timestamp
            row_data = [
                timestamp.isoformat(),
                timestamp.strftime('%Y-%m-%d'),
                timestamp.strftime('%H:%M:%S'),
                mood_entry.mood_score,
                mood_entry.stress_level,
                mood_entry.energy_level,
                mood_entry.sleep_hours,
                mood_entry.notes,
                ', '.join(mood_entry.tags) if mood_entry.tags else ''
            ]
            
            # Append to sheet
            range_name = f"{sheet_name}!A:I"
            body = {
                'values': [row_data]
            }
            
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error adding mood entry: {e}")
            return False
    
    def add_multiple_entries(self, mood_entries: List, sheet_name: str = "MoodTracker") -> bool:
        """Add multiple mood entries to the sheet"""
        if not self.is_connected():
            return False
            
        try:
            # Convert all entries to row data
            rows_data = []
            for entry in mood_entries:
                timestamp = entry.timestamp
                row_data = [
                    timestamp.isoformat(),
                    timestamp.strftime('%Y-%m-%d'),
                    timestamp.strftime('%H:%M:%S'),
                    entry.mood_score,
                    entry.stress_level,
                    entry.energy_level,
                    entry.sleep_hours,
                    entry.notes,
                    ', '.join(entry.tags) if entry.tags else ''
                ]
                rows_data.append(row_data)
            
            # Append all rows to sheet
            range_name = f"{sheet_name}!A:I"
            body = {
                'values': rows_data
            }
            
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            print(f"Added {len(mood_entries)} entries to sheet")
            return True
            
        except Exception as e:
            print(f"Error adding multiple entries: {e}")
            return False
    
    def get_all_entries(self, sheet_name: str = "MoodTracker") -> List[Dict]:
        """Retrieve all mood entries from the sheet"""
        if not self.is_connected():
            return []
            
        try:
            range_name = f"{sheet_name}!A:I"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range=range_name).execute()
            
            values = result.get('values', [])
            
            if not values:
                return []
            
            # Skip header row
            data_rows = values[1:] if len(values) > 1 else []
            
            entries = []
            for row in data_rows:
                if len(row) >= 4:  # Minimum required columns
                    entry = {
                        'timestamp': row[0] if len(row) > 0 else '',
                        'date': row[1] if len(row) > 1 else '',
                        'time': row[2] if len(row) > 2 else '',
                        'mood_score': int(row[3]) if len(row) > 3 and row[3].isdigit() else 0,
                        'stress_level': int(row[4]) if len(row) > 4 and row[4].isdigit() else 5,
                        'energy_level': int(row[5]) if len(row) > 5 and row[5].isdigit() else 5,
                        'sleep_hours': float(row[6]) if len(row) > 6 and row[6].replace('.', '').isdigit() else 8.0,
                        'notes': row[7] if len(row) > 7 else '',
                        'tags': [tag.strip() for tag in row[8].split(',')] if len(row) > 8 and row[8] else []
                    }
                    entries.append(entry)
            
            return entries
            
        except Exception as e:
            print(f"Error retrieving entries: {e}")
            return []
    
    def get_entries_by_date_range(self, start_date: str, end_date: str, 
                                 sheet_name: str = "MoodTracker") -> List[Dict]:
        """Get entries within a specific date range"""
        all_entries = self.get_all_entries(sheet_name)
        
        filtered_entries = []
        for entry in all_entries:
            entry_date = entry.get('date', '')
            if start_date <= entry_date <= end_date:
                filtered_entries.append(entry)
        
        return filtered_entries
    
    def clear_sheet(self, sheet_name: str = "MoodTracker") -> bool:
        """Clear all data from the sheet (except headers)"""
        if not self.is_connected():
            return False
            
        try:
            # Clear all data except header row
            range_name = f"{sheet_name}!A2:Z"
            body = {}
            
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                body=body
            ).execute()
            
            print(f"Cleared data from sheet '{sheet_name}'")
            return True
            
        except Exception as e:
            print(f"Error clearing sheet: {e}")
            return False
    
    def backup_to_file(self, filename: str = None, sheet_name: str = "MoodTracker") -> bool:
        """Backup sheet data to a JSON file"""
        if not filename:
            filename = f"mood_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        entries = self.get_all_entries(sheet_name)
        
        try:
            with open(filename, 'w') as f:
                json.dump(entries, f, indent=2)
            
            print(f"Backup saved to {filename}")
            return True
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def get_sheet_info(self) -> Dict:
        """Get information about the spreadsheet"""
        if not self.is_connected():
            return {}
            
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id).execute()
            
            info = {
                'title': spreadsheet.get('properties', {}).get('title', 'Unknown'),
                'sheets': [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])],
                'spreadsheet_id': self.spreadsheet_id
            }
            
            return info
            
        except Exception as e:
            print(f"Error getting sheet info: {e}")
            return {}

# Utility function to setup Google Sheets integration
def setup_sheets_integration(spreadsheet_id: str = None) -> Optional[SheetsAPI]:
    """Setup and test Google Sheets integration"""
    if not GOOGLE_API_AVAILABLE:
        print("Google API libraries not available.")
        print("Install with: pip install google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib")
        return None
    
    sheets_api = SheetsAPI(spreadsheet_id)
    
    if sheets_api.is_connected():
        print("Google Sheets integration ready!")
        info = sheets_api.get_sheet_info()
        if info:
            print(f"Connected to: {info.get('title', 'Unknown')}")
            print(f"Available sheets: {', '.join(info.get('sheets', []))}")
        return sheets_api
    else:
        print("Failed to connect to Google Sheets")
        return None
