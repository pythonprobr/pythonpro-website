# Generated by Django 4.1.1 on 2022-09-14 10:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('discord', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='discorduser',
            index=models.Index(fields=['-created_at'], name='discord_created_at_desc_index'),
        ),
    ]
