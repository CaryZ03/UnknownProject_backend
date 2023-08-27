import os
import re
from django.db.models import Q
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http.response import JsonResponse
from datetime import timedelta
from django.core.management.utils import get_random_secret_key
import json

from user.models import User, UserToken
from random import randint
from django.core.cache import cache
import smtplib
from email.mime.text import MIMEText
from email.header import Header

import base64
from django.core.files.base import ContentFile


def send_email_verification(email, code):
    # 邮件内容
    subject = "验证码"
    message = code
    sender = "2843004375@qq.com"  # 发件人邮箱
    receiver = email  # 收件人邮箱

    # 邮件对象
    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = sender
    msg["To"] = receiver

    # SMTP服务器和端口
    smtp_server = "smtp.qq.com"
    smtp_port = 465

    # 发件人邮箱和授权码
    username = "2843004375@qq.com"
    password = "atawlpndwpqodfhe"

    # 连接SMTP服务器并发送邮件
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(username, password)
        server.sendmail(sender, receiver, msg.as_string())


def create_token(user):
    token_key = get_random_secret_key()
    expire_time = now() + timedelta(minutes=user.user_expire_time)
    token = UserToken(key=token_key, user=user, expire_time=expire_time)
    token.save()

    return token.key


def get_avatar_base64(image):
    if image is None:
        return None
    with open(image.path, 'rb') as file:
        image_data = file.read()
        ext = os.path.splitext(image.path)[-1]
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
    # 'data:image/' + ext + ';base64,' +
    return base64_encoded


# def get_image_url(request):
#     city_name = request.POST.get('city_name')
#     city = City.objects.get(name=city_name)
#     return JsonResponse({'image_url': city.img.url})


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        token_key = request.headers.get('Authorization')
        token = UserToken.objects.filter(key=token_key).first()
        if token:
            if token.expire_time < now():
                return JsonResponse({'errno': 1002, 'msg': "登录信息已过期"})
            else:
                user = token.user
                return view_func(request, *args, user=user, **kwargs)
        else:
            return JsonResponse({'errno': 1001, 'msg': "未登录"})

    return wrapper


def not_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        token_key = request.headers.get('Authorization')
        token = UserToken.objects.filter(key=token_key).first()
        if token and token.expire_time > now():
            return JsonResponse({'errno': 1003, 'msg': "已有用户登录"})
        else:
            return view_func(request, *args, **kwargs)

    return wrapper


@csrf_exempt
@not_login_required
@require_http_methods(['POST'])
def user_register_check(request):
    data_json = json.loads(request.body)
    email = data_json.get('email')
    password1 = data_json.get('password1')
    password2 = data_json.get('password2')
    if User.objects.filter(user_email=email).exists():
        return JsonResponse({'errno': 1010, 'msg': "该邮箱已存在注册用户"})
    elif password1 != password2:
        return JsonResponse({'errno': 1011, 'msg': "两次输入的密码不同"})
    elif not bool(re.match('^(?=.*\\d)(?=.*[a-zA-Z]).{6,20}$', str(password1))):
        return JsonResponse({'errno': 1012, 'msg': "密码不合法"})
    else:
        return JsonResponse({'errno': 0, 'msg': "信息验证成功"})


@csrf_exempt
@require_http_methods(['POST'])
def send_verification_code(request):
    data_json = json.loads(request.body)
    email = data_json.get('email')
    code = randint(100000, 999999)
    cache.set(email, str(code), 120)
    send_email_verification(email, str(code))
    return JsonResponse({'errno': 0, 'msg': '邮件已发送'})


@csrf_exempt
@require_http_methods(['POST'])
def check_verification_code(request):
    data_json = json.loads(request.body)
    email = data_json.get('email')
    verification_code = data_json.get('verification_code')
    code = None
    if verification_code:
        code = cache.get(email)
    if code and code == verification_code:
        return JsonResponse({'errno': 0, 'msg': '验证码正确'})
    return JsonResponse({'errno': 1030, 'msg': '验证码错误'})


@csrf_exempt
@not_login_required
@require_http_methods(['POST'])
def user_register(request):
    data_json = json.loads(request.body)
    email = data_json.get('email')
    password1 = data_json.get('password1')
    password2 = data_json.get('password2')
    if User.objects.filter(user_email=email).exists():
        return JsonResponse({'errno': 1040, 'msg': "该邮箱已存在注册用户"})
    elif password1 != password2:
        return JsonResponse({'errno': 1041, 'msg': "两次输入的密码不同"})
    elif not bool(re.match('^(?=.*\\d)(?=.*[a-zA-Z]).{6,20}$', str(password1))):
        return JsonResponse({'errno': 1042, 'msg': "密码不合法"})
    else:
        new_user = User.objects.create(user_email=email, user_password=password1)
        new_user.user_name = new_user.user_id
        new_user.save()
        return JsonResponse({'errno': 0, 'msg': "注册成功"})


@csrf_exempt
@not_login_required
@require_http_methods(['POST'])
def user_login(request):
    data_json = json.loads(request.body)
    email = data_json.get('email')
    password = data_json.get('password')
    if not User.objects.filter(user_email=email).exists():
        return JsonResponse({'errno': 1050, 'msg': "用户不存在"})
    user = User.objects.get(user_email=email)
    if user.user_password != password:
        return JsonResponse({'errno': 1051, 'msg': "密码错误"})
    UserToken.objects.filter(user=user).delete()
    token_key = request.headers.get('Authorization')
    if token_key and UserToken.objects.filter(key=token_key).exists():
        token = UserToken.objects.get(key=token_key)
        token.expire_time = now() + timedelta(minutes=user.user_expire_time)
        token.save()
        token_key = token.key
    else:
        token_key = create_token(user)
    return JsonResponse({'errno': 0, 'msg': "登录成功", 'uid': user.user_id, 'token_key': token_key, 'user_name': user.user_name})


@csrf_exempt
@not_login_required
@require_http_methods(['POST'])
def reset_password_check(request):
    data_json = json.loads(request.body)
    email = data_json.get('email')
    password1 = data_json.get('password1')
    password2 = data_json.get('password2')
    if not User.objects.filter(user_email=email).exists():
        return JsonResponse({'errno': 1060, 'msg': "用户不存在"})
    if password1 != password2:
        return JsonResponse({'errno': 1061, 'msg': "两次输入的密码不同"})
    if not re.match('^(?=.*\\d)(?=.*[a-zA-Z]).{6,20}$', str(password1)):
        return JsonResponse({'errno': 1062, 'msg': "密码不合法"})
    return JsonResponse({'errno': 0, 'msg': "信息验证成功"})


@csrf_exempt
@not_login_required
@require_http_methods(['POST'])
def reset_password(request):
    data_json = json.loads(request.body)
    email = data_json.get('email')
    password1 = data_json.get('password1')
    password2 = data_json.get('password2')
    if not User.objects.filter(user_email=email).exists():
        return JsonResponse({'errno': 1070, 'msg': "用户不存在"})
    user = User.objects.get(user_email=email)
    if password1 != password2:
        return JsonResponse({'errno': 1071, 'msg': "两次输入的密码不同"})
    if not re.match('^(?=.*\\d)(?=.*[a-zA-Z]).{6,20}$', str(password1)):
        return JsonResponse({'errno': 1072, 'msg': "密码不合法"})
    user.user_password = password1
    user.save()
    return JsonResponse({'errno': 0, 'msg': "重置密码成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def logout(request, user):
    token_key = request.headers.get('Authorization')
    UserToken.objects.get(key=token_key).delete()
    return JsonResponse({'errno': 0, 'msg': "登出成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def cancel_account(request, user):
    user.delete()
    return JsonResponse({'errno': 0, 'msg': "注销成功"})


@csrf_exempt
@login_required
@require_http_methods(['GET'])
def check_profile_self(request, user):
    user_info = user.to_json()
    user_avatar = None
    if user.user_avatar:
        user_avatar = get_avatar_base64(user.user_avatar)
    return JsonResponse({'errno': 0, 'msg': '返回用户信息成功', 'user_info': user_info, 'user_avatar': user_avatar})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def change_profile(request, user):
    data_json = json.loads(request.body)
    username = data_json.get('username')
    password1 = data_json.get('password1')
    password2 = data_json.get('password2')
    signature = data_json.get('signature')
    real_name = data_json.get('real_name')
    visible = data_json.get('visible')
    tel = data_json.get('tel')
    expire_time = data_json.get('expire_time')
    if not bool(re.match("^[A-Za-z0-9][A-Za-z0-9_]{2,29}$", str(username))):
        return JsonResponse({'errno': 1110, 'msg': "用户名不合法"})
    if not bool(re.match("^[A-Za-z]{2,29}$", str(username))):
        return JsonResponse({'errno': 1111, 'msg': "真实姓名不合法"})
    elif password1 != password2:
        return JsonResponse({'errno': 1112, 'msg': "两次输入的密码不同"})
    elif not re.match('^(?=.*\\d)(?=.*[a-zA-Z]).{6,20}$', str(password1)):
        return JsonResponse({'errno': 1113, 'msg': "密码不合法"})
    else:
        user.user_name = username
        user.user_password = password1
        user.user_signature = signature
        user.user_tel = tel
        user.user_expire_time = expire_time
        user.user_real_name = real_name
        user.user_visible = visible
        user.save()
        return JsonResponse({'errno': 0, 'msg': '修改用户信息成功'})


@csrf_exempt
@login_required
@require_http_methods(['GET'])
def check_team_list(request, user, tm_list_type):
    if tm_list_type == 'created':
        teams = user.user_created_teams.all()
    elif tm_list_type == 'managed':
        teams = user.user_managed_teams.all()
    elif tm_list_type == 'joined':
        teams = user.user_joined_teams.all()
    else:
        return JsonResponse({'errno': 1120, 'msg': '未指定团队列表'})
    tm_info = []
    for tm in teams:
        tm_info.append(tm.to_json())
    return JsonResponse({'errno': 0, 'msg': '返回团队列表成功', 'tm_info': tm_info})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def upload_avatar(request, user):
    # 获取 JSON 数据
    data_json = json.loads(request.body)
    data = data_json.get('data')

    # 解码 Base64 图片数据
    # format, imgstr = data.split(';base64,')
    # ext = format.split('/')[-1]
    image = ContentFile(base64.b64decode(data), name=f"{user.user_id}.png")

    user.user_avatar.save(image.name, image)
    user.save()

    return JsonResponse({'errno': 0, 'msg': "用户头像上传成功"})


@csrf_exempt
@require_http_methods(['GET'])
def check_token(request):
    token_key = request.headers.get('Authorization')
    token = UserToken.objects.filter(key=token_key).first()
    if token is None or token.expire_time < now():
        return JsonResponse({'errno': 1151, 'msg': "token错误"})
    return JsonResponse({'errno': 0, 'msg': "token有效"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def upload_email_check(request, user):
    # 获取 JSON 数据
    data_json = json.loads(request.body)
    email = data_json.get('email')
    if User.objects.filter(user_email=email).exists():
        return JsonResponse({'errno': 1060, 'msg': "该邮箱已存在注册用户"})
    return JsonResponse({'errno': 0, 'msg': "信息验证成功"})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def upload_email(request, user):
    # 获取 JSON 数据
    data_json = json.loads(request.body)
    email = data_json.get('email')
    if User.objects.filter(user_email=email).exists():
        return JsonResponse({'errno': 1070, 'msg': "该邮箱已存在注册用户"})
    else:
        user.user_email = email
        print(email)
        user.save()
    return JsonResponse({'errno': 0, 'msg': "用户更改邮箱成功"})


@csrf_exempt
@require_http_methods(['POST'])
def deploy_test(request):
    return JsonResponse({'errno': 0, 'ver': "114514", 'cur_time': now()})


@csrf_exempt
@require_http_methods(['POST'])
def check_profile(request):
    data_json = json.loads(request.body)
    user_id = data_json.get('user_id')
    if not User.objects.filter(user_id=user_id).exists():
        return JsonResponse({'errno': 1130, 'msg': '该用户不存在'})
    user = User.objects.get(user_id=user_id)
    if user.user_visible:
        user_info = user.to_json()
        user_avatar = None
        if user.user_avatar:
            user_avatar = get_avatar_base64(user.user_avatar)
        return JsonResponse({'errno': 0, 'msg': '返回用户信息成功', 'visible': 'True', 'user_info': user_info, 'user_avatar': user_avatar})
    else:
        user_avatar = None
        if user.user_avatar:
            user_avatar = get_avatar_base64(user.user_avatar)
        return JsonResponse({'errno': 0, 'msg': '返回部分用户信息成功', 'visible': 'False', 'user_name': user.user_name, 'user_avatar': user_avatar, 'user_signature': user.user_signature})


