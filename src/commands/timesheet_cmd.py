from argparse import _SubParsersAction, ArgumentParser, Namespace, FileType

from lib.colors import *
from lib.odoo_client import OdooClient
from lib.time_functions import *


class TimesheetCommand:
    def __init__(self, odoo_client: OdooClient, subparsers: _SubParsersAction):
        self.odoo_client = odoo_client

        self.cmd: ArgumentParser = subparsers.add_parser(
            "timesheet", help="Créer des feuilles de temps à partir d'un fichier csv."
        )
        self.cmd.set_defaults(execute=self.execute)
        self.cmd.add_argument(
            "timesheets_file",
            help="Le fichier CSV, correctement formaté, contenant les feuilles de temps.",
            type=FileType(),
        )

    def execute(self, args: Namespace):
        csv_file = args.timesheets_file
        if not csv_file.name.endswith(".csv"):
            print(red("Le fichier des feuilles de temps doit être un fichier CSV."))
            exit(1)

        lines = []
        for line in csv_file.readlines()[1:]:
            lines.append(TimesheetLine.parse(line.strip()))


class TimesheetLine:
    def __init__(
        self,
        sp_id: str,
        date: datetime.date,
        description: str,
        worked_time: float,
        project_id: int,
        task_id: int,
    ):
        self.sp_id = sp_id
        self.date = date
        self.description = description
        self.worked_time = worked_time
        self.project_id = project_id
        self.task_id = task_id

    @classmethod
    def parse(cls, line: str):
        fields = line.split(";")
        return TimesheetLine(
            fields[0],
            datetime.strptime(fields[1], "%Y-%m-%d").date(),
            fields[2],
            float(fields[3]),
            int(fields[4]),
            int(fields[5]),
        )
