""" --- Imports --- """
# For making API calls
import httplib2
# For saving candidate info
import json
# User written module for Google API Calls
import google_api_functions as api


""" --- Get ID for MIC Chore Candidates spreadsheet --- """
# ID for the sheet is stored in a text file for security
def get_sheetID():
  with open('../bin/sheetID.txt', 'r') as f:
    lines = f.read().splitlines()
    # ID stored on the first line of the file
    return lines[0]


def update_candidates():
  """ Update candidates.json
  This script extracts information from the MIC Chore Candidates
  spreadsheet and saves it to candidates.json. Use check_candidates.py
  to see what candidates are currently eligible to be assigned chores.
  """
  # Get service object for the sheets API
  sheets_service = api.get_sheets_service()
  # Get data in the spreadsheet. First row has column labels
  rangeName= 'Sheet1!A2:G'
  result = sheets_service.spreadsheets().values().get( 
  		spreadsheetId=get_sheetID(), range=rangeName).execute()
  values = result.get('values', [])

  if not values:
    print('No data found in the spreadsheet.')
  else:
    # Add all candidates information to candidates.json
    candidates = []
    for row in values:
      # Stop when there are no more names in the spreadsheet
      if row[0] != '':
        print("Adding %s" % row[0])
        try:
          candidates.append( \
		{"name" : row[0],
		"email" : row[1],
		"mon" : row[2],
		"tues" : row[3],
		"wed" : row[4],
		"thurs" : row[5],
		"fri" : row[6]})
        except:
          print("Error adding %s. Make sure their information"
	  	"is complete" % row[0])
    # Store candidate information
    with open('../bin/candidates.json', 'w') as candidatesJSON:
      json.dump(candidates, candidatesJSON)

if __name__ == '__main__':
  update_candidates()
