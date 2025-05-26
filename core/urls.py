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
from user_app.api import urls as user_urls
from offers_app.api import urls as offers_urls
from orders_app.api import urls as orders_urls
from auth_app.api import urls as auth_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/registration/', include((auth_urls.registration_urlpatterns, 'auth_app'), namespace='registration')),
    path('api/login/', include((auth_urls.login_urlpatterns, 'auth_app'), namespace='login')),
    path('api/profile/', include((user_urls.userprofile_urlpatterns, 'user_app'), namespace='userprofile')),
    path('api/profiles/', include((user_urls.userprofiles_urlpatterns, 'user_app'), namespace='userprofiles')),
    path('api/offers/', include((offers_urls.offers_urlpatterns, 'offers_app'), namespace='offers')),
    path('api/offerdetails/', include((offers_urls.details_urlpatterns, 'offers_app'), namespace='offerdetails')),
    path('api/orders/', include((orders_urls.orders_urlpatterns, 'orders_app'), namespace='orders')),
    path('api/order-count/', include((orders_urls.order_count_urlpatterns, 'orders_app'), namespace='ordercount')),
    path('api/completed-order-count/', include((orders_urls.completed_order_count_urlpatterns, 'orders_app'), namespace='completedordercount')),
    path('api/reviews/', include('reviews_app.api.urls')),
    path('api/base-info/', include('baseinfo_app.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)