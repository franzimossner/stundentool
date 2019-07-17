# Generated by Django 2.0.13 on 2019-07-11 19:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datainput', '0010_auto_20190709_1013'),
    ]

    operations = [
        migrations.CreateModel(
            name='OptimierungsErgebnis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Zeit', models.DateTimeField()),
            ],
        ),
        migrations.RemoveField(
            model_name='lehreinheit',
            name='Klassenstundenplan',
        ),
        migrations.RemoveField(
            model_name='lehreinheit',
            name='Lehrerstundenplan',
        ),
        migrations.AddField(
            model_name='lehreinheit',
            name='Klasse',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='datainput.Schulklasse'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lehreinheit',
            name='Lehrer',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='datainput.Lehrer'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='vorgabeeinheit',
            unique_together={('Schulklasse', 'Fach', 'Zeitslot')},
        ),
        migrations.AddField(
            model_name='lehreinheit',
            name='run',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='datainput.OptimierungsErgebnis'),
            preserve_default=False,
        ),
    ]