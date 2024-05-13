from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from .models import Classe,Eleve,Enseignant,Scolarite,Versement,AnneeScolaire,Inscription,ArticlesInscription



@admin.register(AnneeScolaire)
class admin_annee_scolaire(admin.ModelAdmin):
    list_display = ('annee_scolaire','annee_debut','annee_fin')
    
@admin.register(Eleve)
class admin_eleve(admin.ModelAdmin):
    list_display = ('nom','prenom','date_naissance','sexe','numero_pere','numero_mere')
    search_fields = ['nom_eleve', 'prenom_eleve']

@admin.register(Classe)
class admin_classe(admin.ModelAdmin):
    list_display = ('nom','annee_scolaire','Effectif_classe','montant_scolarité')
    search_fields = ['nom', 'annee_scolaire']
    
@admin.register(Enseignant)
class admin_enseignant(admin.ModelAdmin):
    list_display = ('nom_enseignant','prenom_enseignant','classe','sexe','numero_telephone')

@admin.register(Inscription)
class admin_inscription(admin.ModelAdmin):
    list_display = ('eleve','classe','annee_scolaire_inscription','date_inscription')
    search_fields = ['eleve__nom','date_inscription']

@admin.register(Scolarite)
class ScolariteAdmin(admin.ModelAdmin):
    actions = ['voir_reçu']
    
    list_display = ('inscription', 'montant_total', 'reste_a_payer')
    search_fields = ['inscription__eleve__nom', 'inscription__eleve__prenom','inscription__classe__nom','inscription__annee_scolaire_inscription__annee_scolaire']
    
    def montant_total(self,x):
        return x.inscription.classe.montant_scolarité

    def voir_reçu(self, request, queryset):
        for scolarite in queryset:
            url = reverse('voir_facture', args=[scolarite.id])
            return HttpResponseRedirect(url)
        self.message_user(request, "Redirection vers la facture effectuée.")

    voir_reçu.short_description = "Voir Reçu"
        
    
    
    
@admin.register(Versement)
class admin_versement(admin.ModelAdmin):
    list_display = ('montant','date_paiement','scolarite')
    
@admin.register(ArticlesInscription)
class admin_ArticlesInscription(admin.ModelAdmin):
    list_display = ('inscription','carte_de_retraite','boite_de_craie','macarons','tricot','releve_des_notes','ramette')
    search_fields = ['inscription__eleve__nom', 'inscription__eleve__prenom','inscription__classe__nom','inscription__annee_scolaire_inscription__annee_scolaire']