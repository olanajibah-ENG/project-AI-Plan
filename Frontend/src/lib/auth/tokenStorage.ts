export type UserRole = "admin" | "user";

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  role: UserRole;
}

const ACCESS_KEY = "trip_access_token";
const REFRESH_KEY = "trip_refresh_token";
const USER_KEY = "trip_auth_user";
const SESSION_KEY = "trip_ai_session_id";

export const tokenStorage = {
  getAccessToken: () => localStorage.getItem(ACCESS_KEY),
  getRefreshToken: () => localStorage.getItem(REFRESH_KEY),
  getUser: (): AuthUser | null => {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as AuthUser;
    } catch {
      return null;
    }
  },
  setAuth: (access: string, refresh: string, user: AuthUser) => {
    localStorage.setItem(ACCESS_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  clearAuth: () => {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(SESSION_KEY);
  },
  getAiSessionId: () => localStorage.getItem(SESSION_KEY),
  setAiSessionId: (sessionId: string) => localStorage.setItem(SESSION_KEY, sessionId),
  clearAiSessionId: () => localStorage.removeItem(SESSION_KEY),
};
