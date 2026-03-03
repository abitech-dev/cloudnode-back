from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServerViewSet, ServerUserViewSet

router = DefaultRouter()
router.register(r'servers', ServerViewSet)
router.register(r'server-users', ServerUserViewSet)  # To avoid conflict with potential system users

urlpatterns = [
    path('', include(router.urls)),
]
