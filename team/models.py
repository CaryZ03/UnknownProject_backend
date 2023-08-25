from django.db.models import *
from user.models import User
from project.models import Project


class Team(Model):
    team_id = AutoField(primary_key=True)
    team_name = CharField(max_length=100)
    team_description = TextField(null=True)
    team_avatar = ImageField(upload_to='avatar/', max_length=225, blank=True, null=True)
    team_tel = TextField(null=True)
    team_create_time = DateTimeField(null=True)
    team_creator = ForeignKey(User, on_delete=SET_NULL, null=True)
    team_projects = ManyToManyField(Project)
    # team_chats = ManyToManyField(Chat, )

    # def to_json(self):
    #     info = {
    #         "team_id": self.team_id,
    #         "team_name": self.team_name,
    #         "team_password": self.team_password,
    #         "team_signature": self.team_signature,
    #         "team_email": self.team_email,
    #         "team_company": self.team_company,
    #         "team_tel": self.team_tel,
    #         "team_status": self.team_status
    #     }
    #     return json.dumps(info)


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


class Chat(Model):
    chat_id = AutoField(primary_key=True)
    chat_name = CharField(max_length=100)
    chat_signature = TextField(null=True)
    chat_avatar = ImageField(upload_to='avatar/', max_length=225, blank=True, null=True)
    chat_tel = TextField(null=True)
    chat_creator = ForeignKey(User, on_delete=SET_NULL, null=True)
    chat_admins = ManyToManyField(User, related_name='chat_admins')
    chat_members = ManyToManyField(User, related_name='chat_members')
    chat_projects = ManyToManyField(Project)
