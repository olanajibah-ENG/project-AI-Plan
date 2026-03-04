import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil, Trash2, Upload, CheckCircle2, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { Toggle } from "@/components/ui/toggle";
import { listDestinationsCatalog } from "@/features/shared/catalog-api";
import {
  createEvent,
  deleteEvent,
  listEvents,
  updateEvent,
  type EventPayload,
} from "@/features/admin-events/events-api";
import type { EventItem } from "@/lib/api/types";

const seasonOptions: EventPayload["season"][] = [
  "summer",
  "winter",
  "spring",
  "autumn",
  "all",
];

const seasonLabels: Record<string, string> = {
  summer: "صيف",
  winter: "شتاء",
  spring: "ربيع",
  autumn: "خريف",
  all: "جميع المواسم",
};

const initialForm: EventPayload = {
  destination: 0,
  name: "",
  description: "",
  season: "summer",
  price_per_person: "",
  duration_hours: 2,
  is_free: false,
  images: null,
};

export function EventsPage() {
  const queryClient = useQueryClient();
  const [notice, setNotice] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [selectedSeason, setSelectedSeason] = useState<
    EventPayload["season"] | "all_filter"
  >("all_filter");
  const [form, setForm] = useState<EventPayload>(initialForm);
  const [fileNames, setFileNames] = useState<string[]>([]);

  const destinationsQuery = useQuery({
    queryKey: ["catalog-destinations"],
    queryFn: listDestinationsCatalog,
    retry: 2,
  });
  const eventsQuery = useQuery({
    queryKey: ["events"],
    queryFn: listEvents,
    retry: 2,
  });

  const createMutation = useMutation({
    mutationFn: createEvent,
    onSuccess: () => {
      setNotice("تمت إضافة الفعالية");
      setForm(initialForm);
      setFileNames([]);
      queryClient.invalidateQueries({ queryKey: ["events"] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: EventPayload }) =>
      updateEvent(id, payload),
    onSuccess: () => {
      setNotice("تم تحديث الفعالية");
      setEditingId(null);
      setForm(initialForm);
      setFileNames([]);
      queryClient.invalidateQueries({ queryKey: ["events"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteEvent,
    onSuccess: () => {
      setNotice("تم حذف الفعالية");
      queryClient.invalidateQueries({ queryKey: ["events"] });
    },
  });

  const filteredEvents = useMemo(() => {
    const list = eventsQuery.data ?? [];
    if (selectedSeason === "all_filter") return list;
    return list.filter(
      (e) => e.season === selectedSeason || e.season === "all",
    );
  }, [eventsQuery.data, selectedSeason]);

  /* Map destination IDs to names */
  const destNameMap = useMemo(() => {
    const map: Record<number, string> = {};
    for (const d of destinationsQuery.data ?? []) {
      map[d.id] = d.name;
    }
    return map;
  }, [destinationsQuery.data]);

  function startEdit(item: EventItem) {
    setEditingId(item.id);
    setForm({
      destination: item.destination,
      name: item.name,
      description: item.description,
      season: item.season,
      price_per_person: item.price_per_person,
      duration_hours: item.duration_hours,
      is_free: item.is_free,
      images: null,
    });
    setFileNames([]);
    setNotice("");
  }

  function submit() {
    if (!form.destination) return;
    if (editingId) {
      updateMutation.mutate({ id: editingId, payload: form });
    } else {
      createMutation.mutate(form);
    }
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl text-base-900">
            إدارة الفعاليات
          </h1>
          <p className="mt-1 text-sm text-base-500">
            أضف وعدّل الفعاليات والأنشطة السياحية.
          </p>
        </div>
        <Badge variant="terracotta">{filteredEvents.length} فعالية</Badge>
      </div>

      {/* Notice */}
      {notice && (
        <div className="flex items-center gap-2 rounded-xl border border-teal-100 bg-teal-50 p-3 text-sm text-teal animate-fade-up">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          {notice}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-[1fr_1.4fr]">
        {/* ── Form ── */}
        <Card className="self-start">
          <h2 className="mb-5 font-display text-lg text-base-900">
            {editingId ? "تعديل الفعالية" : "إضافة فعالية جديدة"}
          </h2>

          <div className="space-y-4">
            <div className="space-y-1.5">
              <label className="block text-xs font-display text-base-500">
                الوجهة
              </label>
              <Select
                value={form.destination || ""}
                onChange={(e) =>
                  setForm((p) => ({
                    ...p,
                    destination: Number(e.target.value),
                  }))
                }
              >
                <option value="">اختر الوجهة</option>
                {(destinationsQuery.data ?? []).map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-display text-base-500">
                اسم الفعالية
              </label>
              <Input
                placeholder="مثال: جولة بحرية"
                value={form.name}
                onChange={(e) =>
                  setForm((p) => ({ ...p, name: e.target.value }))
                }
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-display text-base-500">
                الوصف
              </label>
              <Textarea
                placeholder="وصف تفصيلي للفعالية..."
                value={form.description}
                onChange={(e) =>
                  setForm((p) => ({ ...p, description: e.target.value }))
                }
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-display text-base-500">
                الموسم
              </label>
              <Select
                value={form.season}
                onChange={(e) =>
                  setForm((p) => ({
                    ...p,
                    season: e.target.value as EventPayload["season"],
                  }))
                }
              >
                {seasonOptions.map((season) => (
                  <option key={season} value={season}>
                    {seasonLabels[season]}
                  </option>
                ))}
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="block text-xs font-display text-base-500">
                  سعر الشخص ($)
                </label>
                <Input
                  placeholder="0.00"
                  value={form.price_per_person}
                  disabled={form.is_free}
                  onChange={(e) =>
                    setForm((p) => ({
                      ...p,
                      price_per_person: e.target.value,
                    }))
                  }
                />
              </div>
              <div className="space-y-1.5">
                <label className="block text-xs font-display text-base-500">
                  المدة (ساعات)
                </label>
                <Input
                  placeholder="2"
                  value={String(form.duration_hours)}
                  onChange={(e) =>
                    setForm((p) => ({
                      ...p,
                      duration_hours: Number(e.target.value || 0),
                    }))
                  }
                />
              </div>
            </div>

            <Toggle
              id="is_free"
              checked={form.is_free}
              onChange={(v) => setForm((p) => ({ ...p, is_free: v }))}
              label="فعالية مجانية"
            />

            {/* File upload */}
            <div className="space-y-1.5">
              <label className="block text-xs font-display text-base-500">
                الصور
              </label>
              <label className="flex cursor-pointer flex-col items-center gap-2 rounded-xl border-2 border-dashed border-base-300 p-5 transition hover:border-terracotta-200 hover:bg-terracotta-50/30">
                <Upload className="h-5 w-5 text-base-400" />
                <span className="text-sm text-base-500">
                  {fileNames.length
                    ? `${fileNames.length} صورة محددة`
                    : "اضغط لرفع الصور"}
                </span>
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  className="sr-only"
                  onChange={(e) => {
                    setForm((p) => ({ ...p, images: e.target.files }));
                    setFileNames(
                      e.target.files
                        ? Array.from(e.target.files).map((f) => f.name)
                        : [],
                    );
                  }}
                />
              </label>
            </div>

            <div className="flex gap-2 pt-1">
              <Button onClick={submit} variant="secondary" className="flex-1">
                {editingId ? "تحديث" : "إضافة"}
              </Button>
              {editingId && (
                <Button
                  onClick={() => {
                    setEditingId(null);
                    setForm(initialForm);
                    setFileNames([]);
                  }}
                  variant="ghost"
                >
                  إلغاء
                </Button>
              )}
            </div>
          </div>
        </Card>

        {/* ── List ── */}
        <div className="space-y-4">
          <Select
            value={selectedSeason}
            onChange={(e) =>
              setSelectedSeason(
                e.target.value as EventPayload["season"] | "all_filter",
              )
            }
          >
            <option value="all_filter">كل المواسم</option>
            {seasonOptions.map((season) => (
              <option key={season} value={season}>
                {seasonLabels[season]}
              </option>
            ))}
          </Select>

          {eventsQuery.isLoading && (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-20 animate-pulse rounded-2xl bg-base-200/50"
                />
              ))}
            </div>
          )}

          <div className="space-y-3">
            {filteredEvents.map((event) => (
              <div
                key={event.id}
                className="group rounded-2xl border border-base-200 bg-white p-4 transition-all hover:shadow-card"
              >
                <div className="flex items-start gap-4">
                  {event.event_images?.[0] && (
                    <img
                      src={event.event_images[0].file}
                      alt={event.name}
                      className="h-14 w-14 shrink-0 rounded-xl object-cover"
                    />
                  )}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-display text-base-900">
                        {event.name}
                      </h3>
                      <Badge
                        variant={event.is_free ? "teal" : "gold"}
                        className="text-[10px]"
                      >
                        {event.is_free ? "مجانية" : `$${event.price_per_person}`}
                      </Badge>
                    </div>
                    <p className="mt-0.5 text-xs text-base-500">
                      {destNameMap[event.destination] ?? `وجهة #${event.destination}`}
                    </p>
                    {event.description && (
                      <p className="mt-1 line-clamp-2 text-xs text-base-600">
                        {event.description}
                      </p>
                    )}
                    <div className="mt-2 flex items-center gap-3 text-xs text-base-400">
                      <span className="inline-flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {event.duration_hours} ساعة
                      </span>
                      <Badge variant="muted" className="text-[10px]">
                        {seasonLabels[event.season]}
                      </Badge>
                    </div>
                  </div>
                  <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-8 w-8"
                      onClick={() => startEdit(event)}
                    >
                      <Pencil className="h-3.5 w-3.5" />
                    </Button>
                    <Button
                      size="icon"
                      variant="danger"
                      className="h-8 w-8"
                      onClick={() => deleteMutation.mutate(event.id)}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}

            {!eventsQuery.isLoading && filteredEvents.length === 0 && (
              <div className="py-12 text-center">
                <p className="text-sm text-base-400">لا توجد فعاليات بعد.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
