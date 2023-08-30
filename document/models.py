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
        return json.dumps(info, ensure_ascii=False)


class Document(Model):
    document_id = AutoField(primary_key=True)
    document_name = CharField(max_length=100)
    document_project = ForeignKey('project.project', on_delete=CASCADE, null=True)
    document_allowed_editors = ManyToManyField('user.User')
    document_saves = ManyToManyField(SavedDocument)
    document_create_time = DateTimeField(null=True, auto_now_add=True)
    document_recycle = BooleanField(default=False)
    document_editable = BooleanField(default=False)

    def to_json(self):
        info = {
            "document_id": self.document_id,
            "name": self.document_name,
            "document_team": self.document_team,
            "document_allowed_editors": self.document_allowed_editors,
            "size": self.document_saves.last().size(),
            "lastChangeTime": self.document_saves.last().sd_saved_time.strftime("%Y-%m-%d %H:%M:%S"),
            "editable": self.document_editable,
            "save_id": self.document_saves.last().sd_id
        }
        return json.dumps(info, ensure_ascii=False)


class File(Model):
    file_id = AutoField(primary_key=True)
    file_content = FileField(upload_to='file/', max_length=255, null=True)


class Prototype(Model):
    prototype_id = AutoField(primary_key=True)
    prototype_name = CharField(max_length=100)
    prototype_project = ForeignKey('project.project', on_delete=CASCADE, null=True)
    prototype_creator = ForeignKey('team.TeamMember', on_delete=CASCADE)
    prototype_file = FileField(upload_to='prototype/', max_length=255)
    prototype_create_time = DateTimeField(null=True, auto_now_add=True)
    prototype_change_time = DateTimeField(null=True)
    prototype_recycle = BooleanField(default=False)

    def to_json(self):
        info = {
            "prototype_id": self.prototype_id,
            "name": self.prototype_name,
            "prototype_project": self.prototype_project.project_id,
            "prototype_creator": self.prototype_creator.tm_user_nickname,
            "lastChangeTime": self.prototype_change_time,
            "createTime": self.prototype_create_time,
            "size": self.prototype_file.size()
        }
        return json.dumps(info, ensure_ascii=False)
