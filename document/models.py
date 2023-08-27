import json

from django.db.models import *
from user.models import User
from team.models import TeamMember


class SavedDocument(Model):
    sd_id = AutoField(primary_key=True)
    sd_document = ForeignKey('Document', on_delete=CASCADE)
    sd_saved_time = DateTimeField(auto_now_add=True)


class Document(Model):
    document_id = AutoField(primary_key=True)
    document_name = CharField(max_length=100)
    document_team = ForeignKey('team.Team', on_delete=CASCADE, null=True)
    document_allowed_editors = ManyToManyField('user.User')
    document_saves = ManyToManyField(SavedDocument)


class File(Model):
    file_id = AutoField(primary_key=True)
    file_content = FileField(upload_to='file/', max_length=255, null=True)
