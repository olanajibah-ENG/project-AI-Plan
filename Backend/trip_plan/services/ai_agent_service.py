import json
import re
import ast
import logging
import uuid
from typing import Optional
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from ..models.travel_model import Destination, Hotel, ConversationSession, Event
from ..serializers.travel_serializer import DestinationSerializer, HotelSerializer, EventSerializer


logger = logging.getLogger(__name__)


class UserSignalSchema(BaseModel):
    budget: Optional[float] = Field(default=None)
    days: Optional[int] = Field(default=None)
    people: Optional[int] = Field(default=None)
    is_coastal: Optional[bool] = Field(default=None)
    min_stars: Optional[int] = Field(default=None)
    season: Optional[str] = Field(default=None)
    is_sea_view: Optional[bool] = Field(default=None)
    selected_option_id: Optional[int] = Field(default=None)
    asks_to_change: bool = Field(default=False)


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
    
    # ==================== LangChain Integration ====================

    def _build_chat_model(self):
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured.")
        return ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.2,
            max_tokens=1500,
        )

    def get_langchain_tools(self):
        return [
            StructuredTool.from_function(
                func=self.search_destinations_and_hotels,
                name="search_destinations_and_hotels",
                description="البحث عن وجهات سياحية وفنادق مناسبة حسب متطلبات المستخدم",
            ),
            StructuredTool.from_function(
                func=self.calculate_trip_cost_tool,
                name="calculate_trip_cost_tool",
                description="حساب التكلفة الكلية لرحلة معينة اعتماداً على معطيات التكلفة",
            ),
            StructuredTool.from_function(
                func=self.get_destination_details,
                name="get_destination_details",
                description="الحصول على تفاصيل كاملة عن وجهة سياحية محددة",
            ),
            StructuredTool.from_function(
                func=self.get_hotel_details,
                name="get_hotel_details",
                description="الحصول على تفاصيل كاملة عن فندق محدد",
            ),
            StructuredTool.from_function(
                func=self.search_events,
                name="search_events",
                description="البحث عن فعاليات موسمية في وجهة معينة",
            ),
        ]

    # Backward-compatible name to avoid touching the rest of the flow.
    def get_tools_definition(self):
        return self.get_langchain_tools()
    
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
        previous = session.state if isinstance(session.state, dict) else {}
        session.state = {
            'requirements': requirements,
            'messages': messages,
            'last_options': previous.get('last_options', []),
        }
        session.updated_at = timezone.now()
        session.save()

    @staticmethod
    def _required_keys():
        return ["budget", "days", "people", "is_coastal", "min_stars"]

    @staticmethod
    def _missing_requirements(requirements):
        return [k for k in TravelAgentService._required_keys() if requirements.get(k) is None]

    @staticmethod
    def _first_missing_question(missing):
        mapping = {
            "budget": "ما هي ميزانيتك الإجمالية بالدولار؟",
            "days": "كم عدد أيام الرحلة؟",
            "people": "كم عدد الأشخاص المسافرين؟",
            "is_coastal": "هل تفضل وجهة ساحلية أم جبلية؟",
            "min_stars": "ما الحد الأدنى لعدد نجوم الفندق (1 إلى 5)؟",
        }
        for key in TravelAgentService._required_keys():
            if key in missing:
                return mapping[key]
        return "هل يمكن توضيح متطلبات الرحلة الأساسية؟"

    @staticmethod
    def _fallback_extract_signal(user_input):
        text = (user_input or "").lower()
        signal = {
            "budget": None,
            "days": None,
            "people": None,
            "is_coastal": None,
            "min_stars": None,
            "season": None,
            "is_sea_view": None,
            "selected_option_id": None,
            "asks_to_change": False,
        }

        num_map = {"واحد": 1, "واحدة": 1, "اثنين": 2, "اثنان": 2, "ثلاثة": 3, "أربعة": 4, "خمسة": 5}

        m = re.search(r"(budget|ميزاني[تة]|ميزانية)\D*(\d+(?:\.\d+)?)", text)
        if m:
            signal["budget"] = float(m.group(2))

        m = re.search(r"(\d+)\s*(day|days|يوم|أيام)", text)
        if m:
            signal["days"] = int(m.group(1))

        m = re.search(r"(\d+)\s*(person|people|شخص|أشخاص)", text)
        if m:
            signal["people"] = int(m.group(1))
        elif "شخصان" in text:
            signal["people"] = 2
        elif "شخصين" in text:
            signal["people"] = 2

        m = re.search(r"(\d)\s*(star|نجوم|نجمة)", text)
        if m:
            signal["min_stars"] = int(m.group(1))
        else:
            for k, v in num_map.items():
                if k in text and ("نجم" in text):
                    signal["min_stars"] = v
                    break

        if any(tok in text for tok in ["coastal", "ساحل", "ساحلية", "بحر"]):
            signal["is_coastal"] = True
        if any(tok in text for tok in ["mountain", "جبل", "جبلية"]):
            signal["is_coastal"] = False

        for season in ("summer", "winter", "spring", "autumn"):
            if season in text:
                signal["season"] = season

        if "sea view" in text or "مطل" in text:
            signal["is_sea_view"] = True

        m = re.search(r"(?:option|الخيار)\D*(\d+)", text)
        if m:
            signal["selected_option_id"] = int(m.group(1))

        if any(tok in text for tok in ["غيّر", "تغيير", "change", "another", "غير مناسب", "مو مناسب"]):
            signal["asks_to_change"] = True

        return signal

    def _extract_user_signal(self, user_input, requirements):
        if not self.api_key:
            return self._fallback_extract_signal(user_input)
        try:
            model = self._build_chat_model().with_structured_output(UserSignalSchema)
            prompt = (
                "استخرج فقط القيم الصريحة أو المستدل عليها بقوة من رسالة المستخدم.\n"
                "لا تخترع أي قيمة.\n"
                "selected_option_id يظهر فقط إذا اختار المستخدم رقماً.\n"
                f"known_requirements={json.dumps(requirements, ensure_ascii=False)}\n"
                f"user_message={user_input}"
            )
            parsed = model.invoke(prompt)
            if hasattr(parsed, "model_dump"):
                return parsed.model_dump()
            return dict(parsed)
        except Exception:
            logger.exception("Structured extraction failed; using fallback parser")
            return self._fallback_extract_signal(user_input)

    @staticmethod
    def _merge_requirements(requirements, signal):
        merged = dict(requirements or {})
        for key in ("budget", "days", "people", "is_coastal", "min_stars", "season", "is_sea_view"):
            val = signal.get(key)
            if val is not None:
                merged[key] = val
        if merged.get("min_stars") is not None:
            try:
                merged["min_stars"] = max(1, min(5, int(merged["min_stars"])))
            except Exception:
                merged["min_stars"] = 3
        return merged
    
    # ==================== LLM Integration ====================
    
    @staticmethod
    def _normalize_content(content):
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(item.get("text", ""))
                elif isinstance(item, str):
                    parts.append(item)
            return "".join(parts)
        return str(content or "")

    def _convert_to_langchain_messages(self, messages):
        converted = []
        for msg in messages or []:
            role = msg.get("role")
            content = self._normalize_content(msg.get("content", ""))
            if role == "system":
                converted.append(SystemMessage(content=content))
            elif role == "user":
                converted.append(HumanMessage(content=content))
            elif role == "assistant":
                tool_calls = msg.get("tool_calls")
                if isinstance(tool_calls, list) and tool_calls:
                    converted.append(AIMessage(content=content, tool_calls=tool_calls))
                else:
                    converted.append(AIMessage(content=content))
            elif role == "tool":
                converted.append(
                    ToolMessage(
                        content=content,
                        tool_call_id=msg.get("tool_call_id") or "tool-call",
                    )
                )
        return converted

    @staticmethod
    def _convert_tool_calls_to_openai(tool_calls):
        normalized = []
        for call in tool_calls or []:
            normalized.append(
                {
                    "id": call.get("id", ""),
                    "type": "function",
                    "function": {
                        "name": call.get("name"),
                        "arguments": json.dumps(call.get("args", {}), ensure_ascii=False),
                    },
                }
            )
        return normalized

    def call_llm(self, messages, tools=None):
        try:
            model = self._build_chat_model()
            if tools:
                model = model.bind_tools(self.get_langchain_tools())

            lc_messages = self._convert_to_langchain_messages(messages)
            ai_msg = model.invoke(lc_messages)
            return {
                "choices": [
                    {
                        "message": {
                            "content": self._normalize_content(ai_msg.content),
                            "tool_calls": self._convert_tool_calls_to_openai(getattr(ai_msg, "tool_calls", None)),
                        }
                    }
                ]
            }
        except Exception as exc:
            logger.exception("LangChain invocation failed")
            return {"error": str(exc)}

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
        session = None
        try:
            session = self.get_or_create_session(session_id)
            if not session:
                return {"status": "error", "message": "فشل في إنشاء جلسة المحادثة"}

            state = session.state if isinstance(session.state, dict) else {}
            requirements = state.get("requirements", {}) or {}
            messages = state.get("messages", []) or []
            last_options = state.get("last_options", []) or []

            messages.append({"role": "user", "content": user_input})

            signal = self._extract_user_signal(user_input, requirements)
            requirements = self._merge_requirements(requirements, signal)

            # تأكيد خيار محدد من آخر خيارات معروضة فقط (grounding)
            selected_option_id = signal.get("selected_option_id")
            if selected_option_id is not None and last_options:
                chosen = next((o for o in last_options if o.get("option_id") == selected_option_id), None)
                if chosen:
                    plan = {
                        "option_id": chosen["option_id"],
                        "destination_id": chosen["destination_id"],
                        "hotel_id": chosen["hotel_id"],
                        "total_cost": chosen.get("total_cost"),
                        "days": int(requirements.get("days") or 0),
                        "cost_breakdown": chosen.get("cost_breakdown"),
                    }
                    dest_id = chosen["destination_id"]
                    season = requirements.get("season", "all")
                    events = self.search_events(dest_id, season=season, max_price=None)
                    if events:
                        plan["events"] = [
                            {
                                "event_id": ev.get("id"),
                                "name": ev.get("name"),
                                "price_per_person": ev.get("price_per_person"),
                            }
                            for ev in events[:3]
                        ]

                    response = {
                        "status": "plan_confirmed",
                        "message": f"تم اعتماد الخيار رقم {selected_option_id}. إليك ملخص الرحلة النهائي.",
                        "collected_requirements": requirements,
                        "selected_plan": plan,
                        "session_id": session.session_id,
                    }
                    messages.append({"role": "assistant", "content": json.dumps(response, ensure_ascii=False)})
                    session.state = {"requirements": requirements, "messages": messages, "last_options": last_options}
                    session.updated_at = timezone.now()
                    session.save()
                    return response

                response = {
                    "status": "gather_info",
                    "message": "رقم الخيار غير موجود في الخيارات الحالية. اختر رقماً صحيحاً من الخيارات المعروضة.",
                    "collected_requirements": requirements,
                    "session_id": session.session_id,
                }
                messages.append({"role": "assistant", "content": json.dumps(response, ensure_ascii=False)})
                session.state = {"requirements": requirements, "messages": messages, "last_options": last_options}
                session.updated_at = timezone.now()
                session.save()
                return response if not self.legacy_status_mode else {**response, "status": "missing_info"}

            missing = self._missing_requirements(requirements)
            if missing:
                response = {
                    "status": "gather_info",
                    "message": self._first_missing_question(missing),
                    "collected_requirements": requirements,
                    "session_id": session.session_id,
                }
                messages.append({"role": "assistant", "content": json.dumps(response, ensure_ascii=False)})
                session.state = {"requirements": requirements, "messages": messages, "last_options": last_options}
                session.updated_at = timezone.now()
                session.save()
                return response if not self.legacy_status_mode else {**response, "status": "missing_info"}

            options_raw = self.search_destinations_and_hotels(
                budget=requirements.get("budget"),
                days=requirements.get("days"),
                people=requirements.get("people"),
                is_coastal=requirements.get("is_coastal"),
                min_stars=requirements.get("min_stars", 3),
                season=requirements.get("season"),
                is_sea_view=requirements.get("is_sea_view"),
            )

            if not options_raw:
                response = {
                    "status": "no_options",
                    "message": "لم أجد خيارات مناسبة بهذه المعايير. هل تفضّل زيادة الميزانية أو تقليل النجوم/الأيام؟",
                    "collected_requirements": requirements,
                    "session_id": session.session_id,
                }
                messages.append({"role": "assistant", "content": json.dumps(response, ensure_ascii=False)})
                session.state = {"requirements": requirements, "messages": messages, "last_options": []}
                session.updated_at = timezone.now()
                session.save()
                return response

            options = []
            for idx, item in enumerate(options_raw[:3], start=1):
                options.append(
                    {
                        "option_id": idx,
                        "destination_id": item["destination_id"],
                        "hotel_id": item["hotel_id"],
                        "total_cost": item.get("total_cost"),
                        "cost_breakdown": item.get("cost_breakdown"),
                    }
                )

            response = {
                "status": "options_presented",
                "message": "وجدت أفضل الخيارات المناسبة لك. اختر رقم الخيار الذي تفضله.",
                "collected_requirements": requirements,
                "options": options,
                "session_id": session.session_id,
            }

            messages.append({"role": "assistant", "content": json.dumps(response, ensure_ascii=False)})
            session.state = {"requirements": requirements, "messages": messages, "last_options": options}
            session.updated_at = timezone.now()
            session.save()
            return response
        except Exception as e:
            return {
                "status": "error",
                "message": f"حدث خطأ غير متوقع: {str(e)}",
                "session_id": session.session_id if session else None,
            }
