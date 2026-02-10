from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('voitures/', views.liste_voitures, name='liste_voitures'),
    path('voiture/<int:voiture_id>/', views.detail_voiture, name='detail_voiture'),
    path('voiture/ajouter/', views.ajouter_voiture, name='ajouter_voiture'),
    path('voiture/<int:voiture_id>/modifier/', views.modifier_voiture, name='modifier_voiture'),
    path('voiture/<int:voiture_id>/supprimer/', views.supprimer_voiture, name='supprimer_voiture'),  # AJOUTÉ
    path('voiture/<int:voiture_id>/favori/', views.toggle_favori, name='toggle_favori'),
    path('voiture/<int:voiture_id>/acheter/', views.acheter_voiture, name='acheter_voiture'),
    
    path('mes-voitures/', views.mes_voitures, name='mes_voitures'),
    path('mes-favoris/', views.mes_favoris, name='mes_favoris'),
    path('mes-achats/', views.mes_achats, name='mes_achats'),
    path('mes-ventes/', views.mes_ventes, name='mes_ventes'),
    path('transaction/<int:transaction_id>/confirmer/', views.confirmer_vente, name='confirmer_vente'),
    
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    
    # Pages d'administration (pour les utilisateurs staff)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Page de test
    path('test/', views.test, name='test'),
]