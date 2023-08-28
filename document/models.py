import json

from django.db.models import *
from user.models import User
from team.models import TeamMember


class SavedDocument(Model):
    sd_id = AutoField(primary_key=True)
    sd_document = ForeignKey('Document', on_delete=CASCADE)
    sd_file = FileField(upload_to='SavedDocument/', max_length=255, null=True)
    sd_saved_time = DateTimeField(auto_now_add=True)

    def to_json(self):
        info = {
            "sd_id": self.sd_id,
            "sd_file": self.sd_file.url,
            "sd_saved_time": self.sd_saved_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return json.dumps(info)


class Document(Model):
    document_id = AutoField(primary_key=True)
    document_name = CharField(max_length=100)
    document_team = ForeignKey('team.Team', on_delete=CASCADE, null=True)
    document_allowed_editors = ManyToManyField('user.User')
    document_saves = ManyToManyField(SavedDocument)

    def to_json(self):
        info = {
            "document_id": self.document_id,
            "document_name": self.document_name,
            "document_team": self.document_team,
            "document_allowed_editors": self.document_allowed_editors,
        }
        return json.dumps(info)


class File(Model):
    file_id = AutoField(primary_key=True)
    file_content = FileField(upload_to='file/', max_length=255, null=True)


class Prototype(Model):
    prototype_id = AutoField(primary_key=True)
    prototype_name = CharField(max_length=100)
    prototype_team = ForeignKey('team.Team', on_delete=CASCADE)
    prototype_creator = ForeignKey('user.User', on_delete=CASCADE)
    prototype_file = FileField(upload_to='prototype/', max_length=255)
