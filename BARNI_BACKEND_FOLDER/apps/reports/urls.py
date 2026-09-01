from django.urls import path
from .views import daily_report_view, waiter_reports_view, kitchen_reports_view

urlpatterns = [
    path('daily/', daily_report_view, name='daily-report'),
    path('waiter/', waiter_reports_view, name='waiter-report'),
    path('kitchen/', kitchen_reports_view, name='kitchen-report'),
]
