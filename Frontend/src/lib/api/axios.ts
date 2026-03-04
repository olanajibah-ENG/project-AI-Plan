import axios, { AxiosError } from "axios";
import type { AxiosInstance, AxiosRequestConfig } from "axios";
import { API_BASE_URL, endpoints } from "@/lib/api/endpoints";
import { tokenStorage } from "@/lib/auth/tokenStorage";

interface RetryableRequestConfig extends AxiosRequestConfig {
  _retry?: boolean;
}

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const access = tokenStorage.getAccessToken();
  if (access) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetryableRequestConfig | undefined;
    const status = error.response?.status;

    if (!original || status !== 401 || original._retry) {
      return Promise.reject(error);
    }

    const refresh = tokenStorage.getRefreshToken();
    if (!refresh) {
      tokenStorage.clearAuth();
      return Promise.reject(error);
    }

    try {
      original._retry = true;
      const refreshResponse = await axios.post(`${API_BASE_URL}${endpoints.auth.refresh}`, {
        refresh,
      });

      const access = refreshResponse.data?.access as string | undefined;
      if (!access) {
        tokenStorage.clearAuth();
        return Promise.reject(error);
      }

      const currentUser = tokenStorage.getUser();
      if (!currentUser) {
        tokenStorage.clearAuth();
        return Promise.reject(error);
      }

      tokenStorage.setAuth(access, refresh, currentUser);
      original.headers = original.headers ?? {};
      original.headers.Authorization = `Bearer ${access}`;
      return api(original);
    } catch {
      tokenStorage.clearAuth();
      return Promise.reject(error);
    }
  },
);

export default api;
