import { request, type Match, type MatchStatus, type Player } from "./api";

export const EVENT_LABELS = {
  GOAL: "Golo", OWN_GOAL: "Autogolo", SHOT_ON_TARGET: "Remate à baliza", SHOT_OFF_TARGET: "Remate fora",
  SHOT_BLOCKED: "Remate bloqueado", CORNER: "Canto", FREE_KICK: "Livre", FOUL: "Falta",
  YELLOW_CARD: "Amarelo", RED_CARD: "Vermelho", OFFSIDE: "Fora de jogo", SAVE: "Defesa",
  PENALTY: "Penálti", SUBSTITUTION: "Substituição",
} as const;
export type EventType = keyof typeof EVENT_LABELS;
export type EventTeam = "US" | "OPPONENT";
export interface EventFields {
  event_type: EventType;
  team: EventTeam;
  player_id: number | null;
  related_player_id: number | null;
  notes?: string | null;
}
export interface MatchEvent extends EventFields {
  recorded_by_id?: number | null;
  id: number; match_id: number; period: number; elapsed_seconds: number; created_at: string;
}
export interface LiveState {
  match: Match;
  score: { us: number; opponent: number };
  server_now: string;
  clock_elapsed_seconds: number;
  period: number | null;
  events: MatchEvent[];
  squad: Player[];
}
export type TransitionStatus = "FIRST_HALF" | "HALF_TIME" | "SECOND_HALF" | "FINISHED";
export const NEXT_ACTION: Partial<Record<MatchStatus, { status: TransitionStatus; label: string }>> = {
  SCHEDULED: { status: "FIRST_HALF", label: "Iniciar 1.ª parte" },
  FIRST_HALF: { status: "HALF_TIME", label: "Terminar 1.ª parte" },
  HALF_TIME: { status: "SECOND_HALF", label: "Iniciar 2.ª parte" },
  SECOND_HALF: { status: "FINISHED", label: "Terminar 2.ª Parte" },
};
export const liveApi = {
  reopen: (id: number) => request<LiveState>(`/matches/${id}/reopen`, { method: "POST" }),
  resume: (id: number) => request<LiveState>(`/matches/${id}/resume`, { method: "POST" }),
  get: (id: number) => request<LiveState>(`/matches/${id}/live`),
  transition: (id: number, status: TransitionStatus) => request<LiveState>(`/matches/${id}/transition`, { method: "POST", body: JSON.stringify({ status }) }),
  createEvent: (id: number, fields: EventFields) => request<LiveState>(`/matches/${id}/events`, { method: "POST", body: JSON.stringify(fields) }),
  updateEvent: (id: number, eventId: number, fields: EventFields) => request<LiveState>(`/matches/${id}/events/${eventId}`, { method: "PATCH", body: JSON.stringify(fields) }),
  deleteEvent: (id: number, eventId: number) => request<LiveState>(`/matches/${id}/events/${eventId}`, { method: "DELETE" }),
};

export function formatClock(seconds: number): string {
  return `${Math.floor(seconds / 60).toString().padStart(2, "0")}:${(seconds % 60).toString().padStart(2, "0")}`;
}

export function timelineText(event: MatchEvent, squad: Player[]): string {
  const name = (id: number | null) => squad.find((player) => player.id === id)?.name ?? (id ? `Jogador #${id}` : "Nossa equipa");
  let text = `${Math.floor(event.elapsed_seconds / 60)}' — ${EVENT_LABELS[event.event_type]} — ${event.team === "OPPONENT" ? "Adversário" : name(event.player_id)}`;
  if (event.related_player_id !== null) text += ` — ${event.event_type === "GOAL" ? "Assistência" : "Entra"}: ${name(event.related_player_id)}`;
  return text;
}
