from django.urls import path
from orders_app import views 

urlpatterns = [
    path('<int:id>/', views.completed_order_count, name='completedordercount'),
]
