# Generated by Django 2.0.13 on 2019-07-09 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datainput', '0008_auto_20190709_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lehrer',
            name='Tandem',
            field=models.CharField(choices=[(1, 1), (0, 0)], default=1, max_length=10),
        ),
    ]
