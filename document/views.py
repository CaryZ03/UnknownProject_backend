from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from team.models import *
from message.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import File
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
