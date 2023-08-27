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
from user.models import *
from team.models import *
from message.models import *
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


@csrf_exempt
@require_http_methods(['POST'])
def store_message(request):
    data = json.loads(request.body)
    message = data.get('message')
    user_id = data.get('user_id')
    team_id = data.get('team_id')
    is_at = data.get('is_at')
    is_at_all = data.get('is_at_all')
    array_data = data.get('array_data', [])

    user = User.objects.get(user_id=user_id)
    team = Team.objects.get(team_id=team_id)
    team_chat = team.team_chat
    history = team_chat.tc_history

    if is_at:
        new_chat_message = ChatMessage.objects.create(cm_from=user, cm_content=message, cm_isat=is_at)
        for at_id in array_data:
            at_user = User.objects.get(user_id=at_id)
            at_team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=at_user)
            new_chat_message.cm_at.add(at_team_member)
    elif is_at_all:
        new_chat_message = ChatMessage.objects.create(cm_from=user, cm_content=message, cm_at_all=is_at_all)
    else:
        new_chat_message = ChatMessage.objects.create(cm_from=user, cm_content=message)
    new_chat_message.save()
    history.add(new_chat_message)
    team_chat.save()
    return JsonResponse({'errno': 0, 'msg': "插入消息成功"})


@csrf_exempt
@require_http_methods(['POST'])
def get_team_chat_history(request, team_id):
    team = Team.objects.get(team_id=team_id)
    team_chat = team.team_chat
    chat_messages = team_chat.tc_history.all().order_by('cm_create_time')

    message_list = []
    for message in chat_messages:
        message_info = {
            "message": message.cm_content,
            "user_id": message.cm_from.user_id,
            "cm_create_time": message.cm_create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_at": message.cm_isat,
            "is_at_all": message.cm_at_all,
            "array_data": [member.tm_user_id.user_id for member in message.cm_at.all()]
        }
        message_list.append(message_info)

    return JsonResponse({"chat_history": message_list})

