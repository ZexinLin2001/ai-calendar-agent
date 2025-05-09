import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

# Scopes define access level; 'readonly' is enough for listing events
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Load from environment variables
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", "token.pickle")


def get_calendar_service():
    """
    Authenticate and return a Google Calendar API service object.
    Stores access token to avoid repeated logins.
    """
    creds = None

    # Load token if it exists
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token_file:
            creds = pickle.load(token_file)

    # Refresh or request new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the new credentials
        with open(TOKEN_PATH, 'wb') as token_file:
            pickle.dump(creds, token_file)

    # Build the API service
    service = build('calendar', 'v3', credentials=creds)
    return service
