import shutil
import zipfile
import tempfile
import subprocess
import urllib.request
from lib.odoo_client import OdooClient
from argparse import _SubParsersAction, ArgumentParser, Namespace


class UpdateCommand:

    def __init__(
        self,
        odoo_client: OdooClient,
        subparsers: _SubParsersAction,
        version: str,
    ):
        self.odoo_client = odoo_client
        self.version = version

        self.cmd: ArgumentParser = subparsers.add_parser(
            "update", help="Met à jour le script automatiquement."
        )
        self.cmd.set_defaults(execute=self.execute)

    def execute(self, _: Namespace):
        # TODO Update the command to download the latest release instead of building the script.

        zip_file_url = (
            "https://github.com/uAtomicBoolean/pointage/archive/refs/heads/main.zip"
        )
        build_script = "/tmp/pointage-main/build_script.sh"

        print("Downloading the script sources...")
        with urllib.request.urlopen(zip_file_url) as response:
            with tempfile.NamedTemporaryFile() as tmp_file:
                shutil.copyfileobj(response, tmp_file)
                tmp_filename = tmp_file.name + "_script"
                with zipfile.ZipFile(tmp_file.name) as zip:
                    zip.extractall("/tmp")

        print("Building the script...")
        subprocess.call(f"chmod u+x {build_script}", shell=True)
        subprocess.call(
            f"{build_script} /tmp/pointage-main/src {tmp_filename}",
            shell=True,
        )
        subprocess.call(f"sudo mv {tmp_filename} /usr/local/bin/pointage", shell=True)

        print("Cleaning after update...")
        subprocess.call(f"rm -rf /tmp/pointage-main", shell=True)

        print("Update done !")
