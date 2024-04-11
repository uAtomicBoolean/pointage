from typing import Annotated
from termargs import TermArgs
from command import Argument


commands = TermArgs()


@commands.root()
def root(name: Annotated[str, Argument(["name"], "Your name")]):
    print(f"Hello {name} !")


@commands.command("test", "A simple command to test termargs.")
def test(
    number: Annotated[
        int,
        Argument(["number"], "A number to display."),
    ],
    name: Annotated[str, Argument(["-n", "--name"], "Set the name.")],
    surname: Annotated[str, Argument(["surname"], "Your surname.")],
    enable: Annotated[
        str,
        Argument(["-e"], "Enable the thing.", standalone=True, standalone_value=True),
    ] = False,
):
    """
    Commande de test.
    Cette commande va réaliser plusieurs actions en fonction d'autres choses.
    On peut mettre toutes les indications que l'on veut dans cette doc pour qu'elles soient affichées avec la commande help.
    """

    print(f"number : {number}")
    print(f"name : {name}")
    print(f"surname : {surname}")
    print(f"enable : {enable}")


if __name__ == "__main__":
    commands.execute()
