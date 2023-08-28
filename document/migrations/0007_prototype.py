# Generated by Django 4.2.4 on 2023-08-28 11:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_user_user_notification_list'),
        ('team', '0013_remove_teamchat_tc_name'),
        ('document', '0006_saveddocument_sd_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='Prototype',
            fields=[
                ('prototype_id', models.AutoField(primary_key=True, serialize=False)),
                ('prototype_name', models.CharField(max_length=100)),
                ('prototype_file', models.FileField(max_length=255, upload_to='prototype/')),
                ('prototype_creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
                ('prototype_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='team.team')),
            ],
        ),
    ]
