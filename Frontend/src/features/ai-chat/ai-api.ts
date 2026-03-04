import api from "@/lib/api/axios";
import { endpoints } from "@/lib/api/endpoints";
import type { AIChatResponse } from "@/lib/api/types";

export interface AIChatPayload {
  prompt?: string;
  message?: string;
  session_id?: string;
}

export async function sendChat(payload: AIChatPayload): Promise<AIChatResponse> {
  const response = await api.post<AIChatResponse>(endpoints.ai.chat, payload);
  return response.data;
}
