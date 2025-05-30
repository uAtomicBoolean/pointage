from argparse import ArgumentParser, Namespace, _SubParsersAction

from lib.colors import green
from lib.odoo_client import OdooClient
from lib.time_functions import (
    convert_offset_to_odoo_datetime,
    get_fixed_timestamp,
    parse_odoo_datetime,
)


class PointeCommand:
    def __init__(self, odoo_client: OdooClient, subparsers: _SubParsersAction):
        self.odoo_client = odoo_client

        self.cmd: ArgumentParser = subparsers.add_parser(
            "pointe", help="Réalise un pointage.", aliases=["entree", "sortie"]
        )
        self.cmd.set_defaults(execute=self.execute)
        self.cmd.add_argument(
            "offset",
            help="Soit un offset, soit une heure (ex: 12h30, 12H30, 12:30)",
            type=str,
            default="0",
            nargs="?",
        )

    def execute(self, args: Namespace):
        # Check the offset and convert it to minutes if necessary.
        attendance_time = convert_offset_to_odoo_datetime(args.offset)

        action, date_pointage = self.odoo_client.add_attendance(attendance_time)
        date_pointage = get_fixed_timestamp(parse_odoo_datetime(date_pointage))
        print(green(f"{action} pointée pour l'heure {date_pointage}."))
