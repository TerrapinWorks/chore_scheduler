""" --- Imports --- """
# For saving candidate info
import json
# In case we need to exit on an error
import sys

sys.path.append('google_api_functions/')
# User written module for Google API Calls
import google_api_functions as api

# app_detals.json contains info for the Google API object
APP_DETAILS_PATH = "../bin/app_details.json"
# If no completion frequency is set for a chore, set to default
DEFAULT_COMPLETION_FREQUENCY = "Weekly"


""" --- Get ID for MIC Chore Candidates spreadsheet --- """
# ID for the sheet is stored in a text file for security
def get_sheetID():
	with open('../bin/sheetID.txt', 'r') as f:
		lines = f.read().splitlines()
		# ID stored on the first line of the file
		return lines[0]


def update():
	""" Update candidates.json and chores.json
	This script extracts information from the MIC Chore Scheduler
	spreadsheet 
	"""
	api_object = api.get_api_object(APP_DETAILS_PATH)
	sheets_service = api_object.get_sheets_service()
	# Get candidate information
	print("Updating Candidate Information...")
	sheet_range= 'Candidates!A2:G'
	result = sheets_service.spreadsheets().values().get( 
			spreadsheetId=get_sheetID(), range=sheet_range).execute()
	values = result.get('values', [])

	if not values:
		print('No data found in the spreadsheet.')
		sys.exit()
	# Add all candidates information to candidates.json
	candidates = []
	for row in values:
		try:
			if row[0] != '':
				print("  Candidate: %s" % row[0])
				candidate = {"name" : row[0], "email" : row[1]}
				# Get start times
				weekdays = ["mon", "tues", "wed", "thurs", "fri"]
				for day_num in range(0, len(weekdays)):
					candidate[weekdays[day_num]] = \
								row[day_num + 2] if len(row) > (day_num + 2) else None
			candidates.append(candidate)
		except IndexError:
			print("Index Error: Error adding candidate")
	# Store candidate information
	with open('../bin/candidates.json', 'w') as candidatesJSON:
		json.dump(candidates, candidatesJSON)
	
	# Get chores
	print("Updating Chores...")
	sheet_range = 'Chores!A2:C'
	result = sheets_service.spreadsheets().values().get( 
			spreadsheetId=get_sheetID(), range=sheet_range).execute()
	values = result.get('values', [])

	if not values:
		print('No data found in the spreadsheet.')
		sys.exit()
	# Add chores to chores.json
	chores = []
	for row in values:
		try:
			if row[0] != '':
				print("  Chore: %s" % row[0])
				# Set default completion status if cell is empty
				completion_frequency = row[1] if ((len(row) > 1) and row[1] != '') \
																				else DEFAULT_COMPLETION_FREQUENCY
				# Set completion status to false if cell is empty
				completion_status = row[2] if len(row) > 2 else "FALSE"
				chore = {
									"name" : row[0],
									"completion_frequency" : completion_frequency,
									"completion_status" : completion_status
								}
				chores.append(chore)
		except IndexError:
			print("Index Error: Error adding chore")
	# Store chore information
	with open('../bin/chores.json', 'w') as choresJSON:
		json.dump(chores, choresJSON)
		

if __name__ == '__main__':
	update()
