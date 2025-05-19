from argparse import ArgumentParser, Namespace, _SubParsersAction

from lib.colors import green, red
from lib.odoo_client import OdooClient
from lib.time_functions import (
    convert_offset_to_odoo_datetime,
    get_fixed_timestamp,
    parse_odoo_datetime,
)


class FixCommand:
    def __init__(self, odoo_client: OdooClient, subparsers: _SubParsersAction):
        self.odoo_client = odoo_client

        self.cmd: ArgumentParser = subparsers.add_parser(
            "fix", help="Modifie le dernier pointage."
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
        attendance_time = convert_offset_to_odoo_datetime(args.offset)
        last_attendance = self.odoo_client.get_last_x_attendance(1)[0]
        last_action = "check_in" if not last_attendance["check_out"] else "check_out"

        fixed_att_time = get_fixed_timestamp(parse_odoo_datetime(attendance_time))
        fixed_att_time = fixed_att_time.strftime("%H:%M:%S")

        choice = (
            input(
                f"Voulez-vous modifier le dernier pointage avec cette heure {fixed_att_time} (O/n) : "
            )
            or "n"
        )
        if choice == "O":
            self.odoo_client.update_last(
                last_attendance["id"], last_action, attendance_time
            )
            print(green("Pointage modifié."))
        else:
            print(red("Modification annulée."))
