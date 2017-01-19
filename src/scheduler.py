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

	def load_data(self):
		# Load the candidates from candidates.json
		try: 
			with open(CANDIDATES_FILE, 'r') as dataJSON:
				self.candidates = json.loads(dataJSON.read())
		except:
			sheets.log_message('NOTE in assign_chores(): '
						' candidates.json appears to be empty')
		# Load chores from chores.json
		try:
			with open(CHORES_FILE, 'r') as dataJSON:
				self.chores = json.loads(dataJSON.read())
		except:
			sheets.log_message('NOTE in assign_chores(): '
						' chores.json appears to be empty.')

	def schedule_chores(self):
		""" Randomly assign chores to the candidates. 
		This takes into consideration who has been assigned to
		a particular chore since the last reset so that everyone will
		be assigned a chore before it is given to the same person twice.
		This is achieved using the "Recently Completed" column of the
		Candidates tab. When everyone has recently completed a chore,
		that chore is removed from everyone's recently completed.
		"""
		self.load_data()
		for chore in self.chores:
			assign_chore = False
			# Check if enough time has passed since the chore was last assigned
			# Note that date is stored as "YYYY-MM-DD-HH:MM"
			if chore['assignment_time'] != None:
				date_list = chore['assignment_time'].split('-')
				assignment_date = datetime.date(int(date_list[0]), int(date_list[1]),
							int(date_list[2]))
				current_date = datetime.datetime.now().date()
				time_diff = current_date - assignment_date
				time_diff = time_diff.days
				valid_time = True
			else:
				# If no time string, reassign
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
				self.assign_chore(chore)
				# Save updated information
				self.save_data()

	def assign_chore(self, chore):
		candidate_found = False
		shuffle(self.candidates)
		self.sort_candidates()
		for candidate in self.candidates:
			if candidate_found:
				break
			recently_completed = candidate['recently_completed'].split(', ') if \
						candidate['recently_completed'] != None else []
			if chore['name'] not in recently_completed:
				# Candidate found. Assign chore
				candidate_found = True
				# Add chore to assigned chores
				assigned_chores = candidate['assigned_chores']
				if assigned_chores == None or assigned_chores == "":
					# Blank list
					candidate['assigned_chores'] = chore['name']
				else:
					candidate['assigned_chores'] += ", " + chore['name']
				# Add candidate to assignees
				assignees = chore['assignees']
				if assignees == None or assignees == "":
					# Blank list
					chore['assignees'] = candidate['name']
				else:
					chore['assignees'] += ", " + candidate['name']
				# Add assignment time
				now = datetime.datetime.now()
				chore['assignment_time'] = "%d-%d-%d-%d:%d" % (
							now.year, now.month, now.day, now.hour, now.minute)	
				chore['completion_status'] = 'FALSE'
				sheets.log_message("ASSIGN: %s has been assigned to %s"
							% (chore['name'], candidate['name']))
		if not candidate_found:
			self.reset_recent(chore)
			self.assign_chore(chore)

	def sort_candidates(self):
		""" Sort candidates in order of who has most chores currently assigned
		"""
		sorted_candidates = []
		for candidate in self.candidates:
			candidate_num = len(candidate['assigned_chores'].split(', ')) if \
						candidate['assigned_chores'] != None else 0
			if len(sorted_candidates) == 0:
				sorted_candidates.append(candidate)
				continue
			for index, sorted_candidate in enumerate(sorted_candidates):
				sorted_num = len(sorted_candidate['assigned_chores'].split(', ')) if \
							sorted_candidate['assigned_chores'] != None else 0
				if index == (len(sorted_candidates) - 1):
					sorted_candidates.append(candidate)
					break
				if candidate_num < sorted_num:
					sorted_candidates.insert(index, candidate)
					break
		self.candidates = sorted_candidates
	
	def reset_recent(self, chore):
		""" Remove the chore from everyone's Recently Completed
		"""
		for candidate in self.candidates:
			current_recent = [item.strip() for item in 
						candidate['recently_completed'].split(' ')]
			current_recent.remove(chore['name'])

	def save_data(self):
		""" Save information from the scheduler to the JSON files
		"""
		# Save candidate info
		with open(CANDIDATES_FILE, 'w') as candidatesJSON:
			json.dump(self.candidates, candidatesJSON)
		# Save chore info
		with open(CHORES_FILE, 'w') as choresJSON:
			json.dump(self.chores, choresJSON)
