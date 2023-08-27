import json

from django.db.models import *
from user.models import User
from team.models import TeamMember


class SavedDocument(Model):
    sd_id = AutoField(primary_key=True)
    sd_document = ForeignKey('Document', on_delete=CASCADE)
    sd_description = TextField(null=True)
    sd_saved_time = DateTimeField(auto_now_add=True)
    sd_creator = ForeignKey(TeamMember, on_delete=SET_NULL, null=True)
    # sd_content


class Document(Model):
    document_id = AutoField(primary_key=True)
    document_name = CharField(max_length=100)
    document_description = TextField(null=True)
    document_avatar = ImageField(upload_to='avatar/document/', max_length=225, blank=True, null=True)
    document_create_time = DateTimeField(auto_now_add=True)
    document_creator = ForeignKey(TeamMember, on_delete=SET_NULL, null=True)
    document_editors = ManyToManyField('Editor', related_name='document_members')
    document_complete_date = DateTimeField(null=True)
    document_saves = ManyToManyField(SavedDocument)

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
    editor_document = ForeignKey(Document, on_delete=CASCADE)
    editor_name = CharField(max_length=100)
    editor_current_position = IntegerField(default=0)
