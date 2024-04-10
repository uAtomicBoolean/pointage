from typing import Annotated
from termargs import TermArgs, Argument

commands = TermArgs()


@commands.command("test")
def test(
    number: Annotated[
        int,
        Argument(("number"), "A number to display."),
    ],
    again: Annotated[int, Argument(("again"), "again")],
    name: Annotated[str, Argument(("-n"), "Set the name.")] = None,
    enable: Annotated[str, Argument(("-e"), "Enable the thing.", True)] = False,
):
    """Commande de test."""

    print("Commande de test")


if __name__ == "__main__":
    try:
        commands.execute()
    except Exception as err:
        print(f"Error : {err}")
