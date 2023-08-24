from django.db.models import *
from user.models import User


class Team(Model):
    team_id = AutoField(primary_key=True)
    team_name = CharField(max_length=100)
    team_signature = TextField(null=True)
    team_avatar = ImageField(upload_to='avatar/', max_length=225, blank=True, null=True)
    team_tel = TextField(null=True)
    team_members = ManyToManyField(User)
    # team_created_teams = ManyToManyField(Questionnaire, related_name='created_by_teams')
    # team_joined_teams = ManyToManyField(Questionnaire, related_name='created_by_teams')
    # team_created_projects = ManyToManyField(Questionnaire, related_name='created_by_teams')

    # def to_json(self):
    #     info = {
    #         "team_id": self.team_id,
    #         "team_name": self.team_name,
    #         "team_password": self.team_password,
    #         "team_signature": self.team_signature,
    #         "team_email": self.team_email,
    #         "team_company": self.team_company,
    #         "team_tel": self.team_tel,
    #         "team_status": self.team_status
    #     }
    #     return json.dumps(info)