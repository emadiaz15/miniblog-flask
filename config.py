import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

#configura la ruta del archivo de la bd
basedir = os.path.abspath(os.path.dirname(__file__)) 

class Config:
    #Clave utilizada para proteger las sesiones
    SECRET_KEY = os.getenv('SECRET_KEY')
    #Datos para establecer conexion con la bd 
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    #habilita o deshabilita el seguimiento de modificaciones de objetos.
    SQLALCHEMY_TRACK_MODIFICATIONS = False