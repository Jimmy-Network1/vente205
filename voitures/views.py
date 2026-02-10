from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # IMPORT AJOUTÉ
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum
from django.core.paginator import Paginator
from django.http import HttpResponse
import os
from .models import Marque, Modele, Voiture, Favori, Transaction, Avis
from .forms import InscriptionForm

# ==================== VUES PUBLIQUES ====================

def accueil(request):
    """Page d'accueil du site"""
    voitures_recentes = Voiture.objects.filter(est_vendue=False).order_by('-date_ajout')[:6]
    voitures_promo = Voiture.objects.filter(est_vendue=False).order_by('prix')[:6]
    marques_populaires = Marque.objects.annotate(
        nb_voitures=Count('modeles__voitures')
    ).order_by('-nb_voitures')[:8]
    
    context = {
        'voitures_recentes': voitures_recentes,
        'voitures_promo': voitures_promo,
        'marques_populaires': marques_populaires,
        'total_voitures': Voiture.objects.filter(est_vendue=False).count(),
    }
    return render(request, 'voitures/accueil.html', context)

def liste_voitures(request):
    """Liste toutes les voitures avec filtres"""
    voitures_list = Voiture.objects.filter(est_vendue=False).select_related(
        'modele__marque', 'vendeur'
    ).prefetch_related('favoris')
    
    # Récupération des filtres
    marque_id = request.GET.get('marque')
    prix_min = request.GET.get('prix_min')
    prix_max = request.GET.get('prix_max')
    annee_min = request.GET.get('annee_min')
    annee_max = request.GET.get('annee_max')
    
    # Application des filtres
    if marque_id:
        voitures_list = voitures_list.filter(modele__marque_id=marque_id)
    
    if prix_min:
        voitures_list = voitures_list.filter(prix__gte=prix_min)
    
    if prix_max:
        voitures_list = voitures_list.filter(prix__lte=prix_max)
    
    if annee_min:
        voitures_list = voitures_list.filter(annee__gte=annee_min)
    
    if annee_max:
        voitures_list = voitures_list.filter(annee__lte=annee_max)
    
    # Pagination
    paginator = Paginator(voitures_list, 12)
    page_number = request.GET.get('page')
    voitures = paginator.get_page(page_number)
    
    # Calcul du prix moyen
    prix_moyen = voitures_list.aggregate(Avg('prix'))['prix__avg']
    
    context = {
        'voitures': voitures,
        'marques': Marque.objects.all(),
        'marque_selected': int(marque_id) if marque_id else None,
        'prix_min': prix_min,
        'prix_max': prix_max,
        'annee_min': annee_min,
        'annee_max': annee_max,
        'prix_moyen': prix_moyen,
    }
    return render(request, 'voitures/liste_voitures.html', context)

def detail_voiture(request, voiture_id):
    """Page de détails d'une voiture"""
    voiture = get_object_or_404(Voiture.objects.select_related(
        'modele__marque', 'vendeur'
    ), id=voiture_id)
    
    # Vérifier si l'utilisateur a cette voiture en favoris
    est_favori = False
    if request.user.is_authenticated:
        est_favori = Favori.objects.filter(
            utilisateur=request.user, 
            voiture=voiture
        ).exists()
    
    # Récupérer les avis
    avis = Avis.objects.filter(voiture=voiture, approuve=True)
    
    # Voitures similaires
    voitures_similaires = Voiture.objects.filter(
        modele__marque=voiture.modele.marque,
        est_vendue=False
    ).exclude(id=voiture.id)[:4]
    
    context = {
        'voiture': voiture,
        'est_favori': est_favori,
        'avis': avis,
        'voitures_similaires': voitures_similaires,
    }
    return render(request, 'voitures/detail_voiture.html', context)

# ==================== AUTHENTIFICATION ====================

def inscription(request):
    """Page d'inscription"""
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Création automatique d'un profil utilisateur simple
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            messages.success(request, 'Inscription réussie ! Bienvenue sur AutoMarket.')
            return redirect('accueil')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = InscriptionForm()
    
    context = {'form': form}
    return render(request, 'voitures/inscription.html', context)

def connexion(request):
    """Page de connexion"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} !')
            
            # Redirection vers la page demandée ou l'accueil
            next_page = request.GET.get('next', 'accueil')
            return redirect(next_page)
        else:
            messages.error(request, 'Identifiants incorrects. Veuillez réessayer.')
    
    return render(request, 'voitures/connexion.html')

def deconnexion(request):
    """Déconnexion de l'utilisateur"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('accueil')

# ==================== VUES PROTÉGÉES ====================

@login_required
def ajouter_voiture(request):
    """Ajouter une nouvelle voiture à vendre"""
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            marque_id = request.POST.get('marque')
            modele_nom = request.POST.get('modele')
            prix = request.POST.get('prix')
            kilometrage = request.POST.get('kilometrage')
            annee = request.POST.get('annee')
            couleur = request.POST.get('couleur')
            etat = request.POST.get('etat')
            description = request.POST.get('description')
            
            # Création ou récupération de la marque et du modèle
            marque = get_object_or_404(Marque, id=marque_id)
            modele, created = Modele.objects.get_or_create(
                marque=marque,
                nom=modele_nom,
                defaults={
                    'annee_lancement': annee,
                    'type_carburant': 'essence',
                    'transmission': 'manuelle',
                    'puissance': 100,
                    'consommation': 6.0
                }
            )
            
            # Création de la voiture
            voiture = Voiture.objects.create(
                modele=modele,
                prix=prix,
                kilometrage=kilometrage,
                annee=annee,
                couleur=couleur,
                etat=etat,
                description=description,
                vendeur=request.user
            )
            
            # Gestion de l'image
            if 'image' in request.FILES:
                voiture.image_principale = request.FILES['image']
                voiture.save()
            
            messages.success(request, 'Votre annonce a été publiée avec succès !')
            return redirect('detail_voiture', voiture_id=voiture.id)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    # GET request - afficher le formulaire
    marques = Marque.objects.all()
    context = {'marques': marques}
    return render(request, 'voitures/ajouter_voiture.html', context)

@login_required
def modifier_voiture(request, voiture_id):
    """Modifier une voiture existante"""
    voiture = get_object_or_404(Voiture, id=voiture_id)
    
    # Vérifier que l'utilisateur est le propriétaire
    if voiture.vendeur != request.user:
        messages.error(request, "Vous n'avez pas la permission de modifier cette annonce.")
        return redirect('detail_voiture', voiture_id=voiture_id)
    
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            prix = request.POST.get('prix')
            kilometrage = request.POST.get('kilometrage')
            description = request.POST.get('description')
            est_vendue = 'est_vendue' in request.POST  # Checkbox renvoie 'on' si cochée
            
            # Mettre à jour la voiture
            voiture.prix = prix
            voiture.kilometrage = kilometrage
            voiture.description = description
            voiture.est_vendue = est_vendue
            
            # Gestion de l'image
            if 'image' in request.FILES:
                voiture.image_principale = request.FILES['image']
            
            voiture.save()
            messages.success(request, 'Annonce mise à jour avec succès !')
            return redirect('detail_voiture', voiture_id=voiture.id)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la mise à jour : {str(e)}')
    
    context = {'voiture': voiture}
    return render(request, 'voitures/modifier_voiture.html', context)

@login_required
def supprimer_voiture(request, voiture_id):
    """Supprimer une voiture existante"""
    voiture = get_object_or_404(Voiture, id=voiture_id)
    
    # Vérifier que l'utilisateur est le propriétaire
    if voiture.vendeur != request.user:
        messages.error(request, "Vous n'avez pas la permission de supprimer cette annonce.")
        return redirect('detail_voiture', voiture_id=voiture_id)
    
    if request.method == 'POST':
        try:
            voiture.delete()
            messages.success(request, 'Annonce supprimée avec succès !')
            return redirect('mes_voitures')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression : {str(e)}')
    
    # Si GET, afficher la page de confirmation
    context = {'voiture': voiture}
    return render(request, 'voitures/supprimer_voiture.html', context)

@login_required
def toggle_favori(request, voiture_id):
    """Ajouter/retirer une voiture des favoris"""
    voiture = get_object_or_404(Voiture, id=voiture_id)
    
    # Vérifier si déjà en favori
    favori, created = Favori.objects.get_or_create(
        utilisateur=request.user,
        voiture=voiture
    )
    
    if not created:
        favori.delete()
        messages.info(request, 'Voiture retirée des favoris.')
    else:
        messages.success(request, 'Voiture ajoutée aux favoris.')
    
    return redirect('detail_voiture', voiture_id=voiture_id)

@login_required
def acheter_voiture(request, voiture_id):
    """Processus d'achat d'une voiture"""
    voiture = get_object_or_404(Voiture, id=voiture_id, est_vendue=False)
    
    if request.user == voiture.vendeur:
        messages.error(request, 'Vous ne pouvez pas acheter votre propre voiture.')
        return redirect('detail_voiture', voiture_id=voiture_id)
    
    if request.method == 'POST':
        try:
            # Création de la transaction
            transaction = Transaction.objects.create(
                voiture=voiture,
                acheteur=request.user,
                vendeur=voiture.vendeur,
                prix_final=voiture.prix,
                statut='en_attente'
            )
            
            # Marquer la voiture comme vendue
            voiture.est_vendue = True
            voiture.save()
            
            messages.success(request, 
                'Votre demande d\'achat a été envoyée au vendeur. '
                'Il vous contactera pour finaliser la transaction.'
            )
            return redirect('mes_achats')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'achat : {str(e)}')
    
    context = {'voiture': voiture}
    return render(request, 'voitures/acheter_voiture.html', context)

@login_required
def mes_voitures(request):
    """Liste des voitures de l'utilisateur"""
    voitures = Voiture.objects.filter(vendeur=request.user).order_by('-date_ajout')
    
    # Calcul des statistiques
    voitures_en_vente = voitures.filter(est_vendue=False).count()
    voitures_vendues = voitures.filter(est_vendue=True).count()
    total_favoris = Favori.objects.filter(voiture__vendeur=request.user).count()
    
    context = {
        'voitures': voitures,
        'voitures_en_vente': voitures_en_vente,
        'voitures_vendues': voitures_vendues,
        'total_favoris': total_favoris,
    }
    return render(request, 'voitures/mes_voitures.html', context)

@login_required
def mes_favoris(request):
    """Liste des favoris de l'utilisateur"""
    favoris = Favori.objects.filter(utilisateur=request.user).select_related(
        'voiture__modele__marque'
    ).order_by('-date_ajout')
    
    context = {'favoris': favoris}
    return render(request, 'voitures/mes_favoris.html', context)

@login_required
def mes_achats(request):
    """Historique des achats de l'utilisateur"""
    achats = Transaction.objects.filter(acheteur=request.user).select_related(
        'voiture__modele__marque', 'vendeur'
    ).order_by('-date_transaction')
    
    context = {'achats': achats}
    return render(request, 'voitures/mes_achats.html', context)

@login_required
def mes_ventes(request):
    """Historique des ventes de l'utilisateur"""
    ventes = Transaction.objects.filter(vendeur=request.user).select_related(
        'voiture__modele__marque', 'acheteur'
    ).order_by('-date_transaction')
    
    context = {'ventes': ventes}
    return render(request, 'voitures/mes_ventes.html', context)

@login_required
def confirmer_vente(request, transaction_id):
    """Confirmer une vente"""
    transaction = get_object_or_404(
        Transaction, 
        id=transaction_id, 
        vendeur=request.user,
        statut='en_attente'
    )
    
    transaction.statut = 'confirmee'
    transaction.save()
    
    messages.success(request, 'Vente confirmée avec succès !')
    return redirect('mes_ventes')

# ==================== VUES ADMIN UTILISATEURS ====================

@login_required
def dashboard(request):
    """Tableau de bord utilisateur"""
    if not request.user.is_staff:
        return redirect('accueil')
    
    # Statistiques pour l'admin
    total_utilisateurs = User.objects.count()
    total_voitures = Voiture.objects.count()
    total_transactions = Transaction.objects.count()
    chiffre_affaires = Transaction.objects.filter(
        statut__in=['confirmee', 'terminee']
    ).aggregate(Sum('prix_final'))['prix_final__sum'] or 0
    
    # Dernières transactions
    transactions_recentes = Transaction.objects.select_related(
        'voiture', 'acheteur', 'vendeur'
    ).order_by('-date_transaction')[:10]
    
    # Voitures récentes
    voitures_recentes = Voiture.objects.select_related(
        'modele__marque', 'vendeur'
    ).order_by('-date_ajout')[:10]
    
    context = {
        'total_utilisateurs': total_utilisateurs,
        'total_voitures': total_voitures,
        'total_transactions': total_transactions,
        'chiffre_affaires': chiffre_affaires,
        'transactions_recentes': transactions_recentes,
        'voitures_recentes': voitures_recentes,
    }
    return render(request, 'admin/dashboard.html', context)

# ==================== VUES D'ERREUR ====================

def handler404(request, exception):
    """Page 404 personnalisée"""
    return render(request, 'voitures/404.html', status=404)

def handler500(request):
    """Page 500 personnalisée"""
    return render(request, 'voitures/500.html', status=500)

# ==================== VUE DE TEST ====================

def test(request):
    """Page de test pour vérifier le fonctionnement"""
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Django</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            .success { color: green; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <h1>Test de l'application Django</h1>
        <h2>Statut : <span class="success">✓ EN COURS</span></h2>
        <ul>
            <li>Serveur Django : ✓ Opérationnel</li>
            <li>Base de données : ✓ Connectée</li>
            <li>Templates : ✓ Chargés</li>
            <li>URLs : ✓ Configurées</li>
        </ul>
        <p><a href="/">Retour à l'accueil</a></p>
    </body>
    </html>
    """)