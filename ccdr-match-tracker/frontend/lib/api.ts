// Central HTTP boundary. Future screens should use this module instead of
// scattering URLs and fetch calls throughout components.
import { authDebug, authApiOrigin } from "./auth-debug";
export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
let csrfToken: string | null = null;
export function setCsrfToken(token: string | null) { csrfToken = token; }
export type UserRole = "ADMIN" | "COACH" | "VIEWER";
export interface AuthUser { id: number; name: string; email: string; role: UserRole; is_active: boolean }
export interface AuthState { user: AuthUser; csrf_token: string }
export interface UserCreate { name: string; email: string; password: string; role: UserRole; is_active: boolean }

export const PLAYER_POSITIONS = ["GR", "DC", "ALA", "MDC", "MC", "PL", "UNIVERSAL"] as const;
export type PlayerPosition = (typeof PLAYER_POSITIONS)[number];
export type MatchStatus = "SCHEDULED" | "FIRST_HALF" | "HALF_TIME" | "SECOND_HALF" | "FINISHED" | "CANCELLED";

export interface PlayerCreate {
  photo_path?: string | null;
  name: string;
  season_id: number;
  team_id: number;
  position: PlayerPosition;
  shirt_number: number;
}

export interface Player extends Omit<PlayerCreate, "shirt_number"> {
  id: number;
  shirt_number: number | null;
  is_active: boolean;
  created_at: string;
}

export type PlayerUpdate = Partial<Pick<PlayerCreate, "name" | "shirt_number" | "position" | "photo_path"> & { is_active: boolean }>;

export interface RosterContext {
  season_id: number;
  season_name: string;
  team_id: number;
  team_name: string;
  team_crest_path?: string | null;
}

export interface MatchCreate {
  season_id: number;
  team_id: number;
  matchday: number;
  opponent_name: string;
  kickoff_at: string; // ISO 8601 with timezone, e.g. 2026-10-04T15:00:00+01:00
  is_home?: boolean;
  venue?: string | null;
}

export type MatchUpdate = Partial<Omit<MatchCreate, "season_id" | "team_id">>;

export interface Match extends Omit<MatchCreate, "matchday"> {
  can_delete?: boolean;
  can_cancel?: boolean;
  team_crest_path?: string | null;
  opponent_crest_path?: string | null;
  score?: { us: number; opponent: number };
  id: number;
  opponent_id: number;
  matchday: number | null;
  is_home: boolean;
  venue: string | null;
  status: MatchStatus;
  elapsed_seconds: number;
  clock_started_at: string | null;
  created_at: string;
}

export type SquadRole = "TITULAR" | "SUPLENTE" | "NAO_CONVOCADO";
export interface SquadPlayer { player: Player; role: SquadRole }
export interface SquadEntry { player_id: number; is_starter: boolean }

export class ApiError extends Error {
  constructor(public readonly status: number, public readonly details: unknown) {
    super(typeof details === "string" ? details : `Erro da API (${status})`);
    this.name = "ApiError";
  }
}

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const diagnostic = ["/auth/login", "/auth/me", "/auth/logout"].includes(path);
  if (diagnostic) { authApiOrigin(API_URL); authDebug(path, "request"); }
  let response: Response;
  try { response = await fetch(`${API_URL}${path}`, {
    ...init,
    cache: "no-store",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-Requested-With": "CCDR",
      ...(csrfToken ? { "X-CSRF-Token": csrfToken } : {}), ...init?.headers },
  }); } catch (reason) {
    if (diagnostic) authDebug(path, "fetch_error");
    throw reason;
  }
  if (diagnostic) authDebug(path, "response", { status: response.status, request_id: response.headers.get("X-Request-ID") });
  if (!response.ok) {
    if (response.status === 401 && path !== "/auth/login" && path !== "/auth/me" && typeof window !== "undefined") {
      setCsrfToken(null);
      window.dispatchEvent(new Event("ccdr:unauthenticated"));
    }
    const body = await response.json().catch(() => null);
    throw new ApiError(response.status, body?.detail ?? response.statusText);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

type ListOptions = { season_id?: number; team_id?: number; limit?: number; offset?: number };
function query(options: ListOptions): string {
  const params = new URLSearchParams();
  Object.entries(options).forEach(([key, value]) => {
    if (value !== undefined) params.set(key, String(value));
  });
  return params.size ? `?${params}` : "";
}

export const api = {
  login: (email: string, password: string) => request<AuthState>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  me: () => request<AuthState>("/auth/me"),
  logout: () => request<void>("/auth/logout", { method: "POST" }),
  users: () => request<AuthUser[]>("/users"),
  createUser: (data: UserCreate) => request<AuthUser>("/users", { method: "POST", body: JSON.stringify(data) }),
  updateUser: (id: number, data: Partial<UserCreate>) => request<AuthUser>(`/users/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  health: () => request<{ status: string }>("/health"),
  players: (options: ListOptions = {}) => request<Player[]>(`/players${query(options)}`),
  createPlayer: (data: PlayerCreate) => request<Player>("/players", { method: "POST", body: JSON.stringify(data) }),
  rosterContext: () => request<RosterContext>("/players/context"),
  rosterPlayers: async (context: Pick<RosterContext, "team_id" | "season_id">): Promise<Player[]> => {
    const players: Player[] = [];
    for (let offset = 0; ; offset += 200) {
      const page = await request<Player[]>(`/players${query({ ...context, limit: 200, offset })}`);
      players.push(...page);
      if (page.length < 200) return players;
    }
  },
  updatePlayer: (id: number, data: PlayerUpdate) => request<Player>(`/players/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  matches: (options: ListOptions = {}) => request<Match[]>(`/matches${query(options)}`),
  createMatch: (data: MatchCreate) => request<Match>("/matches", { method: "POST", body: JSON.stringify(data) }),
  seasonMatches: async (context: Pick<RosterContext, "season_id" | "team_id">): Promise<Match[]> => {
    const rows: Match[] = [];
    for (let offset = 0; ; offset += 200) {
      const page = await request<Match[]>(`/matches${query({ season_id: context.season_id, team_id: context.team_id, limit: 200, offset })}`);
      rows.push(...page);
      if (page.length < 200) return rows;
    }
  },
  match: (id: number) => request<Match>(`/matches/${id}`),
  deleteMatch: (id: number) => request<void>(`/matches/${id}`, { method: "DELETE" }),
  forceDeleteMatch: (id: number) => request<void>(`/matches/${id}/force`, { method: "DELETE", body: JSON.stringify({ confirmation: "ELIMINAR" }) }),
  cancelMatch: (id: number) => request<Match>(`/matches/${id}/cancel`, { method: "POST" }),
  updateMatch: (id: number, data: MatchUpdate) => request<Match>(`/matches/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  squad: (id: number) => request<SquadPlayer[]>(`/matches/${id}/squad`),
  saveSquad: (id: number, players: SquadEntry[]) => request<SquadPlayer[]>(`/matches/${id}/squad`, { method: "PUT", body: JSON.stringify({ players }) }),
};
