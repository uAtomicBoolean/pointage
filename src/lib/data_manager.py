import os
import pickle
import getpass
import pathlib


class DataManager:
    """Manage the credentials for Odoo's API."""

    CONFIG_FOLDER = ".config/pointage"
    FILENAME = ".pointage"

    def __init__(self):
        self.home_path = str(pathlib.Path.home())
        self.config_folder_path = f"{self.home_path}/{DataManager.CONFIG_FOLDER}"
        self.config_file_path = f"{self.config_folder_path}/{DataManager.FILENAME}"

        # Check if the configuration folder does exists.
        if not os.path.isdir(self.config_folder_path):
            os.mkdir(self.config_folder_path)

        self.__data = self.get_all_data()

    def get_all_data(self) -> dict:
        """Loads the credentials from the configuration file."""

        if not os.path.isfile(self.config_file_path):
            self.build_data_file()

        with open(self.config_file_path, "rb") as file:
            data = pickle.load(file)

        if os.environ.get("ENV") == "dev":
            data["server_url"] = os.environ.get("SERVER_URL")

        print(data)
        return data

    def build_data_file(self):
        """Creates the configuration file."""

        print(
            "Les identifiants pour Odoo n'ont pas été trouvés. Veuillez les indiquer."
        )
        ident = input("Identifiant: ")
        pwd = getpass.getpass("Mot de passe: ")
        server_url = input("URL du serveur: ")
        db = input("Base de donnees: ")
        data = {
            "id": ident,
            "pwd": pwd,
            "server_url": server_url,
            "db": db,
        }

        with open(self.config_file_path, "wb") as file:
            pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)

    def get(self, key: str):
        """Safely gets a credential."""

        return self.__data.get(key)
