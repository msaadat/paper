import configparser
from pathlib import Path


class PaperConfig(configparser.ConfigParser):
    config_path = Path.home() / Path(".paper.cfg")

    def __init__(self):
        super().__init__()
        self["DEFAULT"] = {'WindowX': 300,
                           'WindowY': 300,
                           'Width': 550,
                           'Height': 350,
                           'PapersPath': Path.home() / Path('.papers/')}
        self["Paper"] = {}
        self.LoadConfig()

    def LoadConfig(self):
        if self.config_path.exists():
            self.read(self.config_path)

    def SaveConfig(self):
        with open(self.config_path, 'w') as config_file:
            self.write(config_file)
