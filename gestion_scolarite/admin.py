from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Classe,Eleve,Enseignant,Scolarite,Versement,AnneeScolaire,Inscription,ArticlesInscription
from .forms import VersementForm
import openpyxl
from django.http import HttpResponse
from .widgets import DatalistWidget, DatalistWiget2
from django import forms

class VersementInline(admin.TabularInline):
    model = Versement
    form = VersementForm
    extra = 0 # Nombre de formulaires vierges supplémentaires à afficher
    max_num = 6
    can_delete = True
    
 # Widget pour la selection des élèves   
class InscriptionAdminForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = '__all__'
        widgets = {
            'eleve': DatalistWidget(attrs={'list': 'eleve_datalist'}),
        }
        
# widget pour la selection des inscripts pour la scolarité        
class ScolariteAdminForm(forms.ModelForm):
    class Meta:
        model = Scolarite
        fields = '__all__'
        widgets = {
            'inscription': DatalistWiget2(attrs={'list': 'inscription_datalist'}),
        }

# widget pour la selection des inscripts pour les article d'inscription
class ArticleInscriptionAdminForm(forms.ModelForm):
    
    class Meta:
        model = ArticlesInscription
        fields = '__all__'
        widgets = {
            'inscription': DatalistWiget2(attrs={'list': 'inscription_datalist'}),
        }


# methode pour exporter la liste des élèves d'une classe
def export_eleves_xlsx(modeladmin, request, queryset):
    """
    Action pour exporter les élèves d'une ou plusieurs classes sélectionnées au format XLSX.
    """
    # Créer un classeur et une feuille de calcul
    classe_selected = queryset[0]
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Liste des élèves'
    

    # Définir les en-têtes
    headers = ['Nom', 'Prénom', 'Date de naissance', 'Sexe', 'Numéro du père', 'Numéro de la mère']
    sheet.append(headers)

    # Boucle sur les classes sélectionnées
    for classe in queryset:
        inscriptions = Inscription.objects.filter(classe=classe).order_by("eleve__nom")
        for inscription in inscriptions:
            eleve = inscription.eleve
            sheet.append([eleve.nom, eleve.prenom, eleve.date_naissance, eleve.sexe, eleve.numero_pere, eleve.numero_mere])

    # Créer une réponse HTTP avec le type de contenu XLSX
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=liste des eleves {classe_selected}.xlsx'
    
    # Enregistrer le fichier dans la réponse
    workbook.save(response)
    
    return response

export_eleves_xlsx.short_description = "Exporter la liste des élèves (XLSX)"

@admin.register(AnneeScolaire)
class admin_annee_scolaire(admin.ModelAdmin):
    list_display = ('annee_scolaire','annee_debut','annee_fin')
    
@admin.register(Eleve)
class admin_eleve(admin.ModelAdmin):
    list_display = ('nom','prenom','matricule','date_naissance','sexe','numero_pere','numero_mere')
    search_fields = ['nom_eleve', 'prenom_eleve','matricule']

@admin.register(Classe)
class admin_classe(admin.ModelAdmin):
    list_display = ('nom','annee_scolaire','Effectif_classe','montant_scolarité')
    search_fields = ['nom', 'annee_scolaire']
    actions = [export_eleves_xlsx]
    
@admin.register(Enseignant)
class admin_enseignant(admin.ModelAdmin):
    list_display = ('nom_enseignant','prenom_enseignant','classe','sexe','numero_telephone')

@admin.register(Inscription)
class admin_inscription(admin.ModelAdmin):
    form = InscriptionAdminForm
    list_display = ('eleve','classe','annee_scolaire_inscription','date_inscription')
    search_fields = ['eleve__nom','date_inscription']

@admin.register(Scolarite)
class ScolariteAdmin(admin.ModelAdmin):
    actions = ['voir_reçu']
    form = ScolariteAdminForm
    inlines = [VersementInline]
    
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
    search_fields = ['scolarite__inscription__eleve__nom','scolarite__inscription__eleve__prenom','date_paiement']
    
@admin.register(ArticlesInscription)
class admin_ArticlesInscription(admin.ModelAdmin):
    forms = ArticleInscriptionAdminForm
    list_display = ('inscription','carte_de_retraite','boite_de_craie','macarons','tricot','releve_des_notes','ramette')
    search_fields = ['inscription__eleve__nom', 'inscription__eleve__prenom','inscription__classe__nom','inscription__annee_scolaire_inscription__annee_scolaire']