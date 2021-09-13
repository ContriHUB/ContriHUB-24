from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('authorize/', views.authorize, name='authorize'),
    path('logout/', views.logout_, name='logout')
]
