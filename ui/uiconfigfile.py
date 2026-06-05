from configparser import ConfigParser
import os

carpeta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_archivos_configfile = os.path.join(carpeta_actual, "uiconfigfile.ini")

class Config:
    def __init__(self, config_file = ruta_archivos_configfile):
        self.config = ConfigParser()
        self.config.read(config_file)

    def get_page_title(self):
        return self.config["DEFAULT"].get("PAGE_TITLE")
    
    def get_user_options(self):
        return self.config["DEFAULT"].get("USER_OPTIONS").split(", ")
    
    def get_usecase_user_options(self):
        return self.config["DEFAULT"].get("USECASE_USER_OPTIONS").split(", ")
    
    def get_usecase_reclutador_options(self):
        return self.config["DEFAULT"].get("USECASE_RECLUTADOR_OPTIONS").split(", ")










