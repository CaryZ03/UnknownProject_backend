import os
import shutil

from django.forms import model_to_dict

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
    return JsonResponse({'errno': 0, 'message': 'File uploaded successfully.', 'document_id': document.document_id})


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
    recent_save = document.document_saves.last()
    response = HttpResponse(recent_save.sd_file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{recent_save.sd_file.name}"'
    return JsonResponse({'errno': 0, 'message': 'File uploaded successfully.', 'document_id': document.document_id})


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

    return JsonResponse({'errno': 0, 'message': 'File deleted successfully.'})


@csrf_exempt
@require_http_methods(['POST'])
def callback_document(request):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    savedDocument_id = data.get('savedDocument_id')
    document = Document.objects.get(document_id=document_id)
    saves = document.document_saves.all()
    for s in saves:
        if s.sd_id > savedDocument_id:
            s.delete()

    recent_save = document.document_saves.last()
    response = HttpResponse(recent_save.sd_file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{recent_save.sd_file.name}"'

    return JsonResponse({'errno': 0, 'message': 'File callback successfully.'})


@csrf_exempt
@require_http_methods(['POST'])
def show_save(request):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    document = Document.objects.get(document_id=document_id)
    saves = document.document_saves.all()

    s_info = []
    for s in saves:
        s_info.append(s.to_json())
    return JsonResponse({'errno': 0, 'message': 'File callback successfully.', 's_info': s_info})


@csrf_exempt
@require_http_methods(['POST'])
def search_save(request):
    data = json.loads(request.body)
    save_id = data.get('save_id')
    recent_save = SavedDocument.objects.create(sd_id=save_id)
    response = HttpResponse(recent_save.sd_file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{recent_save.sd_file.name}"'
    return JsonResponse({'errno': 0, 'message': 'File callback successfully.'})


@csrf_exempt
@require_http_methods(['POST'])
def upload_prototype(request):
    data_json = json.loads(request.body)
    prototype_name = data_json.get('prototype_name')
    team_id = data_json.get('team_id')
    creator_id = data_json.get('creator_id')
    team = Team.objects.get(team_id=team_id)
    creator = User.objects.get(user_id=creator_id)
    prototype = Prototype.objects.create(prototype_name=prototype_name, prototype_team=team, prototype_creator=creator)
    uploaded_file = request.FILES['file']
    prototype.prototype_file = uploaded_file
    prototype.save()

    return JsonResponse({'errno': 0, 'message': 'File uploaded successfully.'})


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
@require_http_methods(['POST'])
def create_prototype(request):
    data_json = json.loads(request.body)
    prototype_name = data_json.get('prototype_name')
    project_id = data_json.get('project_id')
    creator_id = data_json.get('creator_id')
    project = Project.objects.get(project_id=project_id)
    creator = User.objects.get(user_id=creator_id)
    prototype = Prototype.objects.create(prototype_name=prototype_name, prototype_project=project, prototype_creator=creator)
    project.project_prototype.add(prototype)
    # uploaded_file = request.FILES['file']
    # prototype.prototype_file = uploaded_file
    # prototype.save()
    return JsonResponse({'errno': 0, 'message': 'File uploaded successfully.'})


@csrf_exempt
@require_http_methods(['POST'])
def delete_prototype(request):
    data_json = json.loads(request.body)
    prototype_id = data_json.get('prototype_id')
    prototype = Prototype.objects.get(prototype_id=prototype_id)
    project = prototype.prototype_project
    project.project_prototype.remove(prototype)
    prototype.delete()
    # uploaded_file = request.FILES['file']
    # prototype.prototype_file = uploaded_file
    # prototype.save()
    return JsonResponse({'errno': 0, 'message': '删除成功.'})


@csrf_exempt
@require_http_methods(['POST'])
def show_prototype(request):
    data_json = json.loads(request.body)
    project_id = data_json.get('project_id')
    project = Project.objects.get(project_id=project_id)
    prototypes = project.project_prototype.add()
    # uploaded_file = request.FILES['file']
    # prototype.prototype_file = uploaded_file
    # prototype.save()
    p_info = []
    for prototype in prototypes:
        p_info.append(prototype.to_json())
    return JsonResponse({'errno': 0, 'msg': '返回原型列表成功', 'user_info': p_info})


@csrf_exempt
@require_http_methods(['POST'])
def show_document(request):
    data = json.loads(request.body)
    project_id = data.get('project_id')
    project = Project.objects.get(project_id=project_id)
    document_info_list = []
    for document in project.document_list:
        document_info_list.append(document.to_json())
    return JsonResponse({"errno": 0, "msg": "返回文件列表成功", "document_info_list": document_info_list})


def copy_document(project, old_document):
    data = model_to_dict(old_document)
    new_document = Document(**data)
    new_document.pk = None
    new_document.requirement_project = project
    new_document.save()
    project.project_document.add(new_document)
    for old_saved_document in old_document.document_saves:
        data = model_to_dict(old_saved_document)
        new_saved_document = SavedDocument(**data)
        new_saved_document.pk = None
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
