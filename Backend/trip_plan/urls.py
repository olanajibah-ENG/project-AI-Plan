from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views.auth_view import RegisterView, LoginView
from .views.admin_view import AdminDestinationViewSet, AdminHotelViewSet, AdminEventViewSet
from .views.travel_view import AIChatPlanView

# إعداد الـ Router لعمليات الـ CRUD (إضافة، تعديل، حذف، عرض)
router = DefaultRouter()
router.register(r'admin/destinations', AdminDestinationViewSet, basename='admin-destinations')
router.register(r'admin/hotels', AdminHotelViewSet, basename='admin-hotels')
router.register(r'admin/events', AdminEventViewSet, basename='admin-events')

urlpatterns = [
    # --- روابط المصادقة (Authentication) ---
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', LoginView.as_view(), name='auth_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- روابط الذكاء الاصطناعي (AI Chat) ---
    path('ai/chat/', AIChatPlanView.as_view(), name='ai_chat_plan'),

    # --- دمج روابط الـ CRUD التابعة للـ Router ---
    path('', include(router.urls)),
]