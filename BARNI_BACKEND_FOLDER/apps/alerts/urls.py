from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertViewSet, respond_alert_view

router = DefaultRouter()
router.register('alerts', AlertViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<uuid:alert_id>/respond/', respond_alert_view, name='respond-alert'),
]
