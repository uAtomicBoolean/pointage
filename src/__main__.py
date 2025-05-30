import argparse

from commands import (
    FixCommand,
    LastCommand,
    PointeCommand,
    ResumeCommand,
    TimeCommand,
    UpdateCommand,
)
from lib.odoo_client import OdooClient

VERSION = "v1.2.0"


def main():
    parser = argparse.ArgumentParser(
        prog="pointage",
        description="Plus besoin d'aller dans Odoo pour gérer votre pointage "
        "grâce à ce script dernière génération utilisant les plus grand "
        "modèles d'intelligence artificielles. "
        "Licence gratuite jusqu'au 31 décembre 2024 puis passage à une licence payante "
        "renouvelable annuellement à un prix de 9 999€ au 1er janvier 2025.",
    )
    parser.set_defaults(execute=lambda _: parser.print_help())
    parser.add_argument(
        "--version", help="Affiche la version du script.", action="store_true"
    )

    subparsers = parser.add_subparsers(help="Liste des commandes.")

    odoo_client = OdooClient()

    FixCommand(odoo_client, subparsers)
    LastCommand(odoo_client, subparsers)
    PointeCommand(odoo_client, subparsers)
    ResumeCommand(odoo_client, subparsers)
    TimeCommand(odoo_client, subparsers)
    UpdateCommand(odoo_client, subparsers, VERSION)

    args = parser.parse_args()

    if args.version:
        return print(f"pointage {VERSION}")

    args.execute(args)


if __name__ == "__main__":
    main()
