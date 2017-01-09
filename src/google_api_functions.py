"""--- Imports ---"""
# For making API requests
import httplib2
# For retrieving and storing credentials
import os

# Google API modules
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# oauth2client.tools.run_flow() is a command-line tool, so it needs
# command-line flags. argeparse module is used to handle these
import argparse
flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

# Email creation modules
from email.mime.text import MIMEText
import base64


"""--- Information for Authorization ---"""
APPLICATION_NAME = 'TW Chore Scheduler'
CLIENT_SECRET_FILE = 'client_secret.json'
# Sheets - read only 
# Gmail - Read, compose, send
SCOPES = ('https://www.googleapis.com/auth/spreadsheets.readonly '
		'https://www.googleapis.com/auth/gmail.readonly '
		'https://www.googleapis.com/auth/gmail.compose '
		'https://www.googleapis.com/auth/gmail.send')


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


def get_sheets_service():
  """ Return service object for the Sheets API """
  http = get_authorized_http()
  sheets_discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?' 
  			'version=v4')
  return discovery.build('sheets', 'v4', http=http, 
  			    discoveryServiceUrl=sheets_discoveryUrl)

def get_gmail_service():
  """ Return service object for the Gmail API """
  http = get_authorized_http()
  return discovery.build('gmail', 'v1', http=http)


def get_authorized_http():
  """ Create an authorized httplib2.Http object in
  order to acces user data
  """
  credentials = get_credentials()
  return(credentials.authorize(httplib2.Http()))


def create_message(sender, to, subject, message_text):
  """ Create message to send using the Gmail API
  This function creates a MIME format email and encodes it using
  base64 so that it can be sent using the Gmail API. To send
  the message returned by this function, use the send_message()
  function
  """
  # Construct the email using the MIME format
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  
  """ String probelms in Python 3
  base64.urlsafe_b64encode() takes a byte string.
  message.as_string() returns a Python 3 str string, so we have to encode it
  """

  byte_string = base64.urlsafe_b64encode(message.as_string().encode('ascii'))

  """ More string problems in Python 3
  base64.urlsafe_b64encode() returns a byte string, so we have to decode it
  to be an str type string so give to the Gmail API so that the string will
  JSON Serializable 
  """

  raw = byte_string.decode()
  return {'raw' : raw}


def send_message(service, user_id, message):
  """ Send message to the Gmail API
  This function assumes that service is a Service object fir the Gmail API,
  and that message is constructed using create_message()
  """

  try:
    message = (service.users().messages().send(userId = user_id, body=message)
    		.execute())
    print('Sending email')
  except:
    print('Error sending email')
