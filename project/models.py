import json

from django.db.models import *
from user.models import User
from team.models import TeamMember, Team


class Project(Model):
    project_id = AutoField(primary_key=True)
    project_name = CharField(max_length=100)
    project_description = TextField(null=True)
    project_avatar = ImageField(upload_to='avatar/project/', max_length=225, blank=True, null=True)
    project_create_time = DateTimeField(auto_now_add=True, null=True)
    project_estimated_start_time = DateTimeField(null=True)
    project_estimated_end_time = DateTimeField(null=True)
    project_end_time = DateTimeField(null=True)
    project_start_time = DateTimeField(null=True)
    project_creator = ForeignKey(TeamMember, on_delete=SET_NULL, null=True)
    project_editable = BooleanField(default=True)
    project_team = ForeignKey(Team, on_delete=CASCADE, null=True)
    status_choices = (
        ('not_started', "未开始"),
        ('doing', "进行中"),
        ('finished', "已完成")
    )
    project_status = CharField(max_length=20, choices=status_choices, default='not_started')
    project_recycle = BooleanField(default=False)
    project_requirement = ManyToManyField('Requirement')
    project_prototype = ManyToManyField('document.Prototype')
    project_document = ManyToManyField('document.Document')

    def to_json(self):
        info = {
            "project_id": self.project_id,
            "name": self.project_name,
            "project_description": self.project_description,
            "date": self.project_create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "person": self.project_creator.tm_user_nickname if self.project_creator else None,
            "project_estimated_start_time": self.project_estimated_start_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.project_estimated_start_time else None,
            "project_estimated_end_time": self.project_estimated_end_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.project_estimated_end_time else None,
            "project_start_time": self.project_start_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.project_start_time else None,
            "project_end_time": self.project_end_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.project_end_time else None,
            "project_team": self.project_team.team_id,
            "editable": self.project_editable,
            "project_team": self.project_team.team_name,
        }
        return json.dumps(info, ensure_ascii=False)


class Requirement(Model):
    requirement_id = AutoField(primary_key=True)
    requirement_name = CharField(max_length=100)
    requirement_creator = ForeignKey(TeamMember, on_delete=SET_NULL, null=True)
    requirement_create_time = DateTimeField(auto_now_add=True, null=True)
    requirement_estimated_start_time = DateTimeField(null=True)
    requirement_estimated_end_time = DateTimeField(null=True)
    requirement_end_time = DateTimeField(null=True)
    requirement_start_time = DateTimeField(null=True)
    requirement_project = ForeignKey(Project, on_delete=CASCADE, null=True)
    status_choices = (
        ('not_started', "未开始"),
        ('doing', "进行中"),
        ('finished', "已完成")
    )
    requirement_status = CharField(max_length=20, choices=status_choices, default='not_started')

    def to_json(self):
        info = {
            "requirement_id": self.requirement_id,
            "name": self.requirement_name,
            "person": self.requirement_creator.tm_user_nickname if self.requirement_creator else None,
            "requirement_create_time": self.requirement_create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "startTime": self.requirement_estimated_start_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.requirement_estimated_start_time else None,
            "endTime": self.requirement_estimated_end_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.requirement_estimated_end_time else None,
            "requirement_end_time": self.requirement_end_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.requirement_end_time else None,
            "requirement_start_time": self.requirement_start_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.requirement_start_time else None,
            "status": self.requirement_status,
        }
        return json.dumps(info, ensure_ascii=False)
