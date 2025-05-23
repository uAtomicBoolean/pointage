import datetime
from argparse import ArgumentParser, Namespace, _SubParsersAction

from lib.colors import green, red
from lib.odoo_client import OdooClient
from lib.time_functions import get_fixed_timestamp, parse_odoo_datetime


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

        txt_entree = green("Entrée")
        txt_sortie = red("Sortie")

        for att in last_atts:
            if att["check_out"]:
                check_out = get_fixed_timestamp(parse_odoo_datetime(att["check_out"]))
                print(f"{txt_sortie} à {self.beautify_date(check_out)}")

            if att["check_in"]:
                check_in = get_fixed_timestamp(parse_odoo_datetime(att["check_in"]))
                print(f"{txt_entree} à {self.beautify_date(check_in)}")

    def beautify_date(self, date: datetime.datetime):
        return date.strftime("%H:%M:%S le %d/%m/%Y")
