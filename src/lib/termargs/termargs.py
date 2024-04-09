"""
Library to interact with the terminal.
The class command manager is used to create a command manager (lol).
It comes with a function that will load all the command at initialisation.
A decorator can be used to add some metadata on some commands (such as an alternative name, the help, the parameter description, etc).
The commands' parameters are determined from the functions typings.
It could be useful to create a Command metaclass that would store all the data of the commands.

Each command's function needs to start with the 'do_' prefix

The CommandManager class needs to be inherited to work.

TODO :
- Load the commands from the functions (basic -> name and exec function).
- Manage the arguments for the commands.
- Add decorators to manage the commands data.
"""

from typing import Any, Union
from dataclasses import dataclass, field


@dataclass
class ArgumentData:
    names: Union[str]
    description: str
    required: bool = False
    default: Any = None
    arg_type: type = None


@dataclass
class CommandData:
    names: Union[str]
    description: str
    func_name: str

    arguments: Union[ArgumentData] = field(default_factory=list)

    def help(self):
        return f"{self.names.join(',')}\n{self.description}"


class CommandsManager:

    __commands_list: Union[CommandData] = list()
    
    def __init__(self, name: str, description: str = None):
        """Initialisation function of the class.

        Args:
            name (str): The program's name.
            description (str): The program description.
        """

        self.name = name
        self.description = description

        self._commands = list()
        self.load_commands()
    
    def load_commands(self):
        self._commands = CommandsManager.__commands_list
        CommandsManager.__commands_list = list()
    
    @classmethod
    def command(cls, names: Union[str], description: str, meta_params: Union[ArgumentData] = None):
        """Creates a command from a function.

        Args:
            names (list[str]): A list of the command's names.
            description (str): The command's description.
            meta_params (tuple[ArgumentData]): A tuple with the metadata for all the command's parameters.
        """
        
        def cmd_function(func: 'function'):
            command_data = CommandData(names, description, func.__name__)
            CommandsManager.__commands_list.append(command_data)

            # Allow us to know when we are switching to optional parameters
            # as optional parameters are always last in a python function.
            first_non_req = len(func.__annotations__) - len(func.__defaults__)
            arg_count = 0
            for name, arg_type in func.__annotations__.items():
                pass

            # TODO gérer les paramètres avec les ArgumentData.
            #   Il faut donc créer les arguments data si il en manque.
            #   Il faut aussi trouver comment relier efficacement les ArgumentData avec les arguments.

            def wrapper(*args, **kargs):
                return func(*args, **kargs)
            return wrapper        

        return cmd_function
