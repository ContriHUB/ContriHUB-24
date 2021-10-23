from django.urls import path
from . import views

urlpatterns = [
    path('complete/', views.complete, name='complete_profile'),
    path('user/<str:username>/', views.profile, name='user_profile'),
    path('rankings/', views.rankings, name='rankings'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('create_issue/', views.create_issue, name='create_issue'),
    path('edit_contact_info/', views.change_contact_info, name='change_contact_info'),
]
