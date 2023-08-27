from django.shortcuts import render
import os
import re
import secrets
import json
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http.response import JsonResponse
from datetime import timedelta
from user.models import User, UserToken
from team.models import Team, TeamMember, TeamApplicant
import base64
from django.core.files.base import ContentFile
from user.views import login_required, not_login_required


@require_http_methods(['POST'])
def get_team_members_and_permissions(request):
    data = json.loads(request.body)
    team_id = data.get('team_id')
    tm_user_id = data.get('tm_user_id')

    team = Team.objects.get(team_id=team_id)
    user = TeamMember.objects.get(team_id=team_id, tm_user_id=tm_user_id)

    members_info = []
    is_creator_or_manager = False

    for member in team.team_member.all():
        member_info = {
            'tm_user_id': member.tm_user_id,
            'tm_user_nickname': member.tm_user_nickname,
        }
        members_info.append(member_info)

    if user.permission_choices in ['creator', 'manager']:
        is_creator_or_manager = True

    response_data = {
        'members': members_info,
        'is_creator_or_manager': is_creator_or_manager,
    }

    return JsonResponse(response_data)
