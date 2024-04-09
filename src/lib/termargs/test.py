from termargs import CommandsManager, ArgumentData


class Pointage(CommandsManager):

    def __init__(self):
        super().__init__("pointage")
    
    @CommandsManager.command(
        ('test', 't'),
        'A simple command to test the project.',
        meta_params=(
            ArgumentData(('-n', '--number'), 'A number to display.'),
            ArgumentData(('-n', '--number'), 'A number to display.'),
        )
    )
    def do_test(self, number: int, test: str = "Test", listing: list = [0]):
        print("Test command")
        print(f"Number : {number}")


if __name__ == "__main__":
    pointage = Pointage()
