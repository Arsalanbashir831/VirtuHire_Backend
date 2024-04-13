# Generated by Django 4.2.7 on 2024-04-13 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0012_rename_candidate_id_appliedjobs_candidate_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appliedjobs',
            old_name='score',
            new_name='avg_score',
        ),
        migrations.RemoveField(
            model_name='appliedjobs',
            name='predictedDomain',
        ),
        migrations.AddField(
            model_name='appliedjobs',
            name='description_score',
            field=models.FloatField(blank=True, default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appliedjobs',
            name='domain_score',
            field=models.FloatField(blank=True, default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appliedjobs',
            name='education_score',
            field=models.FloatField(blank=True, default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appliedjobs',
            name='experience_score',
            field=models.FloatField(blank=True, default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appliedjobs',
            name='skills_score',
            field=models.FloatField(blank=True, default=None),
            preserve_default=False,
        ),
    ]
