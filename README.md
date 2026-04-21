# 📚 Portail Étudiant

Application web et mobile de gestion des paiements, notes et documents pour étudiants.

## 🚀 Démarrage rapide

### Windows
```bash
setup.bat
python run_app.py
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
python run_app.py
```

## 📋 Prérequis

- Python 3.11+
- MySQL 5.7+ ou MariaDB
- Git

## 🔧 Configuration

### 1. Configuration de la base de données

```bash
cp .env.example .env
# Modifiez .env avec vos paramètres MySQL
```

Variables d'environnement :
- `DB_HOST` : Adresse du serveur MySQL (ex: localhost, 192.168.1.10)
- `DB_PORT` : Port MySQL (défaut: 3306)
- `DB_USER` : Utilisateur MySQL (défaut: root)
- `DB_PASSWORD` : Mot de passe MySQL
- `DB_NAME` : Nom de la base (défaut: portail_etudiant)

### 2. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 3. Initialisation de la base de données

```bash
# Créer la base de données
mysql -u root < sql/schema.sql

# Vérifier la connexion
python run_login.py
```

## 🏃 Utilisation

### Lancer l'application

```bash
python run_app.py
```

L'application se lance sur `http://localhost:8550`

### Identifiants de démonstration

- **Admin** : `admin` / `password123`
- **Étudiant 1** : `etudiant1` / `password123`
- **Étudiant 2** : `etudiant2` / `password123`

## 📱 Générer une APK

Voir [DEPLOYMENT.md](DEPLOYMENT.md) pour :
- Configuration GitHub Actions
- Secrets pour l'APK
- Créer une Release automatique

### Commande locale (optionnel)

```bash
flet build apk
```

## 📁 Structure du projet

```
.
├── main.py                    # Point d'entrée Flet
├── auth.py                    # Authentification & sessions
├── config.py                  # Configuration DB
├── database.py                # Couche d'accès DB
├── services.py                # Logique métier
├── pages/
│   ├── login_page.py         # Page de connexion
│   ├── student_pages.py       # Pages étudiant
│   └── admin_pages.py         # Pages administrateur
├── sql/
│   └── schema.sql            # Schéma de la base
├── tests/
│   └── test_services.py      # Tests unitaires
└── .github/workflows/
    └── build-apk.yml         # Workflow APK
```

## 👤 Rôles

### Administrateur
- Tableau de bord
- Gestion des étudiants
- Saisie des notes
- Gestion des paiements (export CSV)
- Gestion des enseignants
- Gestion des documents

### Étudiant
- Consulter son profil
- Voir ses notes
- Consulter l'emploi du temps
- Télécharger les supports
- Consulter ses paiements
- Soumettre un paiement

## 🔐 Sécurité

- Mots de passe hashés avec bcrypt
- Sessions locales
- Connexion MySQL sécurisée
- Variables d'environnement pour les identifiants

## 🐛 Tests

```bash
python -m pytest tests/
```

## 📝 Notes importantes

### Pour le développement local

1. Les variables d'environnement se chargent automatiquement depuis `.env`
2. Le fichier `.env` est ignoré par Git (ne commitez jamais vos identifiants !)
3. Utilisez `.env.example` comme template

### Pour l'APK sur GitHub

1. Configurez les secrets GitHub (voir [DEPLOYMENT.md](DEPLOYMENT.md))
2. Assurez-vous que votre base de données est **accessible depuis Internet**
3. Le workflow se déclenche automatiquement à chaque push

## 🐛 Dépannage

```bash
# Tester la connexion MySQL
python run_login.py

# Vérifier les variables d'environnement
python -c "from config import DB_CONFIG; print(DB_CONFIG)"

# Vérifier que le fichier .env est chargé
python run_app.py --debug
```

## 📄 Licence

MIT


## Comptes de démo

| Login      | Mot de passe  | Rôle      |
|------------|---------------|-----------|
| admin      | password123   | admin     |
| etudiant1  | password123   | étudiant  |
| etudiant2  | password123   | étudiant  |

## Schéma BDD

8 tables avec clés étrangères et contraintes :
`utilisateurs`, `etudiants`, `matieres`, `notes`, `cours`, `emploi_temps`,
`paiements`, `documents`. Voir `sql/schema.sql`.

## Sécurité

- Mots de passe hachés avec **bcrypt** (jamais en clair).
- Session stockée dans un fichier local `.session` (cookie), supprimé à la
  déconnexion.
- Requêtes paramétrées (anti-injection SQL).
- Contrôle d'accès par rôle (étudiant / admin) dans `main.py`.

## Fonctionnalités

### Étudiant
- Fiche profil (matricule, filière, spécialité, photo)
- Notes par semestre + moyenne pondérée automatique
- Emploi du temps hebdomadaire
- Téléchargement des supports (PDF / liens)
- État des paiements (total dû, payé, reste) + historique

### Administration
- Dashboard : nombre d'étudiants, moyenne promo, taux de paiement
- CRUD étudiants (ajout / modification / suppression)
- Saisie / mise à jour des notes par étudiant et matière
