# Generated by Django 4.2.7 on 2024-04-13 05:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0013_rename_score_appliedjobs_avg_score_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appliedjobs',
            name='avg_score',
        ),
        migrations.RemoveField(
            model_name='appliedjobs',
            name='description_score',
        ),
        migrations.RemoveField(
            model_name='appliedjobs',
            name='domain_score',
        ),
        migrations.RemoveField(
            model_name='appliedjobs',
            name='education_score',
        ),
        migrations.RemoveField(
            model_name='appliedjobs',
            name='experience_score',
        ),
        migrations.RemoveField(
            model_name='appliedjobs',
            name='skills_score',
        ),
    ]
