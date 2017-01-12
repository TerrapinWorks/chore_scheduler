""" Log messages internally and to the spreadsheet
To log any kind of message to the internal log and 
to the Log tab of the spreadsheet, just import this
module and call
publish_log(message)
"""

# For printing date with log message
from datetime import datetime

# Publish to spreadsheet
import sys
sys.path.append('google_api_functions/')
import google_api_functions as api

APP_DETAILS_FILE = "../bin/app_details.json"

def log_message(message):
	""" Publish log messages to the Log tab 
	of the MIC Chore Scheduler spreadsheet
	Log messages are also saved locally to
	chore_scheduler/bin/log.txt
	"""
	# Get the current time
	now = datetime.now()
	time_str = "%d-%d-%d %d:%d" % (
					   now.year, now.month, now.day, now.hour, now.minute)
	# Save log message to the log file
	with open("../bin/log.txt", "a") as log_file:
		log_file.write(time_str + "\n" + message + "\n")
	# Log to the Google Sheet
	with open("../bin/sheetID.txt", "r") as sheet_id_file:
		# Id on first line of sheetID.txt
		sheet_id = sheet_id_file.read().splitlines()[0]
	# Get the next usable row on the spreadsheet
	api_object = api.get_api_object(APP_DETAILS_FILE)
	sheets_service = api_object.get_sheets_service()
	# Skip the first row, which has column labels
	sheets_range = "Log!A2:B"
	values_result = sheets_service.spreadsheets().values().get(
				spreadsheetId=sheet_id, range=sheets_range).execute()
	# First usable row will be 2
	empty_row = str(len(values_result.get("values",[])) + 2)
	sheets_range = "Log!A" + empty_row + ":B" + empty_row
	values = [[time_str, message]]
	body = {"values" : values}
	update_result = sheets_service.spreadsheets().values().update(
				spreadsheetId=sheet_id, range=sheets_range,
				valueInputOption="RAW", body=body).execute()
	print("Sending message: %s" % message)
