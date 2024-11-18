import datetime
from lib.odoo_client import OdooClient
from argparse import _SubParsersAction, ArgumentParser, Namespace


class PresenceCommand:

    def __init__(self, odoo_client: OdooClient, subparsers: _SubParsersAction):
        self.odoo_client = odoo_client

        self.cmd_entree: ArgumentParser = subparsers.add_parser(
            "entree", help="Pointe l'entrée."
        )
        self.cmd_sortie: ArgumentParser = subparsers.add_parser(
            "sortie", help="Pointe la sortie."
        )
        self.cmd_entree.set_defaults(execute=self.execute, action="entree")
        self.cmd_sortie.set_defaults(execute=self.execute, action="sortie")

        offset_params = {
            "help": "Soit un offset, soit une heure (ex: 12h30, 12H30, 12:30)",
            "type": str,
            "default": "0",
            "nargs": "?",
        }
        self.cmd_entree.add_argument("offset", **offset_params)
        self.cmd_sortie.add_argument("offset", **offset_params)

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

        attendance_id, date_pointage = self.odoo_client.add_attendance(
            args.action, offset
        )
        if attendance_id == -1:
            print(f"Erreur lors de la création du pointage (action: {args.action}).")
            print(
                "Vérifiez si vous n'avez pas déjà créé un pointage avec cette action."
            )
        else:
            print(f"Pointage créé (id: {attendance_id}) pour l'heure {date_pointage}")
