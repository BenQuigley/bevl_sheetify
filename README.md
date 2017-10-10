BEVL Sheetify
=============
A Python script that parses the output of Colleague's Degree Audit, formatting
it as a spreadsheet.

User Notes
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
and "bevl_sheetify" should appear as an option. Clicking it will result in a "sheetified"
version of the file appearing on the user's desktop.