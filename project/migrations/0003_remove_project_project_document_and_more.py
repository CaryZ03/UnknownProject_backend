# Generated by Django 4.2.4 on 2023-08-31 14:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0004_remove_document_document_project_directory_and_more'),
        ('project', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='project_document',
        ),
        migrations.AddField(
            model_name='project',
            name='project_directory',
            field=models.ManyToManyField(related_name='normal_directory', to='document.directory'),
        ),
        migrations.AddField(
            model_name='project',
            name='project_root_directory',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='root_directory', to='document.directory'),
        ),
    ]
