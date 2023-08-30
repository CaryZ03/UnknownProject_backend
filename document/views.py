import os
import shutil

from django.forms import model_to_dict
from django.utils.timezone import now

from project.models import Project
from team.models import *
from message.models import *
from .models import File, Document, SavedDocument, Prototype
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
    if not Document.objects.filter(document_id=document_id).exists():
        return JsonResponse({'errno': 3120, 'msg': "该文档类不存在"})
    document = Document.objects.get(document_id=document_id)
    project = document.document_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
    if document.document_recycle:
        return JsonResponse({'errno': 3122, 'msg': "文档在回收站中，无法操作"})
    uploaded_file = request.FILES['file']
    savedDocument = SavedDocument.objects.create(sd_document=document, sd_file=uploaded_file)
    document.document_saves.add(savedDocument)
    return JsonResponse({'errno': 0, 'message': '副本保存成功.'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def create_document(request, user):
    data_json = json.loads(request.body)
    document_name = data_json.get('document_name')
    project_id = data_json.get('project_id')
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3120, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
    document = Document.objects.create(document_name=document_name, document_project=project)
    project.project_document.add(document)
    return JsonResponse({'errno': 0, 'message': '创建文档成功', 'document_id': document.document_id})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def download_saved_document(request, user):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    if not Document.objects.filter(document_id=document_id).exists():
        return JsonResponse({'errno': 3120, 'msg': "该文档类不存在"})
    document = Document.objects.get(document_id=document_id)
    project = document.document_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
    if document.document_recycle:
        return JsonResponse({'errno': 3122, 'msg': "文档在回收站中，无法操作"})
    recent_save = document.document_saves.last()
    response = HttpResponse(recent_save.sd_file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{recent_save.sd_file.name}"'
    return JsonResponse({'errno': 0, 'message': 'File uploaded successfully.', 'document_id': document.document_id})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def show_document_list(request, user):
    data = json.loads(request.body)
    project_id = data.get('project_id')
    recycle = data.get('recycle')
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3120, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
    documents = project.project_document.filter(document_recycle=recycle)
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
        return JsonResponse({'errno': 3120, 'msg': "该文档类不存在"})
    document = Document.objects.get(document_id=document_id)
    project = document.document_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
    project.project_document.remove(document)
    document.delete()
    return JsonResponse({'errno': 0, 'message': '文档删除成功'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def callback_document(request, user):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    savedDocument_id = data.get('savedDocument_id')
    if not Document.objects.filter(document_id=document_id).exists():
        return JsonResponse({'errno': 3120, 'msg': "该文档类不存在"})
    document = Document.objects.get(document_id=document_id)
    project = document.document_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
    if document.document_recycle:
        return JsonResponse({'errno': 3122, 'msg': "文档在回收站中，无法操作"})
    saves = document.document_saves.all()
    for s in saves:
        if s.sd_id > savedDocument_id:
            s.delete()
    recent_save = document.document_saves.last()
    response = HttpResponse(recent_save.sd_file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{recent_save.sd_file.name}"'
    return JsonResponse({'errno': 0, 'message': '文档回滚成功.'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def show_save(request, user):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    if not Document.objects.filter(document_id=document_id).exists():
        return JsonResponse({'errno': 3120, 'msg': "该文档类不存在"})
    document = Document.objects.get(document_id=document_id)
    project = document.document_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
    if document.document_recycle:
        return JsonResponse({'errno': 3122, 'msg': "文档在回收站中，无法操作"})
    saves = document.document_saves.all()
    s_info = []
    for s in saves:
        s_info.append(s.to_json())
    return JsonResponse({'errno': 0, 'message': '返回副本成功', 's_info': s_info})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def search_save(request, user):
    data = json.loads(request.body)
    save_id = data.get('save_id')
    if not SavedDocument.objects.filter(sd_id=save_id).exists():
        return JsonResponse({'errno': 3120, 'msg': "该副本不存在"})
    recent_save = SavedDocument.objects.create(sd_id=save_id)
    document = recent_save.sd_document
    project = document.document_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
    if document.document_recycle:
        return JsonResponse({'errno': 3122, 'msg': "文档在回收站中，无法操作"})
    response = HttpResponse(recent_save.sd_file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{recent_save.sd_file.name}"'
    return JsonResponse({'errno': 0, 'message': '查找文档副本成功.'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def create_prototype(request, user):
    data_json = json.loads(request.body)
    prototype_name = data_json.get('prototype_name')
    project_id = data_json.get('project_id')
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({'errno': 3120, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
    team_member = TeamMember.objects.get(tm_team_id=team, tm_user_id=user)
    prototype = Prototype.objects.create(prototype_name=prototype_name, prototype_project=project, prototype_creator=team_member)
    prototype.prototype_change_time = prototype.prototype_create_time
    # uploaded_file = request.FILES['file']
    # prototype.prototype_file = uploaded_file
    prototype.save()
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
        return JsonResponse({'errno': 3120, 'msg': "该原型不存在"})
    prototype = Prototype.objects.get(prototype_id=prototype_id)
    project = prototype.prototype_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
    if prototype.prototype_recycle:
        return JsonResponse({'errno': 3122, 'msg': "原型在回收站中，无法操作"})
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
        return JsonResponse({'errno': 3120, 'msg': "该原型不存在"})
    prototype = Prototype.objects.get(prototype_id=prototype_id)
    project = prototype.prototype_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
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
        return JsonResponse({'errno': 3120, 'msg': "该项目不存在"})
    project = Project.objects.get(project_id=project_id)
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
    prototypes = project.project_prototype.filter(prototype_recycle=recycle)
    p_info = []
    for prototype in prototypes:
        p_info.append(prototype.to_json())
    return JsonResponse({'errno': 0, 'msg': '返回原型列表成功', 'protoTable': p_info})


def copy_document(project, old_document):
    new_document = Document()
    new_document.document_name = old_document.document_name
    new_document.document_project = project
    new_document.document_recycle = old_document.document_recycle
    new_document.document_editable = old_document.document_editable

    new_document.save()
    project.project_document.add(new_document)
    for old_saved_document in old_document.document_saves:
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


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def search_prototype(request, user):
    data = json.loads(request.body)
    prototype_id = data.get('prototype_id')
    if not Prototype.objects.filter(prototype_id=prototype_id).exists():
        return JsonResponse({'errno': 3120, 'msg': "该原型不存在"})
    prototype = Prototype.objects.get(prototype_id=prototype_id)
    project = prototype.prototype_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
    if prototype.prototype_recycle:
        return JsonResponse({'errno': 3122, 'msg': "原型在回收站中，无法操作"})
    response = HttpResponse(prototype.prototype_file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{prototype.prototype_file.name}"'
    return JsonResponse({'errno': 0, 'message': '查找原型成功.'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_prototype(request, user):
    data = json.loads(request.body)
    prototype_id = data.get('prototype_id')
    prototype_name = data.get('name')
    prototype_recycle = data.get('recycle')
    if not Prototype.objects.filter(prototype_id=prototype_id).exists():
        return JsonResponse({'errno': 3120, 'msg': "该原型不存在"})
    prototype = Prototype.objects.get(prototype_id=prototype_id)
    project = prototype.prototype_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
    if prototype.prototype_recycle:
        return JsonResponse({'errno': 3122, 'msg': "原型在回收站中，无法操作"})
    prototype.prototype_name = prototype_name
    prototype.prototype_recycle = prototype_recycle
    prototype.save()
    return JsonResponse({'errno': 0, 'message': '查找原型成功.'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_document(request, user):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    document_name = data.get('name')
    document_recycle = data.get('recycle')
    if not Document.objects.filter(document_id=document_id).exists():
        return JsonResponse({'errno': 3120, 'msg': "该文档类不存在"})
    document = Document.objects.get(document_id=document_id)
    project = document.document_project
    team = project.project_team
    if not TeamMember.objects.filter(tm_team_id=team, tm_user_id=user).exists():
        return JsonResponse({'errno': 3121, 'msg': "当前用户不在该团队内"})
    if project.project_recycle:
        return JsonResponse({'errno': 3122, 'msg': "项目在回收站中，无法操作"})
    if document.document_recycle:
        return JsonResponse({'errno': 3122, 'msg': "文档在回收站中，无法操作"})
    document.document_recycle = document_recycle
    document.document_name = document_name
    document.save()
    return JsonResponse({'errno': 0, 'message': '文档回滚成功.'})
