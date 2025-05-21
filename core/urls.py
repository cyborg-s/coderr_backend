"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/registration/', include('auth_app.api.urls.registration')),
    path('api/login/', include('auth_app.api.urls.login')),
    path('api/profile/', include('user_app.api.urls.user')),
    path('api/profiles/', include('user_app.api.urls.profiles')),
    path('api/offers/', include('offers_app.api.urls.offers')),
    path('api/offerdetails/', include('offers_app.api.urls.details')),
    path('api/orders/', include('orders_app.api.urls.orders')),
    path('api/order-count/', include('orders_app.api.urls.order_count')),
    path('api/completed-order-count/', include('orders_app.api.urls.completed_order_count')),
    path('api/reviews/', include('reviews_app.api.urls')),
    path('api/base-info/', include('baseinfo_app.api.urls')),
    path('api/', include('offers_app.api.urls.offers')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)