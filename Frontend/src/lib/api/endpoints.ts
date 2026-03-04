export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export const endpoints = {
  auth: {
    register: "/auth/register/",
    login: "/auth/login/",
    refresh: "/auth/refresh/",
  },
  ai: {
    chat: "/ai/chat/",
  },
  admin: {
    destinations: "/admin/destinations/",
    hotels: "/admin/hotels/",
    events: "/admin/events/",
  },
};
