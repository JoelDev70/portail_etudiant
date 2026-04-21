# Petit script de diagnostic pour tester l'authentification sans lancer Flet
from auth import login

if __name__ == '__main__':
    try:
        print('Tentative de lecture de la table utilisateurs...')
        # Import query localement to inspect rows
        from database import query
        rows = query('SELECT id, login, role, actif FROM utilisateurs')
        print('Utilisateurs trouvés:', rows)
    except Exception as e:
        print('Erreur lors de la lecture de la base:')
        import traceback; traceback.print_exc()

    try:
        print('\nAppel de login("admin","password123")')
        u = login('admin', 'password123')
        print('Résultat login:', u)
    except Exception:
        print('Erreur lors de login:')
        import traceback; traceback.print_exc()
    
    # Vérification directe du hash bcrypt stocké
    try:
        print('\nRécupération du hash stocké pour admin et test de vérification bcrypt')
        rows = query("SELECT mot_de_passe_hash FROM utilisateurs WHERE login=%s", ('admin',))
        if rows:
            h = rows[0]['mot_de_passe_hash']
            print('Hash stocké:', h)
            from auth import verify_password
            print('verify_password("password123", hash) =>', verify_password('password123', h))
        else:
            print('Utilisateur admin introuvable lors de la vérif directe')
    except Exception:
        print('Erreur lors du test du hash:')
        import traceback; traceback.print_exc()
