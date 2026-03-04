import api from "@/lib/api/axios";
import { endpoints } from "@/lib/api/endpoints";
import type { Destination } from "@/lib/api/types";

export interface DestinationPayload {
  name: string;
  country: string;
  flight_cost: string;
  daily_living_cost: string;
  is_coastal: boolean;
  description: string;
  best_seasons: string;
  images?: FileList | null;
}

export async function listDestinations() {
  const response = await api.get<Destination[]>(endpoints.admin.destinations);
  return response.data;
}

function toDestinationFormData(payload: DestinationPayload) {
  const formData = new FormData();
  formData.append("name", payload.name);
  formData.append("country", payload.country);
  formData.append("flight_cost", payload.flight_cost);
  formData.append("daily_living_cost", payload.daily_living_cost);
  formData.append("is_coastal", String(payload.is_coastal));
  formData.append("description", payload.description);
  formData.append("best_seasons", payload.best_seasons);
  if (payload.images) {
    Array.from(payload.images).forEach((img) => formData.append("images", img));
  }
  return formData;
}

export async function createDestination(payload: DestinationPayload) {
  const hasImages = payload.images && payload.images.length > 0;
  const response = await api.post<Destination>(
    endpoints.admin.destinations,
    hasImages ? toDestinationFormData(payload) : { ...payload },
    hasImages ? { headers: { "Content-Type": "multipart/form-data" } } : undefined,
  );
  return response.data;
}

export async function updateDestination(id: number, payload: DestinationPayload) {
  const hasImages = payload.images && payload.images.length > 0;
  const response = await api.put<Destination>(
    `${endpoints.admin.destinations}${id}/`,
    hasImages ? toDestinationFormData(payload) : { ...payload },
    hasImages ? { headers: { "Content-Type": "multipart/form-data" } } : undefined,
  );
  return response.data;
}

export async function deleteDestination(id: number) {
  await api.delete(`${endpoints.admin.destinations}${id}/`);
}
