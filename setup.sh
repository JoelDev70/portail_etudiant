#!/bin/bash
# Script de configuration rapide du projet

echo "🚀 Setup du Portail Étudiant"
echo "=============================="

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "✓ Python trouvé: $(python3 --version)"

# Créer .env s'il n'existe pas
if [ ! -f .env ]; then
    echo ""
    echo "📝 Création du fichier .env..."
    cp .env.example .env
    echo "✓ Fichier .env créé. Modifiez-le avec vos paramètres de base de données."
else
    echo "✓ Fichier .env existe déjà"
fi

# Créer venv
echo ""
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate || . venv/Scripts/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup terminé!"
echo ""
echo "Prochaines étapes:"
echo "1. Modifiez .env avec vos paramètres MySQL"
echo "2. Lancez l'app avec: python run_app.py"
echo "3. Ou testez la connexion: python run_login.py"
