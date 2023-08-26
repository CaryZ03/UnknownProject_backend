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
from user.views import login_required, not_login_required


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
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 3000, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3001, 'msg': "当前用户不在该团队内"})
    if not bool(re.match("^[A-Za-z0-9][A-Za-z0-9_]{2,99}$", str(name))):
        return JsonResponse({'errno': 3002, 'msg': "项目名不合法"})
    if complete_time <= now():
        return JsonResponse({'errno': 3003, 'msg': "项目完成时间不合法"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    new_project = Project.objects.create(project_name=name, project_description=description, project_complete_date=complete_time, project_creator=team_member, project_team=team)
    team.team_projects.add(new_project)
    user.user_created_projects.add(new_project)
    if avatar:
        image = ContentFile(base64.b64decode(avatar), name=f"{new_project.project_id}.png")
        new_project.project_avatar.save(image.name, image)
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
    new_project = Project.objects.create(project_name=name, project_description=description, project_complete_date=complete_time, project_creator=team_member, project_team=team)
    team.team_projects.add(new_project)
    user.user_created_projects.add(new_project)
    if avatar:
        image = ContentFile(base64.b64decode(avatar), name=f"{new_project.project_id}.png")
        new_project.project_avatar.save(image.name, image)
    new_project.save()
    team.team_projects.add(new_project)
    return JsonResponse({'errno': 0, 'msg': "项目创建成功"})

