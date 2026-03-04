import api from "@/lib/api/axios";
import { endpoints } from "@/lib/api/endpoints";
import type { Hotel } from "@/lib/api/types";

export interface HotelPayload {
  destination: number;
  name: string;
  stars: number;
  price_per_night: string;
  is_sea_view: boolean;
  images?: FileList | null;
}

export async function listHotels() {
  const response = await api.get<Hotel[]>(endpoints.admin.hotels);
  return response.data;
}

function toHotelFormData(payload: HotelPayload) {
  const formData = new FormData();
  formData.append("destination", String(payload.destination));
  formData.append("name", payload.name);
  formData.append("stars", String(payload.stars));
  formData.append("price_per_night", payload.price_per_night);
  formData.append("is_sea_view", String(payload.is_sea_view));
  if (payload.images) {
    Array.from(payload.images).forEach((img) => formData.append("images", img));
  }
  return formData;
}

export async function createHotel(payload: HotelPayload) {
  const hasImages = payload.images && payload.images.length > 0;
  const response = await api.post<Hotel>(
    endpoints.admin.hotels,
    hasImages ? toHotelFormData(payload) : { ...payload },
    hasImages ? { headers: { "Content-Type": "multipart/form-data" } } : undefined,
  );
  return response.data;
}

export async function updateHotel(id: number, payload: HotelPayload) {
  const hasImages = payload.images && payload.images.length > 0;
  const response = await api.put<Hotel>(
    `${endpoints.admin.hotels}${id}/`,
    hasImages ? toHotelFormData(payload) : { ...payload },
    hasImages ? { headers: { "Content-Type": "multipart/form-data" } } : undefined,
  );
  return response.data;
}

export async function deleteHotel(id: number) {
  await api.delete(`${endpoints.admin.hotels}${id}/`);
}
