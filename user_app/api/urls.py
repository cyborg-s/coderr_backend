from django.urls import path
from .views import UserProfileView, BusinessProfilesView, CustomerProfilesView

# Für api/profile/
userprofile_urlpatterns = [
    path('<int:pk>/', UserProfileView.as_view(), name='userprofile'),
]

# Für api/profiles/
userprofiles_urlpatterns = [
    path('business/', BusinessProfilesView.as_view(), name='businessprofiles'),
    path('customer/', CustomerProfilesView.as_view(), name='customerprofiles'),
]
