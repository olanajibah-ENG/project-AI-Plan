import { describe, expect, it } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { render, screen } from "@testing-library/react";
import { AuthGuard } from "@/lib/auth/authGuard";
import { tokenStorage } from "@/lib/auth/tokenStorage";

describe("AuthGuard", () => {
  it("redirects unauthenticated users", () => {
    tokenStorage.clearAuth();
    render(
      <MemoryRouter initialEntries={["/admin"]}>
        <Routes>
          <Route element={<AuthGuard roles={["admin"]} />}>
            <Route path="/admin" element={<div>Admin</div>} />
          </Route>
          <Route path="/login" element={<div>Login</div>} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText("Login")).toBeInTheDocument();
  });

  it("allows authorized role", () => {
    tokenStorage.setAuth("a", "r", { id: 2, username: "admin", email: "a@a.com", role: "admin" });
    render(
      <MemoryRouter initialEntries={["/admin"]}>
        <Routes>
          <Route element={<AuthGuard roles={["admin"]} />}>
            <Route path="/admin" element={<div>Admin</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText("Admin")).toBeInTheDocument();
  });
});
