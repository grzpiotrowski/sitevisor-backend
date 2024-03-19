from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from sitevisorapi import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'rooms', views.RoomViewSet)
router.register(r'sensors', views.SensorViewSet)
router.register(r'projects', views.ProjectViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/register/', views.RegistrationAPIView.as_view(), name='register'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/kafka-proxy/', views.KafkaBridgeProxy.as_view(), name='kafka-proxy'),
]
