"""Couche d'accès MySQL."""

  


import mysql.connector
from mysql.connector import pooling, errors as mysql_errors
from config import DB_CONFIG

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="portail_pool", pool_size=5, **DB_CONFIG
        )
    return _pool

def get_conn():
    return get_pool().get_connection()

def query(sql, params=None, fetch=True, dict_cursor=True):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=dict_cursor)
        cur.execute(sql, params or ())
        if fetch:
            rows = cur.fetchall()
            return rows
        conn.commit()
        return cur.lastrowid
    except mysql.errors.DatabaseError as e:
        # Provide a clearer message for the common plugin/auth issues
        if getattr(e, 'errno', None) == 1524:
            raise RuntimeError(
                "Erreur de connexion MySQL : Plugin d'authentification manquant (1524).\n"
                "Cela signifie que le serveur MySQL ne charge pas le plugin demandé.\n"
                "Solutions recommandées :\n"
                " 1) Sur le serveur MySQL, exécuter (avec privilèges root) :\n"
                "    ALTER USER 'votre_user'@'localhost' IDENTIFIED WITH mysql_native_password BY 'votre_mot_de_passe';\n"
                "    FLUSH PRIVILEGES;\n"
                " 2) Ou créer un utilisateur configuré avec mysql_native_password.\n"
                " 3) Si le serveur utilise 'caching_sha2_password', décommentez ou définissez\n"
                "    `auth_plugin` dans `config.py` à 'caching_sha2_password' et réessayez.\n"
                "Si vous ne pouvez pas modifier le serveur, créez un utilisateur local avec\n"
                "le plugin approprié et mettez à jour `DB_CONFIG` en conséquence.",
            ) from e
        raise
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()

def execute(sql, params=None):
    return query(sql, params, fetch=False)
