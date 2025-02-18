import datetime

from lib import time_functions
from lib.colors import *
from lib.odoo_client import OdooClient
from argparse import _SubParsersAction, ArgumentParser, Namespace


class TimeCommand:
    def __init__(self, odoo_client: OdooClient, subparsers: _SubParsersAction):
        self.odoo_client = odoo_client

        self.cmd: ArgumentParser = subparsers.add_parser(
            "time", help="Affiche le temps de travail de la journée actuelle."
        )
        self.cmd.set_defaults(execute=self.execute)

    def execute(self, _: Namespace):
        week_attendances = self.odoo_client.get_week_attendances()

        if not week_attendances:
            return print(red("Pas de pointages pour la semaine."))

        curr_day = datetime.date.today().day
        week_work_time = time_functions.get_work_time(week_attendances)
        day_work_time = time_functions.get_work_time(
            [a for a in week_attendances if a["check_in"].day == curr_day]
        )

        exit_hour_d, overtime_d = self.get_exit_hour(day_work_time)
        exit_hour_w, overtime_w = self.get_exit_hour(week_work_time, True)

        exit_hour_d = exit_hour_d if not overtime_d else f"{exit_hour_d} {overtime_d}"
        exit_hour_w = exit_hour_w if not overtime_w else f"{exit_hour_w} {overtime_w}"

        print(
            bold("Journée actuelle :"),
            self.beautify_work_time(day_work_time),
            faint(f"(sortie : {exit_hour_d})"),
        )
        print(
            bold("Semaine actuelle :"),
            self.beautify_work_time(week_work_time),
            faint(f"(sortie : {exit_hour_w})"),
        )

    def get_exit_hour(self, work_time: int, week: bool = False) -> str:
        curr_day = datetime.date.today().weekday()

        if week:
            work_time = work_time - (3600 * 7 * curr_day)

        base_seconds = 25200
        overtime = 0
        if base_seconds < work_time:
            overtime = work_time - base_seconds
            work_time = base_seconds

        remaining_time = datetime.timedelta(seconds=(3600 * 7) - work_time)
        exit_time = datetime.datetime.now() + remaining_time

        return exit_time.strftime("%Hh%M"), time_functions.convert_seconds_to_strtime(
            overtime
        )
