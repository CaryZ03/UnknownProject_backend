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


@csrf_exempt
@require_http_methods(['POST'])
def get_team_members_and_permissions(request):
    data = json.loads(request.body)
    team_id = data.get('team_id')
    tm_user_id = data.get('tm_user_id')

    team = Team.objects.get(team_id=team_id)
    user = User.objects.get(user_id=tm_user_id)
    tm_user = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)

    members_info = []
    is_creator_or_manager = False

    for member in team.team_member.all():
        member_info = {
            'tm_user_id': member.tm_user_id.user_id,
            'tm_user_nickname': member.tm_user_nickname,
        }
        members_info.append(member_info)

    if tm_user.tm_user_permissions in ['creator', 'manager']:
        is_creator_or_manager = True

    response_data = {
        'members': members_info,
        'is_creator_or_manager': is_creator_or_manager
    }

    return JsonResponse(response_data)


@csrf_exempt
@require_http_methods(['POST'])
def get_teams_for_user(request):
    data = json.loads(request.body)
    tm_user_id = data.get('tm_user_id')
    user = User.objects.get(user_id=tm_user_id)

    teams_info = []

    for team_member in TeamMember.objects.filter(tm_user_id=user):
        team_info = {
            'team_id': team_member.tm_team_id.team_id
        }
        teams_info.append(team_info)

    return JsonResponse({'teams': teams_info})

