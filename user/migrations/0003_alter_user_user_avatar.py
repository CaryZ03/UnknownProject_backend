# Generated by Django 4.2.4 on 2023-08-27 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_usertoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_avatar',
            field=models.ImageField(blank=True, max_length=225, null=True, upload_to='avatar/user/'),
        ),
    ]
