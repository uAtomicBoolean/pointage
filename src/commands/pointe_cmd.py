import datetime
from argparse import _SubParsersAction, ArgumentParser, Namespace
from lib.colors import green
from lib.odoo_client import OdooClient
from lib.time_functions import get_fixed_timestamp, parse_odoo_datetime


class PointeCommand:

    def __init__(self, odoo_client: OdooClient, subparsers: _SubParsersAction):
        self.odoo_client = odoo_client

        self.cmd: ArgumentParser = subparsers.add_parser(
            "pointe", help="Réalise un pointage."
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
        try:
            offset = int(args.offset)
        except ValueError:
            try:
                raw_hour = args.offset.lower().replace("h", ":")
                hour = datetime.datetime.strptime(raw_hour, "%H:%M")
                full_date = datetime.datetime.combine(
                    datetime.date.today(), hour.time()
                )

                # Convert the fulldate to an integer offset.
                time_diff = full_date - datetime.datetime.now()
                offset = int(time_diff.total_seconds() // 60)
            except:
                print("Erreur dans le formatage de l'heure (ex: 12H30, 12h30, 12:30).")
                return

        action, date_pointage = self.odoo_client.add_attendance(offset)
        date_pointage = get_fixed_timestamp(parse_odoo_datetime(date_pointage))
        print(green(f"{action} pointée pour l'heure {date_pointage}."))
