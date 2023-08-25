import json

from django.db.models import *
from user.models import User
from team.models import TeamMember


class Document(Model):
    document_id = AutoField(primary_key=True)
    document_name = CharField(max_length=100)
    document_description = TextField(null=True)
    document_avatar = ImageField(upload_to='avatar/', max_length=225, blank=True, null=True)
    document_create_time = DateTimeField(auto_now_add=True)
    document_creator = ForeignKey(TeamMember, on_delete=SET_NULL, null=True)
    document_editors = ManyToManyField(Editor, related_name='document_members')
    document_complete_date = DateTimeField(null=True)

    def to_json(self):
        info = {
            "document_id": self.document_id,
            "document_name": self.document_name,
            "document_description": self.document_description,
            "document_create_time": self.document_create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "document_creator": self.document_creator.tm_user_nickname if self.document_creator else None,
            "document_complete_date": self.document_complete_date.strftime("%Y-%m-%d %H:%M:%S")
            if self.document_complete_date else None,
        }
        return json.dumps(info)


class Editor(Model):
    editor_id = AutoField(primary_key=True)
    editor_name = CharField(max_length=100)
    editor_description = TextField(null=True)
    editor_avatar = ImageField(upload_to='avatar/', max_length=225, blank=True, null=True)
    editor_create_time = DateTimeField(auto_now_add=True)
    editor_creator = ForeignKey(TeamMember, on_delete=SET_NULL, null=True)
    editor_editors = ManyToManyField(Editor, related_name='editor_members')
    editor_complete_date = DateTimeField(null=True)

    def to_json(self):
        info = {
            "editor_id": self.editor_id,
            "editor_name": self.editor_name,
            "editor_description": self.editor_description,
            "editor_create_time": self.editor_create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "editor_creator": self.editor_creator.tm_user_nickname if self.editor_creator else None,
            "editor_complete_date": self.editor_complete_date.strftime("%Y-%m-%d %H:%M:%S")
            if self.editor_complete_date else None,
        }
        return json.dumps(info)
