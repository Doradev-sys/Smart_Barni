from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WastageRecordViewSet

router = DefaultRouter()
router.register('records', WastageRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
