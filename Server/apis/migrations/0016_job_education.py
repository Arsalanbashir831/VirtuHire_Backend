# Generated by Django 4.2.7 on 2024-04-13 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0015_appliedjobs_avg_score_appliedjobs_description_score_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='education',
            field=models.TextField(blank=True),
        ),
    ]
