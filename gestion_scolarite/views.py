from django.shortcuts import render
from .models import Scolarite

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
    }

    return render(request, 'voir_facture.html', context)

