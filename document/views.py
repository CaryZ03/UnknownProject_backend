import os
import shutil

from django.forms import model_to_dict
from django.utils.timezone import now

from project.models import Project
from team.models import *
from message.models import *
from .models import File, Document, SavedDocument, Prototype, Directory, Template
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http.response import JsonResponse
import json

from user.models import User, UserToken
from team.models import Team, TeamMember
from project.models import Project
from user.views import login_required, not_login_required


@csrf_exempt
@require_http_methods(['POST'])
def upload_file(request):
    uploaded_file = request.FILES['file']
    file_obj = File(file_content=uploaded_file)
    file_obj.save()
    return JsonResponse({'message': 'File uploaded successfully.',
                         'file_id': file_obj.file_id})


@csrf_exempt
@require_http_methods(['POST'])
def download_file(request):
    data = json.loads(request.body)
    file_id = data.get('file_id')
    file_obj = File.objects.get(file_id=file_id)
    response = HttpResponse(file_obj.file_content.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_obj.file_content.name}"'

    return response


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def upload_saved_document(request, user):
    data_json = json.loads(request.body)
    document_id = data_json.get('document_id')
    document_content = data_json.get('document_content')
    if not Document.objects.filter(document_id=document_id).exists():
        return JsonResponse({'errno': 4030, 'msg': "该文档类不存在"})
    document = Document.objects.get(document_id=document_id)
    directory = document.document_directory
    project = directory.directory_project
    team = project.project_team
    if not document.document_allow_edit:
        if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
            return JsonResponse({'errno': 4031, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4032, 'msg': "项目在回收站中，无法操作"})
    if document.document_recycle:
        return JsonResponse({'errno': 4033, 'msg': "文档在回收站中，无法操作"})
    savedDocument = SavedDocument.objects.create(sd_document=document, sd_file=document_content)
    document.document_saves.add(savedDocument)
    return JsonResponse({'errno': 0, 'msg': '副本保存成功.'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def create_document(request, user):
    data_json = json.loads(request.body)
    document_name = data_json.get('document_name')
    directory_id = data_json.get('directory_id')
    template_id = data_json.get('template_id')
    if not Directory.objects.filter(directory_id=directory_id).exists():
        return JsonResponse({'errno': 4040, 'msg': "该文件夹不存在"})
    directory = Directory.objects.get(directory_id=directory_id)
    project = directory.directory_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4041, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4042, 'msg': "项目在回收站中，无法操作"})
    document = Document.objects.create(document_name=document_name, document_directory=directory)
    save = SavedDocument.objects.create(sd_document=document)
    if template_id:
        if not Template.objects.filter(template_id=template_id).exists():
            return JsonResponse({'errno': 4043, 'msg': "模板不存在"})
        template = Template.objects.get(template_id=template_id)
        save.sd_file = template.template_file
    save.save()
    document.document_saves.add(save)
    document.save()
    directory.directory_document.add(document)
    return JsonResponse({'errno': 0, 'msg': '创建文档成功', 'document_id': document.document_id})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def download_saved_document(request, user):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    if not Document.objects.filter(document_id=document_id).exists():
        return JsonResponse({'errno': 4050, 'msg': "该文档类不存在"})
    document = Document.objects.get(document_id=document_id)
    directory = document.document_directory
    project = directory.directory_project
    team = project.project_team
    if not document.document_allow_check:
        if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
            return JsonResponse({'errno': 4051, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4052, 'msg': "项目在回收站中，无法操作"})
    if document.document_recycle:
        return JsonResponse({'errno': 4053, 'msg': "文档在回收站中，无法操作"})
    recent_save = document.document_saves.last()
    return JsonResponse({'errno': 0, 'msg': '返回文档成功', 'document_content': recent_save.sd_file})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def show_document_list(request, user):
    data = json.loads(request.body)
    directory_id = data.get('directory_id')
    if not Directory.objects.filter(directory_id=directory_id).exists():
        return JsonResponse({'errno': 4060, 'msg': "该文件夹不存在"})
    directory = Directory.objects.get(directory_id=directory_id)
    project = directory.directory_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4061, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4062, 'msg': "项目在回收站中，无法操作"})
    documents = directory.directory_document.all()
    d_info = []
    for d in documents:
        d_info.append((d.to_json()))
    return JsonResponse({'errno': 0, 'msg': "文档列表查询成功", 'documentTable': d_info})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def delete_document(request, user):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    if not Document.objects.filter(document_id=document_id).exists():
        return JsonResponse({'errno': 4070, 'msg': "该文档类不存在"})
    document = Document.objects.get(document_id=document_id)
    directory = document.document_directory
    project = directory.directory_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4071, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4072, 'msg': "项目在回收站中，无法操作"})
    directory.directory_document.remove()
    document.delete()
    return JsonResponse({'errno': 0, 'msg': '文档删除成功'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def callback_document(request, user):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    savedDocument_id = data.get('savedDocument_id')
    if not Document.objects.filter(document_id=document_id).exists():
        return JsonResponse({'errno': 4080, 'msg': "该文档类不存在"})
    document = Document.objects.get(document_id=document_id)
    directory = document.document_directory
    project = directory.directory_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4081, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4082, 'msg': "项目在回收站中，无法操作"})
    if document.document_recycle:
        return JsonResponse({'errno': 4083, 'msg': "文档在回收站中，无法操作"})
    saves = document.document_saves.all()
    for s in saves:
        if s.sd_id > savedDocument_id:
            s.delete()
    recent_save = document.document_saves.last()
    return JsonResponse({'errno': 0, 'msg': '退回存档成功', 'document_content': recent_save.sd_file})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def show_save(request, user):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    if not Document.objects.filter(document_id=document_id).exists():
        return JsonResponse({'errno': 4090, 'msg': "该文档类不存在"})
    document = Document.objects.get(document_id=document_id)
    directory = document.document_directory
    project = directory.directory_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4091, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4092, 'msg': "项目在回收站中，无法操作"})
    if document.document_recycle:
        return JsonResponse({'errno': 4093, 'msg': "文档在回收站中，无法操作"})
    saves = document.document_saves.all()
    s_info = []
    for s in saves:
        s_info.append({
            "sd_id": s.sd_id,
            "sd_file": s.sd_file,
            "sd_saved_time": s.sd_saved_time.strftime("%Y-%m-%d %H:%M:%S")
        })
    return JsonResponse({'errno': 0, 'msg': '返回副本成功', 's_info': s_info})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def search_save(request, user):
    data = json.loads(request.body)
    save_id = data.get('save_id')
    if not SavedDocument.objects.filter(sd_id=save_id).exists():
        return JsonResponse({'errno': 4100, 'msg': "该副本不存在"})
    recent_save = SavedDocument.objects.get(sd_id=save_id)
    document = recent_save.sd_document
    directory = document.document_directory
    project = directory.directory_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4101, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4102, 'msg': "项目在回收站中，无法操作"})
    if document.document_recycle:
        return JsonResponse({'errno': 4103, 'msg': "文档在回收站中，无法操作"})
    return JsonResponse({'errno': 0, 'msg': '查找文档副本成功', 'document_content': recent_save.sd_file})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def create_prototype(request, user):
    data_json = json.loads(request.body)
    prototype_name = data_json.get('prototype_name')
    project_id = data_json.get('project_id')
    template_id = data_json.get('template_id')
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 4110, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4111, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4112, 'msg': "项目在回收站中，无法操作"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    prototype = Prototype.objects.create(prototype_name=prototype_name, prototype_project=project,
                                         prototype_creator=team_member)
    if template_id:
        template = Template.objects.get(template_id=template_id)
        prototype.prototype_components = template.template_file
    prototype.prototype_change_time = prototype.prototype_create_time
    prototype.save()
    project.project_prototype.add(prototype)
    return JsonResponse({'errno': 0, 'message': '原型新建成功'})


# @csrf_exempt
# @require_http_methods(['POST'])
# def show_prototype(request):
#     data_json = json.loads(request.body)
#     prototype_name = data_json.get('prototype_name')
#     team_id = data_json.get('team_id')
#     creator_id = data_json.get('creator_id')
#     team = Team.objects.get(team_id=team_id)
#     creator = User.objects.get(user_id=creator_id)
#     prototype = Prototype.objects.create(prototype_name=prototype_name, prototype_team=team, prototype_creator=creator)
#     uploaded_file = request.FILES['file']
#     prototype.prototype_file = uploaded_file
#     prototype.save()
#
#     return JsonResponse({'errno': 0, 'message': 'File uploaded successfully.'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def upload_prototype(request, user):
    data_json = json.loads(request.body)
    prototype_id = data_json.get('prototype_id')
    if not Prototype.objects.filter(prototype_id=prototype_id).exists():
        return JsonResponse({'errno': 4120, 'msg': "该原型不存在"})
    prototype = Prototype.objects.get(prototype_id=prototype_id)
    project = prototype.prototype_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4122, 'msg': "项目在回收站中，无法操作"})
    if prototype.prototype_recycle:
        return JsonResponse({'errno': 4123, 'msg': "原型在回收站中，无法操作"})
    uploaded_file = request.FILES['file']
    prototype.prototype_file = uploaded_file
    prototype.prototype_change_time = now()
    prototype.save()
    return JsonResponse({'errno': 0, 'message': '原型修改成功'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def delete_prototype(request, user):
    data_json = json.loads(request.body)
    prototype_id = data_json.get('prototype_id')
    if not Prototype.objects.filter(prototype_id=prototype_id).exists():
        return JsonResponse({'errno': 4130, 'msg': "该原型不存在"})
    prototype = Prototype.objects.get(prototype_id=prototype_id)
    project = prototype.prototype_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4131, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4132, 'msg': "项目在回收站中，无法操作"})
    project.project_prototype.remove(prototype)
    prototype.delete()
    return JsonResponse({'errno': 0, 'message': '删除成功.'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def show_prototype_list(request, user):
    data_json = json.loads(request.body)
    project_id = data_json.get('project_id')
    recycle = data_json.get('recycle')
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 4140, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4141, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4142, 'msg': "项目在回收站中，无法操作"})
    prototypes = project.project_prototype.filter(prototype_recycle=recycle)
    p_info = []
    for prototype in prototypes:
        p_info.append(prototype.to_json())
    return JsonResponse({'errno': 0, 'msg': '返回原型列表成功', 'protoTable': p_info})


def copy_document(new_directory, old_document):
    new_document = Document()
    new_document.document_name = old_document.document_name
    new_document.document_directory = new_directory
    new_document.document_recycle = old_document.document_recycle
    new_document.document_editable = old_document.document_editable

    new_document.save()
    new_directory.directory_document.add(new_document)
    for old_saved_document in old_document.document_saves.all():
        new_saved_document = SavedDocument()
        new_saved_document.sd_saved_time = old_saved_document.sd_saved_time
        new_saved_document.sd_document = new_document
        if old_saved_document.sd_file:
            old_file_path = old_saved_document.sd_file.path
            old_file_name, old_file_extension = os.path.splitext(os.path.basename(old_file_path))

            # 假设 new_saved_document 是新的 SavedDocument 实例
            new_file_id = new_saved_document.pk  # 新文件的 ID
            new_file_path = f'SavedDocument/{old_file_name}_{new_file_id}{old_file_extension}'

            shutil.copy(old_file_path, new_file_path)
            new_saved_document.sd_file.name = new_file_path
        new_saved_document.save()
        new_document.document_saves.add(new_saved_document)
    return new_document


def copy_directory(new_project, old_directory):
    new_directory = Directory()
    new_directory.directory_name = old_directory.directory_name
    new_directory.directory_project = new_project

    new_directory.save()

    for old_document in old_directory.directory_document.all():
        copy_document(new_directory, old_document)

    return new_directory


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def search_prototype(request, user):
    data = json.loads(request.body)
    prototype_id = data.get('prototype_id')
    if not Prototype.objects.filter(prototype_id=prototype_id).exists():
        return JsonResponse({'errno': 4150, 'msg': "该原型不存在"})
    prototype = Prototype.objects.get(prototype_id=prototype_id)
    project = prototype.prototype_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4151, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4152, 'msg': "项目在回收站中，无法操作"})
    if prototype.prototype_recycle:
        return JsonResponse({'errno': 4153, 'msg': "原型在回收站中，无法操作"})
    prototype_components = prototype.prototype_components
    return JsonResponse({'errno': 0, 'msg': '查找原型成功', 'components': prototype_components})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_prototype(request, user):
    data = json.loads(request.body)
    prototype_id = data.get('prototype_id')
    prototype_name = data.get('prototype_name')
    prototype_recycle = data.get('prototype_recycle')
    if not Prototype.objects.filter(prototype_id=prototype_id).exists():
        return JsonResponse({'errno': 4160, 'msg': "该原型不存在"})
    prototype = Prototype.objects.get(prototype_id=prototype_id)
    project = prototype.prototype_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4161, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4162, 'msg': "项目在回收站中，无法操作"})
    if prototype.prototype_recycle:
        return JsonResponse({'errno': 4163, 'msg': "原型在回收站中，无法操作"})
    prototype.prototype_name = prototype_name
    prototype.prototype_recycle = prototype_recycle
    prototype.save()
    return JsonResponse({'errno': 0, 'msg': '修改原型成功.'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_document(request, user):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    document_name = data.get('document_name')
    if not Document.objects.filter(document_id=document_id).exists():
        return JsonResponse({'errno': 4170, 'msg': "该文档类不存在"})
    document = Document.objects.get(document_id=document_id)
    directory = document.document_directory
    project = directory.directory_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4171, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4172, 'msg': "项目在回收站中，无法操作"})
    if document.document_recycle:
        return JsonResponse({'errno': 4173, 'msg': "文档在回收站中，无法操作"})
    document.document_name = document_name
    document.save()
    return JsonResponse({'errno': 0, 'msg': '文档修改成功.'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_document_permission(request, user):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    permission = data.get('permission')
    if not Document.objects.filter(document_id=document_id).exists():
        return JsonResponse({'errno': 4180, 'msg': "该文档类不存在"})
    document = Document.objects.get(document_id=document_id)
    directory = document.document_directory
    project = directory.directory_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4181, 'msg': "当前用户不在该团队内"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    if team_member.tm_user_permissions == "member":
        return JsonResponse({'errno': 4182, 'msg': "当前用户权限不足"})
    if project.project_recycle:
        return JsonResponse({'errno': 4183, 'msg': "项目在回收站中，无法操作"})
    if document.document_recycle:
        return JsonResponse({'errno': 4184, 'msg': "文档在回收站中，无法操作"})
    if permission == "edit":
        document.document_allow_check = True
        document.document_allow_edit = True
    elif permission == "check":
        document.document_allow_check = True
        document.document_allow_edit = False
    else:
        document.document_allow_check = False
        document.document_allow_edit = False
    document.save()
    return JsonResponse({'errno': 0, 'msg': '修改权限成功'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_document_recycle(request, user):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    recycle = data.get('recycle')
    if not Document.objects.filter(document_id=document_id).exists():
        return JsonResponse({'errno': 4190, 'msg': "该文档类不存在"})
    document = Document.objects.get(document_id=document_id)
    directory = document.document_directory
    project = directory.directory_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4191, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4192, 'msg': "项目在回收站中，无法操作"})
    if recycle == "True":
        if document.document_recycle:
            return JsonResponse({'errno': 4193, 'msg': '文档已在回收站'})
        document.document_recycle = True
        directory.directory_document.remove(document)
        project.project_recycle_bin.directory_document.add(document)
        document.document_directory = project.project_recycle_bin
    else:
        if not document.document_recycle:
            return JsonResponse({'errno': 4194, 'msg': '文档不在回收站'})
        document.document_recycle = False
        directory.directory_document.remove(document)
        project.project_root_directory.directory_document.add(document)
        document.document_directory = project.project_root_directory
    document.save()
    return JsonResponse({'errno': 0, 'msg': '修改状态成功'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_prototype_recycle(request, user):
    data = json.loads(request.body)
    prototype_id = data.get('prototype_id')
    recycle = data.get('recycle')
    if not Prototype.objects.filter(prototype_id=prototype_id).exists():
        return JsonResponse({'errno': 4200, 'msg': "该原型不存在"})
    prototype = Prototype.objects.get(prototype_id=prototype_id)
    project = prototype.prototype_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4201, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4202, 'msg': "项目在回收站中，无法操作"})
    if recycle == "True":
        if prototype.prototype_recycle:
            return JsonResponse({'errno': 4203, 'msg': '原型已在回收站'})
        prototype.prototype_recycle = True
    else:
        if not prototype.prototype_recycle:
            return JsonResponse({'errno': 4204, 'msg': '原型不在回收站'})
        prototype.prototype_recycle = False
    prototype.save()
    return JsonResponse({'errno': 0, 'msg': '修改状态成功.'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def create_directory(request, user):
    data = json.loads(request.body)
    project_id = data.get('project_id')
    name = data.get('name')
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 4210, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4211, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4212, 'msg': "项目在回收站中，无法操作"})
    directory = Directory.objects.create(directory_name=name)
    project.project_directory.add(directory)
    directory.directory_project = project
    directory.save()
    return JsonResponse({'errno': 0, 'msg': '文件夹创建成功', 'directory_id': directory.directory_id})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def delete_directory(request, user):
    data = json.loads(request.body)
    directory_id = data.get('directory_id')
    if not Directory.objects.filter(directory_id=directory_id).exists():
        return JsonResponse({'errno': 4220, 'msg': "该文件夹不存在"})
    directory = Directory.objects.get(directory_id=directory_id)
    project = directory.directory_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4221, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4222, 'msg': "项目在回收站中，无法操作"})
    project.project_directory.remove(directory)
    directory.delete()
    return JsonResponse({'errno': 0, 'msg': '文件夹删除成功'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def show_directory(request, user):
    data = json.loads(request.body)
    project_id = data.get('project_id')
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 4230, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4231, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4232, 'msg': "项目在回收站中，无法操作"})
    directories = project.project_directory.all()
    d_info = []
    for directory in directories:
        d_info.append(directory.to_json())
    return JsonResponse({'errno': 0, 'd_info': d_info, 'root_id': project.project_root_directory.directory_id, 'recycle_id': project.project_recycle_bin.directory_id})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def save_prototype_components(request, user):
    data = json.loads(request.body)
    prototype_id = data.get('prototype_id')
    prototype_components = data.get('prototype_components')
    if not Prototype.objects.filter(prototype_id=prototype_id).exists():
        return JsonResponse({'errno': 4240, 'msg': "该原型不存在"})
    prototype = Prototype.objects.get(prototype_id=prototype_id)
    project = prototype.prototype_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4241, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4242, 'msg': "项目在回收站中，无法操作"})
    if prototype.prototype_recycle:
        return JsonResponse({'errno': 4243, 'msg': "原型在回收站中，无法操作"})
    prototype.prototype_components = prototype_components
    prototype.save()
    return JsonResponse({'errno': 0, 'msg': '原型修改成功'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def get_prototype_components(request, user):
    data = json.loads(request.body)
    prototype_id = data.get('prototype_id')
    if not Prototype.objects.filter(prototype_id=prototype_id).exists():
        return JsonResponse({'errno': 4250, 'msg': "该原型不存在"})
    prototype = Prototype.objects.get(prototype_id=prototype_id)
    project = prototype.prototype_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4251, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4252, 'msg': "项目在回收站中，无法操作"})
    if prototype.prototype_recycle:
        return JsonResponse({'errno': 4253, 'msg': "原型在回收站中，无法操作"})
    prototype_components = prototype.prototype_components
    return JsonResponse({'errno': 0, 'msg': '返回原型成功', 'components': prototype_components})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def move_document(request, user):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    directory_id = data.get('directory_id')
    if not Document.objects.filter(document_id=document_id).exists():
        return JsonResponse({'errno': 4260, 'msg': "该文档类不存在"})
    document = Document.objects.get(document_id=document_id)
    old_directory = document.document_directory
    project = old_directory.directory_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4261, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4262, 'msg': "项目在回收站中，无法操作"})
    if document.document_recycle:
        return JsonResponse({'errno': 4263, 'msg': "文档在回收站中，无法操作"})
    if not Directory.objects.filter(directory_id=directory_id).exists():
        return JsonResponse({'errno': 4264, 'msg': "该文件夹不存在"})
    new_directory = Directory.objects.get(directory_id=directory_id)
    if new_directory.directory_recycle:
        return JsonResponse({'errno': 4265, 'msg': "文件夹在回收站中，无法操作"})
    if new_directory.directory_project != project:
        return JsonResponse({'errno': 4266, 'msg': "文件与文档不在同一项目中"})
    old_directory.directory_document.remove(document)
    new_directory.directory_document.add(document)
    document.document_directory = new_directory
    document.save()
    return JsonResponse({'errno': 0, 'msg': '文件移动成功'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def show_directory_tree(request, user):
    data = json.loads(request.body)
    project_id = data.get('project_id')
    project = Project.objects.get(project_id=project_id)
    items_info = []
    if project.project_root_directory is not None:
        for document in project.project_root_directory.directory_document.all():
            document_info = {
                'id': document.document_id,
                'label': document.document_name,
                'isFolder': False,
                'parent_id': project.project_root_directory.directory_id
            }
            items_info.append(document_info)
    if project.project_directory.exists():
        for directory in project.project_directory.all():
            children_info = []
            if directory.directory_document.exists():
                for document in directory.directory_document.all():
                    document_info = {
                        'id': document.document_id,
                        'label': document.document_name,
                        'isFolder': False,
                        'parent_id': directory.directory_id
                    }
                    children_info.append(document_info)
            directory_info = {
                'id': directory.directory_id,
                'label': directory.directory_name,
                'isFolder': True,
                'parent_id': project.project_root_directory.directory_id,
                'children': children_info
            }
            items_info.append(directory_info)

    return JsonResponse({'errno': 0, 'items_info': items_info, 'root_id': project.project_root_directory.directory_id})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def show_recycle_tree(request, user):
    data = json.loads(request.body)
    project_id = data.get('project_id')
    project = Project.objects.get(project_id=project_id)
    items_info = []

    if project.project_recycle_bin is not None:
        for document in project.project_recycle_bin.directory_document.all():
            document_info = {
                'id': document.document_id,
                'label': document.document_name,
                'isFolder': False,
                'parent_id': project.project_recycle_bin.directory_id
            }
            items_info.append(document_info)

    if project.project_recycle_directory.exists():
        for directory in project.project_recycle_directory.all():
            children_info = []
            if directory.directory_document.exists():
                for document in directory.directory_document.all():
                    document_info = {
                        'id': document.document_id,
                        'label': document.document_name,
                        'isFolder': False,
                        'parent_id': directory.directory_id
                    }
                    children_info.append(document_info)
            directory_info = {
                'id': directory.directory_id,
                'label': directory.directory_name,
                'isFolder': True,
                'parent_id': project.project_recycle_bin.directory_id,
                'children': children_info
            }
            items_info.append(directory_info)

    return JsonResponse({'errno': 0, 'items_info': items_info, 'recycle_id': project.project_recycle_bin.directory_id})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def search_document(request, user):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    if not Document.objects.filter(document_id=document_id).exists():
        return JsonResponse({'errno': 4040, 'msg': "该文件不存在"})
    document = Document.objects.get(document_id=document_id)
    project = document.document_directory.directory_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4061, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4062, 'msg': "项目在回收站中，无法操作"})
    return JsonResponse({'errno': 0, 'msg': "文档查询成功", 'document_info': document.to_json()})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_directory_recycle(request, user):
    data = json.loads(request.body)
    directory_id = data.get('directory_id')
    recycle = data.get('recycle')
    if not Directory.objects.filter(directory_id=directory_id).exists():
        return JsonResponse({'errno': 4190, 'msg': "该文档类不存在"})
    directory = Directory.objects.get(directory_id=directory_id)
    project = directory.directory_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 4191, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 4192, 'msg': "项目在回收站中，无法操作"})
    if recycle == "True":
        if directory.directory_recycle:
            return JsonResponse({'errno': 4193, 'msg': '文档已在回收站'})
        directory.directory_recycle = True
        project.project_directory.remove(directory)
        project.project_recycle_directory.add(directory)
        for document in directory.directory_document.all():
            document.document_recycle = True
            document.save()
    else:
        if not directory.directory_recycle:
            return JsonResponse({'errno': 4194, 'msg': '文档不在回收站'})
        directory.directory_recycle = False
        project.project_recycle_directory.remove(directory)
        project.project_directory.add(directory)
        for document in directory.directory_document.all():
            document.document_recycle = False
            document.save()
    directory.save()
    return JsonResponse({'errno': 0, 'msg': '修改状态成功'})


@csrf_exempt
@require_http_methods(['POST'])
def create_template(request):
    data = json.loads(request.body)
    template_name = data.get('template_name')
    template_file = data.get('template_file')
    template_type = data.get('template_type')
    template = Template.objects.create(template_name=template_name, template_file=template_file, template_type=template_type)
    return JsonResponse({'errno': 0, 'msg': "创建模板成功", 'template_id': template.template_id})


@csrf_exempt
@require_http_methods(['POST'])
def show_template_list(request):
    data = json.loads(request.body)
    template_type = data.get('template_type')
    template_list = Template.objects.filter(template_type=template_type).all()
    t_info = []
    for template in template_list:
        t_info.append(template.to_json())
    return JsonResponse({'errno': 0, 'msg': "返回模板成功", 'template_info': t_info})

