import argparse
import datetime
from .odoo_client import OdooClient


class Pointage:
    """Classe principale gérant les commandes du scripts."""

    def __init__(self):
        self.parser = self.build_args_parser()
        self.odoo_client = OdooClient()

    def build_args_parser(self):
        parser = argparse.ArgumentParser(
            prog="pointage",
            description="Plus besoin d'aller dans Odoo pour gérer notre pointage "
            "grâce à ce script dernière génération utilisant les plus grand "
            "modèles d'intelligences artificielles. "
            "Licence gratuite jusqu'en 2025 puis passage à une licence payante "
            "renouvelable annuellement à un prix de 9 999€.",
        )
        parser.set_defaults(func=lambda _: parser.print_help())

        subparsers = parser.add_subparsers(help="Liste des commandes.")

        # Ajoute le parser pour la commande de pointage propre.
        cmd_pointe = subparsers.add_parser(
            "pointe", help="Permet de pointer une présence."
        )
        cmd_pointe.set_defaults(func=self.pointe_presence)
        cmd_pointe.add_argument(
            "action",
            choices=["entree", "sortie"],
            type=str,
            help="L'action du pointage.",
        )
        cmd_pointe.add_argument(
            "-o",
            "--offset",
            help="Décalage en minutes par rapport à l'heure actuelle.",
            type=int,
            required=False,
            default=0,
        )

        cmd_last = subparsers.add_parser("last", help="Affiche le dernier pointage.")
        cmd_last.set_defaults(func=self.last)
        cmd_last.add_argument(
            "limit",
            nargs="?",
            default=1,
            help="Le nombre de lignes à afficher.",
            type=int,
        )

        cmd_time = subparsers.add_parser(
            "time", help="Affiche le temps de travail de la journée actuelle."
        )
        cmd_time.set_defaults(func=self.time)
        cmd_time.add_argument(
            "-w",
            "--week",
            help="Indique le temps travaillé sur la semaine.",
            action="store_const",
            const=True,
        )

        return parser

    def parse(self) -> argparse.Namespace:
        """Wrapper pour le parsing des arguments du script."""

        return self.parser.parse_args()

    def pointe_presence(self, args: argparse.Namespace):
        attendance_id, date_pointage = self.odoo_client.add_attendance(
            args.action, args.offset
        )
        if attendance_id == -1:
            print(f"Erreur lors de la création du pointage (action: {args.action}).")
            print(
                "Vérifiez si vous n'avez pas déjà créé un pointage avec cette action."
            )
        else:
            print(f"Pointage créé (id: {attendance_id}) pour l'heure {date_pointage}")

    def last(self, args: argparse.Namespace):
        last_atts = self.odoo_client.get_last_x_attendance(args.limit)

        for att in last_atts:
            date = datetime.datetime.strptime(att["name"], "%Y-%m-%d %H:%M:%S")
            att["name"] = date + datetime.timedelta(hours=1)
            action_name = [
                act
                for act, o_act in OdooClient.ATT_ACTIONS.items()
                if o_act == att["action"]
            ][0]
            action_name = (
                f"\033[92m{action_name}"
                if action_name == "entree"
                else f"\033[91m{action_name}"
            )
            print(f"{action_name}\033[0m à {att['name']}")

    def time(self, args: argparse.Namespace):
        current_time = self.odoo_client.get_current_time(args.week)
        print(f"Journée actuelle : {current_time}")
