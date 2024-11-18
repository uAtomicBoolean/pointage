from datetime import date, datetime, timedelta
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

        if not day_time or not week_time:
            print(f"{bold('Journée actuelle :')} 0h")
            print(f"{bold('Semaine actuelle :')} 0h")
            return

        exit_time_d, overtime_d = self.get_exit_hour(day_time)
        exit_time_w, overtime_w = self.get_exit_hour(week_time, week=True)

        exit_time_d = exit_time_d if not overtime_d else f"{exit_time_d} {overtime_d}"
        exit_time_w = exit_time_w if not overtime_w else f"{exit_time_w} {overtime_w}"

        print(
            f"{bold('Journée actuelle :')} {day_time} {faint(f'(sortie : {exit_time_d})')}"
        )
        print(
            f"{bold('Semaine actuelle :')} {week_time} {faint(f'(sortie : {exit_time_w})')}"
        )

    def get_exit_hour(self, worked_time: str, week: bool = False) -> Tuple[str, int]:
        """Return the hour at which the user finish + the current overtime."""

        if not week:
            hours, minutes = worked_time.split("h")
        else:
            hours, minutes = worked_time.split("h")
            hours = int(hours) % 7

        base_seconds = 25200
        worked_seconds = int(hours) * 3600 + int(minutes) * 60

        overtime = 0
        if base_seconds < worked_seconds:
            overtime = worked_seconds - base_seconds
            worked_seconds = base_seconds

        delta_seconds = base_seconds - worked_seconds
        delta = timedelta(seconds=delta_seconds)
        exit_time = datetime.now() + delta

        return exit_time.strftime("%Hh%M"), convert_seconds_to_strtime(overtime)
