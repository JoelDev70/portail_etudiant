"""Utilitaires pour charger les variables d'environnement depuis .env"""
import os
from dotenv import load_dotenv

def load_env():
    """Charge les variables d'environnement depuis .env si le fichier existe"""
    if os.path.exists('.env'):
        load_dotenv('.env')
        print("✓ Variables d'environnement chargées depuis .env")
    else:
        print("⚠ Fichier .env non trouvé, utilisation des variables système")

if __name__ == '__main__':
    load_env()
