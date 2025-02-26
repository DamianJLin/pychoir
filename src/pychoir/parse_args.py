import pathlib


class RollConfig():
    def __init__(self, rehid, rehdesc, messagedir):
        self.rehid = rehid
        self.rehdesc = rehdesc
        self.messagedir = messagedir


class MarkConfig():
    def __init__(self, rehname):
        self.rehname = rehname


def parse_args(args):
    """pychoir

    Key: <required_arg>, [optional_arg]

    ##### Commands
      roll <rehearsal_id> <desc> [message]  : Create roll files for all parts. [message] is a path
                                              to a file containing a text message. Will prompt for
                                              a message if this argument is missing.
      mark <rehearsal_id> <desc>            : Record attendance in system.
      help                                  : You're already here! Prints this help string.
    """
    here = pathlib.Path.cwd()

    if len(args) < 2:
        print("pychoir needs at least 1 argument")
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
            print("mark needs at least 2 arguments")
            exit()
        rehname = args[0] + '_' + args[1]

        return MarkConfig(rehname)

    elif command in ('help', '-h', '--help'):
        print(parse_args.__doc__)
        exit()

    else:
        print(f"{command} is not a command. Try 'pychoir help'.")
