import datetime
from argparse import ArgumentParser, Namespace, _SubParsersAction

from lib import time_functions
from lib.colors import red
from lib.odoo_client import OdooClient


class ResumeCommand:
    def __init__(self, odoo_client: OdooClient, subparsers: _SubParsersAction):
        self.odoo_client = odoo_client

        self.cmd: ArgumentParser = subparsers.add_parser(
            "resume", help="Affiche un résumé de la semaine de travail."
        )
        self.cmd.set_defaults(execute=self.execute)

    def execute(self, _: Namespace):
        first_day = time_functions.get_week_first_day()
        raw_attendances = self.odoo_client.get_week_attendances()
        raw_attendances = sorted(raw_attendances, key=lambda a: a["id"])

        french_days = ["Lun", "Mar", "Mer", "Jeu", "Ven"]
        worked_days = []
        for k in range(5):
            curr_day_data = {
                "name": french_days[k],
                "worked_time": "",
                "s_worked_time": 0,
            }
            current_day = first_day + datetime.timedelta(days=k)
            day_work_time = time_functions.get_work_time(
                [a for a in raw_attendances if a["check_in"].day == current_day.day]
            )
            curr_day_data["s_worked_time"] = day_work_time
            curr_day_data["worked_time"] = (
                time_functions.beautify_work_time(day_work_time)
                if day_work_time
                else ""
            )
            worked_days.append(curr_day_data)

        print("+-------+-------+-------+-------+-------+\n|", end="")
        for day in worked_days:
            print(f"  {day['name']}  |", end="")
        print("\n+-------+-------+-------+-------+-------+\n|", end="")
        for day in worked_days:
            if not day["worked_time"]:
                print("       |", end="")
            elif day["s_worked_time"] > 25200:
                print(f" {day['worked_time']} |", end="")
            else:
                print(f" {red(day['worked_time'])} |", end="")
        print("\n+-------+-------+-------+-------+-------+")
