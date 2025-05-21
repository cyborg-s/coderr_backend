from django.urls import path
from user_app import views 

print("user_app.urls.user wurde geladen")

urlpatterns = [
    path('<int:pk>/', views.user_profile, name='userprofile'),
]
