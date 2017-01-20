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
CANDIDATES_RANGE = "Candidates!A2:I"
# Sheet region with Chores info
CHORES_RANGE = "Chores!A2:E"

# For making Google API calls
api_object = api.get_api_object(APP_DETAILS_FILE)
sheets_service = api_object.get_sheets_service()

""" --- Get ID for MIC Chore Candidates spreadsheet --- """
# ID for the sheet is stored in a text file for security
with open('../bin/sheet_id.txt', 'r') as f:
		sheet_id = f.read().splitlines()[0]

""" --- Simplified log_message for use by chore scheduler --- """
def log_message(message):
	api_object.log_message(sheet_id, message, LOGFILE)

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
	data_upper = data_type.upper()
	# Make sure that the requested data is one of the two allowed types
	if data_type != 'candidates' and data_type != 'chores':
		log_message("ERROR in get_data(): %s is invalid data type" 
					% data_upper)
		return False
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
		log_message("NOTE in get_data() for " + data_upper
					+ ": No data on sheet")
		# Save backup
		system("cp " + data_file + " " + backup_file)
		if save:
			with open(data_file, 'w') as dataJSON:
				json.dumps('[]', dataJSON)
		return True 
	else:
		# Spreadsheet contains data. 
		data_dict = []
		for row_num, row in enumerate(values):
			try:
				if row[0] == '':
					# Nameless row is skipped
					log_message("ERROR in get_data(): %s does not have a name on line %d"
								% (data_upper, row_num + 2))
					continue
				length = len(row)
				name = row[0]
				if data_type == 'candidates':
					# Ignore entries in the sheet past the useful columns
					length = length if length < 10 else 9
					# Tuples = (email, assigned_chores, recently_completed)
					email = row[1] if length > 1 else None
					assigned_chores = row[7] if length > 7 else None
					recently_completed = row[8] if length > 8 else None
					candidate = {
								"name": name,
								"email": email,
								"assigned_chores": assigned_chores,
								"recently_completed": recently_completed
								}
					# Get start times
					weekdays = ["mon", "tues", "wed", "thurs", "fri"]
					for day_num, day in enumerate(weekdays):
						candidate[day] = \
									row[day_num + 2] if length > (day_num + 2) else None
					data_dict.append(candidate)
				elif data_type == 'chores':
					# Ignore entries in the sheet past the useful columns
					length = length if length < 6 else 5
					# Set default completion status if cell is empty
					completion_frequency = row[1] if ((length > 1) and row[1] != '') \
																					else DEFAULT_COMPLETION_FREQUENCY
					# Completion frequency can only be:
					# Daily, Weekly, Biweekly, or Monthly
					if not (completion_frequency == 'Daily' or
								completion_frequency == 'Weekly' or
								completion_frequency == 'Biweekly' or
								completion_frequency == 'Monthly'):
						log_message("NOTE in get_gata() for %s: Invalid Completion Frequency on row %d. "
									"Setting to default of %s" %(data_upper, row_num + 2, DEFAULT_COMPLETION_FREQUENCY))
						completion_frequency = DEFAULT_COMPLETION_FREQUENCY	
					# Set fields to None if empty
					assignees = row[2] if length > 2 else None
					assignment_time = row[3] if length > 3 else None
					completion_status = row[4] if length > 4 else None
					chore = {
								"name" : name,
								"completion_frequency" : completion_frequency,
								"assignees" : assignees,
								"assignment_time" : assignment_time,
								"completion_status" : completion_status
								}
					data_dict.append(chore)
			except IndexError:
				log_message("INDEX ERROR in get_data() for " + data_upper +
				" on row %d" % (row_num + 2))
		# Save backup
		system("cp " + data_file + " " + backup_file)
		# Store candidate information
		if save:
			try:
				with open(data_file, 'w') as dataJSON:
					json.dump(data_dict, dataJSON)
			except:
				log_message(sheet_id, "ERROR in get_data() for " + data_upper
							+ ": Error saving Candidate info candidates.json.")
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
	data_upper = data_type.upper()
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
		log_message("ERROR in set_data for " + data_upper +
		": data file is empty: " + data_file)
		return False
		# Clear current sheet contents
	api_object.clear_sheet_range(sheet_id, sheet_range)
	# Sheet contents with JSON contents
	uploaded = json_to_sheet(data_type, data_file)
	return uploaded

def json_to_sheet(data_type, json_file):
	""" Upload from either candidates.json or chores.json to the sheet
	We assume that this is run after clear_sheet_range() so the sheet
	will be empty
	"""
	data_upper = data_type.upper()
	# Set range based on data being uploaded
	sheet_range = CANDIDATES_RANGE if data_type == 'candidates' else CHORES_RANGE
	# Load data from JSON into dictionary
	with open(json_file, 'r') as dataJSON:
		data_dict = json.loads(dataJSON.read())
	# Make sure one of the two allowed types of data is being uploaded
	if data_type != 'candidates' and data_type != 'chores':
		log_message("ERROR in json_to_sheet() for " + data_upper + 
		" is invalid data type")
		return False
	# Upload to the sheet
	values = []
	for data in data_dict:
		if data_type == 'candidates':
			values.append(
				[data['name'], data['email'], data['mon'], data['tues'],
				 data['wed'], data['thurs'], data['fri'],
				 data['assigned_chores'], data['recently_completed']]
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
