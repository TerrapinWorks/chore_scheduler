""" Chore Scheduler for the MIC
An instance of the Scheduler class will be run continuously
to reassign chores randomly to candidates. 
The scheduler will download information from the spreadsheet
to candidates.json and chores.json, calculate assignments and
update the JSON files, and then update the information on the sheet
using the JSON files
"""

# For reading candidate info from ../bin/candidates.json
import json

# For updating candidates.json
import sheets_interface as sheets

# For handling time
import datetime

# For randomizing chore scheduling
from random import shuffle

# Files where information is stored
CANDIDATES_FILE = '../bin/candidates.json'
CHORES_FILE = '../bin/chores.json'

# Used to calculate when chores should be reassigned
reassignment_intervals = {
	'Daily': 1,
	'Weekly': 7,
	'Biweekly': 14,
	'Monthly': 30
}

class Scheduler:
	def __init__(self):
		""" Start the Sheduler
		Downloads all information from the spreadsheet and loads it
		as instance variables
		"""
		sheets.log_message("UPDATING SCHEDULER. CHORE STATUSES WILL NOT CHANGE.")
		sheets.update_json()

	def schedule_chores(self):
		""" Randomly assign chores to the candidates. 
		This takes into consideration who has been assigned to
		a particular chore since the last reset so that everyone will
		be assigned a chore before it is given to the same person twice.
		This is achieved using the "Recently Completed" column of the
		Candidates tab. When everyone has recently completed a chore,
		that chore is removed from everyone's recently completed.
		"""
		# Load the candidates from candidates.json
		try: 
			with open(CANDIDATES_FILE, 'r') as dataJSON:
				candidates = json.loads(dataJSON.read())
				self.candidates = shuffle(candidates)
		except:
			sheets.log_message('NOTE in assign_chores(): '
						' candidates.json appears to be empty')
			return True
		# Load chores from chores.json
		try:
			with open(CHORES_FILE, 'r') as dataJSON:
				self.chores = json.loads(dataJSON.read())
		except:
			sheets.log_message('NOTE in assign_chores(): '
						' chores.json appears to be empty.'
			return True
		# Data has been successfully loaded. Assign chores.
		for chore in self.chores:
			assign_chore = False
			# Check if enough time has passed since the chore was last assigned
			# Note that date is stored as "YYYY-MM-DD-HH:MM"
			try :
				date_list = chore['assignment_time'].split('-')
				assignment_date = datetime.date(int(date_list[0], int(date_list[1]),
							int(date_list[2]))
				current_date = datetime.datetime.now().date()
				time_diff = current_date - assignment_date
				time_diff = time_diff.days
				valid_time = True
			except:
				# If an error is detected in the time string, reassign the chore
				valid_time = False
				assign_chore = True
			if valid_time:
				try:
					# Check if enough days have passed since assignment date
					if time_diff > reassignment_intervals[chore['completion_frequency']]:
						# Chore should be reassigned
						assign_chore = True
				except KeyError:
					# Completion Frequency was invalid
					sheets.log_message("ERROR in assign_chores(): Key Error for chore "
								+ chore['name'] + " . Make sure Completion Frequency is valid.")
					chore['completion_frequency'] = sheets.DEFAULT_COMPLETION_FREQUENCY
					assign_chore = True
			if assign_chore:
				assign_chore(chore)
				self.save_data()
				return True

	def assign_chore(self, chore):
			candidate_found = False
			# Find candidate who has not recently completed
			for candidate in self.candidates:
				recently_completed = candidate['recently_completed'].split(' ')
				if recently_completed.find(chore['name']) < 0:
					# Candidate found. Assign chore
					candidate_found = True
					candidate['assigned_chores'] += chore['name'] + " "
					chore['assignees'] += candidate['name'] + " "
					now = datetime.datetime.now()
					chore['assignment_time'] = "%d-%d-%d-%d:%d" % (
								now.year, now.month, now.day, now.hour, now.minute)	
					chore['completion_status'] = 'FALSE'
