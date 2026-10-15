import { ApiError, request } from "./api";
import { competitionError, type FixtureInput } from "./competitions";

export interface FPFStanding { name: string; rank: number; played: number; wins: number; draws: number; losses: number; goals_for: number; goals_against: number; goal_difference: number; points: number }
export interface FPFRound { fixture_id: number; matchday: number; current: boolean }
export interface FPFGame { home_name: string; away_name: string; home_goals: number | null; away_goals: number | null; schedule_text: string | null; venue: string | null; match_id: number | null; fixture_id: number; matchday: number }
export interface FPFSeries { series_id: number; standings: FPFStanding[]; rounds: FPFRound[]; matches: FPFGame[] }
export interface FPFCompetition { competition_id: number; season_id: number; name: string; season: string; series: FPFSeries[]; coverage: string }
export interface FPFPerson { name: string; player_id: number | null; side?: string | null }
export interface FPFPlayer extends FPFPerson { shirt_number: number }
export interface FPFEvent { type: string; period: number; minute: number; added_minute: number; minute_text: string; player?: FPFPerson; player_in?: FPFPerson; player_out?: FPFPerson }
export interface FPFMatch {
  match_id: number; home: { club_id: number; name: string }; away: { club_id: number; name: string };
  home_goals: number; away_goals: number; date: string | null; time: string | null; venue: string | null;
  lineups: Record<"home" | "away", { starters: FPFPlayer[]; substitutes: FPFPlayer[] }>;
  events: FPFEvent[]; staff: { name: string; role: string; side: string | null }[];
  officials: { name: string; role: string }[]; warnings: string[];
  availability?: { starters: boolean; substitutes: boolean; events: boolean; staff: boolean; officials: boolean };
}
export interface FPFSnapshot {
  identity: [number, number, number]; competition: FPFCompetition; team_mapping: Record<string, number>;
  match_sheets: Record<string, FPFMatch>; imported_at: string; mode: "captured_html" | "http";
  source_url: string; internal_match_links: Record<string, number>;
  round_captures?: Record<string, { series_id: number; fixture_id: number; matchday: number; complete: boolean; matches: FPFGame[] }>;
}
export interface FPFRead { source: "FPF"; available: boolean; snapshot: FPFSnapshot | null; note: string }
export type FPFDocument = { name: string; kind: "competition"; supported: true; data: FPFCompetition }
  | { name: string; kind: "match"; supported: true; data: FPFMatch }
  | { name: string; kind: "fixture" | "invalid"; supported: false; data: null; error: string };
export interface FPFFile { name: string; html: string }
export interface FPFCapture { competition_html?: string; series_id: number; team_mapping: Record<string, number>; match_htmls: string[]; match_rounds: Record<string, number>; internal_match_links: Record<string, number>; expected_state?: string }
export interface FPFPreview {
  snapshot: FPFSnapshot; fixtures: FixtureInput[]; state_token: string; add_participants: number[];
  pending_internal_links: { external_key: string; reason: string; official: FPFGame }[];
  changes: { external_key: string; action: "create" | "update" | "unchanged"; before: FixtureInput | null; after: FixtureInput }[];
  standings_before: FPFSeries[];
}
export const fpfApi = {
  read: (id: number) => request<FPFRead>(`/competitions/${id}/fpf`),
  inspect: (id: number, files: FPFFile[]) => request<{ documents: FPFDocument[] }>(`/competitions/${id}/fpf/documents`, { method: "POST", body: JSON.stringify({ files }) }),
  preview: (id: number, payload: FPFCapture) => request<FPFPreview>(`/competitions/${id}/fpf/preview`, { method: "POST", body: JSON.stringify(payload) }),
  apply: (id: number, payload: FPFCapture, confirmation: string) => request<{ imported: number; pending_internal_links: unknown[] }>(`/competitions/${id}/fpf`, { method: "PUT", body: JSON.stringify({ ...payload, confirmation }) }),
};
export function fpfError(reason: unknown): string {
  if (reason instanceof ApiError && reason.status === 422 && !Array.isArray(reason.details)) return reason.message;
  if (reason instanceof ApiError && reason.status === 503) return "FPF indisponível. A última captura válida permanece disponível.";
  return competitionError(reason);
}
