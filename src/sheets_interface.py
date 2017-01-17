#!/usr/bin/python3
""" --- Imports --- """
# For saving candidate info
import json

# In case we need to exit on an error
import sys

# For saving backups
from os import system

# User written module for Google API Calls
sys.path.append('google_api_functions/')
import google_api_functions as api

# app_detals.json contains info for the Google API object
APP_DETAILS_FILE = "../bin/app_details.json"
# Paths to files where info is stored/backed up
CANDIDATES_FILE = "../bin/candidates.json"
CANDIDATES_BACKUP = "../bin/backup_candidates.json"
CHORES_FILE = "../bin/chores.json"
CHORES_BACKUP = "../bin/backup_chores.json"
# For logging errors internally
LOGFILE = "../bin/log.txt"
# If no completion frequency is set for a chore, set to default
DEFAULT_COMPLETION_FREQUENCY = "Weekly"
# Sheet region with Candidate info
CANDIDATES_RANGE = "Candidates!A2:H"
# Sheet region with Chores info
CHORES_RANGE = "Chores!A2:E"

# For making Google API calls
api_object = api.get_api_object(APP_DETAILS_FILE)
sheets_service = api_object.get_sheets_service()

""" --- Get ID for MIC Chore Candidates spreadsheet --- """
# ID for the sheet is stored in a text file for security
with open('../bin/sheet_id.txt', 'r') as f:
		sheet_id = f.read().splitlines()[0]


""" --- Functions to get data from spreadsheet --- """
def update_json():
	""" Update candidates.json and chores.json
	This script extracts information from the MIC Chore Scheduler
	spreadsheet and saves it locally
	Returns true only if both updates are successful
	"""
	candidates_update =	get_data('candidates')
	chores_update = get_data('chores')
	return (candidates_update and chores_update)

def get_data(data_type='candidates', save=True):
	""" Get information from spreadsheet and save to local JSON
	Candidates and Chores with no name are skipped
	Blank sheets count as a successful get_data()
	Returns true on success
	"""
	api_object.log_message(sheet_id, 'GET: downloading DATA'
				' = ' + data_type + ' to the Pi', LOGFILE)
	# Set range/files to use depending on whether function is getting
	# candidates or chores data
	sheet_range = CANDIDATES_RANGE if data_type == 'candidates' else CHORES_RANGE
	data_file = CANDIDATES_FILE if data_type == 'candidates' else CHORES_FILE
	backup_file = CANDIDATES_BACKUP if data_type == 'candidates' else CHORES_BACKUP
	result = sheets_service.spreadsheets().values().get( 
			spreadsheetId=sheet_id, range=sheet_range).execute()
	values = result.get('values', [])
	if not values:
		# No data on the sheet
		# Clear candidates.json and count as success
		api_object.log_message(sheet_id, "NOTE in get_data() for " + 
					"DATA = " + data_type + ": No data on sheet", LOGFILE)
		# Save backup
		system("cp " + data_file + " " + backup_file)
		if save:
			with open(data_file, 'w') as dataJSON:
				json.dumps('[]', dataJSON)
		return True 
	else:
		# Spreadsheet contains data. 
		# Make sure that the requested data is one of the two allowed types
		if not (data_type == 'candidates' or data_type == 'chores'):
			api_object.log_message(sheet_id, "ERROR in get_data(): "
						"DATA = " + data + " is invalid data type", LOGFILE)
			return False
		data_dict = []
		for row_num, row in enumerate(values):
			try:
				if row[0] != '':
					if data_type == 'candidates':
						email = row[1] if len(row) > 1 else None
						candidate = {"name" : row[0], "email" : email}
						# Get start times
						weekdays = ["mon", "tues", "wed", "thurs", "fri"]
						for day_num in range(0, len(weekdays)):
							candidate[weekdays[day_num]] = \
										row[day_num + 2] if len(row) > (day_num + 2) else None
						candidate["assigned_chores"] = row[7] if len(row) > 7 else None
						data_dict.append(candidate)
					elif data_type == 'chores':
						# Set default completion status if cell is empty
						completion_frequency = row[1] if ((len(row) > 1) and row[1] != '') \
																						else DEFAULT_COMPLETION_FREQUENCY
						# Set fields to None if empty
						assignees = row[2] if ((len(row) > 2) and row[2] != '') else None
						assignment_time = row[3] if ((len(row) > 3) and row[3] != '') else None
						# Set completion status to false if cell is empty
						completion_status = row[4] if len(row) > 4 else "FALSE"
						chore = {
											"name" : row[0],
											"completion_frequency" : completion_frequency,
											"assignees" : assignees,
											"assignment_time" : assignment_time,
											"completion_status" : completion_status
										}
						data_dict.append(chore)
				else:
					api_object.log_message(sheet_id, "ERROR in get_data(): "
								+ data_type + " does not have a name on line %d" % (row_num + 2))
			except IndexError:
				api_object.log_message(sheet_id, "INDEX ERROR in get_data(): "
						"DATA = " + data_type + " on row %d" % (row_num + 2))
		# Save backup
		system("cp " + data_file + " " + backup_file)
		# Store candidate information
		if save:
			try:
				with open(data_file, 'w') as dataJSON:
					json.dump(data_dict, dataJSON)
			except:
				api_object.log_message(sheet_id, "ERROR in get_data() for" 
							"DATA = " + data + ": "
							"Error saving Candidate info candidates.json.", LOGFILE)
				return False
		return True


""" --- Functions to update spreadsheet with data stored locally ---"""
def update_spreadsheet():
	""" Update spreadsheet using information stored in local JSON files
	This only changes information TO THE RIGHT of the black lines on the
	spreadsheet
	On the candidates tab - Assigned chores
	On the chores tab - Assignee(s), Assignment Time, Completion Status
	Returns True only if both updates are successful
	"""
	candidates_update = set_data(data_type='candidates')
	chores_update = set_data(data_type='chores')
	return (candidates_update and chores_update)

def set_data(data_type='candidates'):
	""" Reset Candidate information on spreadsheet
	Deletes current information in Candidates tab
	and replaces with current contents of candidates.json
	Returns true on success
	"""
	api_object.log_message(sheet_id, 'BACKUP: Backing up data to the PI',	LOGFILE)
	# Set range/files to use depending on whether function is getting
	# candidates or chores data
	sheet_range = CANDIDATES_RANGE if data_type == 'candidates' else CHORES_RANGE
	data_file = CANDIDATES_FILE if data_type == 'candidates' else CHORES_FILE
	# Save backup of what is currently on the sheet
	get_data(data_type=data_type, save=False)
	# Read candidate information
	try:
		with open(data_file, 'r') as dataJSON:
			data = json.loads(dataJSON.read())
	except:
		api_object.log_message(sheet_id, "ERROR in set_data for DATA"
					" = " + data_type + ": data file is empty: " + data_file, LOGFILE)
		return False
	api_object.log_message(sheet_id, 'SET: uploading DATA = '
				+ data_type + ' from the Pi', LOGFILE)
	# Clear current sheet contents
	api_object.clear_sheet_range(sheet_id, sheet_range)
	# Sheet contents with JSON contents
	return json_to_sheet(data_type, data_file)

def json_to_sheet(data_type, json_file):
	""" Upload from either candidates.json or chores.json to the sheet
	We assume that this is run after clear_sheet_range() so the sheet
	will be empty
	"""
	# Set range based on data being uploaded
	sheet_range = CANDIDATES_RANGE if data_type == 'candidates' else CHORES_RANGE
	# Load data from JSON into dictionary
	with open(json_file, 'r') as dataJSON:
		data_dict = json.loads(dataJSON.read())
	# Make sure one of the two allowed types of data is being uploaded
	if data_type != 'candidates' and data_type != 'chores':
		api_object.log_message(sheet_id, "ERROR in json_to_sheet(): "
						"DATA = " + data + " is invalid data type", LOGFILE)
		return False
	# Upload to the sheet
	values = []
	for data in data_dict:
		if data_type == 'candidates':
			values.append(
				[data['name'], data['email'], data['mon'], data['tues'],
				 data['wed'], data['thurs'], data['fri'],
				 data['assigned_chores']]
			)
		elif data_type == 'chores':
			values.append(
				[data['name'], data['completion_frequency'],
				 data['assignees'], data['assignment_time'], 
				 data['completion_status']]
			)
	body = {'values': values}
	sheets_service.spreadsheets().values().update (
				spreadsheetId=sheet_id, range=sheet_range,
				valueInputOption='RAW', body=body).execute()


if __name__ == '__main__':
	update_json()
