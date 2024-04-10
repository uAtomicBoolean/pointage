import sys

from classes import Command


class TermArgs:
    __commands_list = list()

    @classmethod
    def command(cls, name: str):
        def cmd_func(func):
            cmd = Command(name, func.__doc__)
            cmd.exec_func = func
            TermArgs.__commands_list.append(cmd)

            def wrapper(*args, **kargs):
                return func(*args, **kargs)

            return wrapper

        return cmd_func

    def execute(self):
        if len(sys.argv) < 2:
            print("Missing command name.")
            return

        command_name = sys.argv[1]
        for cmd in TermArgs.__commands_list:
            if cmd.name == command_name:
                return cmd.exec_func()

        print(f"No command named '{command_name}' !")
