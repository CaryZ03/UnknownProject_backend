import os
import re
from django.db.models import Q
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http.response import JsonResponse
from datetime import timedelta
from django.core.management.utils import get_random_secret_key
import json

from user.models import User, UserToken
from random import randint
from django.core.cache import cache
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from django.utils import timezone

import base64
from django.core.files.base import ContentFile


@csrf_exempt
# @login_required
@require_http_methods(['POST'])
def create_team(request, user):
    data_json = json.loads(request.body)
    name = data_json.get('name')
    description = data_json.get('description')
    avatar = data_json.get('data')
    tel = data_json.get('tel')
    if not bool(re.match("^[A-Za-z0-9][A-Za-z0-9_]{2,99}$", str(name))):
        return JsonResponse({'errno': 1101, 'msg': "团队名不合法"})
    new_team = Team.objects.create(team_name=name, team_description=description, team_tel=tel)
    new_team.team_creator = user.user_id
    current_time = datetime.now()  # 获取当前时间（本地时区）
    new_team.team_create_time = timezone.make_aware(current_time, timezone.get_current_timezone())  # 转换为带有时区的时间
    if avatar:
        image = ContentFile(base64.b64decode(avatar), name=f"{new_team.team_id}.png")
        new_team.team_avatar.save(image.name, image)
    new_team.save()
    new_TeamMember = TeamMember.objects.create(tm_team_id=new_team.team_id, tm_user_id=user.user_id, tm_user_nickname=user.user_name, tm_user_permissions='creator', tm_user_join_time=new_team.team_create_time)
    # user 中添加他创建该团队
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
        return JsonResponse({'errno': 1200, 'msg': "该团队不存在"})
    team = User.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 1200, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user.user_id)
    if team_member.tm_user_permissions != 'creator' and team_member.tm_user_permissions != 'manager':
        return JsonResponse({'errno': 0, 'msg': "用户权限不足"})
    elif not bool(re.match("^[A-Za-z0-9][A-Za-z0-9_]{2,99}$", str(name))):
        return JsonResponse({'errno': 1101, 'msg': "团队名不合法"})
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
        return JsonResponse({'errno': 1200, 'msg': "该团队不存在"})
    team = User.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 1200, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user.user_id)
    if team_member.tm_user_permissions != 'creator' and team_member.tm_user_permissions != 'manager':
        return JsonResponse({'errno': 0, 'msg': "用户权限不足"})
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
        return JsonResponse({'errno': 1200, 'msg': "该团队不存在"})
    team = User.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 1200, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user.user_id)
    if team_member.tm_user_permissions != 'creator':
        return JsonResponse({'errno': 0, 'msg': "用户权限不足"})
    if not User.objects.filter(user_id=user_id).exisis():
        return JsonResponse({'errno': 1200, 'msg': "该用户不存在"})
    user_change = User.objects.get(user_id=user_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user_id).exists():
        return JsonResponse({'errno': 1200, 'msg': "添加用户不在该团队内"})
    team_member_change = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user_id)
    if team_member_change.tm_user_permissions == 'create' or team_member_change.tm_user_permissions == 'manager':
        return JsonResponse({'errno': 1200, 'msg': "添加用户已有管理员权限"})
    # 修改user里内容
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
        return JsonResponse({'errno': 1200, 'msg': "该团队不存在"})
    team = User.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 1200, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user.user_id)
    if team_member.tm_user_permissions != 'creator':
        return JsonResponse({'errno': 0, 'msg': "用户权限不足"})
    if not User.objects.filter(user_id=user_id).exisis():
        return JsonResponse({'errno': 1200, 'msg': "该用户不存在"})
    user_change = User.objects.get(user_id=user_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user_id).exists():
        return JsonResponse({'errno': 1200, 'msg': "删除用户不在该团队内"})
    team_member_change = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user_id)
    if team_member_change.tm_user_permissions == 'create':
        return JsonResponse({'errno': 1200, 'msg': "该用户为团队创建者，不可取消其管理员权限"})
    if team_member_change.tm_user_permissions == 'member':
        return JsonResponse({'errno': 1200, 'msg': "该用户无管理员权限"})
    # 修改用户里内容
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
        return JsonResponse({'errno': 1200, 'msg': "该团队不存在"})
    team = User.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 1200, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user.user_id)
    if team_member.tm_user_permissions != 'creator' and team_member.tm_user_permissions != 'manager':
        return JsonResponse({'errno': 0, 'msg': "用户权限不足"})
    if not User.objects.filter(user_id=user_id).exisis():
        return JsonResponse({'errno': 1200, 'msg': "该用户不存在"})
    user_change = User.objects.get(user_id=user_id)
    if TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user_id).exists():
        return JsonResponse({'errno': 1200, 'msg': "添加用户已在该团队内"})
    new_TeamMember = TeamMember.objects.create(tm_team_id=team.team_id, tm_user_id=user_id,
                                               tm_user_nickname=user_change.user_name, tm_user_permissions='member')
    current_time = datetime.now()  # 获取当前时间（本地时区）
    new_TeamMember.tm_user_join_time = timezone.make_aware(current_time, timezone.get_current_timezone())  # 转换为带有时区的时间
    new_TeamMember.save()
    # 修改用户里内容
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
        return JsonResponse({'errno': 1200, 'msg': "该团队不存在"})
    team = User.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 1200, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team.team_id, tm_user_id=user.user_id)
    if team_member.tm_user_permissions != 'creator' and team_member.tm_user_permissions != 'manager':
        return JsonResponse({'errno': 0, 'msg': "用户权限不足"})
    if not User.objects.filter(user_id=user_id).exisis():
        return JsonResponse({'errno': 1200, 'msg': "该用户不存在"})
    user_change = User.objects.get(user_id=user_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user_id).exists():
        return JsonResponse({'errno': 1200, 'msg': "删除用户不在该团队内"})
    team_member.delete()
    # 修改user内容
    # 修改群聊内容
    return JsonResponse({'errno': 0, 'msg': "添加用户成功"})


@csrf_exempt
# @login_required
@require_http_methods(['POST'])
def show_member(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 1200, 'msg': "该团队不存在"})
    team = User.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team.team_id, tm_user_id=user.user_id).exists():
        return JsonResponse({'errno': 1200, 'msg': "当前用户不在该团队内"})
    if TeamMember.objects.filter(tm_team_id=team_id).exists():
        members = TeamMember.objects.filter(tm_team_id=team_id)
        data = {"members": [
            {"user_id": member.tm_user_id, "nickname": member.tm_user_nickname, "permission": member.tm_user_permissions, "join_time": members.tm_user_join_time
             } for member in members]}
        return JsonResponse({'errno': 0, 'data': data, 'msg': '查询成员列表成功'})


@csrf_exempt
# @login_required
@require_http_methods(['POST'])
def show_team(request, team):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 1200, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    team_info = team.to_json()
    team_avatar = None
    if team.team_avatar:
        team_avatar = get_avatar_base64(team.team_avatar)
    return JsonResponse({'errno': 0, 'msg': '返回用户信息成功', 'user_info': team_info, 'user_avatar': team_avatar})


def get_avatar_base64(image):
    if image is None:
        return None
    with open(image.path, 'rb') as file:
        image_data = file.read()
        ext = os.path.splitext(image.path)[-1]
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
    # 'data:image/' + ext + ';base64,' +
    return base64_encoded
