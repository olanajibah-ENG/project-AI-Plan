import type { AIChatResponse } from "@/lib/api/types";

const allowed = new Set([
  "missing_info",
  "gather_info",
  "no_options",
  "searching",
  "options_presented",
  "plan_confirmed",
  "error",
  "text_response",
]);

export function normalizeAiResponse(payload: unknown): AIChatResponse {
  if (!payload || typeof payload !== "object") {
    return {
      status: "error",
      message: "استجابة غير صالحة من الخادم",
      collected_requirements: {},
    };
  }

  const candidate = payload as Partial<AIChatResponse> & { status?: string };
  const status = candidate.status && allowed.has(candidate.status) ? candidate.status : "error";
  return {
    status,
    message: candidate.message,
    collected_requirements: candidate.collected_requirements ?? {},
    options: candidate.options,
    selected_plan: candidate.selected_plan,
    visual_data: candidate.visual_data,
    session_id: candidate.session_id,
    details: candidate.details,
  };
}
