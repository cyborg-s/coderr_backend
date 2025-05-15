from django.urls import path
from auth_app import views 

urlpatterns = [
    path('', views.registration, name='registration'),
]
