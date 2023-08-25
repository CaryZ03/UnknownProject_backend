import json

from django.db.models import *
from user.models import User


class Team(Model):
    team_id = AutoField(primary_key=True)
    team_key = CharField(max_length=200, null=True)
    team_key_expire_time = DateTimeField(null=True)
    team_name = CharField(max_length=100)
    team_description = TextField(null=True)
    team_avatar = ImageField(upload_to='avatar/', max_length=225, blank=True, null=True)
    team_tel = TextField(null=True)
    team_create_time = DateTimeField(null=True)
    team_creator = ForeignKey(User, on_delete=SET_NULL, null=True)
    team_member = ManyToManyField('TeamMember')
    team_projects = ManyToManyField('project.Project')
    team_chats = ManyToManyField('Chat')
    team_applicants = ManyToManyField('TeamApplicant')

    def to_json(self):
        info = {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "team_description": self.team_description,
            "team_tel": self.team_tel,
            "team_create_time": self.team_create_time,
            "team_creator": self.team_creator,
        }
        return json.dumps(info)


class TeamMember(Model):
    tm_team_id = ForeignKey(Team, on_delete=CASCADE, null=False)
    tm_user_id = ForeignKey(User, on_delete=CASCADE, null=False)
    tm_user_nickname = CharField(max_length=100)
    permission_choices = (
        ('creator', "创建者"),
        ('manager', "管理员"),
        ('member', "成员")
    )
    tm_user_permissions = CharField(max_length=20, choices=permission_choices, default='member')
    tm_user_join_time = DateTimeField(null=True)

    class Meta:
        unique_together = ['tm_team_id', 'tm_user_id']


class TeamApplicant(Model):
    ta_team_id = ForeignKey(Team, on_delete=CASCADE, null=False)
    ta_user_id = ForeignKey(User, on_delete=CASCADE, null=False)
    ta_apply_time = DateTimeField(null=True)
    ta_message = CharField(max_length=100)

    class Meta:
        unique_together = ['ta_team_id', 'ta_user_id']


class Chat(Model):
    chat_id = AutoField(primary_key=True)
    chat_name = CharField(max_length=100)
    chat_avatar = ImageField(upload_to='avatar/', max_length=225, blank=True, null=True)
    chat_owner = ForeignKey(User, on_delete=SET_NULL, null=True)
    chat_admins = ManyToManyField(TeamMember, related_name='chat_admins')
    chat_members = ManyToManyField(TeamMember, related_name='chat_members')
