# Utiliser une image Python officielle
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de votre application
COPY . /app

# Installer les dépendances
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exposer le port de l'application
EXPOSE 8000

# Définir la commande par défaut
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "monprojet.wsgi:application"]
