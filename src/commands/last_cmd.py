import datetime
from lib.colors import *
from lib.odoo_client import OdooClient
from lib.time_functions import get_fixed_timestamp
from argparse import _SubParsersAction, ArgumentParser, Namespace


class LastCommand:

    def __init__(self, odoo_client: OdooClient, subparsers: _SubParsersAction):
        self.odoo_client = odoo_client

        self.cmd: ArgumentParser = subparsers.add_parser(
            "last", help="Affiche le dernier pointage."
        )
        self.cmd.add_argument(
            "limit",
            nargs="?",
            default=1,
            help="Le nombre de lignes à afficher.",
            type=int,
        )
        self.cmd.set_defaults(execute=self.execute)

    def execute(self, args: Namespace):
        last_atts = self.odoo_client.get_last_x_attendance(args.limit)

        for att in last_atts:
            att["name"] = get_fixed_timestamp(att["name"])
            action_name = [
                act
                for act, o_act in OdooClient.ATT_ACTIONS.items()
                if o_act == att["action"]
            ][0]
            action_name = (
                green(action_name) if action_name == "entree" else red(action_name)
            )
            print(f"{action_name} à {att['name']}")
