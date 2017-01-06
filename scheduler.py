import httplib2
import os

# Google API imports
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# oauth2client.tools.run_flow() is a command-line tool, so it needs
# command-line flags. argeparse module is used to handle these
import argparse
flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

# Scope = read only
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'TW Chore Scheduler'

# Get ID for the sheet, which is stored in a text file for security
def get_sheetID():
  with open('./sheetID.txt', 'r') as f:
    lines = f.read().splitlines()
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
  discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?' 
  			'version=v4')
  service = discovery.build('sheets', 'v4', http=http, 
  			    discoveryServiceUrl=discoveryUrl)
  # Look at first 2 columns of the sheet
  rangeName= 'Sheet1!A:B'
  result = service.spreadsheets().values().get( 
  		spreadsheetId=get_sheetID(), range=rangeName).execute()
  values = result.get('values', [])

  if not values:
    print('No data found.')
  else:
    for row in values:
      # Columns A and B = indices 0 and 1
      if row[0] != '':
        print('%s %s' % (row[0], row[1]))

if __name__ == '__main__':
  main()
