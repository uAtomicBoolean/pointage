import shutil
import zipfile
import argparse
import datetime
import tempfile
import subprocess
import urllib.request
from .odoo_client import OdooClient
from .colors import red, green, bold


class Pointage:
    """Classe principale gérant les commandes du scripts."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="pointage",
            description="Plus besoin d'aller dans Odoo pour gérer notre pointage "
            "grâce à ce script dernière génération utilisant les plus grand "
            "modèles d'intelligence artificielles. "
            "Licence gratuite jusqu'au 31 décembre 2024 puis passage à une licence payante "
            "renouvelable annuellement à un prix de 9 999€ au 1er janvier 2025.",
        )
        self.parser.set_defaults(func=lambda _: self.parser.print_help())
        self.subparsers = self.parser.add_subparsers(help="Liste des commandes.")

        self.build_parser_presence()
        self.build_parser_last()
        self.build_parser_time()
        self.build_parser_update()

        self.odoo_client = OdooClient()

    def build_parser_presence(self):
        """
        Build the parser for both 'entree' and 'sortie' subcommands.
        These commands are separated to ease the use of the script.
        They could be grouped as a parameter of a subcommand but it
        adds a step when writing the command.
        """

        cmd_entree = self.subparsers.add_parser("entree", help="Pointe l'entrée.")
        cmd_sortie = self.subparsers.add_parser("sortie", help="Pointe la sortie.")
        cmd_entree.set_defaults(func=self.pointe_presence, action="entree")
        cmd_sortie.set_defaults(func=self.pointe_presence, action="sortie")
        cmd_entree.add_argument(
            "offset",
            help="Décalage en minutes par rapport à l'heure actuelle.",
            type=int,
            default=0,
            nargs="?",
        )
        cmd_sortie.add_argument(
            "offset",
            help="Décalage en minutes par rapport à l'heure actuelle.",
            type=int,
            default=0,
            nargs="?",
        )

    def build_parser_last(self):
        # Commande last pour afficher les N derniers pointages.
        cmd_last = self.subparsers.add_parser(
            "last", help="Affiche le dernier pointage."
        )
        cmd_last.set_defaults(func=self.last)
        cmd_last.add_argument(
            "limit",
            nargs="?",
            default=1,
            help="Le nombre de lignes à afficher.",
            type=int,
        )
    
    def build_parser_time(self):
        # Commande time pour afficher le temps travaille.
        cmd_time = self.subparsers.add_parser(
            "time", help="Affiche le temps de travail de la journée actuelle."
        )
        cmd_time.set_defaults(func=self.time)
    
    def build_parser_update(self):
        cmd_update = self.subparsers.add_parser(
            "update",
            help="Met à jour le script automatiquement."
        )
        cmd_update.set_defaults(func=self.update)

    # ------------------------------- #
    # Args handlers                   #
    # ------------------------------- #
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
                green(action_name)
                if action_name == "entree"
                else red(action_name)
            )
            print(f"{action_name} à {att['name']}")

    def time(self, _: argparse.Namespace):
        day_time, week_time = self.odoo_client.get_current_time()
        print(bold("Journée actuelle :"), day_time)
        print(bold("Semaine actuelle :"), week_time)

    def update(self, _: argparse.Namespace):
        """Update the script."""

        zip_file_url = "https://github.com/uAtomicBoolean/pointage/archive/refs/heads/main.zip"
        build_script = "/tmp/pointage-main/build_script.sh"

        print("Downloading the script sources...")
        with urllib.request.urlopen(zip_file_url) as response:
            with tempfile.NamedTemporaryFile() as tmp_file:
                shutil.copyfileobj(response, tmp_file)
                with zipfile.ZipFile(tmp_file.name) as zip:
                    zip.extractall("/tmp")

        print("Building the script...")
        subprocess.call(f"chmod u+x {build_script}", shell=True)
        subprocess.call(f"{build_script} /tmp/pointage-main/src", shell=True)
        subprocess.call(f"sudo mv pointage /usr/bin/pointage", shell=True)

        print("Cleaning after update...")
        subprocess.call(f"rm -rf /tmp/pointage-main", shell=True)

        print("Update done !")
