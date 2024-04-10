from typing import Any


class CommandNotFound(Exception):

    def __init__(self, command_name: str):
        super().__init__(f"no command named '{command_name}'")


class TooFewArguments(Exception):

    def __init__(self):
        super().__init__("Too few arguments passed in the command.")


class MissingValueForArgument(Exception):

    def __init__(self, arg_name: str):
        super().__init__(f"Missing value for argument '{arg_name}'.")


class WrongValueForArgument(Exception):

    def __init__(self, arg_name: str, value: Any, req_type):
        cleaned_type = str(req_type).split("'")[1]
        message = (
            f"Wrong value '{value}' for argument '{arg_name}'."
            + f"\n\tRequired type : {cleaned_type}"
        )
        super().__init__(message)
