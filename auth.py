"""Authentification : hachage bcrypt + session locale."""
import os, json, bcrypt
from database import query, execute
from config import SESSION_FILE

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False

def login(login_name: str, password: str):
    rows = query(
        "SELECT id, login, mot_de_passe_hash, role, actif FROM utilisateurs WHERE login=%s",
        (login_name,),
    )
    if not rows:
        return None
    u = rows[0]
    if not u["actif"] or not verify_password(password, u["mot_de_passe_hash"]):
        return None
    user = {"id": u["id"], "login": u["login"], "role": u["role"]}
    if u["role"] == "etudiant":
        et = query("SELECT * FROM etudiants WHERE utilisateur_id=%s", (u["id"],))
        if et:
            user["etudiant"] = et[0]
    save_session(user)
    return user

def save_session(user: dict):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(user, f, default=str)

def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def logout():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def create_user(login_name, password, role):
    return execute(
        "INSERT INTO utilisateurs (login, mot_de_passe_hash, role) VALUES (%s,%s,%s)",
        (login_name, hash_password(password), role),
    )
