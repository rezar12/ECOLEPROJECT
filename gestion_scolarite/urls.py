from django.urls import path
from .views import voir_facture

urlpatterns = [
    # Autres URL...
    path('voir_facture/<int:scolarite_id>/', voir_facture, name='voir_facture'),
]
