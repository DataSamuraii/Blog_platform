# Generated by Django 4.2.6 on 2023-11-19 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_alter_category_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='date_scheduled',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='date_published',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
