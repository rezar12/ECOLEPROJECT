from django.db import models
from django.utils.text import slugify
from django.utils import timezone
#from django.db import models
from django.core.exceptions import ValidationError

GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ]
class AnneeScolaire(models.Model):
    annee_debut = models.DateField()
    annee_fin = models.DateField()
    annee_scolaire = models.SlugField(max_length=20, unique=True, editable=False)

    def save(self, *args, **kwargs):
        # Générer le slug en utilisant les valeurs de annee_debut et annee_fin
        self.annee_scolaire = slugify(f"{self.annee_debut.year}-{self.annee_fin.year}")
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f'{self.annee_debut.year}-{self.annee_fin.year}'

class Classe(models.Model):
    nom = models.CharField(max_length=255)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    Effectif_classe = models.IntegerField(default=0,editable=False)
    montant_scolarité = models.BigIntegerField(null=False,blank=False)
        
    def __str__(self) -> str:
        return f'{self.nom}/{self.annee_scolaire}'

class Eleve(models.Model):
    
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=1, choices=GENDER_CHOICES)
    numero_pere = models.CharField(max_length=10)
    numero_mere = models.CharField(max_length=10)
    
    def __str__(self) -> str:
        return f'{self.nom} {self.prenom}'

class Inscription(models.Model):
    
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    annee_scolaire_inscription = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    date_inscription = models.DateField(default=timezone.now)
 
    def clean(self):
        if Inscription.objects.filter(
            eleve=self.eleve,
            annee_scolaire_inscription=self.annee_scolaire_inscription,
        ).exists():
            raise ValidationError("L'élève est déjà inscrit pour cette année scolaire.")
        
        
    def save(self, *args, **kwargs):
        # Incrémenter Effectif_classe lorsqu'un nouvel élève est ajouté à une classe
        if self.classe:
            self.classe.Effectif_classe += 1
            self.classe.save()
            
            montant_scolarite_classe = self.classe.montant_scolarité
            
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if self.classe:
            self.classe.Effectif_classe -= 1
            self.classe.save()
        
        super().delete(*args, **kwargs)
        
    def __str__(self) -> str:
        return f'{self.eleve.nom} {self.eleve.prenom} {self.classe.nom} {self.date_inscription}'

class Scolarite(models.Model):
    inscription = models.OneToOneField(Inscription, on_delete=models.CASCADE)
    
    def reste_a_payer(self):
        montant_scolarite = self.inscription.classe.montant_scolarité
        total_versements = self.versement_set.aggregate(total=models.Sum('montant'))['total'] or 0

        return max(0, montant_scolarite - total_versements)
    
    def __str__(self) -> str:
        return f"eleve : {self.inscription.eleve.nom} {self.inscription.eleve.prenom} incrit : {self.inscription.date_inscription} pour l'annné : {self.inscription.annee_scolaire_inscription}"
    
class Enseignant(models.Model):
    nom_enseignant= models.CharField(max_length=255)
    prenom_enseignant= models.CharField(max_length=255)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    sexe = models.CharField(max_length=1, choices=GENDER_CHOICES)
    numero_telephone = models.CharField(max_length=10)
    

   
class Versement(models.Model):
    montant = models.BigIntegerField(null=False,blank=False)
    date_paiement = models.DateField(default=timezone.now)
    scolarite = models.ForeignKey(Scolarite, on_delete=models.CASCADE)

    def clean(self):
        if Versement.objects.filter(scolarite=self.scolarite, date_paiement=self.date_paiement).exists():
            raise ValidationError("Un versement existe déjà pour cette date.")
        if Versement.objects.filter(scolarite=self.scolarite).count() >= 6:
            raise ValidationError("Le nombre de versements ne peut pas dépasser 6.")
        if self.scolarite.reste_a_payer() == 0:
            raise ValidationError("La scolarité est déjà soldée. Aucun versement supplémentaire n'est nécessaire.")
        # Vérification : Le montant versé ne peut pas être supérieur au reste à payer ou au montant de scolarité.
        difference = self.montant - self.scolarite.reste_a_payer()
        if difference > 0:
            raise ValidationError(f"Le montant versé ({self.montant}) ne peut pas être supérieur au reste à payer ({self.scolarite.reste_a_payer()}). Différence: {difference}")
        
        
class ArticlesInscription(models.Model):
    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE)
    carte_de_retraite = models.BooleanField(default=False)
    boite_de_craie = models.BooleanField(default=True)
    macarons = models.BooleanField(default=True)
    tricot = models.BooleanField(default=True)
    releve_des_notes = models.BooleanField(default=True)
    ramette = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.inscription} - {self.get_articles_list()}"

    def get_articles_list(self):
        articles = []
        for field in ["carte_de_retraite", "boite_de_craie", "macarons", "tricot", "releve_des_notes", "ramette"]:
            if getattr(self, field):
                articles.append(field.replace("_", " "))
        return ", ".join(articles)