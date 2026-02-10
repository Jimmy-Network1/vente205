import os
import sys
import django
from datetime import date

# Configuration de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from voitures.models import Marque, Modele, Voiture
from django.contrib.auth.models import User

def creer_marques():
    marques_data = [
        {'nom': 'Renault', 'pays': 'France', 'date_creation': date(1899, 2, 25)},
        {'nom': 'Peugeot', 'pays': 'France', 'date_creation': date(1810, 9, 26)},
        {'nom': 'Citroën', 'pays': 'France', 'date_creation': date(1919, 6, 4)},
        {'nom': 'Volkswagen', 'pays': 'Allemagne', 'date_creation': date(1937, 5, 28)},
        {'nom': 'BMW', 'pays': 'Allemagne', 'date_creation': date(1916, 3, 7)},
        {'nom': 'Mercedes-Benz', 'pays': 'Allemagne', 'date_creation': date(1926, 6, 28)},
        {'nom': 'Toyota', 'pays': 'Japon', 'date_creation': date(1937, 8, 28)},
        {'nom': 'Ford', 'pays': 'États-Unis', 'date_creation': date(1903, 6, 16)},
    ]
    
    for data in marques_data:
        Marque.objects.get_or_create(**data)
    
    print("Marques créées avec succès!")

def creer_modeles():
    marques = Marque.objects.all()
    
    modeles_data = [
        {'marque': 'Renault', 'nom': 'Clio', 'annee_lancement': 1990, 'type_carburant': 'essence', 'transmission': 'manuelle', 'puissance': 90, 'consommation': 5.2},
        {'marque': 'Peugeot', 'nom': '208', 'annee_lancement': 2012, 'type_carburant': 'diesel', 'transmission': 'manuelle', 'puissance': 75, 'consommation': 3.8},
        {'marque': 'Citroën', 'nom': 'C3', 'annee_lancement': 2002, 'type_carburant': 'essence', 'transmission': 'automatique', 'puissance': 82, 'consommation': 5.8},
        {'marque': 'Volkswagen', 'nom': 'Golf', 'annee_lancement': 1974, 'type_carburant': 'diesel', 'transmission': 'manuelle', 'puissance': 115, 'consommation': 4.5},
        {'marque': 'BMW', 'nom': 'Série 3', 'annee_lancement': 1975, 'type_carburant': 'essence', 'transmission': 'automatique', 'puissance': 184, 'consommation': 6.8},
        {'marque': 'Mercedes-Benz', 'nom': 'Classe A', 'annee_lancement': 1997, 'type_carburant': 'essence', 'transmission': 'automatique', 'puissance': 163, 'consommation': 6.5},
        {'marque': 'Toyota', 'nom': 'Yaris', 'annee_lancement': 1999, 'type_carburant': 'hybride', 'transmission': 'automatique', 'puissance': 116, 'consommation': 3.8},
        {'marque': 'Ford', 'nom': 'Fiesta', 'annee_lancement': 1976, 'type_carburant': 'essence', 'transmission': 'manuelle', 'puissance': 100, 'consommation': 5.4},
    ]
    
    for data in modeles_data:
        marque = Marque.objects.get(nom=data.pop('marque'))
        Modele.objects.get_or_create(marque=marque, **data)
    
    print("Modèles créés avec succès!")

def creer_utilisateur_test():
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("Utilisateur test créé avec succès!")
    return user

def creer_voitures_test():
    user = User.objects.get(username='testuser')
    
    voitures_data = [
        {
            'modele': Modele.objects.get(marque__nom='Renault', nom='Clio'),
            'prix': 12500,
            'kilometrage': 45000,
            'annee': 2020,
            'couleur': 'blanc',
            'etat': 'occasion',
            'description': 'Clio en excellent état, très bien entretenue.',
            'vendeur': user
        },
        {
            'modele': Modele.objects.get(marque__nom='Peugeot', nom='208'),
            'prix': 18500,
            'kilometrage': 15000,
            'annee': 2021,
            'couleur': 'gris',
            'etat': 'occasion',
            'description': 'Peugeot 208 presque neuve, garantie constructeur.',
            'vendeur': user
        },
        {
            'modele': Modele.objects.get(marque__nom='BMW', nom='Série 3'),
            'prix': 32500,
            'kilometrage': 75000,
            'annee': 2019,
            'couleur': 'noir',
            'etat': 'occasion',
            'description': 'BMW Série 3 full options, très bon état général.',
            'vendeur': user
        },
    ]
    
    for data in voitures_data:
        Voiture.objects.get_or_create(**data)
    
    print("Voitures de test créées avec succès!")

if __name__ == '__main__':
    print("Initialisation des données...")
    creer_marques()
    creer_modeles()
    creer_utilisateur_test()
    creer_voitures_test()
    print("Initialisation terminée!")