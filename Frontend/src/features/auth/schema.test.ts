import { describe, expect, it } from "vitest";
import { loginSchema, registerSchema } from "@/features/auth/schema";

describe("auth schemas", () => {
  it("rejects short password", () => {
    const parsed = loginSchema.safeParse({ username: "test", password: "123" });
    expect(parsed.success).toBe(false);
  });

  it("accepts valid register payload", () => {
    const parsed = registerSchema.safeParse({
      username: "userdemo",
      email: "user@example.com",
      password: "Pass12345!",
    });
    expect(parsed.success).toBe(true);
  });
});
