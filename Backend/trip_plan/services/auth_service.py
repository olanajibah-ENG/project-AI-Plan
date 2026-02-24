from rest_framework_simplejwt.tokens import RefreshToken
from ..serializers.auth_serializer import UserInfoSerializer

class AuthService:
    @staticmethod
    def generate_tokens(user):
        """توليد التوكنات للمستخدم"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def get_user_data_with_tokens(user):
        """تجميع بيانات المستخدم مع التوكنات"""
        tokens = AuthService.generate_tokens(user)
        return {
            "user": UserInfoSerializer(user).data,
            "tokens": tokens
        }