from typing import Any
from django.forms.renderers import BaseRenderer
from django.forms.widgets import Input
from django.utils.safestring import SafeText, mark_safe
from .models import Eleve, Inscription
from django.utils.timezone import now

class DatalistWidget(Input):
    input_type = 'text'

    def render(self, name, value, attrs=None, renderer=None):
        datalist = '<datalist id="eleve_datalist" style="height: 100px; overflow-y: auto;" size="5">'
        for eleve in Eleve.objects.all():
            if eleve.matricule:
                datalist += f'<option value="{eleve.pk}">{eleve.nom} {eleve.prenom} ({eleve.matricule})</option>'
            else:
                datalist += f'<option value="{eleve.pk}">{eleve.nom} {eleve.prenom} ({eleve.matricule})</option>'
        datalist += '</datalist>'

        input_html = super().render(name, value, attrs, renderer)
        return mark_safe(f'{input_html}{datalist}')


# make a widget for scolarity select inscription eleve
class DatalistWiget2(Input):
    input_type = 'text'
    
    def render(self, name, value, attrs=None, renderer=None):
        datalist = '<datalist id="inscription_datalist" style="height: 100px; overflow-y: auto;" size="5">'
        for inscription in Inscription.objects.filter(date_inscription__year=now().date().year):
            datalist += f'<option value="{inscription.pk}">{inscription.eleve.nom} {inscription.eleve.prenom} {inscription.classe}</option>'
        datalist+='</datalist>'
        input_html = super().render(name, value, attrs, renderer)
        return mark_safe(f'{input_html}{datalist}')