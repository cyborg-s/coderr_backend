from django.urls import path
from .views import RegistrationView, LoginView

registration_urlpatterns = [
    path('', RegistrationView.as_view(), name='registration'),
]

login_urlpatterns = [
    path('', LoginView.as_view(), name='login'),
]
