# Generated by Django 4.2.4 on 2023-08-31 14:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0006_remove_document_document_project'),
        ('project', '0003_remove_project_project_document_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='project_recycle_bin',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recycle_directory', to='document.directory'),
        ),
    ]
