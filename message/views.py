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
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def send_(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    day = data_json.get('day')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2100, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2101, 'msg': "当前用户不在该团队内"})
    if team.team_key_expire_time <= now():
        team.team_key = secrets.token_urlsafe(50).replace('#', '')
        team.team_key_expire_time = now() + timedelta(days=day)
        team.save()
    return JsonResponse({'errno': 0, 'msg': team.team_key})


@csrf_exempt
def private_send_notification_to_user(request):
    data_json = json.loads(request.body)
    user_id = data_json.get('user_id')
    message = data_json.get('message')
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "user_notification_receiver_" + str(user_id),
        {
            "type": "send.notification",
            "message": message
        }
    )
    return JsonResponse({'errno': 0, 'msg': "hihi"})


@csrf_exempt
def send_notification_to_user(user_id, notification):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "user_notification_receiver_" + str(user_id),
        {
            "type": "send.notification",
            "notification": notification.to_json()
        }
    )
    return JsonResponse({'errno': 0, 'msg': "hihi"})


@csrf_exempt
@require_http_methods(['POST'])
def group_send_notification_to_user(request):
    data_json = json.loads(request.body)
    notification = data_json.get('notification')
    name = notification.get('name')
    content = notification.get('content')
    creator = notification.get('creator')
    type = notification.get('type')
    receiver_list = data_json.get('receiver_list')
    for user_id in receiver_list:
        notification = Notification.objects.create(name=name, content=content, creator=creator)
        notification.notification_receiver.add(User.objects.get(user_id=user_id))
        send_notification_to_user(user_id, notification)

    return JsonResponse({'errno': 0, 'msg': "hihi"})

