from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from sitevisorapi import views

router = DefaultRouter()
router.register(r'rooms', views.RoomViewSet)
router.register(r'sensors', views.SensorViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
