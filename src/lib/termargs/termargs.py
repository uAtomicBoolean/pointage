import sys
import errors
from typing import Any, Union, List, Tuple
from dataclasses import dataclass, field


@dataclass
class Argument:
    names: Tuple[str]
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
            for _, annot in func_args.items():
                arg_data = ArgumentData(
                    **annot.__metadata__[0].dict(), type=annot.__args__[0]
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

    def _get_arg(self, arg_name: str) -> Union[ArgumentData, None]:
        return None

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

        req_args = list(filter(lambda a: a.required, command.args))

        # List that will store the interpreted required arguments in the right order.
        # The order is determined by the order of the command.args list.
        inter_req_args = [None] * len(req_args)
        # Same as above but for the optionals arguments and the order doesn't need to be respected.
        inter_opt_args = dict()

        # TODO On itere tant que la liste n'est pas vide (ie boucle while).
        #   Avoir un cpt qui tient compte du nombre des args obligatoires interpretes.
        #   Quand on a fini de traiter un argument, on utilise list.pop()
        #   Quand on tombe sur un argument optionnel, alors on l'interprete :
        #       - si c'est un standalone, alors trkl.
        #       - sinon, il faut aussi récupérer la valeur suivante et on pop deux fois.
        #   Quand on tombe sur une chaine de caractères qui n'est pas un argument, alors on regarde si c'est un argument req.
        #   Si ce n'est pas le cas -> raise erreur.
        #   Sinon, on l'interprete, on increment le cpt et on pop.
        #   Puis on l'ajoute dans la liste à la bonne position.

        # TODO Que veut dire 'interpreter un argument' ?
        #   - On tente de le caster dans le bon type.
        #   - Si erreur alors -> raise erreur.

        return command.exec_func()
