# Generated by Django 4.2.4 on 2023-08-25 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0007_alter_team_team_create_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="team",
            name="team_create_time",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
