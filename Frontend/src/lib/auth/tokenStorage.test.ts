import { describe, expect, it } from "vitest";
import { tokenStorage } from "@/lib/auth/tokenStorage";

describe("tokenStorage", () => {
  it("stores and clears auth", () => {
    tokenStorage.setAuth("a", "r", { id: 1, username: "u", email: "u@test.com", role: "user" });
    expect(tokenStorage.getAccessToken()).toBe("a");
    expect(tokenStorage.getRefreshToken()).toBe("r");
    expect(tokenStorage.getUser()?.username).toBe("u");

    tokenStorage.clearAuth();
    expect(tokenStorage.getAccessToken()).toBeNull();
    expect(tokenStorage.getRefreshToken()).toBeNull();
    expect(tokenStorage.getUser()).toBeNull();
  });
});
