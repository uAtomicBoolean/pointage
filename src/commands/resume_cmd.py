from lib.colors import *
from lib.odoo_client import OdooClient
from argparse import _SubParsersAction, ArgumentParser, Namespace


class ResumeCommand:
    def __init__(self, odoo_client: OdooClient, subparsers: _SubParsersAction):
        self.odoo_client = odoo_client

        self.days = []

        self.cmd: ArgumentParser = subparsers.add_parser(
            "resume", help="Affiche un résumé de la semaine de travail."
        )
        self.cmd.set_defaults(execute=self.execute)

    def execute(self, args: Namespace):
        print("resume")
