import api from "@/lib/api/axios";
import { endpoints } from "@/lib/api/endpoints";
import type { LoginResponse, RegisterResponse } from "@/lib/api/types";
import type { LoginFormValues, RegisterFormValues } from "@/features/auth/schema";

export async function register(payload: RegisterFormValues): Promise<RegisterResponse> {
  const response = await api.post<RegisterResponse>(endpoints.auth.register, payload);
  return response.data;
}

export async function login(payload: LoginFormValues): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>(endpoints.auth.login, payload);
  return response.data;
}
