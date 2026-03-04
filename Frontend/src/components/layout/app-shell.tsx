import { useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  Compass,
  LogOut,
  MapPin,
  Building2,
  Calendar,
  Sparkles,
  Menu,
  X,
} from "lucide-react";
import { tokenStorage } from "@/lib/auth/tokenStorage";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils/cn";

const navItems = [
  { to: "/trip-planner", label: "مخطط الرحلة", icon: Sparkles, admin: false },
  { to: "/admin/destinations", label: "الوجهات", icon: MapPin, admin: true },
  { to: "/admin/hotels", label: "الفنادق", icon: Building2, admin: true },
  { to: "/admin/events", label: "الفعاليات", icon: Calendar, admin: true },
];

export function AppShell() {
  const navigate = useNavigate();
  const user = tokenStorage.getUser();
  const [mobileOpen, setMobileOpen] = useState(false);

  function logout() {
    tokenStorage.clearAuth();
    navigate("/login", { replace: true });
  }

  const isAdmin = user?.role === "admin";
  const visibleItems = navItems.filter((item) => !item.admin || isAdmin);

  return (
    <div className="min-h-screen bg-pattern">
      <header className="sticky top-0 z-40 border-b border-base-200/80 bg-base-100/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-3 lg:px-8">
          {/* Logo */}
          <Link
            className="flex items-center gap-2.5 transition-opacity hover:opacity-80"
            to="/trip-planner"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-terracotta to-terracotta-300 shadow-subtle">
              <Compass className="h-[18px] w-[18px] text-white" />
            </div>
            <span className="font-display text-lg text-base-900">رحلتك</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden items-center gap-1 lg:flex">
            {visibleItems.map((item) => (
              <NavLink
                key={item.to}
                className={({ isActive }) =>
                  cn("nav-link", isActive && "active")
                }
                to={item.to}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            ))}
          </nav>

          {/* User area + mobile toggle */}
          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2.5 md:flex">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-base-200 text-xs font-display text-base-600">
                {user?.username?.charAt(0)?.toUpperCase() ?? "?"}
              </div>
              <span className="text-sm text-base-600">{user?.username}</span>
            </div>
            <Button onClick={logout} size="sm" variant="ghost">
              <LogOut className="h-4 w-4" />
              <span className="hidden sm:inline">خروج</span>
            </Button>
            <button
              className="rounded-lg p-2 transition hover:bg-base-200/60 lg:hidden"
              onClick={() => setMobileOpen(!mobileOpen)}
              type="button"
            >
              {mobileOpen ? (
                <X className="h-5 w-5 text-base-700" />
              ) : (
                <Menu className="h-5 w-5 text-base-700" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile nav */}
        {mobileOpen && (
          <div className="border-t border-base-200 bg-white px-4 py-3 lg:hidden animate-fade-in">
            <nav className="space-y-1">
              {visibleItems.map((item) => (
                <NavLink
                  key={item.to}
                  className={({ isActive }) =>
                    cn("nav-link w-full", isActive && "active")
                  }
                  to={item.to}
                  onClick={() => setMobileOpen(false)}
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
        )}
      </header>

      <main className="mx-auto max-w-7xl px-5 py-8 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}
