from typing import Annotated
from termargs import TermArgs, Argument

commands = TermArgs()


@commands.command("test")
def test(
    number: Annotated[
        int,
        Argument(["number"], "A number to display."),
    ],
    again: Annotated[int, Argument(["again"], "again")],
    name: Annotated[int, Argument(["-n"], "Set the name.")],
    enable: Annotated[str, Argument(["-e"], "Enable the thing.", True)] = False,
):
    """Commande de test."""

    print(f"number : {number}")
    print(f"again : {again}")
    print(f"name : {name}")
    print(f"enable : {enable}")


if __name__ == "__main__":
    try:
        commands.execute()
    except Exception as err:
        print(f"Error : {err}")
