from team.models import *
from message.models import *
from .models import File, Document, SavedDocument
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http.response import JsonResponse
import json


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
@require_http_methods(['POST'])
def upload_saved_document(request):
    data_json = json.loads(request.body)
    document_id = data_json.get('document_id')
    document = Document.objects.get(document_id=document_id)
    uploaded_file = request.FILES['file']
    savedDocument = SavedDocument.objects.create(sd_document=document, sd_file=uploaded_file)
    document.document_saves.add(savedDocument)

    return JsonResponse({'errno': 0, 'message': 'File uploaded successfully.'})


@csrf_exempt
@require_http_methods(['POST'])
def create_document(request):
    data_json = json.loads(request.body)
    document_name = data_json.get('document_name')
    team_id = data_json.get('team_id')
    team = Team.objects.get(team_id=team_id)
    document = Document.objects.create(document_name=document_name, document_team=team)

    return JsonResponse({'errno': 0, 'message': 'File uploaded successfully.', 'document_id': document.document_id})


@csrf_exempt
@require_http_methods(['POST'])
def download_saved_document(request):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    document = Document.objects.get(document_id=document_id)
    recent_save = document.document_saves.last()
    response = HttpResponse(recent_save.sd_file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{recent_save.sd_file.name}"'

    return JsonResponse({'errno': 0, 'message': 'File uploaded successfully.', 'document_id': document.document_id})


@csrf_exempt
@require_http_methods(['POST'])
def delete_document_all(request):
    data = json.loads(request.body)
    document_id = data.get('document_id')
    document = Document.objects.get(document_id=document_id)
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
        s_info.append(s.sd_id)
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
