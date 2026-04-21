import flet as ft
from load_env import load_env
from main import main

if __name__ == '__main__':
    # Charger les variables d'environnement
    load_env()
    
    print('Démarrage de l\'application Flet. Si rien n\'apparait, ouvrez votre navigateur sur http://127.0.0.1:8550')
    print("Démarrage de l'application Flet. Lancement du serveur local...")
    # Use default app runner to be compatible with installed flet version
        # Prefer web browser view when available (prevents desktop embedding issues)
    web_view = getattr(ft, 'WEB_BROWSER', None)
    if web_view is not None:
        try:
            ft.app(target=main, view=web_view, port=8550)
        except Exception:
            ft.app(target=main)
    else:
        ft.app(target=main)
