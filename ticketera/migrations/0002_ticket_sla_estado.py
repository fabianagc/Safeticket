# Generated by Django 4.2 on 2025-05-04 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketera', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='sla_estado',
            field=models.CharField(choices=[('Sla en regla', 'Sla en regla'), ('Sla vencido', 'Sla vencido')], default='Cumple', max_length=35),
        ),
    ]
