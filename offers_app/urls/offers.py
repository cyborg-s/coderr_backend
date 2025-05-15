from django.urls import path
from offers_app import views 

urlpatterns = [
    path('', views.offers_list, name='offerslist'),
    path('<int:id>/', views.single_offer, name='singleoffer')
]
