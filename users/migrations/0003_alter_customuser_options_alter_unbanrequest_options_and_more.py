# Generated by Django 4.2.6 on 2023-11-17 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_unbanrequest'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='unbanrequest',
            options={'ordering': ['id']},
        ),
        migrations.AddField(
            model_name='customuser',
            name='bio',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='social_media',
            field=models.JSONField(default=dict),
        ),
    ]