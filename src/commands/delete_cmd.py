from lib.colors import *
from lib.odoo_client import OdooClient
from lib.time_functions import get_fixed_timestamp
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
        print(red("Commande dépréciée."))
        # last_attendance = self.odoo_client.get_last_x_attendance(1)[0]

        # parsed_date = datetime.strptime(last_attendance["name"], "%Y-%m-%d %H:%M:%S")
        # date = get_fixed_timestamp(parsed_date)
        # choice = input(f"Voulez-vous supprimer le pointage du {date} (O/n) : ") or "n"
        # if choice == "O":
        #     self.odoo_client.delete(last_attendance["id"])
        #     print("Pointage supprimé.")
        # else:
        #     print("Suppression annulée.")
