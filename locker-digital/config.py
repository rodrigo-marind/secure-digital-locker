# CONFIGURACIÓN DE LA APP

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "Hola_Profe_Esta_es_la_clave_secreta"

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "locker.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

    # Allowed file extensions for uploads
    ALLOWED_EXTENSIONS = {"pdf", "docx", "zip"}

    # Directory for storing encryption keys
    KEYS_DIR = os.path.join(BASE_DIR, "keys")

