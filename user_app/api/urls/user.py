from django.urls import path

from user_app.api import views 


urlpatterns = [
    path('<int:pk>/', views.user_profile, name='userprofile'),
]
