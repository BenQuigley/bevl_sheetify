import os
from sys import argv

def get_text():
    # Command line mode:
    text = ""
    if len(argv) > 1:
        if os.path.exists(argv[1])
        with open(argv[1]) as infile:
            text = [line for line in infile].join('\n')
    if text == '':
        text = input("Please paste the student's entire Degree Audit (one-column formatted only) here:\n>")

def main():
    text = get_text()

if __name__ == '__main__':
    main()