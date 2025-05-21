from django.urls import path
from orders_app import views 

urlpatterns = [
    path('<int:buissness_user>/', views.order_count, name='ordercount'),
]
