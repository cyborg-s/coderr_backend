from django.urls import path
from orders_app import views 

urlpatterns = [
    path('<int:id>/', views.order_count, name='ordercount'),
]
