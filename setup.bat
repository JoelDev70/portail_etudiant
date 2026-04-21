@echo off
REM Script de configuration rapide du projet pour Windows

echo.
echo 🚀 Setup du Portail Étudiant
echo ==============================
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou n'est pas dans le PATH
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ Python trouvé: %PYTHON_VERSION%

REM Créer .env s'il n'existe pas
if not exist .env (
    echo.
    echo 📝 Création du fichier .env...
    copy .env.example .env
    echo ✓ Fichier .env créé. Modifiez-le avec vos paramètres de base de données.
) else (
    echo ✓ Fichier .env existe déjà
)

REM Créer venv
echo.
echo 📦 Création de l'environnement virtuel...
python -m venv venv
call venv\Scripts\activate.bat

REM Installer les dépendances
echo 📥 Installation des dépendances...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✅ Setup terminé!
echo.
echo Prochaines étapes:
echo 1. Modifiez .env avec vos paramètres MySQL
echo 2. Lancez l'app avec: python run_app.py
echo 3. Ou testez la connexion: python run_login.py
echo.
