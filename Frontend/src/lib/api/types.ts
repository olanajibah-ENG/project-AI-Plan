import type { AuthUser } from "@/lib/auth/tokenStorage";

export interface LoginResponse {
  user: AuthUser;
  tokens: {
    access: string;
    refresh: string;
  };
}

export interface RegisterResponse {
  message: string;
  user: AuthUser;
}

export interface ImageAsset {
  id: number;
  file: string;
}

export interface Hotel {
  id: number;
  destination: number;
  name: string;
  stars: number;
  price_per_night: string;
  is_sea_view: boolean;
  hotel_images?: ImageAsset[];
}

export interface EventItem {
  id: number;
  destination: number;
  name: string;
  description: string;
  season: "summer" | "winter" | "spring" | "autumn" | "all";
  price_per_person: string;
  duration_hours: number;
  is_free: boolean;
  event_images?: ImageAsset[];
}

export interface Destination {
  id: number;
  name: string;
  country: string;
  flight_cost: string;
  daily_living_cost: string;
  is_coastal: boolean;
  description: string;
  best_seasons: string;
  dest_images?: ImageAsset[];
  hotels?: Hotel[];
  events?: EventItem[];
}

export type AIStatus =
  | "missing_info"
  | "gather_info"
  | "no_options"
  | "searching"
  | "options_presented"
  | "plan_confirmed"
  | "error"
  | "text_response";

export interface AIOption {
  option_id: number;
  destination_id: number;
  hotel_id: number;
  total_cost?: number;
  cost_breakdown?: {
    flights?: number;
    accommodation?: number;
    daily_living?: number;
    total?: number;
  };
}

export interface AIPlanDetails {
  option_id?: number;
  destination_id: number;
  hotel_id: number;
  total_cost?: number;
  days: number;
  events?: Array<{ event_id: number; name?: string; price_per_person?: number | string }>;
  cost_breakdown?: {
    flights?: number;
    accommodation?: number;
    daily_living?: number;
    total?: number;
  };
}

export interface AIChatResponse {
  status: AIStatus;
  message?: string;
  collected_requirements: Record<string, unknown>;
  options?: AIOption[];
  selected_plan?: AIPlanDetails;
  visual_data?: {
    destination?: Destination | null;
    hotel?: Hotel | null;
    events?: EventItem[];
  };
  session_id?: string;
  details?: unknown;
}
