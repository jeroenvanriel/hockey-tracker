# Generated by Django 3.2.13 on 2023-03-19 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0013_rename_training_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='type',
            field=models.TextField(default='training'),
        ),
    ]
