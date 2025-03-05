import pathlib
import readchar


class RollConfig():
    def __init__(self, rehid, rehdesc, messagedir):
        self.rehid = rehid
        self.rehdesc = rehdesc
        self.messagedir = messagedir


class MarkConfig():
    def __init__(self, rehname):
        self.rehname = rehname


class AddConfig():
    def __init__(self, chfname, chlname, chpart):
        self.chfname = chfname
        self.chlname = chlname
        self.chpart = chpart


def parse_args(args):
    """pychoir

    Key: <required_arg>, [optional_arg]

    ##### Commands
      roll <rehearsal_id> <desc> [message]  : Create roll files for all parts. [message] is a path
                                              to a file containing a text message. Will prompt for
                                              a message if this argument is missing.
      mark <rehearsal_id> <desc>            : Record attendance in system.
      help                                  : You're already here! Prints this help string.
      add <fname> <lname> <SATB>            : Add a chorister to the attendance list.
    """
    here = pathlib.Path.cwd()

    if len(args) < 2:
        print("pychoir needs at least 1 argument.")
        exit()

    command = args[1]
    comm_args = args[2:]

    if command == 'roll':
        if len(comm_args) < 2:
            print("roll needs at least 2 arguments.")
            exit()
        rehid = comm_args[0]
        rehdesc = comm_args[1].replace('_', ' ')
        if len(comm_args) == 3:
            messagedir = here / comm_args[2]
            if not messagedir.is_file():
                print(f"Could not parse message, no text file at ./{messagedir.name}.")
                exit()
        else:
            messagedir = None  # This indicates the need to prompt.

        return RollConfig(rehid, rehdesc, messagedir)

    elif command == 'mark':
        if len(comm_args) < 2:
            print("mark needs at least 2 arguments.")
            exit()
        rehname = comm_args[0] + '_' + comm_args[1]

        return MarkConfig(rehname)

    elif command == 'add':
        if len(comm_args) != 3:
            print("add needs exactly 3 arguments.")
            exit()
        fname, lname, part = comm_args
        part = part.lower()

        if part not in ('soprano', 'alto', 'tenor', 'bass'):
            print(
                "Warning: argument SATB not one of 'soprano', 'alto', 'tenor', or 'bass'. Please"
                " confirm [y/N]: ",
                end=''
            )
            if readchar.readkey() not in ('y', 'Y'):
                exit()

        return AddConfig(fname, lname, part)

    elif command in ('help', '-h', '--help'):
        print(parse_args.__doc__)
        exit()

    else:
        print(f"{command} is not a command. Try 'pychoir help'.")
