import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil, Trash2, Upload, CheckCircle2, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Toggle } from "@/components/ui/toggle";
import type { Destination } from "@/lib/api/types";
import {
  createDestination,
  deleteDestination,
  listDestinations,
  updateDestination,
  type DestinationPayload,
} from "@/features/admin-destinations/destinations-api";

const emptyPayload: DestinationPayload = {
  name: "",
  country: "",
  flight_cost: "",
  daily_living_cost: "",
  is_coastal: false,
  description: "",
  best_seasons: "",
  images: null,
};

export function DestinationsPage() {
  const queryClient = useQueryClient();
  const [notice, setNotice] = useState<string>("");
  const [search, setSearch] = useState("");
  const [form, setForm] = useState<DestinationPayload>(emptyPayload);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [fileNames, setFileNames] = useState<string[]>([]);

  const destinationsQuery = useQuery({
    queryKey: ["destinations"],
    queryFn: listDestinations,
    retry: 2,
  });

  const createMutation = useMutation({
    mutationFn: createDestination,
    onSuccess: () => {
      setNotice("تمت إضافة الوجهة بنجاح");
      setForm(emptyPayload);
      setFileNames([]);
      queryClient.invalidateQueries({ queryKey: ["destinations"] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: number;
      payload: DestinationPayload;
    }) => updateDestination(id, payload),
    onSuccess: () => {
      setNotice("تم تحديث الوجهة بنجاح");
      setEditingId(null);
      setForm(emptyPayload);
      setFileNames([]);
      queryClient.invalidateQueries({ queryKey: ["destinations"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteDestination,
    onSuccess: () => {
      setNotice("تم حذف الوجهة");
      queryClient.invalidateQueries({ queryKey: ["destinations"] });
    },
  });

  const filtered = useMemo(() => {
    const list = destinationsQuery.data ?? [];
    if (!search.trim()) return list;
    const q = search.toLowerCase();
    return list.filter(
      (d) =>
        d.name.toLowerCase().includes(q) ||
        d.country.toLowerCase().includes(q),
    );
  }, [destinationsQuery.data, search]);

  function startEdit(item: Destination) {
    setEditingId(item.id);
    setForm({
      name: item.name,
      country: item.country,
      flight_cost: item.flight_cost,
      daily_living_cost: item.daily_living_cost,
      is_coastal: item.is_coastal,
      description: item.description,
      best_seasons: item.best_seasons,
      images: null,
    });
    setFileNames([]);
    setNotice("");
  }

  function submit() {
    setNotice("");
    if (editingId) {
      updateMutation.mutate({ id: editingId, payload: form });
      return;
    }
    createMutation.mutate(form);
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl text-base-900">
            إدارة الوجهات
          </h1>
          <p className="mt-1 text-sm text-base-500">
            أضف وعدّل الوجهات السياحية المتاحة.
          </p>
        </div>
        <Badge variant="teal">{filtered.length} وجهة</Badge>
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
            {editingId ? "تعديل الوجهة" : "إضافة وجهة جديدة"}
          </h2>

          <div className="space-y-4">
            <div className="space-y-1.5">
              <label className="block text-xs font-display text-base-500">
                اسم الوجهة
              </label>
              <Input
                placeholder="مثال: جزر المالديف"
                value={form.name}
                onChange={(e) =>
                  setForm((p) => ({ ...p, name: e.target.value }))
                }
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="block text-xs font-display text-base-500">
                  الدولة
                </label>
                <Input
                  placeholder="الدولة"
                  value={form.country}
                  onChange={(e) =>
                    setForm((p) => ({ ...p, country: e.target.value }))
                  }
                />
              </div>
              <div className="space-y-1.5">
                <label className="block text-xs font-display text-base-500">
                  المواسم المناسبة
                </label>
                <Input
                  placeholder="summer,spring"
                  value={form.best_seasons}
                  onChange={(e) =>
                    setForm((p) => ({ ...p, best_seasons: e.target.value }))
                  }
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="block text-xs font-display text-base-500">
                  تكلفة الطيران ($)
                </label>
                <Input
                  placeholder="0.00"
                  value={form.flight_cost}
                  onChange={(e) =>
                    setForm((p) => ({ ...p, flight_cost: e.target.value }))
                  }
                />
              </div>
              <div className="space-y-1.5">
                <label className="block text-xs font-display text-base-500">
                  تكلفة المعيشة/يوم ($)
                </label>
                <Input
                  placeholder="0.00"
                  value={form.daily_living_cost}
                  onChange={(e) =>
                    setForm((p) => ({
                      ...p,
                      daily_living_cost: e.target.value,
                    }))
                  }
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-display text-base-500">
                الوصف
              </label>
              <Textarea
                placeholder="وصف تفصيلي للوجهة..."
                value={form.description}
                onChange={(e) =>
                  setForm((p) => ({ ...p, description: e.target.value }))
                }
              />
            </div>

            <Toggle
              id="is_coastal"
              checked={form.is_coastal}
              onChange={(v) => setForm((p) => ({ ...p, is_coastal: v }))}
              label="وجهة ساحلية"
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
                    setForm(emptyPayload);
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
          <div className="relative">
            <Search className="pointer-events-none absolute start-4 top-1/2 h-4 w-4 -translate-y-1/2 text-base-400" />
            <Input
              className="ps-11"
              placeholder="ابحث بالاسم أو الدولة..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          {destinationsQuery.isLoading && (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-24 animate-pulse rounded-2xl bg-base-200/50"
                />
              ))}
            </div>
          )}

          <div className="space-y-3">
            {filtered.map((item) => (
              <div
                key={item.id}
                className="group rounded-2xl border border-base-200 bg-white p-4 transition-all hover:shadow-card"
              >
                <div className="flex items-start gap-4">
                  {item.dest_images?.[0] && (
                    <img
                      src={item.dest_images[0].file}
                      alt={item.name}
                      className="h-16 w-16 shrink-0 rounded-xl object-cover"
                    />
                  )}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-display text-base-900">
                        {item.name}
                      </h3>
                      {item.is_coastal && (
                        <Badge variant="teal" className="text-[10px]">
                          ساحلية
                        </Badge>
                      )}
                    </div>
                    <p className="mt-0.5 text-xs text-base-500">
                      {item.country}
                    </p>
                    {item.description && (
                      <p className="mt-1 line-clamp-2 text-xs text-base-600">
                        {item.description}
                      </p>
                    )}
                    <div className="mt-2 flex gap-3 text-xs text-base-400">
                      <span>طيران: ${item.flight_cost}</span>
                      <span>معيشة: ${item.daily_living_cost}/يوم</span>
                    </div>
                  </div>
                  <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-8 w-8"
                      onClick={() => startEdit(item)}
                    >
                      <Pencil className="h-3.5 w-3.5" />
                    </Button>
                    <Button
                      size="icon"
                      variant="danger"
                      className="h-8 w-8"
                      onClick={() => deleteMutation.mutate(item.id)}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}

            {!destinationsQuery.isLoading && filtered.length === 0 && (
              <div className="py-12 text-center">
                <p className="text-sm text-base-400">
                  {search ? "لا توجد نتائج مطابقة." : "لا توجد وجهات بعد."}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
