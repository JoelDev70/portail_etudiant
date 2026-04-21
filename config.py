"""Configuration de la base de données MySQL."""
import os

DB_CONFIG = {
    "host": os.getenv('DB_HOST', 'localhost'),
    "port": int(os.getenv('DB_PORT', 3306)),
    "user": os.getenv('DB_USER', 'root'),
    "password": os.getenv('DB_PASSWORD', ''),
    "database": os.getenv('DB_NAME', 'portail_etudiant'),
    "charset": "utf8mb4",
    # Option d'authentification client — si votre serveur MySQL/MariaDB
    # nécessite un plugin d'authentification particulier vous pouvez
    # le préciser ici. Exemple: "mysql_native_password" ou
    # "caching_sha2_password". Laisser vide si non nécessaire.
    # "auth_plugin": "mysql_native_password",
}

APP_NAME = "Portail Étudiant"
SESSION_FILE = ".session"   # cookie de session local
