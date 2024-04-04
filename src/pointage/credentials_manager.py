import os
import pickle
import getpass
import pathlib


class CredentialsManager:
    """Manage the credentials for Odoo's API."""

    CONFIG_FOLDER = ".config/pointage"
    FILENAME = ".pointage"

    def __init__(self):
        self.home_path = str(pathlib.Path.home())
        self.config_folder_path = f"{self.home_path}/{CredentialsManager.CONFIG_FOLDER}"
        self.config_file_path = (
            f"{self.config_folder_path}/{CredentialsManager.FILENAME}"
        )

        # Check if the configuration folder does exists.
        if not os.path.isdir(self.config_folder_path):
            os.mkdir(self.config_folder_path)

        self.__cred_data = self.get_credentials_data()

    def get_credentials_data(self) -> dict:
        """Loads the credentials from the configuration file."""

        if not os.path.isfile(self.config_file_path):
            self.build_credentials_file()

        with open(self.config_file_path, "rb") as file:
            cred_data = pickle.load(file)

        return cred_data

    def build_credentials_file(self):
        """Creates the configuration file."""

        print(
            "Les identifiants pour Odoo n'ont pas été trouvés. Veuillez les indiquer."
        )
        ident = input("Identifiant: ")
        pwd = getpass.getpass("Mot de passe: ")
        data = {"id": ident, "pwd": pwd}

        with open(self.config_file_path, "wb") as file:
            pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)

    def get(self, key: str):
        """Safely gets a credential."""

        return self.__cred_data.get(key)
