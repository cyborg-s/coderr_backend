from django.urls import path

from auth_app.api import views 

urlpatterns = [
    path('', views.registration, name='registration'),
]
