import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  Loader2,
  Send,
  Sparkles,
  DollarSign,
  CalendarDays,
  Users,
  Star,
  Waves,
  Sun,
  Eye,
  MapPin,
  Building2,
  Calendar,
  CheckCircle2,
  ChevronLeft,
  RotateCcw,
} from "lucide-react";
import { sendChat } from "@/features/ai-chat/ai-api";
import { normalizeAiResponse } from "@/features/ai-chat/normalize";
import { tokenStorage } from "@/lib/auth/tokenStorage";
import type { AIChatResponse, AIOption, AIPlanDetails } from "@/lib/api/types";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils/cn";
import type { LucideIcon } from "lucide-react";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  response?: AIChatResponse;
}

/* ------------------------------------------------------------------ */
/*  Requirement label mappings                                         */
/* ------------------------------------------------------------------ */

const reqMeta: Record<string, { label: string; icon: LucideIcon }> = {
  budget: { label: "الميزانية", icon: DollarSign },
  days: { label: "الأيام", icon: CalendarDays },
  people: { label: "المسافرون", icon: Users },
  min_stars: { label: "النجوم", icon: Star },
  is_coastal: { label: "ساحلية", icon: Waves },
  season: { label: "الموسم", icon: Sun },
  is_sea_view: { label: "إطلالة بحرية", icon: Eye },
};

const seasonLabels: Record<string, string> = {
  summer: "صيف",
  winter: "شتاء",
  spring: "ربيع",
  autumn: "خريف",
  all: "جميع المواسم",
};

function formatReqValue(key: string, value: unknown): string {
  if (typeof value === "boolean") return value ? "نعم" : "لا";
  if (key === "budget" && typeof value === "number")
    return `$${value.toLocaleString("en-US")}`;
  if (key === "season") return seasonLabels[String(value)] ?? String(value);
  return String(value);
}

/* ------------------------------------------------------------------ */
/*  Typing indicator                                                   */
/* ------------------------------------------------------------------ */

function TypingIndicator() {
  return (
    <div className="me-auto max-w-fit animate-fade-up">
      <div className="flex items-center gap-1.5 rounded-2xl rounded-ee-md border border-base-200 bg-white px-5 py-3.5 shadow-subtle">
        <span
          className="block h-2 w-2 rounded-full bg-base-400 animate-typing-dot"
          style={{ animationDelay: "0s" }}
        />
        <span
          className="block h-2 w-2 rounded-full bg-base-400 animate-typing-dot"
          style={{ animationDelay: "0.2s" }}
        />
        <span
          className="block h-2 w-2 rounded-full bg-base-400 animate-typing-dot"
          style={{ animationDelay: "0.4s" }}
        />
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Empty chat state with suggestion chips                             */
/* ------------------------------------------------------------------ */

const suggestions = [
  "رحلة شاطئية لشخصين بميزانية 3000 دولار",
  "إجازة عائلية لمدة أسبوع في الصيف",
  "رحلة اقتصادية 5 أيام فندق 3 نجوم",
];

function EmptyChat({
  onSuggestionClick,
}: {
  onSuggestionClick: (text: string) => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center animate-fade-in">
      <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-terracotta to-terracotta-300 shadow-glow">
        <Sparkles className="h-9 w-9 text-white" />
      </div>
      <h2 className="mb-2 font-display text-2xl text-base-900">
        مرحباً! أنا مخطط رحلتك الذكي
      </h2>
      <p className="mb-8 max-w-md font-body leading-relaxed text-base-500">
        أخبرني عن رحلة أحلامك وسأساعدك في إيجاد أفضل الخيارات ضمن ميزانيتك.
      </p>

      <div className="flex flex-wrap justify-center gap-2.5">
        {suggestions.map((text, i) => (
          <button
            key={i}
            onClick={() => onSuggestionClick(text)}
            type="button"
            className={cn(
              "rounded-xl border border-base-200 bg-white px-4 py-2.5 text-sm text-base-600 shadow-subtle transition-all hover:border-terracotta-200 hover:bg-terracotta-50 hover:text-terracotta-600 active:scale-[0.98] animate-fade-up opacity-0",
              `stagger-${i + 1}`,
            )}
          >
            {text}
          </button>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Option card (inline within chat)                                   */
/* ------------------------------------------------------------------ */

function OptionCard({
  option,
  index,
  onClick,
}: {
  option: AIOption;
  index: number;
  onClick: () => void;
}) {
  const breakdown = option.cost_breakdown;

  return (
    <button
      onClick={onClick}
      type="button"
      className={cn(
        "group w-full rounded-2xl border border-base-200 bg-white p-5 text-start transition-all duration-200 hover:border-terracotta-200 hover:shadow-card active:scale-[0.99] animate-fade-up opacity-0",
        `stagger-${index + 1}`,
      )}
    >
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-terracotta-50 font-display text-sm text-terracotta">
            {option.option_id}
          </div>
          <span className="font-display text-base-900">
            الخيار {option.option_id}
          </span>
        </div>
        <div className="flex items-center gap-1 rounded-full bg-teal-50 px-3 py-1.5">
          <DollarSign className="h-3.5 w-3.5 text-teal" />
          <span className="text-sm font-display text-teal">
            {typeof option.total_cost === "number"
              ? option.total_cost.toLocaleString("en-US")
              : "غير محدد"}
          </span>
        </div>
      </div>

      {breakdown && (
        <div className="grid grid-cols-3 gap-2">
          {breakdown.flights != null && (
            <div className="rounded-xl bg-base-50 p-2.5 text-center">
              <p className="text-[11px] text-base-400">الطيران</p>
              <p className="text-sm font-display text-base-700">
                ${breakdown.flights.toLocaleString("en-US")}
              </p>
            </div>
          )}
          {breakdown.accommodation != null && (
            <div className="rounded-xl bg-base-50 p-2.5 text-center">
              <p className="text-[11px] text-base-400">الإقامة</p>
              <p className="text-sm font-display text-base-700">
                ${breakdown.accommodation.toLocaleString("en-US")}
              </p>
            </div>
          )}
          {breakdown.daily_living != null && (
            <div className="rounded-xl bg-base-50 p-2.5 text-center">
              <p className="text-[11px] text-base-400">المعيشة</p>
              <p className="text-sm font-display text-base-700">
                ${breakdown.daily_living.toLocaleString("en-US")}
              </p>
            </div>
          )}
        </div>
      )}

      <div className="mt-3 flex items-center justify-end gap-1 text-xs text-terracotta opacity-0 transition-opacity group-hover:opacity-100">
        <span>اختر هذا الخيار</span>
        <ChevronLeft className="h-3.5 w-3.5" />
      </div>
    </button>
  );
}

/* ------------------------------------------------------------------ */
/*  Confirmed plan itinerary card                                      */
/* ------------------------------------------------------------------ */

function ItineraryCard({
  plan,
  visualData,
}: {
  plan: AIPlanDetails;
  visualData?: AIChatResponse["visual_data"];
}) {
  const dest = visualData?.destination;
  const hotel = visualData?.hotel;
  const events = visualData?.events;

  return (
    <div className="mt-3 rounded-2xl border border-teal-200 bg-gradient-to-br from-teal-50/50 to-white p-6 shadow-card animate-fade-up">
      {/* Header */}
      <div className="mb-5 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal">
          <CheckCircle2 className="h-5 w-5 text-white" />
        </div>
        <div>
          <h3 className="font-display text-lg text-base-900">
            تم تأكيد خطة الرحلة
          </h3>
          <p className="text-xs text-base-500">{plan.days} أيام</p>
        </div>
      </div>

      {/* Destination */}
      {dest && (
        <div className="mb-4 overflow-hidden rounded-xl border border-base-200 bg-white">
          {dest.dest_images?.[0] && (
            <img
              src={dest.dest_images[0].file}
              alt={dest.name}
              className="h-40 w-full object-cover"
            />
          )}
          <div className="p-4">
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-terracotta" />
              <h4 className="font-display text-base-900">{dest.name}</h4>
            </div>
            <p className="mt-0.5 text-sm text-base-500">{dest.country}</p>
            {dest.description && (
              <p className="mt-2 text-sm leading-relaxed text-base-600">
                {dest.description}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Hotel */}
      {hotel && (
        <div className="mb-4 rounded-xl border border-base-200 bg-white p-4">
          {hotel.hotel_images?.[0] && (
            <img
              src={hotel.hotel_images[0].file}
              alt={hotel.name}
              className="mb-3 h-28 w-full rounded-lg object-cover"
            />
          )}
          <div className="flex items-center gap-2">
            <Building2 className="h-4 w-4 text-gold" />
            <h4 className="font-display text-base-900">{hotel.name}</h4>
            <div className="ms-auto flex gap-0.5">
              {Array.from({ length: hotel.stars }).map((_, i) => (
                <Star key={i} className="h-3.5 w-3.5 fill-gold text-gold" />
              ))}
            </div>
          </div>
          <p className="mt-1 text-sm text-base-500">
            ${hotel.price_per_night}/ليلة
            {hotel.is_sea_view ? " · إطلالة بحرية" : ""}
          </p>
        </div>
      )}

      {/* Events */}
      {events && events.length > 0 && (
        <div className="mb-4">
          <h4 className="mb-2 font-display text-sm text-base-700">
            الفعاليات المقترحة
          </h4>
          <div className="space-y-2">
            {events.map((event) => (
              <div
                key={event.id}
                className="flex items-center justify-between rounded-xl border border-base-200 bg-white p-3"
              >
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-teal" />
                  <span className="text-sm text-base-700">{event.name}</span>
                </div>
                <span className="text-xs text-base-500">
                  {event.is_free ? "مجانية" : `$${event.price_per_person}`}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Cost breakdown */}
      {plan.cost_breakdown && (
        <div className="rounded-xl bg-base-900 p-5 text-white">
          <h4 className="mb-3 font-display text-sm text-base-400">
            تفاصيل التكلفة
          </h4>
          <div className="space-y-2.5 text-sm">
            {plan.cost_breakdown.flights != null && (
              <div className="flex justify-between">
                <span className="text-base-400">الطيران</span>
                <span>
                  ${plan.cost_breakdown.flights.toLocaleString("en-US")}
                </span>
              </div>
            )}
            {plan.cost_breakdown.accommodation != null && (
              <div className="flex justify-between">
                <span className="text-base-400">الإقامة</span>
                <span>
                  ${plan.cost_breakdown.accommodation.toLocaleString("en-US")}
                </span>
              </div>
            )}
            {plan.cost_breakdown.daily_living != null && (
              <div className="flex justify-between">
                <span className="text-base-400">المعيشة اليومية</span>
                <span>
                  ${plan.cost_breakdown.daily_living.toLocaleString("en-US")}
                </span>
              </div>
            )}
            <div className="flex justify-between border-t border-white/15 pt-2.5 font-display">
              <span>الإجمالي</span>
              <span className="text-gold-200">
                $
                {(
                  plan.cost_breakdown.total ?? plan.total_cost
                )?.toLocaleString("en-US") ?? "—"}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main page                                                          */
/* ------------------------------------------------------------------ */

export function TripPlannerPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(() =>
    tokenStorage.getAiSessionId(),
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);

  /* Auto-scroll on new content */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /* Latest presented options */
  const latestOptions = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i -= 1) {
      const options = messages[i].response?.options;
      if (options?.length) return options;
    }
    return [] as AIOption[];
  }, [messages]);

  /* Accumulated requirements */
  const collectedRequirements = useMemo(() => {
    const reqs: Record<string, unknown> = {};
    for (const msg of messages) {
      if (msg.response?.collected_requirements) {
        Object.assign(reqs, msg.response.collected_requirements);
      }
    }
    return reqs;
  }, [messages]);

  const mutation = useMutation({
    mutationFn: sendChat,
    onSuccess: (raw) => {
      const response = normalizeAiResponse(raw);
      if (response.session_id) {
        tokenStorage.setAiSessionId(response.session_id);
        setSessionId(response.session_id);
      }
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          text: response.message ?? "تم استلام الرد.",
          response,
        },
      ]);
    },
  });

  function submitPrompt(promptText: string) {
    const trimmed = promptText.trim();
    if (!trimmed) return;

    const lower = trimmed.toLowerCase();
    if (
      (lower.includes("الخيار") || lower.includes("option")) &&
      latestOptions.length === 0
    ) {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          text: "لا يمكن تأكيد خيار قبل عرض الخيارات أولاً.",
        },
      ]);
      return;
    }

    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", text: trimmed },
    ]);
    setInput("");

    mutation.mutate({
      prompt: trimmed,
      session_id: sessionId ?? undefined,
    });
  }

  function resetSession() {
    tokenStorage.clearAiSessionId();
    setSessionId(null);
    setMessages([]);
  }

  const hasRequirements = Object.keys(collectedRequirements).length > 0;

  return (
    <div className="mx-auto max-w-3xl">
      {/* Session bar */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {sessionId ? (
            <>
              <div className="h-2 w-2 rounded-full bg-teal animate-pulse" />
              <span className="text-xs font-display text-base-400">
                جلسة نشطة
              </span>
            </>
          ) : (
            <span className="text-xs font-display text-base-400">
              جلسة جديدة
            </span>
          )}
        </div>
        {messages.length > 0 && (
          <button
            onClick={resetSession}
            type="button"
            className="flex items-center gap-1.5 text-xs text-base-400 transition hover:text-terracotta"
          >
            <RotateCcw className="h-3 w-3" />
            جلسة جديدة
          </button>
        )}
      </div>

      {/* Requirements strip */}
      {hasRequirements && (
        <div className="mb-4 flex flex-wrap gap-2 rounded-2xl border border-base-200 bg-white p-3 shadow-subtle animate-fade-in">
          {Object.entries(collectedRequirements).map(([key, val]) => {
            const meta = reqMeta[key];
            const Icon = meta?.icon;
            return (
              <span
                key={key}
                className="inline-flex items-center gap-1.5 rounded-full bg-base-50 px-3 py-1.5 text-xs"
              >
                {Icon && <Icon className="h-3 w-3 text-terracotta" />}
                <span className="text-base-500">
                  {meta?.label ?? key}:
                </span>
                <span className="font-display text-base-700">
                  {formatReqValue(key, val)}
                </span>
              </span>
            );
          })}
        </div>
      )}

      {/* Chat container */}
      <div className="overflow-hidden rounded-3xl border border-base-200 bg-white/40 shadow-card backdrop-blur-sm">
        {/* Messages area */}
        <div className="max-h-[62vh] min-h-[42vh] space-y-4 overflow-y-auto p-6">
          {messages.length === 0 && (
            <EmptyChat onSuggestionClick={submitPrompt} />
          )}

          {messages.map((msg) => (
            <div key={msg.id}>
              {msg.role === "user" ? (
                /* ── User message ── */
                <div className="ms-10 animate-fade-up opacity-0">
                  <div className="rounded-2xl rounded-ss-md bg-gradient-to-br from-base-900 to-base-800 p-4 text-base-100 shadow-subtle">
                    <p className="font-body text-sm leading-7">{msg.text}</p>
                  </div>
                </div>
              ) : (
                /* ── Assistant message ── */
                <div className="me-10 animate-fade-up opacity-0">
                  <div className="rounded-2xl rounded-ee-md border border-base-200 bg-white p-4 shadow-subtle">
                    <p className="font-body text-sm leading-7 text-base-800 whitespace-pre-wrap">
                      {msg.text}
                    </p>
                  </div>

                  {/* Inline option cards */}
                  {msg.response?.options && msg.response.options.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {msg.response.options.map((option, idx) => (
                        <OptionCard
                          key={option.option_id}
                          option={option}
                          index={idx}
                          onClick={() =>
                            submitPrompt(
                              `أختار الخيار رقم ${option.option_id}`,
                            )
                          }
                        />
                      ))}
                    </div>
                  )}

                  {/* Confirmed plan itinerary */}
                  {msg.response?.selected_plan && (
                    <ItineraryCard
                      plan={msg.response.selected_plan}
                      visualData={msg.response.visual_data}
                    />
                  )}
                </div>
              )}
            </div>
          ))}

          {mutation.isPending && <TypingIndicator />}

          {mutation.isError && (
            <div className="me-10 animate-fade-up opacity-0">
              <div className="rounded-2xl border border-red-100 bg-red-50 p-4">
                <p className="text-sm text-red-600">
                  تعذر الوصول للخادم. حاول مرة أخرى.
                </p>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input bar */}
        <div className="border-t border-base-200 bg-white p-4">
          <div className="flex items-end gap-3">
            <textarea
              className="max-h-28 min-h-[2.75rem] flex-1 resize-none rounded-2xl border-0 bg-base-100 px-4 py-3 font-body text-sm text-base-900 placeholder:text-base-400 outline-none transition focus:ring-2 focus:ring-terracotta/10"
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  submitPrompt(input);
                }
              }}
              placeholder="اكتب رسالتك هنا..."
              value={input}
              rows={1}
            />
            <Button
              className="shrink-0 rounded-xl"
              disabled={mutation.isPending || !input.trim()}
              onClick={() => submitPrompt(input)}
              variant="secondary"
              size="icon"
            >
              {mutation.isPending ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Send className="h-5 w-5" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
