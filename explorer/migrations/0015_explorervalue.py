# Generated by Django 4.2.8 on 2024-04-25 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0014_promptlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExplorerValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(choices=[('UUID', 'Install Unique ID'), ('SMLS', 'Startup metric last send')], max_length=5)),
                ('value', models.TextField(blank=True, null=True)),
            ],
        ),
    ]