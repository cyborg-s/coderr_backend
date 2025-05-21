from django.urls import path

from offers_app.api import views 

urlpatterns = [
    path('', views.OfferListView.as_view(), name='offerslist'),
    path('<int:id>/', views.single_offer, name='singleoffer')
]
