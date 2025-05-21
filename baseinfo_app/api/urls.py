from django.urls import path

from . import views 

urlpatterns = [
    path('', views.baseinfo, name='baseinfo'),
]
