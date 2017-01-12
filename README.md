# Chore Scheduler

Automatic chore scheduler for Terrapin Works Employees in the MIC.
The behavior of the scheduler can be controlled by changing the 
[MIC Chore Scheduler Spreadsheet](https://docs.google.com/a/eng.umd.edu/spreadsheets/d/1c1cVvNhbpoCgtIPOfAcU0H-PAr1Lb6XZJ6tqIjh6Od4/edit?usp=sharing)
On the spreadsheet, an administrator will maintain a list of chore candidates' names, emails,
and start times for shifts during the week. The administrator will also update the
list of chores and how frequently they should be completed. The scheduler will automatically
assign chores to candidates with the desired frequency for each chore. Candidates will recieve
emails at the beginning of their shifts telling them of their responsibility. Chores may include sweeping the MIC, checking the extruder repair station and repairing extruders, etc.

Errors are automatically logged internally to the Pi and to the Log tab on the spreadsheet.
