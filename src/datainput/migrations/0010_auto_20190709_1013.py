# Generated by Django 2.0.13 on 2019-07-09 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datainput', '0009_auto_20190709_1011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lehrer',
            name='Tandem',
            field=models.CharField(choices=[('1', 'Ja'), ('0', 'Nein')], default='1', max_length=10),
        ),
    ]
