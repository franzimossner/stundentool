# Generated by Django 2.0.13 on 2019-07-09 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datainput', '0007_lehrer_tandem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lehrer',
            name='Tandem',
            field=models.CharField(choices=[(1, 'Ja'), (0, 'Nein')], default='Ja', max_length=10),
        ),
    ]