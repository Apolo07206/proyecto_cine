# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # carga las variables del archivo .env

class Config:
    SECRET_KEY = os.getenv('eicwiemcumaehfppiwgqkvr')

    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_USER = os.getenv('root')
    MYSQL_PASSWORD = os.getenv('')
    MYSQL_DB = os.getenv('proyecto_cine')
    MYSQL_CURSORCLASS = 'DictCursor'  # para que los resultados vengan como {clave: valor} en vez de tuplas