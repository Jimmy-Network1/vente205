# 🚗 Vente de Voitures - Plateforme Django

## 🌐 Démo en ligne
**URL :** https://vente-voitures.onrender.com

## 👥 Comptes de test
- **Admin :** admin / Admin123!
- **Vendeur :** vendeur / Vendeur123!
- **Acheteur :** acheteur / Acheteur123!

## 🚀 Déploiement sur Render.com

### Prérequis
- Compte [Render.com](https://render.com)
- Compte [GitHub](https://github.com)

### Étapes
1. Forkez ce dépôt sur GitHub
2. Connectez votre compte GitHub à Render
3. Créez un nouveau "Web Service"
4. Sélectionnez ce dépôt
5. Render détectera automatiquement la configuration
6. Cliquez sur "Create Web Service"

## 🛠 Installation locale

```bash
# Cloner le projet
git clone https://github.com/votreusername/vente-voitures.git
cd vente-voitures

# Créer environnement virtuel
python -m venv env
source env/bin/activate  # Linux/Mac
# ou
env\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer la base de données
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver