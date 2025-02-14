import json
import pathlib
import platform
import subprocess
import urllib.request

from lib.odoo_client import OdooClient
from argparse import _SubParsersAction, ArgumentParser, Namespace

UPDATE_DATA_URL: str = (
    "https://api.github.com/repos/uAtomicBoolean/pointage/releases/latest"
)


class UpdateCommand:
    def __init__(
        self,
        odoo_client: OdooClient,
        subparsers: _SubParsersAction,
        VERSION: str,
    ):
        self.odoo_client = odoo_client
        self.VERSION = VERSION
        self.cmd: ArgumentParser = subparsers.add_parser(
            "update", help="Met à jour le script automatiquement."
        )
        self.cmd.set_defaults(execute=self.execute)

    def get_online_version_data(self) -> tuple[str, str]:
        with urllib.request.urlopen(UPDATE_DATA_URL) as response:
            update_data = json.loads(response.read().decode("utf-8"))

        return update_data["tag_name"], update_data["assets"][0]["browser_download_url"]

    def execute(self, _: Namespace):
        online_version, download_url = self.get_online_version_data()

        if online_version == self.VERSION:
            print(f"Script pointage déjà à jour ({self.VERSION})")
            return

        confirmation = input(
            "Une mise à jour est disponible, souhaitez-vous la télécharger (O/n) : "
        )
        if confirmation != "O":
            return

        bin_path = (
            f"{pathlib.Path.home()}/.local/bin"
            if platform.system() == "Linux"
            else "/usr/local/bin"
        )
        file_path = f"{bin_path}/pointage"

        print("Installation de la mise à jour.")
        with urllib.request.urlopen(download_url) as response:
            with open(file_path, "wb") as file:
                file.write(response.read())

        subprocess.call(f"chmod u+x {file_path}", shell=True)
        print("Mise à jour finie.")
