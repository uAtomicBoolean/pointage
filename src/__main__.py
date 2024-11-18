import argparse
from lib.odoo_client import OdooClient
from commands import *


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
    subparsers = parser.add_subparsers(help="Liste des commandes.")

    odoo_client = OdooClient()

    TimeCommand(odoo_client, subparsers)
    LastCommand(odoo_client, subparsers)
    UpdateCommand(odoo_client, subparsers)
    DeleteCommand(odoo_client, subparsers)
    PresenceCommand(odoo_client, subparsers)

    args = parser.parse_args()
    args.execute(args)


if __name__ == "__main__":
    main()
