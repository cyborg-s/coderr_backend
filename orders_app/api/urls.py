from django.urls import path
from .views import OrderListCreateView, OrderDetailView, OrderCountView, CompletedOrderCountView

orders_urlpatterns = [
    path('', OrderListCreateView.as_view(), name='orderslist'),             
    path('<int:id>/', OrderDetailView.as_view(), name='orderdetails') 
]

order_count_urlpatterns = [
    path('<int:business_user>/', OrderCountView.as_view(), name='ordercount')  
]

completed_order_count_urlpatterns = [
    path('<int:business_user>/', CompletedOrderCountView.as_view(), name='completedordercount') 
    ]
