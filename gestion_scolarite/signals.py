from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from .models import Inscription

@receiver(pre_delete, sender=Inscription)
def update_effectif_classe_on_delete(sender, instance, **kwargs):
    """
    Décrémente l'effectif de la classe lorsque l'inscription est supprimée.
    """
    if instance.classe:
        instance.classe.Effectif_classe -= 1
        instance.classe.save()
