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
from document.models import *
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
            'team_id': team_member.tm_team_id.team_id,
            'team_name': team_member.tm_team_id.team_name
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
    message_type = data.get('message_type')
    array_data = data.get('array_data', [])
    private_connect_id = data.get('private_connect_id', 0)
    user = User.objects.get(user_id=user_id)
    team = Team.objects.get(team_id=team_id)
    team_chat = team.team_chat
    history = team_chat.tc_history

    if is_at:
        new_chat_message = ChatMessage.objects.create(cm_from=user, cm_content=message, cm_isat=is_at,
                                                      cm_type=message_type, cm_private_connect_id=private_connect_id)
        for at_id in array_data:
            at_user = User.objects.get(user_id=at_id)
            at_team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=at_user)
            new_chat_message.cm_at.add(at_team_member)
    elif is_at_all:
        new_chat_message = ChatMessage.objects.create(cm_from=user, cm_content=message, cm_at_all=is_at_all,
                                                      cm_type=message_type, cm_private_connect_id=private_connect_id)
    else:
        new_chat_message = ChatMessage.objects.create(cm_from=user, cm_content=message, cm_type=message_type,
                                                      cm_private_connect_id=private_connect_id)

    if message_type == 'file':
        file_id = data.get('file_id')
        file = File.objects.get(file_id=file_id)
        new_chat_message.cm_file = file
    new_chat_message.save()
    history.add(new_chat_message)
    team_chat.save()
    return JsonResponse({'cm_id': new_chat_message.cm_id, 'msg': "插入消息成功"})


@csrf_exempt
@require_http_methods(['POST'])
def get_team_chat_history(request):
    data = json.loads(request.body)
    team_id = data.get('team_id')
    team = Team.objects.get(team_id=team_id)
    team_chat = team.team_chat
    chat_messages = team_chat.tc_history.all().order_by('cm_create_time')

    message_list = []
    for message in chat_messages:
        if message.cm_type == 'file':
            file_id = message.cm_file.file_id
        else:
            file_id = 0
        message_info = {
            "cm_id": message.cm_id,
            "message": message.cm_content,
            "user_id": message.cm_from.user_id,
            "user_name": message.cm_from.user_name,
            "cm_create_time": message.cm_create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_at": message.cm_isat,
            "is_at_all": message.cm_at_all,
            "message_type": message.cm_type,
            "file_id": file_id,
            "private_connect_id": message.cm_private_connect_id,
            "array_data": [member.tm_user_id.user_id for member in message.cm_at.all()]
        }
        message_list.append(message_info)

    return JsonResponse({"chat_history": message_list})


@csrf_exempt
@require_http_methods(['POST'])
def search_chat_message(request):
    data = json.loads(request.body)
    tm_user_id = data.get('tm_user_id')
    search_info = data.get('search_info')
    user = User.objects.get(user_id=tm_user_id)

    search_res = []

    for team_member in TeamMember.objects.filter(tm_user_id=user):
        team = team_member.tm_team_id
        team_chat = team.team_chat
        chat_messages = team_chat.tc_history.all().order_by('cm_create_time')
        for message in chat_messages:
            message_content = message.cm_content
            if search_info.lower() in message_content.lower():
                if message.cm_type == 'file':
                    file_id = message.cm_file.file_id
                else:
                    file_id = 0
                message_info = {
                    "team_id": team.team_id,
                    "cm_id": message.cm_id,
                    "message_content": message_content,
                    "message_type": message.cm_type,
                    "message_sender_id": message.cm_from.user_id,
                    "message_sender_name": message.cm_from.user_name,
                    "create_time": message.cm_create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "is_at": message.cm_isat,
                    "is_at_all": message.cm_at_all,
                    "file_id": file_id,
                    "private_connect_id": message.cm_private_connect_id,
                    "array_data": [member.tm_user_id.user_id for member in message.cm_at.all()]
                }

                search_res.append(message_info)

    return JsonResponse({'search_res': search_res})


@csrf_exempt
@require_http_methods(['POST'])
def create_private_chat(request):
    data = json.loads(request.body)
    user1_id = data.get('user1_id')
    user1 = User.objects.get(user_id=user1_id)
    user2_id = data.get('user2_id')
    user2 = User.objects.get(user_id=user2_id)
    team_id = data.get('team_id')
    team = Team.objects.get(team_id=team_id)
    team_member1 = TeamMember.objects.get(tm_user_id=user1, tm_team_id=team)
    team_member2 = TeamMember.objects.get(tm_user_id=user2, tm_team_id=team)
    private_chats1 = PrivateChat.objects.filter(pc_members=team_member1)
    private_chats2 = PrivateChat.objects.filter(pc_members=team_member2)
    common_chats = private_chats1.intersection(private_chats2)
    if common_chats.exists():
        return JsonResponse({'msg': '已有私聊，创建私聊失败'})
    else:
        new_private_chat = PrivateChat.objects.create()
        new_private_chat.pc_members.add(team_member1)
        new_private_chat.pc_members.add(team_member2)
        new_private_chat.save()

    return JsonResponse({'msg': "创建私聊成功"})


@csrf_exempt
@require_http_methods(['POST'])
def acquire_private_chat(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')
    user = User.objects.get(user_id=user_id)
    private_chats_info = []
    for team_member in TeamMember.objects.filter(tm_user_id=user):
        private_chats = PrivateChat.objects.filter(pc_members=team_member)
        for pc in private_chats:
            pc_members = pc.pc_members.all()
            for pc_member in pc_members:
                if pc_member != team_member:
                    private_chat_info = {
                        'pc_id': pc.pc_id,
                        'opposite_id': pc_member.tm_user_id.user_id,
                        'opposite_name': pc_member.tm_user_id.user_name
                    }
                    private_chats_info.append(private_chat_info)

    return JsonResponse({'private_chats_info': private_chats_info})


@csrf_exempt
@require_http_methods(['POST'])
def store_private_message(request):
    data = json.loads(request.body)
    message = data.get('message')
    user_id = data.get('user_id')
    pc_id = data.get('pc_id')
    message_type = data.get('message_type')

    user = User.objects.get(user_id=user_id)
    pc = PrivateChat.objects.get(pc_id=pc_id)
    history = pc.pc_history

    new_chat_message = ChatMessage.objects.create(cm_from=user, cm_content=message, cm_type=message_type)

    if message_type == 'file':
        file_id = data.get('file_id')
        file = File.objects.get(file_id=file_id)
        new_chat_message.cm_file = file
    new_chat_message.save()
    history.add(new_chat_message)
    pc.save()
    return JsonResponse({'cm_id': new_chat_message.cm_id, 'msg': "插入消息成功"})


@csrf_exempt
@require_http_methods(['POST'])
def get_private_chat_history(request):
    data = json.loads(request.body)
    pc_id = data.get('pc_id')
    pc = PrivateChat.objects.get(pc_id=pc_id)
    chat_messages = pc.pc_history.all().order_by('cm_create_time')

    message_list = []
    for message in chat_messages:
        if message.cm_type == 'file':
            file_id = message.cm_file.file_id
        else:
            file_id = 0
        message_info = {
            "cm_id": message.cm_id,
            "message": message.cm_content,
            "user_id": message.cm_from.user_id,
            "user_name": message.cm_from.user_name,
            "cm_create_time": message.cm_create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "message_type": message.cm_type,
            "file_id": file_id,
        }
        message_list.append(message_info)

    return JsonResponse({"chat_history": message_list})


@csrf_exempt
@require_http_methods(['POST'])
def create_group_chat(request):
    data = json.loads(request.body)
    creator_id = data.get('creator_id')
    creator = User.objects.get(user_id=creator_id)
    users_id = data.get('users_id', [])
    team_id = data.get('team_id')
    team = Team.objects.get(team_id=team_id)
    team_member_creator = TeamMember.objects.get(tm_user_id=creator, tm_team_id=team)
    new_group_chat = GroupChat.objects.create(gc_creator=team_member_creator)
    for user_id in users_id:
        joiner = User.objects.get(user_id=user_id)
        team_member_joiner = TeamMember.objects.get(tm_user_id=joiner, tm_team_id=team)
        new_group_chat.gc_members.add(team_member_joiner)
    new_group_chat.save()

    return JsonResponse({'msg': "创建群聊成功"})


@csrf_exempt
@require_http_methods(['POST'])
def acquire_group_chat(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')
    user = User.objects.get(user_id=user_id)
    group_chats_info_creator = []
    group_chats_info_joiner = []
    for team_member in TeamMember.objects.filter(tm_user_id=user):
        join_group_chats = GroupChat.objects.filter(gc_members=team_member)
        for jgc in join_group_chats:
            jgc_info = {
                'gc_id': jgc.gc_id,
                'gc_name': jgc.gc_name
            }
            group_chats_info_joiner.append(jgc_info)
        create_group_chats = GroupChat.objects.filter(gc_creator=team_member)
        for cgc in create_group_chats:
            cgc_info = {
                'gc_id': cgc.gc_id,
                'gc_name': cgc.gc_name
            }
            group_chats_info_creator.append(cgc_info)

    return JsonResponse({'group_chats_info_creator': group_chats_info_creator,
                         'group_chats_info_joiner': group_chats_info_joiner})


@csrf_exempt
@require_http_methods(['POST'])
def store_group_message(request):
    data = json.loads(request.body)
    message = data.get('message')
    user_id = data.get('user_id')
    gc_id = data.get('gc_id')
    is_at = data.get('is_at')
    is_at_all = data.get('is_at_all')
    message_type = data.get('message_type')
    array_data = data.get('array_data', [])
    user = User.objects.get(user_id=user_id)
    gc = GroupChat.objects.get(gc_id=gc_id)
    team = gc.gc_team
    history = gc.gc_history

    if is_at:
        new_chat_message = ChatMessage.objects.create(cm_from=user, cm_content=message, cm_isat=is_at, cm_type=message_type)
        for at_id in array_data:
            at_user = User.objects.get(user_id=at_id)
            at_team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=at_user)
            new_chat_message.cm_at.add(at_team_member)
    elif is_at_all:
        new_chat_message = ChatMessage.objects.create(cm_from=user, cm_content=message, cm_at_all=is_at_all, cm_type=message_type)
    else:
        new_chat_message = ChatMessage.objects.create(cm_from=user, cm_content=message, cm_type=message_type)

    if message_type == 'file':
        file_id = data.get('file_id')
        file = File.objects.get(file_id=file_id)
        new_chat_message.cm_file = file
    new_chat_message.save()
    history.add(new_chat_message)
    gc.save()
    return JsonResponse({'cm_id': new_chat_message.cm_id, 'msg': "插入消息成功"})


@csrf_exempt
@require_http_methods(['POST'])
def get_group_chat_history(request):
    data = json.loads(request.body)
    gc_id = data.get('gc_id')
    gc = GroupChat.objects.get(gc_id=gc_id)
    chat_messages = gc.gc_history.all().order_by('cm_create_time')

    message_list = []
    for message in chat_messages:
        if message.cm_type == 'file':
            file_id = message.cm_file.file_id
        else:
            file_id = 0
        message_info = {
            "cm_id": message.cm_id,
            "message": message.cm_content,
            "user_id": message.cm_from.user_id,
            "user_name": message.cm_from.user_name,
            "cm_create_time": message.cm_create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_at": message.cm_isat,
            "is_at_all": message.cm_at_all,
            "message_type": message.cm_type,
            "file_id": file_id,
            "array_data": [member.tm_user_id.user_id for member in message.cm_at.all()]
        }
        message_list.append(message_info)

    return JsonResponse({"chat_history": message_list})
