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
import update


class Scheduler:
	def __init__(self):
		""" Start the Sheduler
		Downloads all information from the spreadsheet and loads it
		as instance variables
		"""
		log_message("UPDATING SCHEDULER. CHORE STATUSES WILL NOT CHANGE.")
		self.update_scheduler()

	def update_scheduler():
		""" Update candidates and chores stored in the scheduler
		We first save information from the Google sheets locally to
		candidates.json and chores.json and then read the data from
		the JSON files into the scheduler.
		"""
		update.update_json()
		# Load candidate information
		with open('../bin/candidates.json', 'r') as candidatesJSON:
			self.candidates = json.loads(candidatesJSON.read())
		# Load chore information
		with open('../bin/chores.json', 'r') as choresJSON:
			self.chores = json.loads(choresJSON.read())

	def update_spreadsheet():
		""" Update MIC Chore Scheduler Google Sheet using information
		stored in candidates.json and chores.json. 
		"""
		# Save candidate information
		with open('../bin/candidates.json', 'w') as candidatesJSON:
			json.dumps(self.candidates, candidatesJSON)
		# Save chore information
		with open('../bin/chores.json', 'w') as choresJSON:
			json.dumps(self.chores, choresJSON)
		update.update_spreadsheet()
