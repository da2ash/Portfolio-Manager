# Generated by Django 2.1.7 on 2019-03-03 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='dividend_rate',
            field=models.FloatField(default=10.0),
        ),
    ]
