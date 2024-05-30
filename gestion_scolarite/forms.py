# forms.py

from django import forms
from django.core.exceptions import ValidationError
from .models import Versement

class VersementForm(forms.ModelForm):
    class Meta:
        model = Versement
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        scolarite = cleaned_data.get("scolarite")
        date_paiement = cleaned_data.get("date_paiement")
        montant = cleaned_data.get("montant")

        # Obtient l'ID de l'instance en cours de modification (si applicable)
        versement_id = self.instance.id

        # Vérifie qu'un versement n'existe pas déjà pour la même date sauf pour l'instance actuelle
        if Versement.objects.filter(scolarite=scolarite, date_paiement=date_paiement).exclude(id=versement_id).exists():
            raise ValidationError("Un versement existe déjà pour cette date.")

        # Vérifie que le nombre de versements ne dépasse pas 6, en excluant l'instance actuelle
        if Versement.objects.filter(scolarite=scolarite).exclude(id=versement_id).count() >= 6:
            raise ValidationError("Le nombre de versements ne peut pas dépasser 6.")

        # Calcul du reste à payer
        reste_a_payer = scolarite.reste_a_payer()

        # Ajuste le reste à payer pour inclure le montant de l'instance actuelle si c'est une mise à jour
        if self.instance.pk:
            reste_a_payer += self.instance.montant

        if reste_a_payer == 0:
            raise ValidationError("La scolarité est déjà soldée. Aucun versement supplémentaire n'est nécessaire.")

        if montant > reste_a_payer:
            raise ValidationError(f"Le montant versé ({montant}) ne peut pas être supérieur au reste à payer ({reste_a_payer}).")

        return cleaned_data
    

