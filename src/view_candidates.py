import json

""" Print information for current candidates
this script loads the information stored for candidates
from candidates.json and prints it out in a readable format
"""

with open('../bin/candidates.json') as candidates:
  JSON_string = candidates.read()

candidates = json.loads(JSON_string)

print()
for candidate in candidates:
  print( 
  	"Name: \t%s\nEmail: \t%s\n"
	"Mon: \t%s\nTues: \t%s\nWed: \t%s\nThurs: \t%s\nFri: \t%s\n"
	% (candidate["name"], candidate["email"], 
	candidate["mon"], candidate["tues"], candidate["wed"],
	candidate["thurs"], candidate["fri"]))
