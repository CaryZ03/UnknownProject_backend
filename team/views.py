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
from .models import Team, TeamMember, TeamApplicant, TeamChat
import base64
from django.core.files.base import ContentFile
from user.views import login_required, not_login_required


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def create_team(request, user):
    data_json = json.loads(request.body)
    name = data_json.get('name')
    description = data_json.get('description')
    tel = data_json.get('tel')
    if not bool(re.match("^[A-Za-z0-9][A-Za-z0-9_]{2,99}$", str(name))):
        return JsonResponse({'errno': 2000, 'msg': "团队名不合法"})
    new_team = Team.objects.create(team_name=name, team_description=description, team_tel=tel)
    new_team.team_creator = user
    new_TeamMember = TeamMember.objects.create(tm_team_id=new_team, tm_user_id=user, tm_user_nickname=user.user_name, tm_user_permissions='creator', tm_user_join_time=new_team.team_create_time)
    user.user_created_teams.add(new_team)
    new_team.team_member.add(new_TeamMember)
    new_chat = TeamChat.objects.create(tc_team=new_team)
    new_team.team_chat = new_chat
    new_team.save()
    return JsonResponse({'errno': 0, 'msg': "团队创建成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_team_profile(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    name = data_json.get('name')
    description = data_json.get('description')
    tel = data_json.get('tel')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2010, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2011, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
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
@login_required
@require_http_methods(['POST'])
def change_team_avatar(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2020, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2021, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    if team_member.tm_user_permissions != 'creator' and team_member.tm_user_permissions != 'manager':
        return JsonResponse({'errno': 2022, 'msg': "用户权限不足"})
    relative_image_path = f'avatar/team/{team.team_id}.png'
    team.team_avatar.name = relative_image_path
    team.save()
    return JsonResponse({'errno': 0, 'msg': "团队头像上传成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def add_manager(request, user):
    data_json = json.loads(request.body)
    user_id = data_json.get('user_id')
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2030, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2031, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    if team_member.tm_user_permissions != 'creator':
        return JsonResponse({'errno': 2032, 'msg': "用户权限不足"})
    if not User.objects.filter(user_id=user_id).exists():
        return JsonResponse({'errno': 2033, 'msg': "该用户不存在"})
    user_change = User.objects.get(user_id=user_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user_change).exists():
        return JsonResponse({'errno': 2034, 'msg': "添加用户不在该团队内"})
    team_member_change = TeamMember.objects.get(tm_team_id=team, tm_user_id=user_change)
    if team_member_change.tm_user_permissions == 'creator' or team_member_change.tm_user_permissions == 'manager':
        return JsonResponse({'errno': 2035, 'msg': "添加用户已有管理员权限"})
    user_change.user_managed_teams.add(team)
    user_change.user_joined_teams.remove(team)
    team_member_change.tm_user_permissions = 'manager'
    team_member_change.save()
    return JsonResponse({'errno': 0, 'msg': "添加管理员成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def delete_manager(request, user):
    data_json = json.loads(request.body)
    user_id = data_json.get('user_id')
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2040, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2041, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    if team_member.tm_user_permissions != 'creator':
        return JsonResponse({'errno': 2042, 'msg': "用户权限不足"})
    if not User.objects.filter(user_id=user_id).exists():
        return JsonResponse({'errno': 2043, 'msg': "该用户不存在"})
    user_change = User.objects.get(user_id=user_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user_change).exists():
        return JsonResponse({'errno': 2044, 'msg': "删除用户不在该团队内"})
    team_member_change = TeamMember.objects.get(tm_team_id=team, tm_user_id=user_change)
    if team_member_change.tm_user_permissions == 'creator':
        return JsonResponse({'errno': 2045, 'msg': "该用户为团队创建者，不可取消其管理员权限"})
    if team_member_change.tm_user_permissions == 'member':
        return JsonResponse({'errno': 2046, 'msg': "该用户无管理员权限"})
    user_change.user_managed_teams.remove(team)
    user_change.user_joined_teams.add(team)
    team_member_change.tm_user_permissions = 'member'
    team_member_change.save()
    return JsonResponse({'errno': 0, 'msg': "删除管理员成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def add_member(request, user):
    data_json = json.loads(request.body)
    user_id = data_json.get('user_id')
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2050, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2051, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    if team_member.tm_user_permissions != 'creator' and team_member.tm_user_permissions != 'manager':
        return JsonResponse({'errno': 2052, 'msg': "用户权限不足"})
    if not User.objects.filter(user_id=user_id).exists():
        return JsonResponse({'errno': 2053, 'msg': "该用户不存在"})
    user_change = User.objects.get(user_id=user_id)
    if TeamMember.objects.filter(tm_team_id=team, tm_user_id=user_change).exists():
        return JsonResponse({'errno': 2054, 'msg': "添加用户已在该团队内"})
    new_TeamMember = TeamMember.objects.create(tm_team_id=team, tm_user_id=user_change,
                                               tm_user_nickname=user_change.user_name, tm_user_permissions='member')
    new_TeamMember.save()
    team.team_member.add(new_TeamMember)
    user_change.user_joined_teams.add(team)
    # 修改群聊内容
    return JsonResponse({'errno': 0, 'msg': "添加用户成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def delete_member(request, user):
    data_json = json.loads(request.body)
    user_id = data_json.get('user_id')
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2060, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2061, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    if team_member.tm_user_permissions == 'member':
        return JsonResponse({'errno': 2062, 'msg': "用户权限不足"})
    if not User.objects.filter(user_id=user_id).exists():
        return JsonResponse({'errno': 2063, 'msg': "该用户不存在"})
    user_change = User.objects.get(user_id=user_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user_change).exists():
        return JsonResponse({'errno': 2064, 'msg': "删除用户不在该团队内"})
    team_member_change = TeamMember.objects.get(tm_team_id=team, tm_user_id=user_change)
    if team_member_change.tm_user_permissions == 'creator':
        return JsonResponse({'errno': 2065, 'msg': "创建者无法踢出团队"})
    elif team_member_change.tm_user_permissions == 'manager':
        if team_member.tm_user_permissions != 'creator':
            return JsonResponse({'errno': 2062, 'msg': "用户权限不足"})
        else:
            team.team_member.remove(team_member_change)
            team_member_change.delete()
            user_change.user_managed_teams.remove(team)
            return JsonResponse({'errno': 0, 'msg': "删除用户成功"})
    else:
        if team_member.tm_user_permissions == 'member':
            return JsonResponse({'errno': 2062, 'msg': "用户权限不足"})
        else:
            team.team_member.remove(team_member_change)
            team_member_change.delete()
            user_change.user_joined_teams.remove(team)
            return JsonResponse({'errno': 0, 'msg': "删除用户成功"})
    # 修改群聊内容


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def show_member(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    m_type = data_json.get('type')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2070, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2071, 'msg': "当前用户不在该团队内"})
    if m_type == 'creator':
        members = team.team_member.filter(tm_user_permissions='creator')
    elif m_type == 'manager':
        members = team.team_member.filter(tm_user_permissions='manager')
    elif m_type == 'normal':
        members = team.team_member.filter(tm_user_permissions='member')
    elif m_type == 'all':
        members = team.team_member.all()
    else:
        return JsonResponse({'errno': 2072, 'msg': "未指定成员类型"})
    data = {"members": [
        {"user_id": member.tm_user_id.user_id, "nickname": member.tm_user_nickname, "permission": member.tm_user_permissions, "join_time": member.tm_user_join_time
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
    return JsonResponse({'errno': 0, 'msg': '返回团队信息成功', 'team_info': team_info, 'team_avatar': team_avatar})


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
@login_required
@require_http_methods(['POST'])
def delete_team(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2090, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2091, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
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
@login_required
@require_http_methods(['POST'])
def show_check(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2130, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2131, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    if team_member.tm_user_permissions == 'member':
        return JsonResponse({'errno': 2132, 'msg': "用户权限不足"})
    waiters = team.team_applicants.all()
    w_info = []
    for w in waiters:
        if TeamMember.objects.filter(tm_team_id=team, tm_user_id=w.ta_user_id).exists():
            member_change = TeamApplicant.objects.get(tm_team_id=team, tm_user_id=w.ta_user_id)
            team.team_applicants.remove(member_change)
            member_change.delete()
        else:
            w_info.append(w.to_json())
    return JsonResponse({'errno': 0, 'msg': '返回审核列表成功', 'tm_info': w_info})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def check_member(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    user_id = data_json.get('user_id')
    choose = data_json.get('choose')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2140, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2141, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    if team_member.tm_user_permissions == 'member':
        return JsonResponse({'errno': 2142, 'msg': "用户权限不足"})
    if not User.objects.filter(user_id=user_id).exists():
        return JsonResponse({'errno': 2143, 'msg': "该用户不存在"})
    user_change = User.objects.get(user_id=user_id)
    if not TeamApplicant.objects.filter(ta_team_id=team, ta_user_id=user_change).exists():
        return JsonResponse({'errno': 2144, 'msg': "待审核用户未提交申请"})
    if choose == 'yes':
        new_TeamMember = TeamMember.objects.create(tm_team_id=team, tm_user_id=user_change,
                                                   tm_user_nickname=user_change.user_name, tm_user_permissions='member')
        user_change.user_joined_teams.add(team)
        member_change = TeamApplicant.objects.get(ta_team_id=team, ta_user_id=user_change)
        team.team_applicants.remove(member_change)
        member_change.delete()
        team.team_member.add(new_TeamMember)
        # 修改群聊
        return JsonResponse({'errno': 0, 'msg': "审核通过"})
    else:
        member_change = TeamApplicant.objects.get(ta_team_id=team, ta_user_id=user_change)
        team.team_applicants.remove(member_change)
        member_change.delete()
        return JsonResponse({'errno': 0, 'msg': "审核不通过"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def join_team_url(request, user):
    data_json = json.loads(request.body)
    team_key = data_json.get('team_key')
    message = data_json.get('message')
    if not Team.objects.filter(team_key=team_key).exists():
        return JsonResponse({'errno': 2110, 'msg': "该团队不存在"})
    team = Team.objects.get(team_key=team_key)
    if team.team_key_expire_time <= now():
        return JsonResponse({'errno': 2111, 'msg': "链接已过期"})
    if TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2112, 'msg': "成员已存在"})
    if TeamApplicant.objects.filter(ta_team_id=team, ta_user_id=user).exists():
        return JsonResponse({'errno': 2113, 'msg': "已提交过申请"})
    else:
        new_team_app = TeamApplicant.objects.create(ta_team_id=team, ta_user_id=user, ta_message=message)
        team.team_applicants.add(new_team_app)
    return JsonResponse({'errno': 0, 'msg': "加入申请成功", 'team_id': team.team_id})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def join_team_straight(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    message = data_json.get('message')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2120, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2121, 'msg': "成员已存在"})
    if TeamApplicant.objects.filter(ta_team_id=team, ta_user_id=user).exists():
        return JsonResponse({'errno': 2122, 'msg': "已提交过申请"})
    else:
        new_team_app = TeamApplicant.objects.create(ta_team_id=team, ta_user_id=user, ta_message=message)
        team.team_applicants.add(new_team_app)
    return JsonResponse({'errno': 0, 'msg': "加入申请成功", 'team_id': team.team_id})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_nickname(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    nickname = data_json.get('nickname')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2150, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2151, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    if not bool(re.match("^[A-Za-z0-9][A-Za-z0-9_]{2,29}$", str(nickname))):
        return JsonResponse({'errno': 2152, 'msg': "昵称不合法"})
    team_member.tm_user_nickname = nickname
    team_member.save()
    return JsonResponse({'errno': 0, 'msg': "修改团队昵称成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def member_role(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    user_id = data_json.get('user_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2160, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2161, 'msg': "当前用户不在该团队内"})
    if not User.objects.filter(user_id=user_id).exists():
        return JsonResponse({'errno': 2162, 'msg': "该用户不存在"})
    user_show = User.objects.get(user_id=user_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user_show).exists():
        return JsonResponse({'errno': 2163, 'msg': "查询用户不在该团队"})
    team_member_show = TeamMember.objects.get(tm_team_id=team, tm_user_id=user_show)
    return JsonResponse({'errno': 0, 'msg': "查询用户角色成功", 'role': team_member_show.tm_user_permissions})
