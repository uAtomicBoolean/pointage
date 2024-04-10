import sys
import errors
from typing import Any, Union, List
from dataclasses import dataclass, field


@dataclass
class Argument:
    # Using list instead of Tuple because a tuple of one element transforms into the element.
    # Ex: ('test') transforms into 'test'.
    names: List[str]
    description: str
    standalone: bool = False

    def dict(self):
        return {
            "names": self.names,
            "description": self.description,
            "standalone": self.standalone,
        }


@dataclass
class ArgumentData(Argument):
    var_name: str = None
    type: "type" = None
    required: bool = True
    default: Any = None


@dataclass
class Command:
    name: str
    description: str
    args: List[ArgumentData] = field(default_factory=list)
    exec_func = None


class TermArgs:
    __commands_list: List[Command] = list()

    @classmethod
    def command(cls, name: str):
        def cmd_func(func):
            # Build the command.
            cmd = Command(name, func.__doc__)
            cmd.exec_func = func

            func_args = func.__annotations__

            # This simplify the defaults management when creating the arguments data.
            defaults = None if not func.__defaults__ else list(func.__defaults__)
            first_defaults = 0
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

                cmd.args.append(arg_data)
                arg_counter += 1

            TermArgs.__commands_list.append(cmd)

            def wrapper(*args, **kargs):
                return func(*args, **kargs)

            return wrapper

        return cmd_func

    def _get_arg(self, command: Command, arg_name: str) -> Union[ArgumentData, None]:
        """Only works on non-positional arguments (ex: -p)."""

        for arg_data in command.args:
            if arg_name.startswith("-") and arg_name in arg_data.names:
                return arg_data

    def _validate_arg(
        self, arg_data: ArgumentData, value: Any, current_arg_name: str
    ) -> Any:
        try:
            return arg_data.type(value)
        except ValueError:
            raise errors.WrongValueForArgument(current_arg_name, value, arg_data.type)

    def execute(self):
        if len(sys.argv) < 2:
            print("Missing command name.")
            return

        # Get the command
        command_name = sys.argv[1]
        command = None
        for cmd in TermArgs.__commands_list:
            if cmd.name == command_name:
                command = cmd

        if not command:
            raise errors.CommandNotFound(command_name)

        input_args = sys.argv[2:]

        required_args = list(filter(lambda a: a.required, command.args))

        # List that will store the interpreted required arguments in the right order.
        # The order is determined by the order of the command.args list.
        inter_req_args = [None] * len(required_args)
        # Same as above but for the optionals arguments and the order doesn't need to be respected.
        inter_opt_args = dict()

        while input_args:
            current_arg = input_args.pop(0)

            # Working on an optional argument.
            if arg_data := self._get_arg(command, current_arg):
                if arg_data.standalone:
                    inter_opt_args[arg_data.var_name] = True
                    continue

                try:
                    arg_value = input_args.pop(0)
                except IndexError:
                    raise errors.MissingValueForArgument(current_arg)

                # Checking if the next value is not an argument.
                if self._get_arg(command, arg_value):
                    raise errors.MissingValueForArgument(current_arg)

                inter_opt_args[arg_data.var_name] = self._validate_arg(
                    arg_data, arg_value, current_arg
                )

            # TODO Gestion des arguments.
            #   Deux types d'arguments : positionels et sans-position (ex: -p).
            #   Il faut changer la gestion des arguments en -
            #   Si l'argument est required, alors il faut l'insérer à la bonne positiond dans la inter_req_list.
            #   Sinon, on le met dans le dictionnaire.
            # Puis on gère les arguments positionel.
            if required_args:
                req_arg = required_args.pop(0)
                print(req_arg)

        #   Quand on tombe sur une chaine de caractères qui n'est pas un argument, alors on regarde si c'est un argument req.
        #   Si ce n'est pas le cas -> raise erreur.
        #   Sinon, on l'interprete, on increment le cpt et on pop.
        #   Puis on l'ajoute dans la liste à la bonne position.

        return command.exec_func(*inter_req_args, **inter_opt_args)
