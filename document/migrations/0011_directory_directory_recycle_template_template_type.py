# Generated by Django 4.2.4 on 2023-09-01 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0010_alter_saveddocument_sd_file_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='directory',
            name='directory_recycle',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='template',
            name='template_type',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
