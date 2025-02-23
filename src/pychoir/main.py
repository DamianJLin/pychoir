import pathlib
import sys
from .manage import build_rolls, mark_rolls


def main():
    if len(sys.argv) < 2:
        raise ValueError("Need at least 1 argument")

    command = sys.argv[1]
    args = sys.argv[2:]

    here = pathlib.Path.cwd()

    attfile = here / 'attendance.csv'
    sectionsdir = here / 'sections'
    rollsdir = here / 'rolls'

    if command == 'roll':
        # roll <rehearsal id> <desc> [message]

        # Parse args
        if len(args) < 2:
            print("Error: pychoir roll needs at least 2 arguments")
            exit(1)
        rehid = args[0]
        rehdesc = args[1].replace('_', ' ')
        if len(args) >= 3:
            messagedir = here / args[2]
        else:
            messagedir = here / 'message.txt'
        if not messagedir.is_file():
            print(f"Error: Could not find message. ./{messagedir.name} is not a file.")
            exit(1)

        build_rolls(
            attfile,
            sectionsdir,
            rollsdir,
            rehid,
            rehdesc,
            messagedir,
        )

    if command == 'mark':
        # mark <rehearsal id> <desc>

        # Parse args
        if len(args) < 2:
            print("Error: pychoir mark needs at least 2 arguments")
        rehname = args[0] + '_' + args[1]

        mark_rolls(
            attfile,
            sectionsdir,
            rehname,
        )

    if command in ['help', '-h', '--help']:
        print(
            "List of commands:\n"
            "\tpychoir roll <rehearsal id> <desc> [message]\n"
            "\tpychoir mark <rehearsal id> <desc>"
        )


if __name__ == '__main__':
    main()
