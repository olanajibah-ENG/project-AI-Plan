import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil, Trash2, Upload, CheckCircle2, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { Toggle } from "@/components/ui/toggle";
import { listDestinationsCatalog } from "@/features/shared/catalog-api";
import {
  createHotel,
  deleteHotel,
  listHotels,
  updateHotel,
  type HotelPayload,
} from "@/features/admin-hotels/hotels-api";
import type { Hotel } from "@/lib/api/types";

const initialForm: HotelPayload = {
  destination: 0,
  name: "",
  stars: 3,
  price_per_night: "",
  is_sea_view: false,
  images: null,
};

export function HotelsPage() {
  const queryClient = useQueryClient();
  const [notice, setNotice] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [selectedDestination, setSelectedDestination] = useState<
    number | "all"
  >("all");
  const [form, setForm] = useState<HotelPayload>(initialForm);
  const [fileNames, setFileNames] = useState<string[]>([]);

  const destinationsQuery = useQuery({
    queryKey: ["catalog-destinations"],
    queryFn: listDestinationsCatalog,
    retry: 2,
  });
  const hotelsQuery = useQuery({
    queryKey: ["hotels"],
    queryFn: listHotels,
    retry: 2,
  });

  const createMutation = useMutation({
    mutationFn: createHotel,
    onSuccess: () => {
      setNotice("تمت إضافة الفندق");
      setForm(initialForm);
      setFileNames([]);
      queryClient.invalidateQueries({ queryKey: ["hotels"] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: HotelPayload }) =>
      updateHotel(id, payload),
    onSuccess: () => {
      setNotice("تم تحديث الفندق");
      setEditingId(null);
      setForm(initialForm);
      setFileNames([]);
      queryClient.invalidateQueries({ queryKey: ["hotels"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteHotel,
    onSuccess: () => {
      setNotice("تم حذف الفندق");
      queryClient.invalidateQueries({ queryKey: ["hotels"] });
    },
  });

  const filteredHotels = useMemo(() => {
    const list = hotelsQuery.data ?? [];
    if (selectedDestination === "all") return list;
    return list.filter((h) => h.destination === selectedDestination);
  }, [hotelsQuery.data, selectedDestination]);

  /* Map destination IDs to names for display */
  const destNameMap = useMemo(() => {
    const map: Record<number, string> = {};
    for (const d of destinationsQuery.data ?? []) {
      map[d.id] = d.name;
    }
    return map;
  }, [destinationsQuery.data]);

  function startEdit(item: Hotel) {
    setEditingId(item.id);
    setForm({
      destination: item.destination,
      name: item.name,
      stars: item.stars,
      price_per_night: item.price_per_night,
      is_sea_view: item.is_sea_view,
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
            إدارة الفنادق
          </h1>
          <p className="mt-1 text-sm text-base-500">
            أضف وعدّل الفنادق المرتبطة بالوجهات.
          </p>
        </div>
        <Badge variant="gold">{filteredHotels.length} فندق</Badge>
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
            {editingId ? "تعديل الفندق" : "إضافة فندق جديد"}
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
                اسم الفندق
              </label>
              <Input
                placeholder="مثال: فندق الواحة"
                value={form.name}
                onChange={(e) =>
                  setForm((p) => ({ ...p, name: e.target.value }))
                }
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="block text-xs font-display text-base-500">
                  عدد النجوم
                </label>
                <div className="flex gap-1 py-2">
                  {[1, 2, 3, 4, 5].map((n) => (
                    <button
                      key={n}
                      type="button"
                      onClick={() => setForm((p) => ({ ...p, stars: n }))}
                      className="transition-transform hover:scale-110"
                    >
                      <Star
                        className={`h-6 w-6 transition-colors ${
                          n <= form.stars
                            ? "fill-gold text-gold"
                            : "text-base-300"
                        }`}
                      />
                    </button>
                  ))}
                </div>
              </div>
              <div className="space-y-1.5">
                <label className="block text-xs font-display text-base-500">
                  سعر الليلة ($)
                </label>
                <Input
                  placeholder="0.00"
                  value={form.price_per_night}
                  onChange={(e) =>
                    setForm((p) => ({
                      ...p,
                      price_per_night: e.target.value,
                    }))
                  }
                />
              </div>
            </div>

            <Toggle
              id="is_sea_view"
              checked={form.is_sea_view}
              onChange={(v) => setForm((p) => ({ ...p, is_sea_view: v }))}
              label="مطل على البحر"
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
            value={selectedDestination}
            onChange={(e) =>
              setSelectedDestination(
                e.target.value === "all" ? "all" : Number(e.target.value),
              )
            }
          >
            <option value="all">كل الوجهات</option>
            {(destinationsQuery.data ?? []).map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </Select>

          {hotelsQuery.isLoading && (
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
            {filteredHotels.map((hotel) => (
              <div
                key={hotel.id}
                className="group rounded-2xl border border-base-200 bg-white p-4 transition-all hover:shadow-card"
              >
                <div className="flex items-start gap-4">
                  {hotel.hotel_images?.[0] && (
                    <img
                      src={hotel.hotel_images[0].file}
                      alt={hotel.name}
                      className="h-14 w-14 shrink-0 rounded-xl object-cover"
                    />
                  )}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-display text-base-900">
                        {hotel.name}
                      </h3>
                      {hotel.is_sea_view && (
                        <Badge variant="teal" className="text-[10px]">
                          إطلالة بحرية
                        </Badge>
                      )}
                    </div>
                    <p className="mt-0.5 text-xs text-base-500">
                      {destNameMap[hotel.destination] ?? `وجهة #${hotel.destination}`}
                    </p>
                    <div className="mt-1.5 flex items-center gap-3">
                      <div className="flex gap-0.5">
                        {Array.from({ length: 5 }).map((_, i) => (
                          <Star
                            key={i}
                            className={`h-3 w-3 ${
                              i < hotel.stars
                                ? "fill-gold text-gold"
                                : "text-base-300"
                            }`}
                          />
                        ))}
                      </div>
                      <span className="text-xs text-base-400">
                        ${hotel.price_per_night}/ليلة
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-8 w-8"
                      onClick={() => startEdit(hotel)}
                    >
                      <Pencil className="h-3.5 w-3.5" />
                    </Button>
                    <Button
                      size="icon"
                      variant="danger"
                      className="h-8 w-8"
                      onClick={() => deleteMutation.mutate(hotel.id)}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}

            {!hotelsQuery.isLoading && filteredHotels.length === 0 && (
              <div className="py-12 text-center">
                <p className="text-sm text-base-400">لا توجد فنادق بعد.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
