import datetime
from lib.colors import *
from lib.odoo_client import OdooClient
from lib.time_functions import get_fixed_timestamp
from argparse import _SubParsersAction, ArgumentParser, Namespace


class LastCommand:

    def __init__(self, odoo_client: OdooClient, subparsers: _SubParsersAction):
        self.odoo_client = odoo_client

        self.cmd: ArgumentParser = subparsers.add_parser(
            "last", help="Affiche les pointages du jour ou n pointages."
        )
        self.cmd.add_argument(
            "limit",
            nargs="?",
            default=False,
            help="Le nombre de pointages à afficher.",
            type=int,
        )
        self.cmd.set_defaults(execute=self.execute)

    def execute(self, args: Namespace):
        if not args.limit:
            last_atts = self.odoo_client.get_day_attendance(datetime.date.today())
        else:
            last_atts = self.odoo_client.get_last_x_attendance(args.limit)

        for att in last_atts:
            parsed_date = datetime.datetime.strptime(att["name"], "%Y-%m-%d %H:%M:%S")
            att["name"] = get_fixed_timestamp(parsed_date)
            action_name = [
                act
                for act, o_act in OdooClient.ATT_ACTIONS.items()
                if o_act == att["action"]
            ][0]
            action_name = (
                green(action_name) if action_name == "entree" else red(action_name)
            )
            print(f"{action_name} à {att['name']}")
