# 📱 Build & Deployment Guide

## GitHub Actions - Build APK Automatique

Ce projet est configuré pour construire automatiquement une APK Android chaque fois que vous poussez du code sur GitHub.

### Comment ça fonctionne ?

1. **Push sur GitHub** → Le workflow GitHub Actions se déclenche automatiquement
2. **Build l'APK** → L'application est compilée pour Android
3. **Crée une Release** → L'APK est disponible en téléchargement

## ⚠️ Configuration MySQL pour l'APK

### Étape 1 : Configurer les secrets GitHub

1. Allez sur votre dépôt GitHub
2. Cliquez sur **Settings** → **Secrets and variables** → **Actions**
3. Cliquez sur **New repository secret**
4. Ajoutez ces secrets :

| Secret Name   | Exemple de valeur    | Description                                        |
| ------------- | -------------------- | -------------------------------------------------- |
| `DB_HOST`     | `mysql.example.com`  | Adresse de votre serveur MySQL (PUBLIC/ACCESSIBLE) |
| `DB_PORT`     | `4306`               | Port MySQL (par défaut 4306)                       |
| `DB_USER`     | `portail_user`       | Utilisateur MySQL                                  |
| `DB_PASSWORD` | `votre_mot_de_passe` | Mot de passe MySQL                                 |
| `DB_NAME`     | `portail_etudiant`   | Nom de la base de données                          |

### ⚠️ Important - Base de données

L'APK mobile doit se connecter à une **base de données distante et accessible depuis Internet**.

**Options recommandées :**

- ✅ Serveur MySQL sur un hébergeur (ex: Heroku, DigitalOcean, AWS)
- ✅ Service de base de données gérée (ex: AWS RDS, Google Cloud SQL)
- ❌ LocalHost ou 127.0.0.1 (n'est pas accessible depuis le mobile)

### Étape 2 : Configuration locale (développement)

1. Créez un fichier `.env` à la racine du projet :

```bash
cp .env.example .env
```

2. Éditez `.env` avec vos valeurs locales :

```
DB_HOST=localhost
DB_PORT=4306
DB_USER=root
DB_PASSWORD=
DB_NAME=portail_etudiant
```

3. Le fichier `.env` est **ignoré par Git** (sécurité)

### Étape 3 : Lancer l'application

```bash
# Installe les dépendances
pip install -r requirements.txt

# Lance l'application (charge automatiquement .env)
python run_app.py
```

## 🚀 Créer une Release avec APK

### Pour tester le build :

```bash
git push origin main
```

Le workflow se lance automatiquement → consultez **Actions** sur GitHub

### Pour créer une Release avec APK :

```bash
# Créez un tag
git tag -a v1.0.0 -m "Version 1.0.0"

# Poussez le tag sur GitHub
git push origin v1.0.0
```

L'APK sera automatiquement téléchargée dans **Releases** !

## 📥 Télécharger l'APK

Les APKs générées sont disponibles à :

- **Artifacts** : Dans les runs GitHub Actions (30 jours de conservation)
- **Releases** : En créant un tag `v*` (ex: v1.0.0)

### Installer l'APK sur Android

```bash
# Via ADB
adb install portail_etudiant.apk

# Ou simplement transférer le fichier sur le téléphone et le lancer
```

## 🔧 Configuration de la base de données pour l'APK

### Structure du flux :

```
APK Mobile (Android)
        ↓
GitHub Actions (Build)
        ↓
Variables d'environnement (Secrets GitHub)
        ↓
Config.py (charge les variables)
        ↓
Database.py (se connecte à MySQL)
        ↓
Serveur MySQL distant ✓
```

### Vérifier la connexion :

Avant de générer l'APK, testez la connexion :

```bash
python run_login.py
```

Cela affichera les utilisateurs de la base si la connexion fonctionne.

## 📋 Exigences

- Python 3.11+
- Java JDK 17+ (fourni par GitHub Actions)
- Android SDK (configuré automatiquement)
- Serveur MySQL **public et accessible**
- Les dépendances Python dans `requirements.txt`

## 🐛 Dépannage

### "Database connection failed"

- ✓ Vérifiez que `DB_HOST` est l'adresse IP/domaine PUBLIC (pas localhost)
- ✓ Vérifiez que le port MySQL est accessible depuis l'extérieur
- ✓ Vérifiez les identifiants MySQL dans les secrets GitHub

### Build APK échoue

- ✓ Consultez les logs sur GitHub Actions
- ✓ Vérifiez que `requirements.txt` inclut toutes les dépendances
- ✓ Assurez-vous que le code ne dépend pas de modules desktop uniquement

### APK se lance mais crashe immédiatement

- ✓ Vérifiez la connexion à la base de données
- ✓ Vérifiez que les identifiants MySQL sont corrects
- ✓ Activez les logs d'erreur de Flet

## 📝 Variables d'environnement

Ces variables sont lues par `config.py` :

```python
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '4306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'portail_etudiant')
```

Les valeurs par défaut s'utilisent si la variable n'est pas définie.
