# Generated by Django 3.1.14 on 2024-02-26 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_scolarite', '0002_auto_20240226_1313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scolarite',
            name='montant_total',
        ),
        migrations.AddField(
            model_name='classe',
            name='montant_scolarité',
            field=models.BigIntegerField(default=1),
            preserve_default=False,
        ),
    ]
