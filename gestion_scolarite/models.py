from django.db import models, transaction
from django.utils.text import slugify
from django.utils import timezone

# from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver

GENDER_CHOICES = [
    ("M", "Masculin"),
    ("F", "Féminin"),
]

NOM_CLASSE = [
    ("Maternelle", "Maternelle"),
    ("CP1", "CP1"),
    ("CP2", "CP2"),
    ("CE1", "CE1"),
    ("CE2", "CE2"),
    ("CM1", "CM1"),
    ("CM2", "CM2"),
    ("6 ème", "6 ème"),
    ("5 ème", "5 ème"),
    ("4 ème", "4 ème"),
    ("3 ème", "3 ème"),
    ("Seconde", "Seconde"),
    ("Première", "Première"),
    ("Terminale", "Terminale"),
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
        return f"{self.annee_debut.year}-{self.annee_fin.year}"

    def clean(self) -> None:
        if AnneeScolaire.objects.filter(
            annee_scolaire=f"{self.annee_debut.year}-{self.annee_fin.year}"
        ).exists():
            raise ValidationError(
                f"L'année scolaire {self.annee_debut.year}-{self.annee_fin.year} existe déjà."
            )


class Classe(models.Model):
    nom = models.CharField(max_length=255, choices=NOM_CLASSE, null=False, blank=False)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    Effectif_classe = models.IntegerField(default=0, editable=False)
    montant_scolarité = models.BigIntegerField(null=False, blank=False)

    def __str__(self) -> str:
        return f"{self.nom} / {self.annee_scolaire}"

    def clean(self) -> None:
        if Classe.objects.filter(
            nom=self.nom, annee_scolaire=self.annee_scolaire
        ).exists():
            raise ValidationError(
                f"Classe existe déjà pour cette année {self.annee_scolaire}"
            )


class Eleve(models.Model):
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    matricule = models.CharField(max_length=255, unique=True, blank=True, null=True)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=1, choices=GENDER_CHOICES)
    numero_pere = models.CharField(max_length=10)
    numero_mere = models.CharField(max_length=10)

    def __str__(self) -> str:
        return f"{self.nom} {self.prenom}"


class Inscription(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    annee_scolaire_inscription = models.ForeignKey(
        AnneeScolaire, on_delete=models.CASCADE
    )
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    date_inscription = models.DateField(default=timezone.now)

    def clean(self):
        if (
            Inscription.objects.filter(
                eleve=self.eleve,
                annee_scolaire_inscription=self.annee_scolaire_inscription,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("L'élève est déjà inscrit pour cette année scolaire.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            is_new = (
                self.pk is None
            )  # Vérifie si l'inscription est nouvelle ou mise à jour
            super().save(*args, **kwargs)

            if is_new:
                self.classe.Effectif_classe += 1
                self.classe.save()

    def delete(self, *args, **kwargs):
        # Pas besoin de décrémenter ici, cela sera fait par le signal
        super().delete(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.eleve.nom} {self.eleve.prenom} {self.classe.nom} {self.date_inscription}"


class Scolarite(models.Model):
    inscription = models.OneToOneField(Inscription, on_delete=models.CASCADE)

    def reste_a_payer(self):
        montant_scolarite = self.inscription.classe.montant_scolarité
        total_versements = (
            self.versement_set.aggregate(total=models.Sum("montant"))["total"] or 0
        )

        return max(0, montant_scolarite - total_versements)

    def __str__(self) -> str:
        return f"eleve : {self.inscription.eleve.nom} {self.inscription.eleve.prenom} incrit : {self.inscription.date_inscription} pour {self.inscription.classe}"


class Enseignant(models.Model):
    nom_enseignant = models.CharField(max_length=255)
    prenom_enseignant = models.CharField(max_length=255)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    sexe = models.CharField(max_length=1, choices=GENDER_CHOICES)
    numero_telephone = models.CharField(max_length=10)


class Versement(models.Model):
    montant = models.BigIntegerField(null=False, blank=False, default=0)
    date_paiement = models.DateField(default=timezone.now)
    scolarite = models.ForeignKey(Scolarite, on_delete=models.CASCADE)

    def get_numero_versement(self):
        # Obtient tous les versements pour la même scolarité, triés par date de paiement
        versements = Versement.objects.filter(scolarite=self.scolarite).order_by(
            "date_paiement", "id"
        )
        # Trouve la position de ce versement parmi tous les versements de la même scolarité
        for i, versement in enumerate(versements, start=1):
            if versement.id == self.id:
                return i
        return None

    def __str__(self) -> str:
        numero_versement = self.get_numero_versement()
        if numero_versement is not None:
            return f"versement {numero_versement}"
        return f"Versement sans numéro pour {self.scolarite}"


@receiver(pre_save, sender=Versement)
def validate_versement(sender, instance, **kwargs):
    if Versement.objects.filter(
        scolarite=instance.scolarite, date_paiement=instance.date_paiement
    ).exists():
        raise ValidationError("Un versement existe déjà pour cette date.")
    if Versement.objects.filter(scolarite=instance.scolarite).count() >= 6:
        raise ValidationError("Le nombre de versements ne peut pas dépasser 6.")
    if instance.scolarite.reste_a_payer() == 0:
        raise ValidationError(
            "La scolarité est déjà soldée. Aucun versement supplémentaire n'est nécessaire."
        )
    # Vérification : Le montant versé ne peut pas être supérieur au reste à payer ou au montant de scolarité.
    difference = instance.montant - instance.scolarite.reste_a_payer()
    if difference > 0:
        raise ValidationError(
            f"Le montant versé ({instance.montant}) ne peut pas être supérieur au reste à payer ({instance.scolarite.reste_a_payer()}). Différence: {difference}"
        )


class ArticlesInscription(models.Model):
    inscription = models.OneToOneField(
        Inscription,
        on_delete=models.CASCADE,
        unique=True,
        error_messages={
            "unique": "Il existe déjà un enregistrement d'articles pour cet élève.",
        },
    )
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
        for field in [
            "carte_de_retraite",
            "boite_de_craie",
            "macarons",
            "tricot",
            "releve_des_notes",
            "ramette",
        ]:
            if getattr(self, field):
                articles.append(field.replace("_", " "))
        return ", ".join(articles)
