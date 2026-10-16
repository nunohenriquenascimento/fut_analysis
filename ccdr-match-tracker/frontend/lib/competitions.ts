import { ApiError, request, type MatchStatus } from "./api";

export const TIEBREAKERS = {
  head_to_head_points: "Pontos no confronto direto",
  head_to_head_goal_difference: "Diferença de golos no confronto direto",
  goal_difference: "Diferença de golos global",
  goals_for: "Golos marcados",
  wins: "Vitórias",
} as const;
export type Tiebreaker = keyof typeof TIEBREAKERS;
export interface CompetitionRules { win: number; draw: number; loss: number; tiebreakers: Tiebreaker[] }
export interface Competition { id: number; name: string; season_id: number; internal_team_id: number; rules: CompetitionRules; provisional: boolean }
export interface CompetitionTeam { id: number; name: string; crest_path: string | null; created_at: string }
export interface FixtureInput {
  external_key: string; matchday: number; home_team_id: number; away_team_id: number;
  kickoff_at?: string | null; venue?: string | null; internal_match_id?: number | null;
  home_goals?: number | null; away_goals?: number | null; source: string;
}
export interface CompetitionFixture extends FixtureInput {
  schedule_text?: string | null;
  id: number; competition_id: number; status: MatchStatus; created_at: string;
  internal_match_id: number | null; home_goals: number | null; away_goals: number | null;
}
export interface Matchday { matchday: number; fixtures: CompetitionFixture[] }
export interface Standing {
  team_id: number; name: string; rank: number; unresolved_tie: boolean;
  points: number; played: number; wins: number; draws: number; losses: number;
  goals_for: number; goals_against: number; goal_difference: number;
}
export interface Standings { provisional: boolean; warning: string; rules: CompetitionRules; completed_fixtures: number; rows: Standing[] }
export interface ParticipantsSelection { team_ids: number[]; expected_team_ids: number[] }
export interface ParticipantsPlan {
  current_team_ids: number[]; proposed_team_ids: number[];
  added: { id: number; name: string }[]; removed: { id: number; name: string }[];
  conflicts: string[]; can_apply: boolean;
}

async function allPages<T>(path: string): Promise<T[]> {
  const rows: T[] = [];
  for (let offset = 0; ; offset += 200) {
    const page = await request<T[]>(`${path}?limit=200&offset=${offset}`);
    rows.push(...page);
    if (page.length < 200) return rows;
  }
}

export const competitionsApi = {
  list: () => allPages<Competition>("/competitions"),
  teams: () => allPages<CompetitionTeam>("/teams"),
  participants: (id: number) => request<CompetitionTeam[]>(`/competitions/${id}/teams`),
  previewParticipants: (id: number, data: ParticipantsSelection) => request<ParticipantsPlan>(`/competitions/${id}/teams/preview`, { method: "POST", body: JSON.stringify(data) }),
  updateParticipants: (id: number, data: ParticipantsSelection & { confirmation: "ALTERAR PARTICIPANTES" }) => request<CompetitionTeam[]>(`/competitions/${id}/teams`, { method: "PUT", body: JSON.stringify(data) }),
  calendar: (id: number) => request<CompetitionFixture[]>(`/competitions/${id}/calendar`),
  matchdays: (id: number) => request<Matchday[]>(`/competitions/${id}/matchdays`),
  standings: (id: number) => request<Standings>(`/competitions/${id}/standings`),
  createTeam: (name: string) => request<CompetitionTeam>("/teams", { method: "POST", body: JSON.stringify({ name }) }),
  create: (data: { name: string; season_id: number; internal_team_id: number; team_ids: number[]; rules: CompetitionRules }) =>
    request<Competition>("/competitions", { method: "POST", body: JSON.stringify(data) }),
  rules: (id: number, rules: CompetitionRules) => request<Competition>(`/competitions/${id}/rules`, { method: "PUT", body: JSON.stringify(rules) }),
  import: (id: number, data: { fixtures: FixtureInput[] }) => request<{ imported: number }>(`/competitions/${id}/fixtures/import`, { method: "POST", body: JSON.stringify(data) }),
};

export function competitionError(reason: unknown): string {
  if (reason instanceof ApiError) {
    if (reason.status === 422) {
      if (Array.isArray(reason.details)) return reason.details.map((item: { loc?: (string | number)[]; msg?: string }) =>
        `${item.loc?.filter((part) => part !== "body").join(" → ") ?? "Dados"}: ${item.msg ?? "Valor inválido"}`).join("; ");
      return "Verifique os campos indicados e tente novamente.";
    }
    if (reason.status >= 500) return "O campeonato está indisponível. Tente novamente mais tarde ou contacte a administração.";
    return reason.message;
  }
  return "Não foi possível contactar o servidor. Verifique a ligação e tente novamente.";
}

export function fixtureDate(value?: string | null): string {
  return value ? new Date(value).toLocaleString("pt-PT", { timeZone: "Europe/Lisbon", dateStyle: "medium", timeStyle: "short" }) : "Data por definir";
}

// Only transport fields, never derived status, scores from internal events or DB metadata.
export function externalCorrection(fixture: CompetitionFixture, home: number, away: number, source: string): FixtureInput {
  return { external_key: fixture.external_key, matchday: fixture.matchday, home_team_id: fixture.home_team_id,
    away_team_id: fixture.away_team_id, kickoff_at: fixture.kickoff_at ?? null, venue: fixture.venue ?? null,
    internal_match_id: null, home_goals: home, away_goals: away, source };
}
