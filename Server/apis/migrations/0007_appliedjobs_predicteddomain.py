# Generated by Django 4.2.7 on 2024-04-08 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0006_alter_job_location_alter_job_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='appliedjobs',
            name='predictedDomain',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
