class CommandNotFound(Exception):

    def __init__(self, command_name: str):
        super().__init__(f"no command named '{command_name}'")


class TooFewArguments(Exception):

    def __init__(self):
        super().__init__("Too few arguments passed in the command.")
