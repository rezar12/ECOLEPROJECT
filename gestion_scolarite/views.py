from django.http import JsonResponse
from django.shortcuts import render
from .models import Scolarite, AnneeScolaire,Classe,Versement
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db.models import Sum, F, ExpressionWrapper, DecimalField


date_courante = now().date().year
annee_scolaire_get = f'{date_courante}-{date_courante+1}'
# lié a une action de consultation des factures
@login_required(login_url="/admin")
def voir_facture(request, scolarite_id):
    scolarite = Scolarite.objects.get(id=scolarite_id)

    # Récupérez toutes les données nécessaires pour la facture
    montant_verse = sum(v.montant for v in scolarite.versement_set.all())
    reste_a_payer = scolarite.reste_a_payer()
    date_inscription = scolarite.inscription.date_inscription
    eleve = scolarite.inscription.eleve
    classe = scolarite.inscription.classe
    annee_scolaire = scolarite.inscription.annee_scolaire_inscription
    montant_scolarite = scolarite.inscription.classe.montant_scolarité
    versements = scolarite.versement_set.all()

    context = {
        'montant_verse': montant_verse,
        'reste_a_payer': reste_a_payer,
        'date_inscription': date_inscription,
        'eleve': eleve,
        'classe': classe,
        'annee_scolaire': annee_scolaire,
        'montant_scolarite':montant_scolarite,
        'versements':versements,
        'title':f'{eleve} {classe} {now().date()}',
        'date_emission':f'{now().date().strftime("%d/%m/%Y")} à {now().time().strftime("%H:%M")}'
    }

    return render(request, 'voir_facture.html', context)

@login_required(login_url="/admin")
def effectifs_annee_scolaire_courante(request):

    try:
        # Récupérer l'année scolaire corespondante
        annee_scolaire = AnneeScolaire.objects.get(annee_scolaire=annee_scolaire_get)
    except AnneeScolaire.DoesNotExist:
        return JsonResponse({'error': 'Année scolaire courante non trouvée'}, status=404)
    # Récupérer les effectifs de toutes les classes pour cette année scolaire
    effectifs_classes = {
        classe.nom: classe.Effectif_classe for classe in Classe.objects.filter(annee_scolaire=annee_scolaire)
    }

    # Préparer les données à retourner en JSON
    data = {
        # 'annee_scolaire': {
        #     'debut': annee_scolaire.annee_debut.strftime('%Y-%m-%d'),
        #     'fin': annee_scolaire.annee_fin.strftime('%Y-%m-%d'),
        # },
        'effectifs_classes': effectifs_classes
    }

    return JsonResponse(data)


@login_required(login_url="/admin")
def effectif_total(request):

    
    try:
        # Récupérer l'année scolaire corespondante
        annee_scolaire = AnneeScolaire.objects.get(annee_scolaire=annee_scolaire_get)
    except AnneeScolaire.DoesNotExist:
        return JsonResponse({'error': 'Année scolaire courante non trouvée'}, status=404)
    effectif_total = Classe.objects.filter(annee_scolaire=annee_scolaire).aggregate(total=Sum('Effectif_classe'))['total']

    data = {
        "effectif_total": effectif_total if effectif_total is not None else 0
    }
    return JsonResponse(data)

@login_required(login_url="/admin")
def solde_ok(request):
    # Annoter les instances de Scolarite avec le total des versements
    try: 
         annee_scolaire = AnneeScolaire.objects.get(annee_scolaire=annee_scolaire_get)
    except AnneeScolaire.DoesNotExist:
        return JsonResponse({'error': 'Année scolaire courante non trouvée'}, status=404)
    inscriptions_soldes = Scolarite.objects.filter(
        inscription__annee_scolaire_inscription=annee_scolaire
    ).annotate(
        total_versements=Sum('versement__montant')
    ).filter(
        total_versements__gte=F('inscription__classe__montant_scolarité')
    ).count()
    return JsonResponse({'inscriptions_soldes': inscriptions_soldes})

@login_required(login_url="/admin")
def montant_total(request):
    try: 
         annee_scolaire = AnneeScolaire.objects.get(annee_scolaire=annee_scolaire_get)
    except AnneeScolaire.DoesNotExist:
        return JsonResponse({'error': 'Année scolaire courante non trouvée'}, status=404)
    
    total_versements = Versement.objects.filter(
        scolarite__inscription__annee_scolaire_inscription=annee_scolaire
    ).aggregate(total=Sum('montant'))['total'] or 0
    return JsonResponse({'total_versements': total_versements})