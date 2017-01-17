#! /usr/bin/python3
""" Print chore information to the console
Loads chore info stored in chores.json and prints
it in a readable format to the console
"""

import json

with open('../bin/chores.json', 'r') as choresJSON:
	chore_list = json.loads(choresJSON.read())

for chore in chore_list:
		print("Chore:\t\t\t%s\nCompletion Frequency:\t%s\nAssignee(s):\t\t%s\n"
					"Assignment Time:\t%s\nCompletion Status:\t%s\n" 
					% (chore['name'], chore['completion_frequency'],
					chore['assignees'], chore['assignment_time'],
					chore['completion_status']))
