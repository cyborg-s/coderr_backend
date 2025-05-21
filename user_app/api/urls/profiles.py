from django.urls import path

from user_app.api import views 

urlpatterns = [
    path('business/', views.business_profiles, name='businessprofiles'),
    path('customer/', views.customer_profiles, name='customerprofiles'),
]
