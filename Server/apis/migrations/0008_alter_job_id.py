# Generated by Django 4.2.7 on 2024-04-08 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0007_appliedjobs_predicteddomain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]