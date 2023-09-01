import os
import django

from UnknownProject_backend import settings


# 设置环境变量，指向 Django 项目的 settings.py 文件
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UnknownProject_backend.settings')
# 加载 Django 的设置
django.setup()

from document.models import Directory
from project.models import Project


if __name__ == "__main__":

    project_list = Project.objects.all()
    for project in project_list:
        if project.project_root_directory is None:
            new_directory = Directory.objects.create()
            new_directory.directory_project = project
            new_directory.save()
            project.project_root_directory = new_directory
        if project.project_recycle_bin is None:
            new_recycle = Directory.objects.create()
            new_recycle.directory_project = project
            new_recycle.save()
            project.project_recycle_bin = new_recycle
        project.save()
