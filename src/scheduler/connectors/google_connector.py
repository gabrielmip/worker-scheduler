import pickle
import os.path

from django.conf import settings
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from scheduler.exceptions import GoogleCredentialsException


def ask_user_for_permission():
    scopes = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file(settings.GOOGLE_API['CREDENTIALS'], scopes)

    return flow.run_local_server(port=0)


def _get_credentials():
    credentials = None

    if os.path.exists(settings.GOOGLE_API['TOKEN']):
        with open(settings.GOOGLE_API['TOKEN'], 'rb') as token:
            credentials = pickle.load(token)

    if not credentials:
        credentials = ask_user_for_permission()
    elif not credentials.valid and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    
    if not credentials.valid:
        raise GoogleCredentialsException('Credentials are invalid and could not be refreshed.')

    with open(settings.GOOGLE_API['TOKEN'], 'wb') as token:
        pickle.dump(credentials, token)
        
    return credentials
    

GOOGLE_CONNECTOR = build('calendar', 'v3', credentials=_get_credentials())

