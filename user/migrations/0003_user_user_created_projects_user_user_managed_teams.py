# Generated by Django 4.2 on 2023-08-25 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0002_alter_project_project_members"),
        ("team", "0004_rename_chat_creator_chat_chat_owner_and_more"),
        ("user", "0002_remove_user_user_company_user_user_created_teams_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="user_created_projects",
            field=models.ManyToManyField(to="project.project"),
        ),
        migrations.AddField(
            model_name="user",
            name="user_managed_teams",
            field=models.ManyToManyField(
                related_name="managed_by_users", to="team.team"
            ),
        ),
    ]
