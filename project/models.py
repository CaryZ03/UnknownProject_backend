import json

from django.db.models import *
from user.models import User
from team.models import TeamMember, Team


class Project(Model):
    project_id = AutoField(primary_key=True)
    project_name = CharField(max_length=100)
    project_description = TextField(null=True)
    project_avatar = ImageField(upload_to='avatar/', max_length=225, blank=True, null=True)
    project_create_time = DateTimeField(auto_now_add=True, null=True)
    project_creator = ForeignKey(TeamMember, on_delete=SET_NULL, null=True)
    project_complete_date = DateTimeField(null=True)
    project_editable = BooleanField(default=True)
    project_team = ForeignKey(Team, on_delete=CASCADE, null=False)

    def to_json(self):
        info = {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "project_description": self.project_description,
            "project_create_time": self.project_create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "project_creator": self.project_creator.tm_user_nickname if self.project_creator else None,
            "project_complete_date": self.project_complete_date.strftime("%Y-%m-%d %H:%M:%S")
            if self.project_complete_date else None,
        }
        return json.dumps(info)


class Requirement(Model):
    requirement_id = AutoField(primary_key=True)
    requirement_name = CharField(max_length=100)
    requirement_description = TextField(null=True)
    requirement_create_time = DateTimeField(auto_now_add=True)
    requirement_creator = ForeignKey(TeamMember, on_delete=SET_NULL, null=True)
    requirement_members = ManyToManyField(TeamMember, related_name='requirement_members')
    requirement_complete_time = DateTimeField(null=True)
    # status_choices = (
    #     ('', "创建者"),
    #     ('manager', "管理员"),
    #     ('member', "成员")
    # )
    # tm_user_permissions = CharField(max_length=20, choices=permission_choices, default='member')

    def to_json(self):
        info = {
            "requirement_id": self.requirement_id,
            "requirement_name": self.requirement_name,
            "requirement_description": self.requirement_description,
            "requirement_create_time": self.requirement_create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "requirement_creator": self.requirement_creator.tm_user_nickname if self.requirement_creator else None,
            "requirement_complete_date": self.requirement_complete_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.requirement_complete_time else None,
        }
        return json.dumps(info)
