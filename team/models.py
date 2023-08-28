import json

from django.db.models import *
from user.models import User
from django.utils.timezone import now


class Team(Model):
    team_id = AutoField(primary_key=True)
    team_key = CharField(max_length=200, null=True)
    team_key_expire_time = DateTimeField(null=True, auto_now_add=True)
    team_name = CharField(max_length=100)
    team_description = TextField(null=True)
    team_avatar = ImageField(upload_to='avatar/team/', max_length=225, blank=True, null=True)
    team_tel = TextField(null=True)
    team_create_time = DateTimeField(null=True, auto_now_add=True)
    team_creator = ForeignKey(User, on_delete=SET_NULL, null=True)
    team_member = ManyToManyField('TeamMember')
    team_projects = ManyToManyField('project.Project')
    team_chat = ForeignKey('TeamChat', on_delete=SET_NULL, null=True)
    team_applicants = ManyToManyField('TeamApplicant')

    def to_json(self):
        info = {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "team_description": self.team_description,
            "team_tel": self.team_tel,
            "team_create_time": self.team_create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "team_creator": self.team_creator.user_name,
            "team_avatar": self.team_avatar.url if self.team_avatar else None,
        }
        return json.dumps(info, ensure_ascii=False)


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
    tm_user_join_time = DateTimeField(null=True, auto_now_add=True)

    class Meta:
        unique_together = ['tm_team_id', 'tm_user_id']


class TeamApplicant(Model):
    ta_team_id = ForeignKey(Team, on_delete=CASCADE, null=False)
    ta_user_id = ForeignKey(User, on_delete=CASCADE, null=False)
    ta_apply_time = DateTimeField(null=True, auto_now_add=True)
    ta_message = CharField(max_length=100, null=True)

    def to_json(self):
        info = {

            "user_id": self.ta_user_id.user_id,
            "user_name": self.ta_user_id.user_name,
            "message": self.ta_message,
            "apply_time": self.ta_apply_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return json.dumps(info, ensure_ascii=False)

    class Meta:
        unique_together = ['ta_team_id', 'ta_user_id']


class TeamChat(Model):
    tc_id = AutoField(primary_key=True)
    tc_team = ForeignKey(Team, on_delete=CASCADE, null=True)
    tc_history = ManyToManyField('message.ChatMessage')


class PrivateChat(Model):
    pc_id = AutoField(primary_key=True)
    pc_members = ManyToManyField(User)
    pc_history = ManyToManyField('message.ChatMessage')
