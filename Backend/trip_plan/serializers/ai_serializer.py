from rest_framework import serializers
from .travel_serializer import DestinationSerializer, HotelSerializer

class AIPlanDetailsSerializer(serializers.Serializer):
    """توصيف تفاصيل الخطة التي يولدها الـ AI"""
    destination_id = serializers.IntegerField(help_text="ID الوجهة المختارة من قاعدة البيانات")
    hotel_id = serializers.IntegerField(help_text="ID الفندق المختار")
    total_cost = serializers.FloatField(help_text="التكلفة الإجمالية المحسوبة")
    days = serializers.IntegerField(help_text="عدد أيام الإقامة")
    events = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )

class AICostBreakdownSerializer(serializers.Serializer):
    flights = serializers.FloatField(required=False)
    accommodation = serializers.FloatField(required=False)
    daily_living = serializers.FloatField(required=False)
    total = serializers.FloatField(required=False)

class AIOptionSerializer(serializers.Serializer):
    option_id = serializers.IntegerField()
    destination_id = serializers.IntegerField()
    hotel_id = serializers.IntegerField()
    total_cost = serializers.FloatField(required=False)
    cost_breakdown = AICostBreakdownSerializer(required=False)

class AIStructuredResponseSerializer(serializers.Serializer):
    """التوصيف النهائي للرد الذي سيصل للمستخدم"""
    status = serializers.ChoiceField(
        choices=[
            'missing_info',        # معلومات ناقصة + سؤال تفاعلي
            'gather_info',         # متوافق مع prompt القديم/LLM
            'no_options',          # لا توجد خيارات مناسبة (متوافق مع prompt)
            'searching',           # النظام يقوم بالبحث
            'options_presented',   # تم عرض خيارات للمستخدم
            'plan_confirmed',      # تم تأكيد الخطة النهائية
            'error',               # خطأ في النظام أو الـ LLM
            'text_response',       # رد نصي فقط (fallback)
        ],
        help_text="حالة الرد كما يحددها الـ AI حسب الـ spec"
    )
    
    # نسمح أن يكون الحقل اختيارياً وفارغاً لأن بعض الردود قد تعتمد فقط على status/الحقول الأخرى
    message = serializers.CharField(
        help_text="الرد النصي من الـ AI",
        required=False,
        allow_blank=True
    )
    
    # تفاصيل الخطة (تظهر فقط عندما تكون الحالة complete)
    selected_plan = AIPlanDetailsSerializer(required=False)

    # خيارات مقترحة (تظهر فقط عندما تكون الحالة options_presented)
    options = AIOptionSerializer(many=True, required=False)
    
    # البيانات المرئية (التي يتم حقنها من الـ View بناءً على الـ IDs)
    visual_data = serializers.DictField(
        required=False, 
        help_text="تحتوي على بيانات الوجهة والفندق كاملة مع الصور"
    )

    def validate(self, data):
        """التحقق من منطقية البيانات المرجعة من الـ AI"""
        # في حالة تأكيد الخطة النهائية يجب أن تحتوي على selected_plan مكتمل
        if data['status'] == 'plan_confirmed' and not data.get('selected_plan'):
            raise serializers.ValidationError("في حالة plan_confirmed، يجب تزويد selected_plan")
        if data['status'] == 'options_presented' and not data.get('options'):
            raise serializers.ValidationError("في حالة options_presented، يجب تزويد options")
        return data