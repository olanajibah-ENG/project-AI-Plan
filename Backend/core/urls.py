from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # لوحة تحكم Django الافتراضية (اختياري)
    path('django-admin/', admin.site.urls),

    # ربط روابط تطبيق trip_plan الأساسي
    path('api/', include('trip_plan.urls')),

] 

# إعدادات عرض الصور في بيئة التطوير RE-FR-16
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)