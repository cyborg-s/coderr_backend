from django.urls import path
from .views import OfferListView, OfferDetailRetrieveView, SingleOfferView

offers_urlpatterns = [
    path('', OfferListView.as_view(), name='offerslist'),              
    path('<int:id>/', SingleOfferView.as_view(), name='singleoffer'),               
]

details_urlpatterns = [
    path('<int:id>/', OfferDetailRetrieveView.as_view(), name='offerdetails'),             
]

