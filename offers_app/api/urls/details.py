from django.urls import path

from offers_app.api import views 

urlpatterns = [
    path('<int:id>/', views.offer_details, name='offerdetails'),
]
