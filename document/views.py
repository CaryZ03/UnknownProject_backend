from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from team.models import *
from message.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import File, Document, SavedDocument
from django.http import HttpResponse


@csrf_exempt
@require_http_methods(['POST'])
def upload_file(request):
    uploaded_file = request.FILES['file']
    file_obj = File(file_content=uploaded_file)
    file_obj.save()
    return JsonResponse({'message': 'File uploaded successfully.'})


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
