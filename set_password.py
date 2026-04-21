"""Script utilitaire (local) pour réinitialiser le mot de passe d'un utilisateur.
Usage (référentiel local, non prod) :

# en mode interactif :
python3 set_password.py

# ou en ligne de commande :
python3 set_password.py admin password123

Remarques :
- Ce script met à jour la table `utilisateurs` de la base connectée via `config.DB_CONFIG`.
- Ne place pas ce script dans un dépôt public contenant des mots de passe en clair.
"""

from auth import hash_password
from database import execute
import getpass
import sys


def set_password(login: str, new_password: str):
    h = hash_password(new_password)
    n = execute("UPDATE utilisateurs SET mot_de_passe_hash=%s WHERE login=%s", (h, login))
    print(f"Mot de passe mis à jour pour '{login}' (rows affected: {n})")


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        login = sys.argv[1]
        pwd = sys.argv[2]
    else:
        login = input('Login à mettre à jour (ex: admin): ').strip()
        pwd = getpass.getpass('Nouveau mot de passe : ')
        pwd2 = getpass.getpass('Confirmer : ')
        if pwd != pwd2:
            print('Les mots de passe ne correspondent pas. Abandon.')
            sys.exit(1)

    if not login or not pwd:
        print('Login ou mot de passe invalide. Abandon.')
        sys.exit(1)

    set_password(login, pwd)
