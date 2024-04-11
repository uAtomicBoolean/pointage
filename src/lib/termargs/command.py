from typing import Any, List
from dataclasses import dataclass, field


@dataclass
class Argument:
    """Basic Argument class used to declare the arguments in a command.

    An argument can be a standalone : script cmd -s
    In that case, the argument doesn't take any values in the command line
    and will use the 'standalone_value' attribute which is 'True' by default.
    """

    # Using list instead of Tuple because a tuple of one element transforms into the element.
    # Ex: ('test') transforms into 'test'.
    names: List[str]
    description: str
    standalone: bool = False
    standalone_value: Any = True

    def dict(self):
        return {
            "names": self.names,
            "description": self.description,
            "standalone": self.standalone,
            "standalone_value": self.standalone_value,
        }


@dataclass
class ArgumentData(Argument):
    """A more complete Argument class used internally by TermArgs
    An user shouldn't use it.
    """

    var_name: str = None
    type: "type" = None
    required: bool = True
    default: Any = None
    has_default: bool = False
    is_interpreted: bool = False


@dataclass
class Command:
    """Holds a command's data."""

    name: str
    line_description: str
    full_description: str
    args: List[ArgumentData] = field(default_factory=list)
    exec_func = None
    is_root_command: bool = False

    def build_example(self) -> str:
        return "example command."
