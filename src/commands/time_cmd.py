import datetime
from lib.colors import *
from typing import Tuple
from lib.odoo_client import OdooClient
from lib.time_functions import convert_seconds_to_strtime
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

        exit_time, overtime = self.get_exit_hour(day_time)

        print(bold("Journée actuelle          :"), day_time)
        print(bold("Semaine actuelle          :"), week_time)
        print(
            bold("Fin de journée à          :"),
            exit_time.strftime("%Hh%M"),
            convert_seconds_to_strtime(overtime),
        )
        print(bold("Heures supp de la semaine :"), self.odoo_client.get_week_overtime())

    def get_exit_hour(self, day_time: str) -> Tuple[datetime.datetime, int]:
        """Return the hour at which the user finish is day + the current overtime."""

        hours, minutes = day_time.split("h")

        # Calculating the remaining time to work for a day of 7 hours.
        day_seconds = 3600 * 7
        worked_seconds = datetime.timedelta(
            hours=int(hours), minutes=int(minutes)
        ).seconds

        overtime = 0
        if day_seconds < worked_seconds:
            overtime = worked_seconds - day_seconds
            worked_seconds = day_seconds

        delta_seconds = day_seconds - worked_seconds
        delta = datetime.timedelta(seconds=delta_seconds)
        exit_time = datetime.datetime.now() + delta
        return exit_time, overtime
