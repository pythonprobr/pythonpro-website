# Generated by Django 3.2.11 on 2022-03-09 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_become_pythonista'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, help_text='WhatsApp', max_length=20, null=True),
        ),
    ]
