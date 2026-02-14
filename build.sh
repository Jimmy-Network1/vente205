#!/bin/bash
# build.sh
echo "🚀 Démarrage du build..."

# Installation des dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Collecte des fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Application des migrations
echo "🔄 Application des migrations..."
python manage.py migrate --noinput

# Créer une image par défaut si manquante (évite les 404 sur /media/voitures/default.jpg)
python manage.py ensure_default_media || true

# Création des données initiales
echo "📊 Création des données de démo..."
python manage.py shell -c "
from django.contrib.auth.models import User
from voitures.models import Marque, Modele, Voiture
import datetime

# Créer admin si non existant
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@automarket.com', 'Admin123!')
    print('✓ Admin créé: admin / Admin123!')

# Créer vendeur de démo
vendeur, created = User.objects.get_or_create(
    username='vendeur',
    defaults={'email': 'vendeur@automarket.com', 'first_name': 'Jean', 'last_name': 'Dupont'}
)
if created:
    vendeur.set_password('Vendeur123!')
    vendeur.save()
    print('✓ Vendeur créé: vendeur / Vendeur123!')

# Créer acheteur de démo
acheteur, created = User.objects.get_or_create(
    username='acheteur',
    defaults={'email': 'acheteur@automarket.com', 'first_name': 'Marie', 'last_name': 'Martin'}
)
if created:
    acheteur.set_password('Acheteur123!')
    acheteur.save()
    print('✓ Acheteur créé: acheteur / Acheteur123!')

# Créer des marques
marques = [
    ('Renault', 'France'),
    ('Peugeot', 'France'),
    ('Citroën', 'France'),
    ('Volkswagen', 'Allemagne'),
    ('BMW', 'Allemagne'),
    ('Toyota', 'Japon'),
    ('Tesla', 'États-Unis'),
]

for nom, pays in marques:
    Marque.objects.get_or_create(
        nom=nom,
        defaults={
            'pays': pays,
            'date_creation': datetime.date(2000, 1, 1),
        }
    )

print(f'✓ {len(marques)} marques créées')

# Créer des modèles
renault = Marque.objects.get(nom='Renault')
peugeot = Marque.objects.get(nom='Peugeot')
vw = Marque.objects.get(nom='Volkswagen')

modeles = [
    (renault, 'Clio', 1990, 'essence', 'manuelle', 90, 5.2),
    (renault, 'Mégane', 1995, 'diesel', 'manuelle', 110, 4.5),
    (peugeot, '208', 2012, 'essence', 'automatique', 82, 5.0),
    (peugeot, '3008', 2009, 'diesel', 'automatique', 130, 5.5),
    (vw, 'Golf', 1974, 'essence', 'manuelle', 115, 5.5),
    (vw, 'Passat', 1973, 'diesel', 'automatique', 150, 5.0),
]

for marque, nom, annee, carburant, trans, puissance, conso in modeles:
    Modele.objects.get_or_create(
        marque=marque,
        nom=nom,
        defaults={
            'annee_lancement': annee,
            'type_carburant': carburant,
            'transmission': trans,
            'puissance': puissance,
            'consommation': conso
        }
    )

print(f'✓ {len(modeles)} modèles créés')

# Créer des voitures
clio = Modele.objects.get(nom='Clio')
megane = Modele.objects.get(nom='Mégane')
peugeot208 = Modele.objects.get(nom='208')
golf = Modele.objects.get(nom='Golf')

voitures = [
    (clio, 12500, 45000, 2020, 'blanc', 'occasion', 'Clio en excellent état'),
    (megane, 18500, 75000, 2019, 'gris', 'occasion', 'Mégane diesel économique'),
    (peugeot208, 15500, 25000, 2021, 'rouge', 'occasion', '208 presque neuve'),
    (golf, 21500, 55000, 2020, 'argent', 'occasion', 'Golf 8 en parfait état'),
]

for modele, prix, km, annee, couleur, etat, desc in voitures:
    Voiture.objects.get_or_create(
        modele=modele,
        annee=annee,
        kilometrage=km,
        defaults={
            'prix': prix,
            'couleur': couleur,
            'etat': etat,
            'description': desc,
            'vendeur': vendeur
        }
    )

print(f'✓ {len(voitures)} voitures créées')
print('✅ Données de démo créées avec succès!')
"

# Générer des images de démo (utile si stockage média non persistant)
python manage.py generate_demo_images || true

echo "✅ Build terminé avec succès!"
