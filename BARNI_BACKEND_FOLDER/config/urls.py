from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/menu/', include('apps.menu.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/kitchen/', include('apps.kitchen.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/finance/', include('apps.finance.urls')),
    path('api/inventory/', include('apps.inventory.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/alerts/', include('apps.alerts.urls')),
    path('api/wastage/', include('apps.wastage.urls')),
    path('api/delivery/', include('apps.delivery.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
