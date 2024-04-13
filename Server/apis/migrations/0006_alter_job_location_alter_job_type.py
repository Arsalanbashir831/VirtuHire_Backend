# Generated by Django 4.2.7 on 2024-04-07 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0005_job_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='location',
            field=models.CharField(blank=True, choices=[('Remote', 'remote'), ('On Site', 'onsite')], max_length=100),
        ),
        migrations.AlterField(
            model_name='job',
            name='type',
            field=models.CharField(blank=True, choices=[('Full Time', 'full_time'), ('Part Time', 'part_time'), ('Contract', 'contract'), ('Freelance', 'freelance')], max_length=100),
        ),
    ]
