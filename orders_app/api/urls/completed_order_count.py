from django.urls import path

from orders_app.api import views 

urlpatterns = [
    path('<int:buissness_user>/', views.completed_order_count, name='completedordercount'),
]
