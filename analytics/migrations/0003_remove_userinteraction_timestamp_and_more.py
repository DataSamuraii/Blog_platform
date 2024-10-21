# Generated by Django 4.2.6 on 2023-12-06 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0002_userinteraction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinteraction',
            name='timestamp',
        ),
        migrations.AddField(
            model_name='visitorgeodata',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='visitorgeodata',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]