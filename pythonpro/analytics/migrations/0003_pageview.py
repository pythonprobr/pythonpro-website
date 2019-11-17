# Generated by Django 2.2.6 on 2019-11-17 14:35

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0002_usersession_uuid'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Criado em')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField()),
                ('session', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics.UserSession', verbose_name='sessão')),
            ],
            options={
                'verbose_name': 'page view',
                'verbose_name_plural': 'page views',
            },
        ),
    ]
