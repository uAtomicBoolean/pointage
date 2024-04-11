import sys
import errors
from typing import Any, Union, List, Tuple
from command import ArgumentData, Command


# TODO add tab autocompletion support.
# TODO add root command support.
# TODO add subcommand support.
# TODO add help args support (always present and takes priority on all other args).
class TermArgs:
    """Creates and manages the commands used in the script."""

    __root_command: Command = None
    __commands_list: List[Command] = list()

    @classmethod
    def root(cls):
        return TermArgs.command(
            "root_function_protected", "root_function_protected_description"
        )

    @classmethod
    def command(cls, name: str, line_desc: str):
        """Create a command from a function.

        To be used as a decorator to create a command from a function.
        The command's arguments are created from the function's arguments
        that are annotated with the Argument class.
        The command's help text will be generated from the function's docstring
        and the arguments metadata.

        Args:
            name (str): The command's name.
            line_desc (str): The command's single line description.
        """

        def cmd_func(func):
            if not name:
                raise errors.MissingCommandData("unknown", "name")
            if not line_desc:
                raise errors.MissingCommandData(name, "line_description")

            # Build the command.
            cmd = Command(name, line_desc, func.__doc__)
            cmd.exec_func = func

            func_args = func.__annotations__

            # This simplify the defaults management when creating the arguments data.
            defaults = None if not func.__defaults__ else list(func.__defaults__)
            first_defaults = len(func_args) + 1
            if defaults:
                first_defaults = len(func_args) - len(defaults)

            arg_counter = 0
            for var_name, annot in func_args.items():
                arg_data = ArgumentData(
                    **annot.__metadata__[0].dict(),
                    type=annot.__args__[0],
                    var_name=var_name,
                )
                if arg_counter >= first_defaults:
                    arg_data.default = defaults.pop(0)
                    arg_data.required = False
                    arg_data.has_default = True

                cmd.args.append(arg_data)
                arg_counter += 1

            if name == "root_function_protected":
                cmd.is_root_command = True
                TermArgs.__root_command = cmd
            TermArgs.__commands_list.append(cmd)

            def wrapper(*args, **kargs):
                return func(*args, **kargs)

            return wrapper

        return cmd_func

    def _get_arg(self, command: Command, arg_name: str) -> Union[ArgumentData, None]:
        """Returns a non-positional argument

        A positional argument always has a name that begins by at least one '-'.

        Args:
            command (Command): The argument's parent command.
            arg_name (str): The argument's name used in the input.

        Returns:
            Union[ArgumentData, None]: Either the argument's data or None if not found.
        """

        for arg_data in command.args:
            if arg_name.startswith("-") and arg_name in arg_data.names:
                return arg_data

    def _validate_arg(
        self, arg_data: ArgumentData, value: Any, current_arg_name: str
    ) -> Any:
        """Validate a value for a specified argument.

        Casts the value to the correct argument's type and returns it if no errors.

        Args:
            arg_data (ArgumentData): The argument's data.
            value (Any): The value to cast.
            current_arg_name (str): The argument's name in the input to display in case of an error.

        Raises:
            errors.WrongValueForArgument: Raised when the value can't be casted to the argument's type.

        Returns:
            Any: The casted value.
        """

        try:
            return arg_data.type(value)
        except ValueError:
            raise errors.WrongValueForArgument(current_arg_name, value, arg_data.type)

    def _interpret_args(
        self, command: Command, input_args: List[str]
    ) -> Tuple[list, dict]:
        """Interpretes the command arguments.
        Once the interpretation is done, it will returns a list and a dict that contains
        the positional arguments and the non-positional arguments.

        Args:
            command (Command): The command to interpret.
            input_args (List[str]): The list of arguments from the terminal.

        Raises:
            errors.MissingValueForArgument: Raised in case an argument doesn't have its value from the input.

        Returns:
            Tuple[list, dict]: A tuple with both interpreted arguments list and dict.
        """

        required_args = list(filter(lambda a: a.required, command.args))

        # List that will store the interpreted required arguments in the right order.
        # The order is determined by the order of the command.args list.
        pos_args = [None] * len(required_args)
        # Same as above but for the optionals arguments and the order doesn't need to be respected.
        non_pos_args = dict()

        while input_args:
            current_arg = input_args.pop(0)

            # Working on an non-positional arguments.
            if arg := self._get_arg(command, current_arg):
                if arg.is_interpreted:
                    raise errors.ArgumentAlreadyInterpreted(current_arg)

                if arg.standalone:
                    non_pos_args[arg.var_name] = arg.standalone_value
                    continue

                try:
                    arg_value = input_args.pop(0)
                except IndexError:
                    raise errors.MissingValueForArgument(current_arg)

                # Checking if the next value is not an argument.
                if self._get_arg(command, arg_value):
                    raise errors.MissingValueForArgument(current_arg)

                validated_value = self._validate_arg(arg, arg_value, current_arg)
                if arg.has_default:
                    non_pos_args[arg.var_name] = validated_value
                else:
                    # Insert the positional argument at the right position.
                    for ind, req_arg in enumerate(required_args):
                        if arg.names == req_arg.names:
                            pos_args[ind] = validated_value
                            break

                arg.is_interpreted = True
            else:
                # Checking if a value is a positional argument.
                arg_not_found = True
                for ind, req_arg in enumerate(required_args):
                    if not req_arg.is_interpreted:
                        validated_value = self._validate_arg(
                            req_arg, current_arg, req_arg.names[0]
                        )
                        pos_args[ind] = validated_value
                        req_arg.is_interpreted = True
                        arg_not_found = False
                        break

                if arg_not_found:
                    raise errors.UnknownValue(command.name)

        for arg_data in required_args:
            if not arg_data.is_interpreted:
                raise errors.MissingValueForArgument(arg_data.names[0])

        return pos_args, non_pos_args

    def execute(self):
        """Execute the script based on the input from sys.

        Raises:
            errors.CommandNotFound: Raised when a command is not found.
        """

        # TODO Il va falloir changer le fonctionnement du cette fonction
        # pour implémenter la commande root et les subcommands.
        if len(sys.argv) < 2:
            print("Missing command name.")
            return

        # Get the command
        command_name = sys.argv[1]
        command = None
        for cmd in TermArgs.__commands_list:
            if cmd.name == command_name:
                command = cmd

        if TermArgs.__root_command:
            command = TermArgs.__root_command

        if not command:
            raise errors.CommandNotFound(command_name)

        if command.is_root_command:
            input_args = sys.argv[1:]
        else:
            input_args = sys.argv[2:]
        pos_args, non_pos_args = self._interpret_args(command, input_args)

        command.exec_func(*pos_args, **non_pos_args)
