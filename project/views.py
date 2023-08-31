import datetime
import os
import re
import secrets
import json
import shutil
from time import strptime

from django.forms import model_to_dict
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http.response import JsonResponse
from datetime import timedelta

from document.views import copy_document, copy_directory
from user.models import User, UserToken
from team.models import Team, TeamMember, TeamApplicant
from .models import Project, Requirement
from document.models import Document, Prototype, Directory
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
    estimated_start_time = data_json.get('estimated_start_time')
    estimated_end_time = data_json.get('estimated_end_time')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 3000, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3001, 'msg': "当前用户不在该团队内"})
    # if not bool(re.match("^[A-Za-z0-9][A-Za-z0-9_]{2,99}$", str(name))):
    #     return JsonResponse({'errno': 3002, 'msg': "项目名不合法"})
    if estimated_start_time and estimated_end_time:
        time_format = "%Y-%m-%d %H:%M:%S"
        estimated_start_time = datetime.datetime.strptime(estimated_start_time, time_format)
        estimated_end_time = datetime.datetime.strptime(estimated_end_time, time_format)
        if estimated_start_time > estimated_end_time:
            return JsonResponse({'errno': 3003, 'msg': "预设时间不合法"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    new_project = Project.objects.create(project_name=name, project_description=description, project_creator=team_member, project_team=team)
    team.team_projects.add(new_project)
    user.user_created_projects.add(new_project)
    new_project.project_estimated_end_time = estimated_end_time
    new_project.project_estimated_start_time = estimated_start_time
    new_directory = Directory.objects.create()
    new_directory.directory_project = new_project
    new_directory.save()
    new_project.project_root_directory = new_directory
    new_recycle = Directory.objects.create()
    new_recycle.directory_project = new_project
    new_recycle.save()
    new_project.project_recycle_bin = new_recycle
    new_project.save()
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
        return JsonResponse({'errno': 3020, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3021, 'msg': "当前用户不在该团队内"})
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3022, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    if project.project_recycle:
        return JsonResponse({'errno': 3023, 'msg': '项目在回收站无法操作'})
    project_info = project.to_json()
    project_avatar = None
    if project.project_avatar:
        project_avatar = get_avatar_base64(project.project_avatar)
    return JsonResponse({'errno': 0, 'msg': '返回项目信息成功', 'project_info': project_info, 'project_avatar': project_avatar})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_profile(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    project_id = data_json.get('project_id')
    name = data_json.get('name')
    description = data_json.get('description')
    project_editable = data_json.get('editable')
    status = data_json.get('status')
    estimated_start_time = data_json.get('estimated_start_time')
    estimated_end_time = data_json.get('estimated_end_time')
    recycle = data_json.get('recycle')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 3030, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3031, 'msg': "当前用户不在该团队内"})
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3032, 'msg': "该项目不存在"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    project = Project.objects.get(project_id=project_id)
    if project.project_recycle:
        return JsonResponse({'errno': 3033, 'msg': '项目在回收站无法操作'})
    if project.project_creator != team_member:
        return JsonResponse({'errno': 3034, 'msg': "当前用户不是该项目创建者，无法改变项目"})
    # if not bool(re.match("^[A-Za-z0-9][A-Za-z0-9_]{2,99}$", str(name))):
    #     return JsonResponse({'errno': 3035, 'msg': "项目名不合法"})
    if estimated_start_time and estimated_end_time:
        time_format = "%Y-%m-%d %H:%M:%S"
        estimated_start_time = datetime.datetime.strptime(estimated_start_time, time_format)
        estimated_end_time = datetime.datetime.strptime(estimated_end_time, time_format)
        if estimated_start_time > estimated_end_time:
            return JsonResponse({'errno': 3036, 'msg': "预设时间不合法"})
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
    project.project_recycle = recycle
    project.save()
    return JsonResponse({'errno': 0, 'msg': "项目信息修改成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_avatar(request, user):
    data_json = json.loads(request.body)
    project_id = data_json.get('project_id')
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3060, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3061, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    if project.project_recycle:
        return JsonResponse({'errno': 3033, 'msg': '项目在回收站无法操作'})
    if project.project_creator != team_member:
        return JsonResponse({'errno': 3034, 'msg': "当前用户不是该项目创建者，无法改变项目"})
    relative_image_path = f'avatar/project/{project.project_id}.png'
    project.project_avatar.name = relative_image_path
    project.save()
    return JsonResponse({'errno': 0, 'msg': "团队头像上传成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_recycle_status(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    project_id = data_json.get('project_id')
    status = data_json.get('status')
    print(status)
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 3140, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3141, 'msg': "当前用户不在该团队内"})
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3142, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    if project.project_creator != team_member:
        return JsonResponse({'errno': 3143, 'msg': "当前用户不是该项目创建者"})
    if status == "True":
        if project.project_recycle:
            return JsonResponse({'errno': 3144, 'msg': '项目已在回收站'})
        project.project_recycle = True
    else:
        if not project.project_recycle:
            return JsonResponse({'errno': 3145, 'msg': '项目不在回收站'})
        project.project_recycle = False
    project.save()
    return JsonResponse({'errno': 0, 'msg': "项目状态修改成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def search_status(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    status = data_json.get('status')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 3040, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3041, 'msg': "当前用户不在该团队内"})
    projects = Project.objects.filter(project_status=status, project_team=team)
    p_info = []
    for p in projects:
        if not p.project_recycle:
            p_info.append(p.to_json())
    return JsonResponse({'errno': 0, 'msg': "项目列表查询成功", 'p_info': p_info})


@csrf_exempt
@login_required
@require_http_methods(['GET'])
def check_project_list(request, user):
    projects = user.user_created_projects.all()
    p_info = []
    for p in projects:
        if not p.project_recycle:
            p_info.append(p.to_json())
    return JsonResponse({'errno': 0, 'msg': "项目列表查询成功", 'p_info': p_info})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def create_requirement(request, user):
    data_json = json.loads(request.body)
    project_id = data_json.get('project_id')
    name = data_json.get('name')
    estimated_start_time = data_json.get('estimated_start_time')
    estimated_end_time = data_json.get('estimated_end_time')
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3060, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3061, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3062, 'msg': "项目在回收站中，无法操作"})
    # if not bool(re.match("^[A-Za-z0-9][A-Za-z0-9_]{2,99}$", str(name))):
    #     return JsonResponse({'errno': 3063, 'msg': "需求名不合法"})
    if estimated_start_time and estimated_end_time:
        time_format = "%Y-%m-%d %H:%M:%S"
        estimated_start_time = datetime.datetime.strptime(estimated_start_time, time_format)
        estimated_end_time = datetime.datetime.strptime(estimated_end_time, time_format)
        if estimated_start_time > estimated_end_time:
            return JsonResponse({'errno': 3064, 'msg': "预设时间不合法"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    new_requirement = Requirement.objects.create(requirement_name=name, requirement_creator=team_member, requirement_estimated_start_time=estimated_start_time, requirement_estimated_end_time=estimated_end_time)
    project.project_requirement.add(new_requirement)
    new_requirement.requirement_project = project
    new_requirement.save()
    return JsonResponse({'errno': 0, 'msg': "项目创建成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def delete_requirement(request, user):
    data_json = json.loads(request.body)
    project_id = data_json.get('project_id')
    requirement_id = data_json.get('requirement_id')
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3070, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3071, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    if project.project_recycle:
        return JsonResponse({'errno': 3072, 'msg': "项目在回收站中，无法操作"})
    if not Requirement.objects.filter(requirement_id=requirement_id).exists():
        return JsonResponse({'errno': 3073, 'msg': "该需求不存在"})
    de_requirement = Requirement.objects.get(requirement_id=requirement_id)
    if de_requirement.requirement_creator != team_member:
        return JsonResponse({'errno': 3083, 'msg': "当前用户不是该项目创建者，无法删除项目"})
    project.project_requirement.remove(de_requirement)
    de_requirement.delete()
    return JsonResponse({'errno': 0, 'msg': "需求删除成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def show_profile_requirement(request, user):
    data_json = json.loads(request.body)
    project_id = data_json.get('project_id')
    requirement_id = data_json.get('requirement_id')
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3080, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3081, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3082, 'msg': "项目在回收站中，无法操作"})
    if not Requirement.objects.filter(requirement_id=requirement_id).exists():
        return JsonResponse({'errno': 3083, 'msg': "该需求不存在"})
    requirement = Requirement.objects.get(requirement_id=requirement_id)
    requirement_info = requirement.to_json()
    return JsonResponse({'errno': 0, 'msg': '返回需求信息成功', 'requirement_info': requirement_info})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_profile_requirement(request, user):
    data_json = json.loads(request.body)
    project_id = data_json.get('project_id')
    requirement_id = data_json.get('requirement_id')
    name = data_json.get('name')
    status = data_json.get('status')
    estimated_start_time = data_json.get('estimated_start_time')
    estimated_end_time = data_json.get('estimated_end_time')
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3090, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3091, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    if project.project_recycle:
        return JsonResponse({'errno': 3092, 'msg': "项目在回收站中，无法操作"})
    if not Requirement.objects.filter(requirement_id=requirement_id).exists():
        return JsonResponse({'errno': 3093, 'msg': "该需求不存在"})
    requirement = Requirement.objects.get(requirement_id=requirement_id)
    if requirement.requirement_creator != team_member:
        return JsonResponse({'errno': 3094, 'msg': "当前用户不是该项目创建者，无法删除项目"})
    # if not bool(re.match("^[A-Za-z0-9][A-Za-z0-9_]{2,99}$", str(name))):
    #     return JsonResponse({'errno': 3095, 'msg': "需求名不合法"})
    if estimated_start_time and estimated_end_time:
        time_format = "%Y-%m-%d %H:%M:%S"
        estimated_start_time = datetime.datetime.strptime(estimated_start_time, time_format)
        estimated_end_time = datetime.datetime.strptime(estimated_end_time, time_format)
        if estimated_start_time > estimated_end_time:
            return JsonResponse({'errno': 3096, 'msg': "预设时间不合法"})
    if requirement.requirement_status != 'not_started' and status == 'not_started':
        requirement.requirement_end_time = None
        requirement.requirement_start_time = None
    if requirement.requirement_status != 'doing' and status == 'doing':
        requirement.requirement_end_time = None
        requirement.requirement_start_time = now()
    if requirement.requirement_status != 'finished' and status == 'finished':
        requirement.requirement_end_time = now()
    requirement.requirement_status = status
    requirement.requirement_estimated_end_time = estimated_end_time
    requirement.requirement_estimated_start_time = estimated_start_time
    requirement.requirement_name = name
    requirement.save()
    return JsonResponse({'errno': 0, 'msg': "需求信息修改成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def check_project_list_team(request, user):
    data_json = json.loads(request.body)
    team_id = data_json.get('team_id')
    recycle = data_json.get('recycle')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 3110, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3111, 'msg': "当前用户不在该团队内"})
    projects = team.team_projects.filter(project_recycle=recycle)
    p_info = []
    for p in projects:
        p_info.append(p.to_json())
    return JsonResponse({'errno': 0, 'msg': "项目列表查询成功", 'p_info': p_info})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def check_requirement_list(request, user):
    data_json = json.loads(request.body)
    project_id = data_json.get('project_id')
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3120, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
    requirements = project.project_requirement.all()
    r_info = []
    for r in requirements:
        r_info.append(r.to_json())
    return JsonResponse({'errno': 0, 'msg': "需求列表查询成功", 'r_info': r_info})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def search_project_by_name(request, user):
    data_json = json.loads(request.body)
    project_name_part = data_json.get('project_name_part')
    team_id = data_json.get('team_id')
    if not Team.objects.filter(team_id=team_id).exists():
        return JsonResponse({'errno': 2180, 'msg': "该团队不存在"})
    team = Team.objects.get(team_id=team_id)
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 2181, 'msg': "当前用户不在该团队内"})
    matching_projects = Project.oobjects.filter(project_name__contains=project_name_part)
    matching_projects_info = []
    for project in matching_projects:
        if project.project_team == team:
            matching_projects_info.append(project.to_json())
    return JsonResponse({'errno': 0, 'msg': '返回项目信息列表成功', 'matching_projects_info': matching_projects_info})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def copy_project(request, user):
    data_json = json.loads(request.body)
    project_id = data_json.get('project_id')
    new_name = data_json.get('new_name')
    old_project = Project.objects.get(project_id=project_id)
    team = old_project.project_team
    creator = team.team_member.get(tm_user_id=user)
    new_project = Project()

    new_project.project_name = new_name
    new_project.project_description = old_project.project_description
    new_project.project_estimated_start_time = old_project.project_estimated_start_time
    new_project.project_estimated_end_time = old_project.project_estimated_end_time
    new_project.project_end_time = old_project.project_end_time
    new_project.project_start_time = old_project.project_start_time
    new_project.project_creator = creator
    new_project.project_editable = old_project.project_editable
    new_project.project_team = team
    new_project.project_status = old_project.project_status
    new_project.project_recycle = old_project.project_recycle

    new_project.save()

    # 复制 ManyToMany 关系
    for old_requirement in old_project.project_requirement.all():
        new_requirement = Requirement()
        new_requirement.requirement_name = old_requirement.requirement_name
        new_requirement.requirement_creator = old_requirement.requirement_creator
        new_requirement.requirement_estimated_start_time = old_requirement.requirement_estimated_start_time
        new_requirement.requirement_estimated_end_time = old_requirement.requirement_estimated_end_time
        new_requirement.requirement_end_time = old_requirement.requirement_end_time
        new_requirement.requirement_start_time = old_requirement.requirement_start_time
        new_requirement.requirement_project = new_project
        new_requirement.requirement_status = old_requirement.requirement_status

        # 保存新的需求实例到数据库
        new_requirement.save()
        new_project.project_requirement.add(new_requirement)

    for old_prototype in old_project.project_prototype.all():
        new_prototype = Prototype()
        # 假设 old_prototype 和 new_prototype 是已经存在的实例
        new_prototype.prototype_name = old_prototype.prototype_name
        new_prototype.prototype_project = new_prototype
        new_prototype.prototype_creator = old_prototype.prototype_creator
        if old_prototype.prototype_file:
            old_file_path = old_prototype.prototype_file.path
            old_file_name, old_file_extension = os.path.splitext(os.path.basename(old_file_path))

            # 假设 new_saved_document 是新的 SavedDocument 实例
            new_file_id = new_prototype.pk  # 新文件的 ID
            new_file_path = f'Prototype/{old_file_name}_{new_file_id}{old_file_extension}'

            shutil.copy(old_file_path, new_file_path)
            new_prototype.prototype_file.name = new_file_path
        new_prototype.prototype_recycle = old_prototype.prototype_recycle

        # 保存新的原型实例到数据库
        new_prototype.save()
        new_project.project_prototype.add(new_prototype)

    new_root = copy_directory(new_project, old_project.project_root_directory)
    new_project.project_root_directory = new_root
    new_recycle = copy_directory(new_project, old_project.project_recycle_bin)
    new_project.project_recycle_bin = new_recycle

    for old_directory in old_project.project_directory:
        new_directory = copy_directory(new_project, old_directory)
        new_project.project_directory.add(new_directory)

    new_project.save()
    team.team_projects.add(new_project)

    return JsonResponse({'errno': 0, 'msg': "项目复制修改成功"})
