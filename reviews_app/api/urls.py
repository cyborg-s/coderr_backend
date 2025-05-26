from django.urls import path

from .views import ReviewListCreateView, ReviewDetailView 

urlpatterns = [
    path('', ReviewListCreateView.as_view(), name='reviewslist'),
    path('<int:id>/', ReviewDetailView.as_view(), name='reviewdetail'),
]
