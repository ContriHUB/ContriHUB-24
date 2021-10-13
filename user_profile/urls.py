from django.urls import path
from . import views

urlpatterns = [
    path('complete/', views.complete, name='complete_profile'),
    path('user/<str:username>/', views.profile, name='user_profile'),
    path('rankings/', views.rankings, name='rankings'),
    path('edit_profile/',views.edit_profile,name='edit_profile'),
    path('edit_msid/',views.change_msid,name='change_msid'),
    path('edit_whatsapp/',views.change_whatsapp_no,name='change_whatsapp_no')
]
