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

# Files where information is stored
CANDIDATES_FILE = '../bin/candidates.json'
CHORES_FILE = '../bin/chores.json'

# Used to calculate when chores should be reassigned
reassignment_time = {
	'Daily': 1,
	'Weekly': 7,
	'Biweekly': 14,
	'Monthly': 30
}

def num_assigned_chores(candidate):
		""" Returns how many chores are currently assigned to a candidate
		"""
		return len(candidate['assigned_chores'].split(', ')) if \
						not candidate['assigned_chores'] is None else 0

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
			sheets.log_message('NOTE in load_data(): '
						' candidates.json appears to be empty')
		# Load chores from chores.json
		try:
			with open(CHORES_FILE, 'r') as dataJSON:
				self.chores = json.loads(dataJSON.read())
		except:
			sheets.log_message('NOTE in load_data(): '
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
			# Check if enough days have passed since assignment date
			assignment_time = chore['assignment_time']
			if (not assignment_time is None) and (assignment_time != ""):
				# Date is stored as dash separated parts: "YYYY-MM-DD-HH:MM"
				date_list = [int(part) 
							for part in chore['assignment_time'].split('-')[0:3]]
				assignment_date = datetime.date(date_list[0], date_list[1],
							date_list[2])
				time_diff = datetime.datetime.now().date() - assignment_date
				try:
					# Skip assignment if it is not time to reassign
					if time_diff.days < \
									reassignment_time[chore['completion_frequency']]:
						continue
				except KeyError:
					# Completion Frequency was invalid
					sheets.log_message("ERROR in schedule_chores(): Key Error for chore %s "
								" . Make sure Completion Frequency is valid." % chore['name'])
					chore['completion_frequency'] = sheets.DEFAULT_COMPLETION_FREQUENCY
			self.assign_chore(chore)
			# Save updated information
			self.save_data()

	def assign_chore(self, chore):
		self.candidates = sorted(self.candidates, key=num_assigned_chores)
		for candidate in self.candidates:
			recently_completed = candidate['recently_completed'].split(', ') if \
						not candidate['recently_completed'] is None else []
			if chore['name'] not in recently_completed:
				# Candidate found. Assign chore
				# Add chore to assigned chores
				assigned_chores = candidate['assigned_chores']
				if assigned_chores == None or assigned_chores == "":
					# Blank list
					assigned_chores = chore['name']
				else:
					assigned_chores = "%s, %s" %(assigned_chores, chore['name'])
				candidate['assigned_chores'] = assigned_chores
				# Add candidate to assignees
				assignees = chore['assignees']
				if assignees == None or assignees == "":
					# Blank list
					assignees = candidate['name']
				else:
					assignees = "%s, %s" %(assignees, candidate['name'])
				chore['assignees'] = assignees
				# Add assignment time
				now = datetime.datetime.now()
				chore['assignment_time'] = "%d-%d-%d-%d:%d" % (
							now.year, now.month, now.day, now.hour, now.minute)	
				chore['completion_status'] = 'FALSE'
				sheets.log_message("ASSIGN: %s has been assigned to %s"
							% (chore['name'], candidate['name']))
				break
		else:
			self.reset_recent(chore)
			self.assign_chore(chore)
	
	def reset_recent(self, chore):
		""" Remove the chore from everyone's Recently Completed
		"""
		for candidate in self.candidates:
			recent = [item.strip() for item in 
						candidate['recently_completed'].split(', ') if item != ""]
			recent.remove(chore['name'])
			candidate['recently_completed'] = ', '.join(recent)

	def save_data(self):
		""" Save information from the scheduler to the JSON files
		"""
		# Save candidate info
		with open(CANDIDATES_FILE, 'w') as candidatesJSON:
			json.dump(self.candidates, candidatesJSON)
		# Save chore info
		with open(CHORES_FILE, 'w') as choresJSON:
			json.dump(self.chores, choresJSON)
