import httplib2
import os
import sys

# User written
import gmail_email

# Google API imports
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# oauth2client.tools.run_flow() is a command-line tool, so it needs
# command-line flags. argeparse module is used to handle these
import argparse
flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

# Sheets - read only 
# Gmail - Read, compose, send
SCOPES = ('https://www.googleapis.com/auth/spreadsheets.readonly '
		'https://www.googleapis.com/auth/gmail.readonly '
		'https://www.googleapis.com/auth/gmail.compose '
		'https://www.googleapis.com/auth/gmail.send')
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'TW Chore Scheduler'

# Get ID for the sheet, which is stored in a text file for security
def get_sheetID():
  with open('./sheetID.txt', 'r') as f:
    lines = f.read().splitlines()
    # ID stored on the first line of the file
    return lines[0]

def get_credentials():
  """ Retreive user credentials so we can access the spreadsheet.
  This function works as follows:
  1) Check if there are credentials already stored (in Storage object)
  2) If there are, return the Credentials object (using store.get())
  3) If not, initiate flow_from_clientsecrets(), which will use a Flow
     object to launch the browser, prompt user for authorization, and
     store credentials.
  """

  # Credentials will be stored in ~/.credentials/chore_creds.json 
  home_dir = os.path.expanduser('~')
  credential_dir = os.path.join(home_dir, '.credentials')
  if not os.path.exists(credential_dir):
    os.makedirs(credential_dir)
  credential_path = os.path.join(credential_dir, 'chore_creds.json')

  store = Storage(credential_path)
  credentials = store.get()
  # If no credentials are already stored, run flow to get credentials
  if not credentials or credentials.invalid:
    print('No stored credentials. Initiating flow...')
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    flow.user_agent = APPLICATION_NAME
    credentials = tools.run_flow(flow, store, flags)
    print('Storing credentials to ' + credential_path)
  return credentials

def main():
  # We need a credential-authorized httplib2.Http object in order to
  # access user data
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  sheets_discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?' 
  			'version=v4')
  # Get services for both APIs. Services expose methods for the API
  sheets_service = discovery.build('sheets', 'v4', http=http, 
  			    discoveryServiceUrl=sheets_discoveryUrl)
  gmail_service = discovery.build('gmail', 'v1', http=http)
  # Get data in the spreadsheet
  rangeName= 'Sheet1!A:B'
  result = sheets_service.spreadsheets().values().get( 
  		spreadsheetId=get_sheetID(), range=rangeName).execute()
  values = result.get('values', [])

  # Use data to send emails
  if not values:
    print('No data found in the spreadsheet.')
  else:
    # Send an email to each person
    sender = 'aander21@eng.umd.edu'
    for row in values:
      if row[0] != '':
        message_text = 'Hello ' + row[0]
        to = row[1]
        subject = 'Test email from the Pi'
        message = gmail_email.create_message(sender=sender,
			to=to, subject=subject, message_text=message_text)
        gmail_email.send_message(gmail_service, 'me', message)

if __name__ == '__main__':
  main()
