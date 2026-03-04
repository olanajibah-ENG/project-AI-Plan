import api from "@/lib/api/axios";
import { endpoints } from "@/lib/api/endpoints";
import type { Destination } from "@/lib/api/types";

export async function listDestinationsCatalog() {
  const response = await api.get<Destination[]>(endpoints.admin.destinations);
  return response.data;
}
