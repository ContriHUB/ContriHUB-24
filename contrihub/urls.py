"""contrihub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from project import views as pro_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('profile/', include('user_profile.urls')),
    path('project/', include('project.urls')),
    path('api/projects/',pro_views.project_list_view),
    path('api/projects/<project_id>/',pro_views.project_detail_view),
    # this url is handled by social_django app under social-auth-app-django python library
    url(r'^oauth/', include('social_django.urls', namespace='social')),
]

handler404 = "home.views.page_not_found_view"
