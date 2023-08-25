import json

from django.db.models import *
from user.models import User
from team.models import TeamMember


class ChatMessage(Model):
    cm_id = AutoField(primary_key=True)
    cm_from = ForeignKey(User, on_delete=SET_NULL)
    cm_content = TextField()
    cm_create_time = DateTimeField(auto_now_add=True)


class Notification(Model):
    notification_id = AutoField(primary_key=True)
    notification_name = CharField(max_length=100)
    notification_content = TextField(null=True)
    notification_create_time = DateTimeField(auto_now_add=True)
    notification_creator = ForeignKey(TeamMember, on_delete=SET_NULL, null=True)
    notification_editors = ManyToManyField('Editor', related_name='notification_members')
    notification_complete_date = DateTimeField(null=True)

    def to_json(self):
        info = {
            "notification_id": self.notification_id,
            "notification_name": self.notification_name,
            "notification_create_time": self.notification_create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "notification_creator": self.notification_creator.tm_user_nickname if self.notification_creator else None,
            "notification_complete_date": self.notification_complete_date.strftime("%Y-%m-%d %H:%M:%S")
            if self.notification_complete_date else None,
        }
        return json.dumps(info)
