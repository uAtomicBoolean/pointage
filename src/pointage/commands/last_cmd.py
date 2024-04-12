import datetime
from ..utils.colors import *
from ..odoo_client import OdooClient
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
            date = datetime.datetime.strptime(att["name"], "%Y-%m-%d %H:%M:%S")
            att["name"] = date + datetime.timedelta(hours=1)
            action_name = [
                act
                for act, o_act in OdooClient.ATT_ACTIONS.items()
                if o_act == att["action"]
            ][0]
            action_name = (
                green(action_name) if action_name == "entree" else red(action_name)
            )
            print(f"{action_name} à {att['name']}")
