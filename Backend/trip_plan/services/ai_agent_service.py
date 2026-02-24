import os
import json
import re
import ast
import logging
import requests
import uuid
from decimal import Decimal
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from ..models.travel_model import Destination, Hotel, ConversationSession, Event
from ..serializers.travel_serializer import DestinationSerializer, HotelSerializer, EventSerializer


logger = logging.getLogger(__name__)


class TravelAgentService:
    """
    خدمة AI متقدمة لتخطيط الرحلات السياحية
    - تكامل كامل مع LLM (OpenRouter)
    - محادثة تفاعلية خطوة بخطوة
    - إدارة حالة المحادثة (State Management)
    - استخدام الأدوات (Function Calling)
    - مخرجات منظمة (Structured Output)
    """
    
    def __init__(self, user=None):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = getattr(settings, "AI_MODEL", "arcee-ai/trinity-large-preview:free")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.user = user
        
        self.legacy_status_mode = getattr(settings, "AI_LEGACY_STATUS_MODE", True)
        self.enable_searching_first_response = getattr(settings, "AI_ENABLE_SEARCHING_FIRST_RESPONSE", False)

        # System Prompt - هندسة الأوامر
        self.system_prompt = """أنت مساعد ذكي متخصص في تخطيط الرحلات السياحية. تتحدث بالعربية الفصحى المبسطة، ودود، محترف، واضح ومباشر.

مهمتك:
1. جمع متطلبات الرحلة بشكل تدريجي وطبيعي (يمكنك طرح سؤال أو اثنين في الرد الواحد)
2. اقتراح وجهات وفنادق مناسبة ضمن الميزانية
3. عرض خيارات منظمة
4. تأكيد خطة نهائية واحدة
5. اقتراح فعاليات موسمية مناسبة ضمن الخطة النهائية (عند توفرها)

المعلومات الأساسية المطلوبة (لا تسأل مرة أخرى إذا وُجدت):
• الميزانية الكلية (بالدولار الأمريكي)
• عدد الأيام
• عدد الأشخاص
• تفضيل الوجهة: ساحلية أم جبلية (أو لا يهم)
• مستوى الرفاهية المطلوب (عدد نجوم الفندق المفضل: 1–5)

───────────────────────────────
كيف يجب أن تبني ردك دائماً:
───────────────────────────────

يجب أن ينتهي كل ردك بكائن JSON صالح تماماً (يبدأ بـ { وينتهي بـ }).
يمكنك كتابة نص عربي واضح وودي قبل الـ JSON، لكن الـ JSON نفسه يجب أن يكون صالح 100%.

الحقول الإلزامية في كل JSON:
{
  "status": string,
  "message": string,
  "collected_requirements": object
}

القيم الممكنة لـ status:

"gather_info"         → ينقص معلومات مهمة → اسأل سؤالاً أو اثنين فقط
"no_options"          → لا توجد خيارات مناسبة → اقترح تعديل المعايير
"options_presented"   → وجدت خيارات → اعرضها في حقل "options"
"plan_confirmed"      → تم اختيار/تأكيد خيار → اعرض الخطة النهائية في "selected_plan"

───────────────────────────────
الحقول الإضافية حسب الحالة:
───────────────────────────────

• عند "options_presented" أضف:
  "options": [
    {
      "option_id": 1,
      "destination_id": 12,
      "hotel_id": 45,
      "total_cost": 1980,
      "cost_breakdown": {"flights": 750, "accommodation": 720, "daily_living": 510, "total": 1980}
    }
  ]

• عند "plan_confirmed" أضف:
  "selected_plan": {
    "option_id": 2,
    "destination_id": 12,
    "hotel_id": 47,
    "total_cost": 2350,
    "days": 7,
    "cost_breakdown": {"flights": 800, "accommodation": 900, "daily_living": 650, "total": 2350}
  }

───────────────────────────────
قواعد صارمة:
───────────────────────────────

• لا تختلق أسعاراً أو وجهات أو فنادق — اعتمد فقط على نتائج الأدوات.
• لا تكرر سؤالاً تمت الإجابة عليه من قبل.
• حقل collected_requirements يجب أن يكون دقيقاً ومحدثاً في كل رد.
• إذا لم تجد نتائج → status = "no_options" + اقترح حلولاً واقعية.
• لا تضع تعليقات أو // داخل الـ JSON.
• لا تستخدم ```json داخل الرد أبداً.

───────────────────────────────
أمثلة (اتبع نفس الهيكلية):
───────────────────────────────

مثال 1 – بداية
مرحبا! لنساعدك بشكل مثالي، أحتاج بعض التفاصيل...
{
  "status": "gather_info",
  "message": "ما هي ميزانيتك الإجمالية بالدولار؟ وكم شخص سيسافر؟",
  "collected_requirements": {}
}

مثال 2 – بعد جمع جزء
شكراً! تبقى نقطة واحدة...
{
  "status": "gather_info",
  "message": "هل تفضل وجهة ساحلية أم جبلية أم لا يهم؟",
  "collected_requirements": {"budget": 3200, "people": 3}
}

مثال 3 – لا نتائج
للأسف لم أجد خيارات مناسبة ضمن هذه الميزانية...
{
  "status": "no_options",
  "message": "الميزانية الحالية منخفضة نسبياً لهذا المستوى. هل يمكن زيادة الميزانية أو تقليل عدد النجوم إلى 3؟",
  "collected_requirements": {"budget": 950, "days": 7, "people": 2, "min_stars": 4}
}

مثال 4 – عرض خيارات
إليك أفضل الخيارات المتاحة...
{
  "status": "options_presented",
  "message": "وجدت ثلاثة خيارات رائعة. أيها تفضل؟ (أجب برقم الخيار)",
  "collected_requirements": {"budget": 2500, "days": 6, "people": 2, "is_coastal": true, "min_stars": 4},
  "options": [
    {"option_id": 1, "destination_id": 12, "hotel_id": 45, "total_cost": 1980, "cost_breakdown": {"flights": 750, "accommodation": 720, "daily_living": 510, "total": 1980}},
    {"option_id": 2, "destination_id": 8, "hotel_id": 23, "total_cost": 2350, "cost_breakdown": {"flights": 800, "accommodation": 900, "daily_living": 650, "total": 2350}}
  ]
}

مثال 5 – تأكيد
تم اختيار الخيار رقم 2. إليك ملخص الرحلة النهائي:
{
  "status": "plan_confirmed",
  "message": "رحلتك مؤكدة! إليك ملخص الرحلة النهائي.",
  "collected_requirements": {"budget": 2500, "days": 6, "people": 2, "is_coastal": true, "min_stars": 4},
  "selected_plan": {"option_id": 2, "destination_id": 8, "hotel_id": 23, "total_cost": 2350, "days": 6, "cost_breakdown": {"flights": 800, "accommodation": 900, "daily_living": 650, "total": 2350}}
}

مثال 6 – إدخال غير مفهوم
{
  "status": "gather_info",
  "message": "لم أفهم طلبك بالكامل. هل يمكن أن تخبرني بميزانيتك وعدد الأيام؟",
  "collected_requirements": {}
}

مثال 7 – ميزانية صفر/غير منطقية
{
  "status": "gather_info",
  "message": "لأقترح خطة واقعية، ما هي ميزانيتك التقريبية بالدولار؟",
  "collected_requirements": {"budget": 0}
}

مثال 8 – المستخدم يرفض كل الخيارات
{
  "status": "gather_info",
  "message": "حسناً، ما الذي تريد تغييره تحديداً: زيادة النجوم، تغيير الوجهة، أم تقليل التكلفة؟",
  "collected_requirements": {"budget": 2500, "days": 6, "people": 2}
}

مثال 9 – تغيير بعد عرض الخيارات
{
  "status": "gather_info",
  "message": "تمام. هل تريد تغيير الوجهة إلى ساحلية/جبلية، أم تغيير عدد الأيام/الميزانية؟",
  "collected_requirements": {"budget": 2500, "days": 6, "people": 2, "min_stars": 4}
}

مثال 10 – المستخدم يطلب وجهة "لا يهم"
{
  "status": "gather_info",
  "message": "ممتاز. ما هو الحد الأدنى لعدد نجوم الفندق الذي تفضله؟",
  "collected_requirements": {"budget": 2500, "days": 6, "people": 2, "is_coastal": null}
}

مثال 11 – لا توجد نتائج (اقتراح عملي)
{
  "status": "no_options",
  "message": "لم أجد خيارات مناسبة بهذه المواصفات. هل تفضل تقليل عدد الأيام أو تقليل عدد النجوم إلى 3؟",
  "collected_requirements": {"budget": 1200, "days": 7, "people": 2, "min_stars": 5}
}

مثال 12 – اختيار خيار بالرقم
{
  "status": "plan_confirmed",
  "message": "تم اعتماد الخيار رقم 1. إليك ملخص الخطة النهائية.",
  "collected_requirements": {"budget": 2500, "days": 6, "people": 2},
  "selected_plan": {"option_id": 1, "destination_id": 12, "hotel_id": 45, "total_cost": 1980, "days": 6, "cost_breakdown": {"flights": 750, "accommodation": 720, "daily_living": 510, "total": 1980}}
}

مثال 13 – حالة searching (لواجهة المستخدم فقط)
{
  "status": "searching",
  "message": "جاري البحث عن أفضل الخيارات المناسبة لك...",
  "collected_requirements": {"budget": 2500, "days": 7, "people": 2}
}

مثال 14 – خطة نهائية مع فعاليات موسمية
تم اختيار الخيار رقم 1 مع فعاليات مناسبة للصيف:
{
  "status": "plan_confirmed",
  "message": "تم تأكيد رحلتك مع فعاليات موسمية ممتعة!",
  "collected_requirements": {"budget": 2800, "days": 7, "people": 2, "season": "summer"},
  "selected_plan": {
    "option_id": 1,
    "destination_id": 15,
    "hotel_id": 38,
    "total_cost": 2450,
    "days": 7,
    "events": [
      {"event_id": 7, "name": "رحلة غوص في الشعاب المرجانية", "price_per_person": 45},
      {"event_id": 12, "name": "عرض السهرة الشرقية", "price_per_person": 30}
    ],
    "cost_breakdown": {"flights": 900, "accommodation": 1050, "daily_living": 500, "total": 2450}
  }
}
"""
    
    # ==================== الأدوات (Tools) ====================
    
    @staticmethod
    def search_destinations_and_hotels(budget=None, days=None, people=None, 
                                      is_coastal=None, min_stars=3, season=None, is_sea_view=None):
        """
        أداة البحث: تبحث عن وجهات وفنادق مناسبة حسب المتطلبات
        
        Args:
            budget: الميزانية الكلية (اختياري)
            days: عدد الأيام (اختياري)
            people: عدد الأشخاص (اختياري)
            is_coastal: ساحلي أم لا (اختياري)
            min_stars: الحد الأدنى للنجوم (افتراضي 3)
        
        Returns:
            قائمة بالخيارات المتاحة مع التكلفة المحسوبة
        """
        # جلب الوجهات
        destinations = Destination.objects.prefetch_related(
            'hotels', 'dest_images'
        ).all()
        
        # فلترة حسب الساحلية
        if is_coastal is not None:
            destinations = destinations.filter(is_coastal=is_coastal)

        # فلترة موسمية حسب best_seasons (قيم نصية مفصولة بفواصل)
        if season and season != "all":
            season_map = {
                "summer": ["summer", "صيف"],
                "winter": ["winter", "شتاء"],
                "spring": ["spring", "ربيع"],
                "autumn": ["autumn", "fall", "خريف"],
            }
            tokens = season_map.get(str(season).lower(), [str(season)])
            season_q = Q()
            for tok in tokens:
                season_q |= Q(best_seasons__icontains=tok)
            destinations = destinations.filter(season_q)
        
        results = []
        
        for dest in destinations:
            # جلب الفنادق المناسبة
            hotels = dest.hotels.prefetch_related('hotel_images').filter(
                stars__gte=min_stars
            )

            if is_sea_view is not None:
                hotels = hotels.filter(is_sea_view=is_sea_view)
            
            for hotel in hotels:
                # حساب التكلفة إذا توفرت المعلومات
                if budget and days and people:
                    total_cost = TravelAgentService.calculate_trip_cost(
                        dest.flight_cost,
                        dest.daily_living_cost,
                        hotel.price_per_night,
                        days,
                        people
                    )
                    
                    # تخطي إذا تجاوز الميزانية
                    if total_cost > budget:
                        continue
                    
                    cost_breakdown = {
                        'flights': float(dest.flight_cost) * people,
                        'accommodation': float(hotel.price_per_night) * days,
                        'daily_living': float(dest.daily_living_cost) * days * people,
                        'total': total_cost
                    }
                else:
                    total_cost = None
                    cost_breakdown = None
                
                # إضافة النتيجة
                results.append({
                    'destination_id': dest.id,
                    'destination_name': dest.name,
                    'country': dest.country,
                    'is_coastal': dest.is_coastal,
                    'description': dest.description,
                    'hotel_id': hotel.id,
                    'hotel_name': hotel.name,
                    'stars': hotel.stars,
                    'is_sea_view': hotel.is_sea_view,
                    'price_per_night': float(hotel.price_per_night),
                    'total_cost': total_cost,
                    'cost_breakdown': cost_breakdown
                })
        
        # ترتيب حسب التكلفة
        if budget and days and people:
            results.sort(key=lambda x: x['total_cost'])
        
        return results
    
    @staticmethod
    def calculate_trip_cost(flight_cost, daily_living_cost, hotel_price, days, people):
        """
        حساب التكلفة الكلية للرحلة
        
        Formula: (flight_cost × people) + (hotel_price × days) + (daily_living × days × people)
        """
        flight_total = float(flight_cost) * people
        accommodation = float(hotel_price) * days
        living = float(daily_living_cost) * days * people
        
        return round(flight_total + accommodation + living, 2)

    @staticmethod
    def calculate_trip_cost_tool(flight_cost, daily_living_cost, hotel_price, days, people):
        """
        أداة مستقلة لحساب التكلفة الكلية يمكن للـ LLM استدعاؤها مباشرة
        """
        total = TravelAgentService.calculate_trip_cost(
            flight_cost, daily_living_cost, hotel_price, days, people
        )
        return {
            "total_cost": total,
            "breakdown": {
                "flights": float(flight_cost) * people,
                "accommodation": float(hotel_price) * days,
                "daily_living": float(daily_living_cost) * days * people,
            }
        }
    
    @staticmethod
    def get_destination_details(destination_id):
        """الحصول على تفاصيل وجهة محددة مع الصور"""
        try:
            dest = Destination.objects.prefetch_related(
                'dest_images', 'hotels__hotel_images'
            ).get(id=destination_id)
            return DestinationSerializer(dest).data
        except Destination.DoesNotExist:
            return None
    
    @staticmethod
    def get_hotel_details(hotel_id):
        """الحصول على تفاصيل فندق محدد مع الصور"""
        try:
            hotel = Hotel.objects.prefetch_related('hotel_images').get(id=hotel_id)
            return HotelSerializer(hotel).data
        except Hotel.DoesNotExist:
            return None

    @staticmethod
    def search_events(destination_id, season="all", max_price=None):
        events = Event.objects.filter(destination_id=destination_id)
        if season != "all":
            events = events.filter(season__in=[season, "all"])
        if max_price is not None:
            events = events.filter(price_per_person__lte=max_price)
        return EventSerializer(events, many=True).data
    
    # ==================== Function Calling Definition ====================
    
    def get_tools_definition(self):
        """تعريف الأدوات المتاحة للـ LLM"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_destinations_and_hotels",
                    "description": "البحث عن وجهات سياحية وفنادق مناسبة حسب متطلبات المستخدم",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "budget": {
                                "type": "number",
                                "description": "الميزانية الكلية بالدولار"
                            },
                            "days": {
                                "type": "integer",
                                "description": "عدد أيام الرحلة"
                            },
                            "people": {
                                "type": "integer",
                                "description": "عدد الأشخاص"
                            },
                            "is_coastal": {
                                "type": "boolean",
                                "description": "هل الوجهة ساحلية؟ true للساحلية، false للجبلية"
                            },
                            "min_stars": {
                                "type": "integer",
                                "description": "الحد الأدنى لعدد نجوم الفندق (1-5)",
                                "default": 3
                            },
                            "season": {
                                "type": "string",
                                "description": "الموسم المفضل (summer, winter, spring, autumn, all)",
                                "enum": ["summer", "winter", "spring", "autumn", "all"]
                            },
                            "is_sea_view": {
                                "type": "boolean",
                                "description": "هل تريد فندقاً مطلاً على البحر؟"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_trip_cost_tool",
                    "description": "حساب التكلفة الكلية لرحلة معينة اعتماداً على معطيات التكلفة",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "flight_cost": {
                                "type": "number",
                                "description": "تكلفة تذكرة الطيران الواحدة"
                            },
                            "daily_living_cost": {
                                "type": "number",
                                "description": "تكلفة المعيشة اليومية للشخص الواحد بدون الفندق"
                            },
                            "hotel_price": {
                                "type": "number",
                                "description": "سعر الليلة في الفندق"
                            },
                            "days": {
                                "type": "integer",
                                "description": "عدد أيام الرحلة"
                            },
                            "people": {
                                "type": "integer",
                                "description": "عدد الأشخاص"
                            }
                        },
                        "required": ["flight_cost", "daily_living_cost", "hotel_price", "days", "people"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_destination_details",
                    "description": "الحصول على تفاصيل كاملة عن وجهة سياحية محددة",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "destination_id": {
                                "type": "integer",
                                "description": "معرف الوجهة"
                            }
                        },
                        "required": ["destination_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_hotel_details",
                    "description": "الحصول على تفاصيل كاملة عن فندق محدد",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "hotel_id": {
                                "type": "integer",
                                "description": "معرف الفندق"
                            }
                        },
                        "required": ["hotel_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_events",
                    "description": "البحث عن فعاليات موسمية في وجهة معينة",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "destination_id": {"type": "integer"},
                            "season": {
                                "type": "string",
                                "enum": ["summer", "winter", "spring", "autumn", "all"]
                            },
                            "max_price": {"type": "number"}
                        },
                        "required": ["destination_id"]
                    }
                }
            }
        ]
    
    # ==================== State Management ====================
    
    def get_or_create_session(self, session_id=None):
        """الحصول على جلسة محادثة أو إنشاء واحدة جديدة"""
        if not self.user:
            return None
            
        if session_id:
            try:
                session = ConversationSession.objects.get(
                    session_id=session_id,
                    user=self.user,
                    is_active=True
                )
                return session
            except ConversationSession.DoesNotExist:
                pass
        
        # إنشاء جلسة جديدة
        session = ConversationSession.objects.create(
            user=self.user,
            session_id=str(uuid.uuid4()),
            state={
                'requirements': {},
                'messages': []
            }
        )
        return session
    
    def save_session_state(self, session, requirements, messages):
        """حفظ حالة المحادثة"""
        session.state = {
            'requirements': requirements,
            'messages': messages
        }
        session.updated_at = timezone.now()
        session.save()
    
    # ==================== LLM Integration ====================
    
    def call_llm(self, messages, tools=None, max_retries=3):
        """
        استدعاء LLM عبر OpenRouter API
        
        Args:
            messages: قائمة الرسائل
            tools: الأدوات المتاحة (اختياري)
            max_retries: عدد المحاولات عند الفشل
        
        Returns:
            رد LLM
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "AI Travel Planner"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "top_p": 0.95,
            "max_tokens": 1500,
        }
        
        # إضافة الأدوات إذا كانت متاحة
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                else:
                    return {
                        "error": f"API Error: {response.status_code}",
                        "details": response.text
                    }
                    
            except requests.Timeout:
                if attempt < max_retries - 1:
                    continue
                return {"error": "Request timeout"}
            except Exception as e:
                return {"error": str(e)}
        
        return {"error": "Max retries exceeded"}

    @staticmethod
    def _extract_json_from_llm_text(text: str):
        """
        يحاول استخراج JSON صالح من ردود LLM غير المنضبطة.
        يدعم الحالات التالية:
        - JSON داخل markdown fences
        - نص مقتبس يحتوي JSON/fragment
        - fragment يبدأ بـ \"status\": ... بدون أقواس خارجية
        - وجود JSON ضمن نص أكبر: نأخذ من أول { إلى آخر }
        """
        if not text:
            return None

        clean = text.strip()

        # إزالة markdown fences إن وجدت
        if "```json" in clean:
            clean = clean.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in clean:
            clean = clean.split("```", 1)[1].split("```", 1)[0].strip()

        def _sanitize_json_like(s: str) -> str:
            if not s:
                return s
            # إزالة trailing commas قبل } أو ]
            s = re.sub(r",\s*(\}|\])", r"\1", s)
            # إزالة محارف لا تظهر لكنها تسبب فشل parsing أحياناً
            s = s.replace("\ufeff", "").replace("\u200b", "")
            return s

        def _try_json_repair(s: str):
            """محاولة إصلاح JSON محلياً إن كانت مكتبة json_repair متاحة."""
            try:
                from json_repair import repair_json  # type: ignore
            except Exception:
                return None
            try:
                repaired = repair_json(s)
                if isinstance(repaired, str):
                    return json.loads(_sanitize_json_like(repaired))
                if isinstance(repaired, dict):
                    return repaired
            except Exception:
                return None
            return None

        def _try_python_dict_like(s: str):
            """يتعامل مع مخرجات تشبه Python dict (single quotes, True/False/None) ثم يحولها لـ dict."""
            try:
                parsed = ast.literal_eval(s)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                return None
            return None

        # 1) محاولة مباشرة
        try:
            return json.loads(_sanitize_json_like(clean))
        except Exception:
            pass

        repaired = _try_json_repair(clean)
        if repaired is not None:
            return repaired

        py_like = _try_python_dict_like(clean)
        if py_like is not None:
            return py_like

        # 2) إذا كان النص عبارة عن JSON مُقتبس كـ string
        if clean.startswith('"') and clean.endswith('"'):
            try:
                inner = json.loads(clean)  # يفك الاقتباس والهروب
                if isinstance(inner, str):
                    clean = inner.strip()
            except Exception:
                pass

        # 3) لو هو fragment بدون أقواس خارجية لكنه يحتوي status
        if not clean.startswith("{") and '"status"' in clean:
            candidate = "{" + clean.strip().strip(",") + "}"
            try:
                return json.loads(_sanitize_json_like(candidate))
            except Exception:
                pass

        # 4) استخراج أول JSON object من النص (بشكل أكثر تحمّلاً)
        if "{" in clean and "}" in clean:
            start = clean.find("{")
            if start != -1:
                depth = 0
                end = None
                for i in range(start, len(clean)):
                    ch = clean[i]
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            end = i
                            break
                if end is None:
                    end = clean.rfind("}")
                if end is not None and end > start:
                    candidate = clean[start:end + 1]
                    try:
                        return json.loads(_sanitize_json_like(candidate))
                    except Exception:
                        repaired = _try_json_repair(candidate)
                        if repaired is not None:
                            return repaired
                        py_like = _try_python_dict_like(candidate)
                        if py_like is not None:
                            return py_like

        return None
    
    def execute_tool_call(self, tool_name, arguments):
        """تنفيذ استدعاء أداة"""
        if tool_name == "search_destinations_and_hotels":
            return self.search_destinations_and_hotels(**arguments)
        elif tool_name == "calculate_trip_cost_tool":
            return self.calculate_trip_cost_tool(**arguments)
        elif tool_name == "get_destination_details":
            return self.get_destination_details(**arguments)
        elif tool_name == "get_hotel_details":
            return self.get_hotel_details(**arguments)
        elif tool_name == "search_events":
            return self.search_events(**arguments)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _repair_json_via_llm(self, bad_text: str):
        """طلب إصلاح/استخراج JSON صالح عندما يفشل parsing."""
        repair_messages = [
            {
                "role": "system",
                "content": "أعد صياغة المحتوى التالي كـ JSON صالح فقط بدون أي نص إضافي. إذا كانت هناك حقول ناقصة، ضعها بقيم null. يجب أن يحتوي JSON على status و message و collected_requirements.",
            },
            {"role": "user", "content": bad_text or ""},
        ]

        llm_response = self.call_llm(repair_messages, tools=None)
        if "error" in llm_response:
            return None

        choice = llm_response.get("choices", [{}])[0]
        message = choice.get("message", {})
        repaired_text = message.get("content", "")
        return self._extract_json_from_llm_text(repaired_text)
    
    # ==================== Main Run Method ====================
    
    def run(self, user_input, session_id=None):
        """
        تشغيل خدمة AI للتخطيط
        
        Args:
            user_input: رسالة المستخدم
            session_id: معرف الجلسة (اختياري)
        
        Returns:
            رد منظم مع حالة المحادثة
        """
        try:
            # الحصول على الجلسة أو إنشاء واحدة جديدة
            session = self.get_or_create_session(session_id)
            
            if not session:
                return {
                    "status": "error",
                    "message": "فشل في إنشاء جلسة المحادثة"
                }
            
            # استرجاع الحالة السابقة
            requirements = session.state.get('requirements', {}) or {}
            messages = session.state.get('messages', []) or []
            
            # إضافة رسالة المستخدم
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            # بناء رسائل LLM
            requirements_context = json.dumps(requirements, ensure_ascii=False)
            llm_messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": f"collected_requirements (known so far) = {requirements_context}"},
            ] + messages
            
            # استدعاء LLM مع الأدوات
            tools = self.get_tools_definition()
            llm_response = self.call_llm(llm_messages, tools)
            
            # معالجة الأخطاء
            if "error" in llm_response:
                return {
                    "status": "error",
                    "message": f"حدث خطأ في الاتصال بخدمة الذكاء الاصطناعي: {llm_response['error']}",
                    "session_id": session.session_id
                }
            
            # استخراج رد AI الأولي
            choice = llm_response.get("choices", [{}])[0]
            message = choice.get("message", {})

            def _extract_tool_calls_from_message(msg: dict):
                """يستخرج tool_calls بصيغتين: الرسمي + نص <tool_call>..."""
                extracted = msg.get("tool_calls", []) or []

                assistant_content_local = msg.get("content", "") or ""
                if (not extracted
                        and "<tool_call>" in assistant_content_local
                        and "</tool_call>" in assistant_content_local):
                    try:
                        raw_tool_section_local = assistant_content_local.split("<tool_call>")[1].split("</tool_call>")[0].strip()
                        logger.info("Inline tool_call detected")

                        def _coerce_arg_value(v: str):
                            vv = (v or "").strip()
                            low = vv.lower()
                            if low == "true":
                                return True
                            if low == "false":
                                return False
                            try:
                                if re.fullmatch(r"[-+]?\d+", vv):
                                    return int(vv)
                                if re.fullmatch(r"[-+]?\d*\.\d+", vv):
                                    return float(vv)
                            except Exception:
                                pass
                            return vv

                        parsed_name_local = None
                        parsed_args_local = None

                        # 1) JSON داخل <tool_call>
                        if raw_tool_section_local.startswith("{"):
                            parsed = json.loads(raw_tool_section_local)
                            parsed_name_local = parsed.get("name")
                            parsed_args_local = parsed.get("arguments", {})
                            logger.info("Inline tool_call parsed as JSON: %s", parsed_name_local)

                        # 2) صيغة XML-like
                        if not parsed_name_local:
                            lines_local = [ln.strip() for ln in raw_tool_section_local.splitlines() if ln.strip()]
                            if lines_local:
                                parsed_name_local = lines_local[0]
                                parsed_args_local = {}
                                logger.info("Inline tool_call parsed as XML-like: %s", parsed_name_local)

                                pairs_local = re.findall(
                                    r"<arg_key>\s*(.*?)\s*</\s*arg_key\s*>\s*<arg_value>\s*(.*?)\s*</\s*arg_value\s*>",
                                    raw_tool_section_local,
                                    flags=re.IGNORECASE | re.DOTALL,
                                )
                                for k, v in pairs_local:
                                    parsed_args_local[k.strip()] = _coerce_arg_value(v)

                                logger.info("Inline tool_call args keys: %s", list(parsed_args_local.keys()))

                        if parsed_name_local and isinstance(parsed_args_local, dict):
                            extracted = [{
                                "id": "inline-tool-call",
                                "type": "function",
                                "function": {
                                    "name": parsed_name_local,
                                    "arguments": json.dumps(parsed_args_local, ensure_ascii=False),
                                },
                            }]
                            msg["content"] = ""
                        else:
                            logger.warning(
                                "Inline tool_call could not be parsed. raw_tool_section=%s",
                                raw_tool_section_local,
                            )
                    except Exception:
                        logger.exception("Inline tool_call parsing failed")
                        extracted = []

                return extracted

            # تنفيذ الأدوات على شكل حلقات (حتى لو النموذج كرر <tool_call> بعد النتائج)
            max_tool_rounds = 4
            seen_tool_signatures = set()
            for round_idx in range(max_tool_rounds):
                tool_calls = _extract_tool_calls_from_message(message)
                if not tool_calls:
                    break

                # Logging مختصر للرد الخام (لتشخيص مشاكل الإنتاج)
                assistant_preview = (message.get("content", "") or "")[:600]
                logger.info(
                    "RAW_LLM_MESSAGE",
                    extra={
                        "round": round_idx,
                        "has_tool_calls": True,
                        "content_preview": assistant_preview,
                        "tool_count": len(tool_calls),
                    },
                )

                # حماية من التكرار (نفس الأدوات ونفس args)
                try:
                    signature = json.dumps(
                        [
                            {
                                "name": tc.get("function", {}).get("name"),
                                "arguments": tc.get("function", {}).get("arguments"),
                            }
                            for tc in tool_calls
                        ],
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                except Exception:
                    signature = str([(tc.get("function", {}).get("name"), tc.get("function", {}).get("arguments")) for tc in tool_calls])

                if signature in seen_tool_signatures:
                    logger.warning("Tool loop repeating detected; stopping early")
                    break
                seen_tool_signatures.add(signature)

                # خيار اختياري: رد 'searching' أولاً (يتطلب أن الواجهة تتصل مرة ثانية بنفس session)
                if self.enable_searching_first_response and round_idx == 0:
                    session.state = {
                        'requirements': requirements,
                        'messages': messages + [message],
                        'pending_tool_calls': tool_calls,
                    }
                    session.updated_at = timezone.now()
                    session.save()
                    return {
                        "status": "searching" if not self.legacy_status_mode else "missing_info",
                        "message": "جاري البحث عن أفضل الخيارات المناسبة لك...",
                        "collected_requirements": requirements,
                        "session_id": session.session_id,
                    }

                logger.info("Executing %d tool_call(s)", len(tool_calls))
                messages.append(message)

                for tool_call in tool_calls:
                    function_name = tool_call["function"]["name"]
                    function_args = json.loads(tool_call["function"]["arguments"])

                    tool_result = self.execute_tool_call(function_name, function_args)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.get("id", ""),
                        "name": function_name,
                        "content": json.dumps(tool_result, ensure_ascii=False)
                    })

                llm_messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "system", "content": f"collected_requirements (known so far) = {json.dumps(requirements, ensure_ascii=False)}"},
                ] + messages

                # نعيد الاستدعاء مع tools لتفادي نماذج لا تلتزم وتعيد tool_call كنص
                llm_response = self.call_llm(llm_messages, tools)

                if "error" in llm_response:
                    return {
                        "status": "error",
                        "message": f"حدث خطأ: {llm_response['error']}",
                        "session_id": session.session_id
                    }

                choice = llm_response.get("choices", [{}])[0]
                message = choice.get("message", {})
            
            # Logging مختصر للرد الخام النهائي
            logger.info(
                "RAW_LLM_FINAL_MESSAGE",
                extra={
                    "has_tool_calls": bool(message.get("tool_calls")),
                    "content_preview": (message.get("content", "") or "")[:600],
                },
            )

            # إضافة رد AI للرسائل
            assistant_message = message.get("content", "")
            messages.append({
                "role": "assistant",
                "content": assistant_message
            })

            # محاولة تحليل الرد كـ JSON
            try:
                response_data = self._extract_json_from_llm_text(assistant_message)
                if response_data is None:
                    response_data = self._repair_json_via_llm(assistant_message)
                if response_data is None:
                    raise json.JSONDecodeError("Invalid JSON from LLM", assistant_message, 0)

                # تحديث requirements من رد الـ LLM لمنع تكرار الأسئلة
                if isinstance(response_data, dict):
                    incoming = response_data.get("collected_requirements")
                    if isinstance(incoming, dict):
                        requirements.update({k: v for k, v in incoming.items() if v is not None})
                        response_data["collected_requirements"] = requirements
                    else:
                        response_data["collected_requirements"] = requirements

                    # توحيد أسماء الحالات (Backward compatibility مع الـ serializer الحالي)
                    if self.legacy_status_mode:
                        status_value = response_data.get("status")
                        if status_value in ("gather_info", "clarify"):
                            response_data["status"] = "missing_info"

                # حفظ الحالة بعد تحديث requirements (لمنع تكرار الأسئلة)
                self.save_session_state(session, requirements, messages)

                response_data["session_id"] = session.session_id
                
                # إضافة البيانات المرئية إذا كانت الخطة مكتملة
                if response_data.get("status") == "plan_confirmed":
                    plan = response_data.get("selected_plan", {})
                    dest_id = plan.get("destination_id")
                    hotel_id = plan.get("hotel_id")
                    
                    if dest_id and hotel_id:
                        dest_details = self.get_destination_details(dest_id)
                        hotel_details = self.get_hotel_details(hotel_id)
                        
                        response_data["visual_data"] = {
                            "destination": dest_details,
                            "hotel": hotel_details
                        }
                
                return response_data
                
            except json.JSONDecodeError:
                # إذا لم يكن JSON، نرجع رد نصي
                self.save_session_state(session, requirements, messages)
                return {
                    "status": "text_response",
                    "message": assistant_message,
                    "session_id": session.session_id
                }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"حدث خطأ غير متوقع: {str(e)}",
                "session_id": session.session_id if session else None
            }
