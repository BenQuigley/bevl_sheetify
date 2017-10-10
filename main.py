#!/usr/bin/python

import os
import re
import csv
import fileinput
from sys import argv

TEST_MODE = False

def read_csv(filename=None):
    data = []
    if len(argv) > 1:
        filename = ' '.join(argv[1:])
    elif TEST_MODE:
        filename = 'sample.txt'
    if filename:
        with open(filename, 'r') as infile:
            for line in infile:
                data.append(line)
    else:
        for i, line in enumerate(fileinput.input()):
            data.append(line)
    return data

class Audit:

    def __init__(self):
        self.requirements = []

    def create_outfile(self, repetitive=False):
        headers = ['Requirement', 'Concentrate', 'Note', 'Subrequirement', 'Course Code', 'Course Name',
                   'Term Met', 'Grade', 'Credits']
        with open('outfile.csv', 'w') as outfile:
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
    print('parsing data in csv file...')
    text = read_csv()
    print('parsing records in data...')
    a = parse_lines(text)
    print('creating csv outfile...')
    a.create_outfile()
    print('csv outfile created.')

if __name__ == '__main__':
    main()