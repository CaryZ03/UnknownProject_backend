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
from .models import Project, Requirement
import base64
from django.core.files.base import ContentFile
from user.views import login_required, not_login_required, get_avatar_base64


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def create_project(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    name = data_json.get('name')
    description = data_json.get('description')
    avatar = data_json.get('data')
    complete_time = data_json.get('complete_date')
    estimated_start_time = data_json.get('estimated_start_time')
    estimated_end_time = data_json.get('estimated_end_time')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 3000, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3001, 'msg': "当前用户不在该团队内"})
    if not bool(re.match("^[A-Za-z0-9][A-Za-z0-9_]{2,99}$", str(name))):
        return JsonResponse({'errno': 3002, 'msg': "项目名不合法"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    new_project = Project.objects.create(project_name=name, project_description=description, project_complete_date=complete_time, project_creator=team_member, project_team=team)
    team.team_projects.add(new_project)
    user.user_created_projects.add(new_project)
    if avatar:
        image = ContentFile(base64.b64decode(avatar), name=f"{new_project.project_id}.png")
        new_project.project_avatar.save(image.name, image)
    new_project.project_estimated_end_time = estimated_end_time
    new_project.project_estimated_start_time = estimated_start_time
    new_project.save()
    team.team_projects.add(new_project)
    return JsonResponse({'errno': 0, 'msg': "项目创建成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def delete_project(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    project_id = data_json.get('project_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 3010, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3011, 'msg': "当前用户不在该团队内"})
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3012, 'msg': "该项目不存在"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    de_project = Project.objects.get(project_id=project_id)
    if de_project.project_creator != team_member:
        return JsonResponse({'errno': 3013, 'msg': "当前用户不是该项目创建者，无法删除项目"})
    user.user_created_projects.remove(de_project)
    team.team_projects.remove(de_project)
    de_project.delete()
    return JsonResponse({'errno': 0, 'msg': "项目删除成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def show_profile(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    project_id = data_json.get('project_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 3010, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3011, 'msg': "当前用户不在该团队内"})
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3012, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    if not project.project_recycle:
        return JsonResponse({'errno': 3013, 'msg': '项目在回收站无法操作'})
    project_info = project.to_json()
    project_avatar = None
    if project.project_avatar:
        project_avatar = get_avatar_base64(project.project_avatar)
    return JsonResponse({'errno': 0, 'msg': '返回用户信息成功', 'project_info': project_info, 'project_avatar': project_avatar})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_profile(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    project_id = data_json.get('project_id')
    name = data_json.get('name')
    description = data_json.get('description')
    complete_time = data_json.get('complete_date')
    project_editable = data_json.get('editable')
    status = data_json.get('status')
    estimated_start_time = data_json.get('estimated_start_time')
    estimated_end_time = data_json.get('estimated_end_time')
    recycle = data_json.get('recycle')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 3010, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3011, 'msg': "当前用户不在该团队内"})
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3012, 'msg': "该项目不存在"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    project = Project.objects.get(project_id=project_id)
    if not project.project_recycle:
        return JsonResponse({'errno': 3013, 'msg': '项目在回收站无法操作'})
    if project.project_creator != team_member:
        return JsonResponse({'errno': 3013, 'msg': "当前用户不是该项目创建者，无法改变项目"})
    if not bool(re.match("^[A-Za-z0-9][A-Za-z0-9_]{2,99}$", str(name))):
        return JsonResponse({'errno': 3002, 'msg': "项目名不合法"})
    if project.project_status != 'not_started' and status == 'not_started':
        project.project_end_time = None
        project.project_start_time = None
    if project.project_status != 'doing' and status == 'doing':
        project.project_end_time = None
        project.project_start_time = now()
    if project.project_status != 'finished' and status == 'finished':
        project.project_end_time = now()
    project.project_status = status
    project.project_estimated_end_time = estimated_end_time
    project.project_estimated_start_time = estimated_start_time
    project.project_editable = project_editable
    project.project_name = name
    project.project_description = description
    project.project_complete_date = complete_time
    project.project_recycle = recycle
    project.save()
    return JsonResponse({'errno': 0, 'msg': "项目删除成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def add_recycle(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    project_id = data_json.get('project_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 3010, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3011, 'msg': "当前用户不在该团队内"})
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3012, 'msg': "该项目不存在"})
    if not project.project_recycle:
        return JsonResponse({'errno': 3013, 'msg': '项目已在回收站'})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    project = Project.objects.get(project_id=project_id)
    if project.project_creator != team_member:
        return JsonResponse({'errno': 3013, 'msg': "当前用户不是该项目创建者，无法回收项目"})
    project.project_recycle = True
    project.save()
    return JsonResponse({'errno': 0, 'msg': "项目删除成功"})



