from lib.colors import *
from lib.odoo_client import OdooClient
from lib.time_functions import get_fixed_timestamp, parse_odoo_datetime
from datetime import datetime
from argparse import _SubParsersAction, ArgumentParser, Namespace


class DeleteCommand:

    def __init__(self, odoo_client: OdooClient, subparsers: _SubParsersAction):
        self.odoo_client = odoo_client

        self.cmd: ArgumentParser = subparsers.add_parser(
            "delete", help="Supprime le dernier pointage."
        )
        self.cmd.set_defaults(execute=self.execute)

    def execute(self, _: Namespace):
        last_attendance = self.odoo_client.get_last_x_attendance(1)[0]

        if not last_attendance["check_out"]:
            last_action = "check_in"
            date = get_fixed_timestamp(parse_odoo_datetime(last_attendance["check_in"]))
        else:
            last_action = "check_out"
            date = get_fixed_timestamp(
                parse_odoo_datetime(last_attendance["check_out"])
            )

        choice = input(f"Voulez-vous supprimer le pointage du {date} (O/n) : ") or "n"
        if choice == "O":
            self.odoo_client.delete_last(last_attendance["id"], last_action)
            print(green("Pointage supprimé."))
        else:
            print(red("Suppression annulée."))
