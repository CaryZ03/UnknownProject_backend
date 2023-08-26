import json

from django.db.models import *
from user.models import User
from team.models import TeamMember


class ChatMessage(Model):
    cm_id = AutoField(primary_key=True)
    cm_from = ForeignKey(User, on_delete=SET_NULL)
    cm_content = TextField()
    cm_create_time = DateTimeField(auto_now_add=True)
    cm_isat = BooleanField(default=False)
    cm_at_all = BooleanField(default=False)
    cm_at = ManyToManyField(TeamMember, on_delete=SET_NULL)



class Notification(Model):
    notification_id = AutoField(primary_key=True)
    notification_name = CharField(max_length=100)
    notification_content = TextField(null=True)
    notification_create_time = DateTimeField(auto_now_add=True)
    notification_creator = ForeignKey(TeamMember, on_delete=SET_NULL, null=True)
    notification_receiver = ManyToManyField(User)
