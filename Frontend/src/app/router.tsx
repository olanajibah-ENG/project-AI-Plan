import { Navigate, createBrowserRouter } from "react-router-dom";
import { AppShell } from "@/components/layout/app-shell";
import { AuthGuard } from "@/lib/auth/authGuard";
import { LoginPage } from "@/features/auth/login-page";
import { RegisterPage } from "@/features/auth/register-page";
import { TripPlannerPage } from "@/features/ai-chat/trip-planner-page";
import { DestinationsPage } from "@/features/admin-destinations/destinations-page";
import { HotelsPage } from "@/features/admin-hotels/hotels-page";
import { EventsPage } from "@/features/admin-events/events-page";
import { NotFoundPage } from "@/features/shared/not-found-page";
import { UnauthorizedPage } from "@/features/shared/unauthorized-page";

export const router = createBrowserRouter([
  { path: "/", element: <Navigate to="/trip-planner" replace /> },
  { path: "/login", element: <LoginPage /> },
  { path: "/register", element: <RegisterPage /> },
  { path: "/unauthorized", element: <UnauthorizedPage /> },
  {
    element: <AuthGuard />,
    children: [
      {
        element: <AppShell />,
        children: [
          { path: "/trip-planner", element: <TripPlannerPage /> },
          {
            element: <AuthGuard roles={["admin"]} />,
            children: [
              { path: "/admin/destinations", element: <DestinationsPage /> },
              { path: "/admin/hotels", element: <HotelsPage /> },
              { path: "/admin/events", element: <EventsPage /> },
            ],
          },
        ],
      },
    ],
  },
  { path: "*", element: <NotFoundPage /> },
]);
