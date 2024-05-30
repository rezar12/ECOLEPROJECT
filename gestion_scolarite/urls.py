from django.urls import path
from .views import voir_facture, effectifs_annee_scolaire_courante, effectif_total, solde_ok, montant_total

urlpatterns = [
    # Autres URL...
    path('voir_facture/<int:scolarite_id>/', voir_facture, name='voir_facture'),
    path('effectifs-annee-scolaire/', effectifs_annee_scolaire_courante, name='effectifs_annee_scolaire_courante'),
    path('effectif-total/',effectif_total,name="effectif_total"),
    path('solde/',solde_ok,name="solde"),
    path('montant_total/',montant_total,name="montant_total"),
]
