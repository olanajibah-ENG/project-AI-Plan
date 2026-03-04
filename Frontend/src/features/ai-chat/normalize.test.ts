import { describe, expect, it } from "vitest";
import { normalizeAiResponse } from "@/features/ai-chat/normalize";

describe("normalizeAiResponse", () => {
  it("normalizes unknown status to error", () => {
    const out = normalizeAiResponse({ status: "unknown", message: "x" });
    expect(out.status).toBe("error");
    expect(out.collected_requirements).toEqual({});
  });

  it("preserves valid status", () => {
    const out = normalizeAiResponse({ status: "options_presented", collected_requirements: { budget: 1000 } });
    expect(out.status).toBe("options_presented");
    expect(out.collected_requirements).toEqual({ budget: 1000 });
  });
});
