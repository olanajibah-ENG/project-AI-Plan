import api from "@/lib/api/axios";
import { endpoints } from "@/lib/api/endpoints";
import type { EventItem } from "@/lib/api/types";

export interface EventPayload {
  destination: number;
  name: string;
  description: string;
  season: "summer" | "winter" | "spring" | "autumn" | "all";
  price_per_person: string;
  duration_hours: number;
  is_free: boolean;
  images?: FileList | null;
}

export async function listEvents() {
  const response = await api.get<EventItem[]>(endpoints.admin.events);
  return response.data;
}

function toEventFormData(payload: EventPayload) {
  const formData = new FormData();
  formData.append("destination", String(payload.destination));
  formData.append("name", payload.name);
  formData.append("description", payload.description);
  formData.append("season", payload.season);
  formData.append("price_per_person", payload.price_per_person);
  formData.append("duration_hours", String(payload.duration_hours));
  formData.append("is_free", String(payload.is_free));
  if (payload.images) {
    Array.from(payload.images).forEach((img) => formData.append("images", img));
  }
  return formData;
}

export async function createEvent(payload: EventPayload) {
  const hasImages = payload.images && payload.images.length > 0;
  const response = await api.post<EventItem>(
    endpoints.admin.events,
    hasImages ? toEventFormData(payload) : { ...payload },
    hasImages ? { headers: { "Content-Type": "multipart/form-data" } } : undefined,
  );
  return response.data;
}

export async function updateEvent(id: number, payload: EventPayload) {
  const hasImages = payload.images && payload.images.length > 0;
  const response = await api.put<EventItem>(
    `${endpoints.admin.events}${id}/`,
    hasImages ? toEventFormData(payload) : { ...payload },
    hasImages ? { headers: { "Content-Type": "multipart/form-data" } } : undefined,
  );
  return response.data;
}

export async function deleteEvent(id: number) {
  await api.delete(`${endpoints.admin.events}${id}/`);
}
