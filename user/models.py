import json

from django.db.models import *


class User(Model):
    user_id = AutoField(primary_key=True)
    user_name = CharField(max_length=100, null=True)
    user_password = CharField(max_length=20)
    user_signature = TextField(null=True)
    user_avatar = ImageField(upload_to='avatar/', max_length=225, blank=True, null=True)
    user_email = EmailField(max_length=50, default=None, blank=True, null=False)
    user_tel = TextField(null=True)
    user_expire_time = IntegerField(null=True, default=30)
    user_created_teams = ManyToManyField('team.Team', related_name='created_by_users')
    user_joined_teams = ManyToManyField('team.Team', related_name='joined_by_users')
    # user_created_projects = ManyToManyField(Questionnaire, related_name='created_by_users')
    #
    # def to_json(self):
    #     info = {
    #         "user_id": self.user_id,
    #         "user_name": self.user_name,
    #         "user_password": self.user_password,
    #         "user_signature": self.user_signature,
    #         "user_email": self.user_email,
    #         "user_company": self.user_company,
    #         "user_tel": self.user_tel,
    #         "user_status": self.user_status
    #     }
    #     return json.dumps(info)

