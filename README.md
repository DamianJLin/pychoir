A python package to track chorister attendance.

# Installation
1. Download and store somewhere.
2. `pip install -e <path_to_package>`
3. Add to path
4. Done!

# Usage tips and development
`pychoir --help` is your best friend.

Certain features are missing, for exmaple:
- swapping an existing chorister's part,
- exporting attendance above a certain threshold (e.g. to see who is eligible to perform at a concert)
- undo for fixing mistakes made in interactive roll entry
- detecting duplicates

More than happy to accept contributions to the project, especially for the above features.

To achieve these things, once can manualy open the .csv files. It would be wise to make sure `pychoir` isn't running when you do this, and also that you don't save the files in a weird format.
