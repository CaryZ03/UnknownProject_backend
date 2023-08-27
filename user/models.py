import json

from django.db.models import *


class User(Model):
    user_id = AutoField(primary_key=True)
    user_name = CharField(max_length=100, null=True)
    user_real_name = CharField(max_length=100, null=True)
    user_password = CharField(max_length=20)
    user_signature = TextField(null=True)
    user_avatar = ImageField(upload_to='avatar/user/', max_length=225, blank=True, null=True)
    user_email = EmailField(max_length=50, default=None, blank=True, null=False)
    user_tel = TextField(null=True)
    user_expire_time = IntegerField(null=True, default=2880)
    user_created_teams = ManyToManyField('team.Team', related_name='created_by_users')
    user_managed_teams = ManyToManyField('team.Team', related_name='managed_by_users')
    user_joined_teams = ManyToManyField('team.Team', related_name='joined_by_users')
    user_created_projects = ManyToManyField('project.Project')
    user_visible = BooleanField(default=True)
    user_notification_list = ManyToManyField('message.Notification')

    def to_json(self):
        info = {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_real_name": self.user_real_name,
            "user_signature": self.user_signature,
            "user_avatar": self.user_avatar.url if self.user_avatar else None,
            "user_email": self.user_email,
            "user_tel": self.user_tel
        }
        return json.dumps(info)


class UserToken(Model):
    key = CharField(max_length=200, unique=True)
    user = ForeignKey(User, on_delete=CASCADE)
    expire_time = DateTimeField(null=True)
