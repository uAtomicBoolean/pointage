from ..colors import *
from ..odoo_client import OdooClient
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
        print(bold("Journée actuelle :"), day_time)
        print(bold("Semaine actuelle :"), week_time)
