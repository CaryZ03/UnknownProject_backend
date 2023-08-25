from django.db.models import *
from user.models import User


class Project(Model):
    project_id = AutoField(primary_key=True)
    project_name = CharField(max_length=100)
    project_description = TextField(null=True)
    project_avatar = ImageField(upload_to='avatar/', max_length=225, blank=True, null=True)
    project_create_time = DateTimeField(null=True)
    project_creator = ForeignKey(User, on_delete=SET_NULL, null=True)
    project_members = ManyToManyField(User, related_name='project_members')
    permission_choices = (
        ('creator', "创建者"),
        ('manager', "管理员"),
        ('member', "成员")
    )
    tm_user_permissions = CharField(max_length=20, choices=permission_choices, default='member')

    # def to_json(self):
    #     info = {
    #         "project_id": self.project_id,
    #         "project_name": self.project_name,
    #         "project_password": self.project_password,
    #         "project_signature": self.project_signature,
    #         "project_email": self.project_email,
    #         "project_company": self.project_company,
    #         "project_tel": self.project_tel,
    #         "project_status": self.project_status
    #     }
    #     return json.dumps(info)