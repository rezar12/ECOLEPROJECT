# Generated by Django 3.1.14 on 2024-02-28 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_scolarite', '0003_auto_20240226_2159'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='Boite_de_Craie',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='inscription',
            name='Carte_de_retraite',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inscription',
            name='Marcarons',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='inscription',
            name='Ramette',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='inscription',
            name='Relevet_des_notes',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='inscription',
            name='Tricot',
            field=models.BooleanField(default=True),
        ),
    ]
