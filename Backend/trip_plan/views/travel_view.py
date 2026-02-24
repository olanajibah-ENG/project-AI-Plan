import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ..services.ai_agent_service import TravelAgentService
from ..models.travel_model import Destination, Hotel, Event
from ..serializers.travel_serializer import DestinationSerializer, HotelSerializer, EventSerializer
from ..serializers.ai_serializer import AIStructuredResponseSerializer

class AIChatPlanView(APIView):
    # حماية المسار: فقط المستخدمين المسجلين يمكنهم الدردشة مع الـ AI
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user_input = request.data.get('prompt') or request.data.get('message')
        session_id = request.data.get('session_id')

        if not user_input:
            return Response({"error": "الرجاء إدخال نص للبدء"}, status=status.HTTP_400_BAD_REQUEST)

        # استدعاء خدمة الـ AI Agent مع ربط المستخدم والجلسة
        agent_service = TravelAgentService(user=request.user)
        ai_response = agent_service.run(user_input, session_id=session_id)

        # في حال وجود خطأ من خدمة الـ AI نرجعه مباشرة
        if ai_response.get("status") == "error":
            return Response(ai_response, status=status.HTTP_200_OK)

        # التحقق من البنية العامة للرد باستخدام الـ Serializer
        serializer = AIStructuredResponseSerializer(data=ai_response)
        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": "الرد القادم من خدمة الذكاء الاصطناعي غير متوافق مع الـ spec.",
                    "details": serializer.errors,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        ai_json = serializer.validated_data

        # معالجة حالة تأكيد الخطة النهائية: plan_confirmed
        if ai_json.get('status') == 'plan_confirmed':
            plan = ai_json.get('selected_plan', {})
            dest_id = plan.get('destination_id')
            hotel_id = plan.get('hotel_id')

            destination = Destination.objects.filter(id=dest_id).first()
            hotel = Hotel.objects.filter(id=hotel_id).first()

            if destination and hotel:
                ai_json['visual_data'] = {
                    "destination": DestinationSerializer(destination, context={'request': request}).data,
                    "hotel": HotelSerializer(hotel, context={'request': request}).data
                }

                selected_events = plan.get('events')
                selected_event_ids = []
                if isinstance(selected_events, list):
                    for item in selected_events:
                        if isinstance(item, dict) and item.get('event_id') is not None:
                            selected_event_ids.append(item.get('event_id'))

                if selected_event_ids:
                    events_qs = Event.objects.filter(id__in=selected_event_ids, destination_id=destination.id)
                else:
                    events_qs = destination.events.all()

                ai_json['visual_data']['events'] = EventSerializer(
                    events_qs, many=True, context={'request': request}
                ).data
            else:
                ai_json['status'] = 'missing_info'
                ai_json['message'] = "عذراً، الوجهة أو الفندق المختار غير متوفر حالياً في قاعدة بياناتنا."

        # تأكد من إعادة session_id للفرونت ليستمر بنفس الجلسة
        if 'session_id' not in ai_json and isinstance(ai_response, dict) and ai_response.get('session_id'):
            ai_json['session_id'] = ai_response['session_id']

        return Response(ai_json, status=status.HTTP_200_OK)