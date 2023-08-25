import os
import re
import secrets

from django.db.models import Q
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http.response import JsonResponse
from datetime import timedelta
from django.core.management.utils import get_random_secret_key
import json

from user.models import User
from random import randint
from django.core.cache import cache
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from .models import Team, TeamMember
from django.utils import timezone

import base64
from django.core.files.base import ContentFile
from user.views import login_required


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def create_team(request, user):
    data_json = json.loads(request.body)
    name = data_json.get('name')
    description = data_json.get('description')
    avatar = data_json.get('data')
    tel = data_json.get('tel')
    if not bool(re.match("^[A-Za-z0-9][A-Za-z0-9_]{2,99}$", str(name))):
        return JsonResponse({'errno': 2000, 'msg': "团队名不合法"})
    new_team = Team.objects.create(team_name=name, team_description=description, team_tel=tel)
    new_team.team_creator = user.user_id
    if avatar:
        image = ContentFile(base64.b64decode(avatar), name=f"{new_team.team_id}.png")
        new_team.team_avatar.save(image.name, image)
    new_team.save()
    new_TeamMember = TeamMember.objects.create(tm_team_id=new_team.team_id, tm_user_id=user.user_id, tm_user_nickname=user.user_name, tm_user_permissions='creator', tm_user_join_time=new_team.team_create_time)
    user.user_created_teams.add(new_team)
    new_team.team_member.add(new_TeamMember)
    # 添加群聊
    return JsonResponse({'errno': 0, 'msg': "团队创建成功"})


@csrf_exempt
# @login_required
@require_http_methods(['POST'])
def change_team_profile(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    name = data_json.get('name')
    description = data_json.get('description')
    tel = data_json.get('tel')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2010, 'msg': "该团队不存在"})
    team = User.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 2011, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user.user_id)
    if team_member.tm_user_permissions != 'creator' and team_member.tm_user_permissions != 'manager':
        return JsonResponse({'errno': 2012, 'msg': "用户权限不足"})
    elif not bool(re.match("^[A-Za-z0-9][A-Za-z0-9_]{2,99}$", str(name))):
        return JsonResponse({'errno': 2013, 'msg': "团队名不合法"})
    else:
        team.team_name = name
        team.team_description = description
        team.tel = tel
        team.save()
        return JsonResponse({'errno': 0, 'msg': "团队信息修改成功"})


@csrf_exempt
# @login_required
@require_http_methods(['POST'])
def change_team_avatar(request, user):
    data_json = json.loads(request.body)
    data = data_json.get('data')
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2020, 'msg': "该团队不存在"})
    team = User.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 2021, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user.user_id)
    if team_member.tm_user_permissions != 'creator' and team_member.tm_user_permissions != 'manager':
        return JsonResponse({'errno': 2022, 'msg': "用户权限不足"})
    image = ContentFile(base64.b64decode(data), name=f"{team.team_id}.png")
    team.team_avatar.save(image.name, image)
    team.save()
    return JsonResponse({'errno': 0, 'msg': "团队头像上传成功"})


@csrf_exempt
# @login_required
@require_http_methods(['POST'])
def add_manager(request, user):
    data_json = json.loads(request.body)
    user_id = data_json.get('user_id')
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2030, 'msg': "该团队不存在"})
    team = User.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 2031, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user.user_id)
    if team_member.tm_user_permissions != 'creator':
        return JsonResponse({'errno': 2032, 'msg': "用户权限不足"})
    if not User.objects.filter(user_id=user_id).exisis():
        return JsonResponse({'errno': 2033, 'msg': "该用户不存在"})
    user_change = User.objects.get(user_id=user_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user_id).exists():
        return JsonResponse({'errno': 2034, 'msg': "添加用户不在该团队内"})
    team_member_change = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user_id)
    if team_member_change.tm_user_permissions == 'create' or team_member_change.tm_user_permissions == 'manager':
        return JsonResponse({'errno': 2035, 'msg': "添加用户已有管理员权限"})
    user_change.user_managed_teams.add(team)
    user_change.user_joined_teams.remove(team)
    team_member.tm_user_permissions = 'manager'
    team_member_change.save()
    return JsonResponse({'errno': 0, 'msg': "添加管理员成功"})


@csrf_exempt
# @login_required
@require_http_methods(['POST'])
def delete_manager(request, user):
    data_json = json.loads(request.body)
    user_id = data_json.get('user_id')
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2040, 'msg': "该团队不存在"})
    team = User.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 2041, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user.user_id)
    if team_member.tm_user_permissions != 'creator':
        return JsonResponse({'errno': 2042, 'msg': "用户权限不足"})
    if not User.objects.filter(user_id=user_id).exisis():
        return JsonResponse({'errno': 2043, 'msg': "该用户不存在"})
    user_change = User.objects.get(user_id=user_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user_id).exists():
        return JsonResponse({'errno': 2044, 'msg': "删除用户不在该团队内"})
    team_member_change = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user_id)
    if team_member_change.tm_user_permissions == 'create':
        return JsonResponse({'errno': 2045, 'msg': "该用户为团队创建者，不可取消其管理员权限"})
    if team_member_change.tm_user_permissions == 'member':
        return JsonResponse({'errno': 2046, 'msg': "该用户无管理员权限"})
    user_change.user_managed_teams.remove(team)
    user_change.user_joined_teams.add(team)
    team_member.tm_user_permissions = 'member'
    team_member_change.save()
    return JsonResponse({'errno': 0, 'msg': "删除管理员成功"})


@csrf_exempt
# @login_required
@require_http_methods(['POST'])
def add_member(request, user):
    data_json = json.loads(request.body)
    user_id = data_json.get('user_id')
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2050, 'msg': "该团队不存在"})
    team = User.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 2051, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user.user_id)
    if team_member.tm_user_permissions != 'creator' and team_member.tm_user_permissions != 'manager':
        return JsonResponse({'errno': 2052, 'msg': "用户权限不足"})
    if not User.objects.filter(user_id=user_id).exisis():
        return JsonResponse({'errno': 2053, 'msg': "该用户不存在"})
    user_change = User.objects.get(user_id=user_id)
    if TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user_id).exists():
        return JsonResponse({'errno': 2054, 'msg': "添加用户已在该团队内"})
    new_TeamMember = TeamMember.objects.create(tm_team_id=team.team_id, tm_user_id=user_id,
                                               tm_user_nickname=user_change.user_name, tm_user_permissions='member')
    current_time = now()  # 获取当前时间（本地时区）
    new_TeamMember.tm_user_join_time = timezone.make_aware(current_time, timezone.get_current_timezone())  # 转换为带有时区的时间
    new_TeamMember.save()
    user_change.user_joined_teams.add(team)
    # 修改群聊内容
    return JsonResponse({'errno': 0, 'msg': "添加用户成功"})


@csrf_exempt
# @login_required
@require_http_methods(['POST'])
def delete_member(request, user):
    data_json = json.loads(request.body)
    user_id = data_json.get('user_id')
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2060, 'msg': "该团队不存在"})
    team = User.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 2061, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user.user_id)
    if team_member.tm_user_permissions == 'member':
        return JsonResponse({'errno': 2062, 'msg': "用户权限不足"})
    if not User.objects.filter(user_id=user_id).exisis():
        return JsonResponse({'errno': 2063, 'msg': "该用户不存在"})
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user_id).exists():
        return JsonResponse({'errno': 2064, 'msg': "删除用户不在该团队内"})
    user_change = User.objects.get(user_id=user_id)
    team_member_change = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user_id)
    if team_member_change.tm_user_permissions == 'creator':
        return JsonResponse({'errno': 2065, 'msg': "创建者无法踢出团队"})
    elif team_member_change.tm_user_permissions == 'manager':
        if team_member.tm_user_permissions != 'creator':
            return JsonResponse({'errno': 2062, 'msg': "用户权限不足"})
        else:
            team.team_member.delete(team_member_change)
            team_member_change.delete()
            user_change.user_managed_teams.delete(team)
            return JsonResponse({'errno': 0, 'msg': "删除用户成功"})
    else:
        if team_member.tm_user_permissions == 'member':
            return JsonResponse({'errno': 2062, 'msg': "用户权限不足"})
        else:
            team.team_member.delete(team_member_change)
            team_member_change.delete()
            user_change.user_joined_teams.delete(team)
            return JsonResponse({'errno': 0, 'msg': "删除用户成功"})
    # 修改群聊内容



@csrf_exempt
# @login_required
@require_http_methods(['POST'])
def show_member(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2070, 'msg': "该团队不存在"})
    team = User.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 2071, 'msg': "当前用户不在该团队内"})
    if TeamMember.objects.filter(tm_team_id=team_id).exists():
        members = TeamMember.objects.filter(tm_team_id=team_id)
        data = {"members": [
            {"user_id": member.tm_user_id, "nickname": member.tm_user_nickname, "permission": member.tm_user_permissions, "join_time": members.tm_user_join_time
             } for member in members]}
        return JsonResponse({'errno': 0, 'data': data, 'msg': '查询成员列表成功'})


@csrf_exempt
@require_http_methods(['POST'])
def show_team(request):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2080, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    team_info = team.to_json()
    team_avatar = None
    if team.team_avatar:
        team_avatar = get_avatar_base64(team.team_avatar)
    return JsonResponse({'errno': 0, 'msg': '返回用户信息成功', 'team_info': team_info, 'team_avatar': team_avatar})


def get_avatar_base64(image):
    if image is None:
        return None
    with open(image.path, 'rb') as file:
        image_data = file.read()
        ext = os.path.splitext(image.path)[-1]
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
    # 'data:image/' + ext + ';base64,' +
    return base64_encoded


@csrf_exempt
# @login_required
@require_http_methods(['POST'])
def delete_team(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2090, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 2091, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user.user_id)
    if team_member.tm_user_permissions != 'creator':
        return JsonResponse({'errno': 2092, 'msg': "用户权限不足"})
    team.delete()
    return JsonResponse({'errno': 0, 'msg': "删除团队成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def invite_link(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2090, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 2091, 'msg': "当前用户不在该团队内"})
    if team.team_key_expire_time <= now():
        team.team_key = secrets.token_urlsafe(50).replace('#', '')
        team.save()
    return JsonResponse({'errno': 0, 'msg': team.team_key})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def invite_link(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2090, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 2091, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user.user_id)
    if team_member.tm_user_permissions == 'member':
        return JsonResponse({'errno': 2092, 'msg': "用户权限不足"})
    return JsonResponse({'errno': 0, 'msg': team.team_key})