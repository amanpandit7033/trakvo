from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('institutes/', include('apps.institutes.urls')),
    path('students/', include('apps.students.urls')),
    path('attendance/', include('apps.attendance.urls')),
    path('fees/', include('apps.fees.urls')),
    path('assessments/', include('apps.assessments.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('core/', include('apps.core.urls')),
    path('platform-admin/', include('apps.platform_admin.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
