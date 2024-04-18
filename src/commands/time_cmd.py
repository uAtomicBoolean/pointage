import datetime
from lib.colors import *
from lib.odoo_client import OdooClient
from lib.time_functions import get_str_from_timesheet
from argparse import _SubParsersAction, ArgumentParser, Namespace


class TimeCommand:

    def __init__(self, odoo_client: OdooClient, subparsers: _SubParsersAction):
        self.odoo_client = odoo_client

        self.cmd: ArgumentParser = subparsers.add_parser(
            "time", help="Affiche le temps de travail de la journée actuelle."
        )
        self.cmd.set_defaults(execute=self.execute)

    def execute(self, _: Namespace):
        day_time, week_time = self.odoo_client.get_current_time()

        hours, minutes = day_time.split("h")

        # Calculating the remaining time to work for a day of 7 hours.
        day_seconds = 3600 * 7
        worked_seconds = datetime.timedelta(hours=int(hours), minutes=int(minutes)).seconds

        overtime = 0
        if day_seconds < worked_seconds:
            overtime = worked_seconds - day_seconds
            worked_seconds = day_seconds

        delta_seconds = day_seconds - worked_seconds
        delta = datetime.timedelta(seconds=delta_seconds)
        exit_time = datetime.datetime.now() + delta

        str_overtime = ""
        if overtime:
            minutes = overtime // 60
            if minutes < 60:
                str_overtime = f"(+{minutes}m)"
            else:
                str_overtime = f"(+{minutes // 60}h{minutes % 60})"

        print(bold("Journée actuelle :"), day_time)
        print(bold("Semaine actuelle :"), week_time)
        print(bold("Fin de journée à :"), exit_time.strftime("%Hh%M"), str_overtime)