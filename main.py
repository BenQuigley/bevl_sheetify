import os
import csv
import fileinput
from sys import argv

TEST_MODE = True

def read_csv():
    data = []
    if len(argv) > 1:
        data = argv[1:]
    elif TEST_MODE:
        with open('sample.txt', 'r') as infile:
            for line in infile:
                data.append(line)
        return data
    else:
        for i, line in enumerate(fileinput.input()):
            data.append(line)
    return data

class Audit:
    def __init__(self):
        self.requirements = []

    def print_all(self):
        with open('outfile.csv', 'w') as outfile:
            writer = csv.writer(outfile)
            for r in self.requirements:
                for c in r.concentrates:
                    for s in c.subrequirements:
                        for course in s.courses:
                            record = [r.name, c.name, s.name, course.full_name,
                                      course.term_met, course.grade, course.credits]
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
    def __init__(self, name):
        self.name = name
        self.courses = []

class Course:
    def __init__(self, full_name, term_met, grade, credits):
        self.name = full_name.split(' ')[0]
        self.full_name = full_name
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
                audit.append(requirement)
            # Process new requirement.
            name = line.split(':')[1].strip()
            print("Found a new requirement:", name)
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
        elif line.find('C)') == 6:
            # Add any previous courses in concentrate's previous subrequirement.
            if subrequirement:
                concentrate.subrequirements.append(subrequirement)
            # Process new subrequirement.
            name = line.split(':')[1].strip()
            subrequirement = Subrequirement(name)
        elif line[:10] == ''*10:
            # Process new course.
            course = Course(full_name=line[10:45], term_met=line[46:52],
                            grade=line[55:57], credits=line[65:66])
            subrequirement.courses.append(course)

    # Add final requirement.
    audit.append(requirement)

    # Make outfile.
    audit.print_all()

def main():
    print('Parsing data in csv file...')
    text = read_csv()
    print('Parsing records in data...')
    parse_lines(text)
    print('Outfile created.')

if __name__ == '__main__':
    main()