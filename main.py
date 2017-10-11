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
MAIN PROGRAM CODE
=================
"""

import os
import re
import csv
import sys
from collections import OrderedDict as o_dict

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

def find_status(string):
    statuses = ['C', 'I', 'N']
    indeces = []
    for s in statuses:
        index = string.find('{})'.format(s))
        if index >= 0:
            indeces.append(index)
    if indeces:
        return min(indeces)
    else:
        return -1

def parse_lines(outfile_name, data):

    # Initialize a blank record.
    headers = ['Requirement', 'Concentrate', 'Note', 'Subrequirement', 'Course Code', 'Course Name',
               'Term Met', 'Grade', 'Credits', 'Status']
    course_specific_vals = headers[4:]
    record = o_dict([(val, '') for val in headers])
    last_vals_written = {val: '' for val in headers}
    with open(outfile_name, 'w') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(headers)
        for line in data:

            # Clear course-specific values:
            for course_specific_val in course_specific_vals:
                record[course_specific_val] = ''

            # Identify any new requirements:
            if find_status(line) == 0:

                # Process new requirement.
                # Clear previous concentrate, concentrate note, and subrequirement values.
                # Write nothing to outfile.

                record['Requirement'] = line.split(':')[1].strip()
                for val in ['Concentrate', 'Note', 'Subrequirement']:
                    record[val] = ''

            elif find_status(line) == 3:

                # Process new concentrate.
                # Clear previous concentrate note and subrequirement values.
                # Write nothing to outfile.

                name = line.split(':')[1].strip()
                record['Concentrate'] = name
                for val in ['Note', 'Subrequirement']:
                    record[val] = ''

            elif line.find('>') == 6:

                # Process new line of concentrate note.
                # Clear no values.
                # Write nothing to outfile.

                record['Note'] = (record['Note'] + line.split('>')[1]).strip()

            elif find_status(line) == 6:

                # Process new subrequirement.
                # Clear no values.
                # Write nothing to outfile.
                # Todo: make sure these get written in the event there are no courses listed.

                record['Subrequirement'] = line.split(')')[1].strip()

            elif line[:10] == ' '*10 and line[10] != ' ':

                # Process new course.

                full_name  = line[10:45]

                record['Course Code'] = full_name.split(' ')[0]
                course_name = ' '.join(full_name.split(' ')[1:])
                record['Course Name'] = re.sub(r'[\.]{4,}', '...', course_name)  # Replace too-long ellipses with normal ones.
                record['Term Met'] = line[46:52]
                record['Grade'] = line[55:57]
                record['Credits'] = line[65:66]
                record['Status'] = line[65:].split('*')[1].strip() if '*' in line[65:] else ''

                # Handle the special requirement lines:
                if record['Course Code'][:8] == '_' * 8:
                    for course_specific_val in course_specific_vals:
                        record[course_specific_val] = ''
                    record['Course Code'] = 'Outstanding requirement:'
                    record['Course Name'] = ' '.join(line[10:].split(' ')[1:]).strip()

                record_to_write = []
                for key, value in record.items():
                    skippable = headers[:4]
                    if EMPTY_CELLS_ALLOWED and key in skippable and value == last_vals_written[key]:
                        record_to_write.append('')
                    else:
                        last_vals_written[key] = value
                        record_to_write.append(value)

                writer.writerow(record_to_write)


def main():
    infile_name = sys.argv[1]
    outfile_name = make_outfile_name(infile_name)

    print('parsing data in csv file...')
    text = read_csv(infile_name)

    print('parsing records in data...')
    parse_lines(outfile_name, text)

    print('csv outfile created ({})'.format(outfile_name))

    if input('Open? [Y/n]\n>').strip().lower() != 'n':
        os.system('open "{}"'.format(outfile_name))

if __name__ == '__main__':
    main()