from termargs import TermArgs

commands = TermArgs()


@commands.command("test")
def test():
    """Commande de test."""

    print("Commande de test")


if __name__ == "__main__":
    commands.execute()
