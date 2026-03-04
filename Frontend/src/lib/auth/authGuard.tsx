import { Navigate, Outlet, useLocation } from "react-router-dom";
import { tokenStorage, type UserRole } from "@/lib/auth/tokenStorage";

interface AuthGuardProps {
  roles?: UserRole[];
}

export function AuthGuard({ roles }: AuthGuardProps) {
  const location = useLocation();
  const user = tokenStorage.getUser();
  const access = tokenStorage.getAccessToken();

  if (!user || !access) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
}
