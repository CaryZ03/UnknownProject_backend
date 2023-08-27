import json

from django.db.models import *
from user.models import User
from team.models import TeamMember


class ChatMessage(Model):
    cm_id = AutoField(primary_key=True)
    cm_from = ForeignKey(User, on_delete=SET_NULL, null=True)
    cm_content = TextField()
    cm_create_time = DateTimeField(auto_now_add=True)
    cm_isat = BooleanField(default=False)
    cm_at_all = BooleanField(default=False)
    cm_at = ManyToManyField(TeamMember)
    cm_type = CharField(max_length=100, default='message')


class Notification(Model):
    notification_id = AutoField(primary_key=True)
    notification_name = CharField(max_length=100)
    notification_content = TextField(null=True)
    notification_create_time = DateTimeField(auto_now_add=True)
    notification_creator = ForeignKey('user.User', on_delete=SET_NULL, null=True, related_name='creator')
    notification_receiver = ForeignKey('user.User', on_delete=SET_NULL, null=True, related_name='receiver')
    notification_type_choices = (
        ('at', "@信息"),
        ('application', "申请信息"),
        ('system', "系统信息")
    )
    notification_type = CharField(max_length=20, choices=notification_type_choices, default='system')

    def to_json(self):
        info = {
            "notification_id": self.notification_id,
            "notification_name": self.notification_name,
            "notification_content": self.notification_content,
            "notification_create_time": self.notification_create_time,
            "notification_creator": self.notification_creator,
            "notification_receiver": self.notification_receiver
        }
        return json.dumps(info)
