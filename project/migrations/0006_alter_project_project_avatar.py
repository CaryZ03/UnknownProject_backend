# Generated by Django 4.2.4 on 2023-08-27 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "project",
            "0005_rename_project_complete_date_project_project_end_time_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="project_avatar",
            field=models.ImageField(
                blank=True, max_length=225, null=True, upload_to="avatar/project/"
            ),
        ),
    ]
