# Generated by Django 4.2.7 on 2024-04-07 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0003_job_job_document'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='description',
            new_name='experience',
        ),
        migrations.RenameField(
            model_name='job',
            old_name='address',
            new_name='title',
        ),
        migrations.RemoveField(
            model_name='job',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='job',
            name='job_title',
        ),
        migrations.RemoveField(
            model_name='job',
            name='start_date',
        ),
        migrations.AddField(
            model_name='job',
            name='postedDate',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='job',
            name='responsibilities',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='skills',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='type',
            field=models.CharField(blank=True, choices=[('full_time', 'Full Time'), ('part_time', 'Part Time'), ('contract', 'Contract'), ('freelance', 'Freelance')], max_length=100),
        ),
    ]