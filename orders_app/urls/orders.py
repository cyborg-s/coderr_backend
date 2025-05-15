from django.urls import path
from orders_app import views 

urlpatterns = [
    path('', views.orders_list, name='orderslist'),
    path('<int:id>/', views.order_details, name='orderdetails'),
]
