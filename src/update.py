# For saving candidate info
import json

# In case we need to exit on an error
import sys

# User written module for Google API Calls
sys.path.append('google_api_functions/')
import google_api_functions as api

# app_detals.json contains info for the Google API object
APP_DETAILS_FILE = "../bin/app_details.json"
# For logging errors internally
LOGFILE = "../bin/log.txt"
# If no completion frequency is set for a chore, set to default
DEFAULT_COMPLETION_FREQUENCY = "Weekly"

# For making Google API calls
api_object = api.get_api_object(APP_DETAILS_FILE)


""" --- Get ID for MIC Chore Candidates spreadsheet --- """
# ID for the sheet is stored in a text file for security
with open('../bin/sheet_id.txt', 'r') as f:
		sheet_id = f.read().splitlines()[0]

def update_json():
	""" Update candidates.json and chores.json
	This script extracts information from the MIC Chore Scheduler
	spreadsheet and saves it locally
	"""
	sheets_service = api_object.get_sheets_service()
	# GET CANDIDATE INFORMATION
	print("Updating Candidate Information...")
	sheet_range= 'Candidates!A2:G'
	result = sheets_service.spreadsheets().values().get( 
			spreadsheetId=sheet_id, range=sheet_range).execute()
	values = result.get('values', [])
	if not values:
		api_object.log_message(sheet_id, "ERROR: No candidates in sheet", LOGFILE)
	else:
		candidates = []
		for row_num, row in enumerate(values):
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
				api_object.log_message(sheet_id, "INDEX ERROR:"
							" for candidate on row %d" % row_num)
		# Store candidate information
		try:
			with open('../bin/candidates.json', 'w') as candidatesJSON:
				json.dump(candidates, candidatesJSON)
		except:
			api_object.log_message(sheet_id, "ERROR saving Candidate info "
						"candidates.json.", LOGFILE)
	
	# GET CHORE INFORMATION
	print("Updating Chores...")
	sheet_range = 'Chores!A2:C'
	result = sheets_service.spreadsheets().values().get( 
			spreadsheetId=sheet_id, range=sheet_range).execute()
	values = result.get('values', [])
	if not values:
		print('No data found in the spreadsheet.')
		api_object.log_message(sheet_id, "ERROR: No chores in sheet", LOGFILE)
		sys.exit()
	# Add chores to chores.json
	chores = []
	for row_num, row in enumerate(values):
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
			api_object.log_message(sheet_id, "INDEX ERROR:"
						" for chore on row %d" % row_num)
	# Store chore information
	try:
		with open('../bin/chores.json', 'w') as choresJSON:
			json.dump(chores, choresJSON)
	except: 
		api_object.log_message(sheet_id, "ERROR saving chores to chores.json",
					LOGFILE)

def update_spreadsheet():
	""" Update spreadsheet using information stored in local JSON files
	This only changes information TO THE RIGHT of the black lines on the
	spreadsheet
	On the candidates tab - Assigned chores
	On the chores tab - Assignee(s), Assignment Time, Completion Status
	"""
	pass

		

if __name__ == '__main__':
	update_json()
