"""
USER NOTES
==========

This script is intended to be run from the right-click menu in OS X.

To do this, it should be pasted into an Automator script.
1. Launch the Automator application.
2. Click Service to create a new right-click Service.
3. Choose "files or folders" for "Service Receives Selected".
4. Drag and drop "Run Shell Script" from the menu of options in the left panel.
5. Choose "/usr/bin/python" for Shell.
6. Choose "as arguments" for "Pass input".
7. Paste this entire script into the text field.

Save and close the Automator file.

To run the script, right-click any text file containing the output of a BEVL or XBEVL run,
and "bevl_sheetify" should appear as an option. Clicking it should result in a "sheetified"
version of the file appearing on the user's desktop.


USER PREFERENCES
================

Here are some preferences that the user can edit.
"""

# EMPTY_CELLS_ALLOWED may be set to either True or False.
# with False, every cell in every row will be populated with a value;
# with True, the report will look cleaner, because each new category of requirement only appears once.
EMPTY_CELLS_ALLOWED = True

# WORKING_DIRECTORY can be updated to any folder in the user's home directory
# that they want the outfile to appear in.
WORKING_DIRECTORY = 'Desktop'

"""
MAIN FUNCTIONS
==============
"""


import os
import re
import csv
import sys

def parse_input(argv):
    file_path = os.path.abspath(argv[1])
    working_directory = os.path.dirname(file_path)
    filename = file_path.split('/')[-1]
    return working_directory, filename

def make_outfile_name(filename):
    base = os.path.splitext(filename.split('/')[-1])[0]
    outfile_name = os.path.expanduser('~/{}/{}-sheetified.csv'.format(WORKING_DIRECTORY, base))
    i = 1
    while os.path.exists(outfile_name):
        outfile_name = os.path.expanduser('~/{}/{}-sheetified ({}).csv'.format(WORKING_DIRECTORY, base, i))
        i += 1
    return outfile_name

def read_csv(filename):
    with open(filename, 'r') as infile:
        return [line for line in infile]

class Audit:

    def __init__(self):
        self.requirements = []

    def create_outfile(self, filename, repetitive=EMPTY_CELLS_ALLOWED):
        headers = ['Requirement', 'Concentrate', 'Note', 'Subrequirement', 'Course Code', 'Course Name',
                   'Term Met', 'Grade', 'Credits']
        with open(filename, 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(headers)
            last_vals = [None] * 8
            for r in self.requirements:
                for c in r.concentrates:
                    for s in c.subrequirements:
                        for course in s.courses:
                            record = [r.name, c.name, c.note, s.name, course.name, course.full_name,
                                      course.term_met, course.grade, course.credits]
                            for i, val in enumerate(record[:4]):
                                if repetitive == False and last_vals[i] == val:
                                    record[i] = ''
                                else:
                                    last_vals[i] = val
                            writer.writerow(record)

class Requirement:
    def __init__(self, name):
        self.name = name
        self.concentrates = []

class Concentrate:
    def __init__(self, name):
        self.name = name
        self.note = ''
        self.subrequirements = []

class Subrequirement:
    def __init__(self, number, name):
        #if name[:5] != 'Group':
        #    name = "Group {}: {}".format(number, name)
        self.name = name
        self.courses = []

class Course:
    def __init__(self, full_name, term_met, grade, credits):
        self.name = full_name.split(' ')[0]
        self.full_name = ' '.join(full_name.split(' ')[1:])
        self.full_name = re.sub(r'[\.]{4,}', '...', self.full_name) # Replace too-long ellipses with normal ones.
        self.term_met = term_met
        self.grade = grade
        self.credits = credits

def parse_lines(data):
    audit = Audit()
    requirement, concentrate, subrequirement, course = None, None, None, None
    for line in data:
        if line.find('C)') == 0:
            # Add any previous requirement.
            if requirement:
                audit.requirements.append(requirement)
            # Process new requirement.
            name = line.split(':')[1].strip()
            requirement = Requirement(name)

        elif line.find('C)') == 3:
            # Add any previous concentrates in audit's previous requirement.
            if concentrate:
                requirement.concentrates.append(concentrate)
            # Process new concentrate.
            name = line.split(':')[1].strip()
            concentrate = Concentrate(name)

        elif line.find('>') == 6:
            note_content = line.split('>')[1].strip()
            concentrate.note += ' '+note_content
            concentrate.note = concentrate.note.strip()

        elif line.find('C)') == 6:
            # Add any previous courses in concentrate's previous subrequirement.
            if subrequirement:
                concentrate.subrequirements.append(subrequirement)
            # Process new subrequirement.
            name = line.split(')')[1].strip()
            number = len(concentrate.subrequirements) + 1
            subrequirement = Subrequirement(number, name)

        elif line[:10] == ' '*10 and line[10] != ' ':
            # Process new course.
            course = Course(full_name=line[10:45], term_met=line[46:52],
                            grade=line[55:57], credits=line[65:66])
            subrequirement.courses.append(course)

    # Add final requirement.
    audit.requirements.append(requirement)

    return audit


def main():
    infile_name = sys.argv[1]

    print('parsing data in csv file...')
    text = read_csv(infile_name)

    print('parsing records in data...')
    a = parse_lines(text)

    print('creating csv outfile...')
    outfile_name = make_outfile_name(infile_name)
    a.create_outfile(outfile_name)

    print('csv outfile created ({})'.format(outfile_name))

if __name__ == '__main__':
    main()
