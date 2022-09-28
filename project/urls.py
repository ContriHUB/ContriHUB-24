from django.urls import path
from . import views

urlpatterns = [
    path('populate_projects/', views.populate_projects, name='populate_projects'),
    path('populate_issues/', views.populate_issues, name='populate_issues'),
]
