from django.urls import path
from . import views 

urlpatterns = [
    path('', views.reviews_list, name='reviewslist'),
    path('<int:id>/', views.review_detail, name='reviewdetail'),
]
