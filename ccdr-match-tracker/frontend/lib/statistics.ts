import { request, type Match, type Player, type RosterContext } from "./api";
import type { MatchEvent } from "./live";

export const STAT_LABELS = {
  goals: "Golos", shots_on_target: "Remates à baliza", shots_off_target: "Remates fora",
  shots_blocked: "Remates bloqueados", shots_total: "Remates totais", corners: "Cantos",
  free_kicks: "Livres", fouls: "Faltas", offsides: "Foras de jogo", penalties: "Penáltis",
  yellow_cards: "Cartões amarelos", red_cards: "Cartões vermelhos", saves: "Defesas do guarda-redes",
} as const;
export type EventTotals = Record<keyof typeof STAT_LABELS, number>;
export interface Comparison { us: EventTotals; opponent: EventTotals }
export interface MatchStatistics {
  match: Match; team_name: string; score: { us: number; opponent: number }; is_final: boolean;
  total_events: number; comparison: Comparison; timeline: MatchEvent[]; players: Player[];
}
export const PLAYER_LABELS = {
  matches_called_up: "Jogos convocado", matches_started: "Jogos titular", goals: "Golos", assists: "Assistências",
  shots_on_target: "Remates à baliza", shots_off_target: "Remates fora", shots_blocked: "Remates bloqueados",
  shots_total: "Remates totais", yellow_cards: "Cartões amarelos", red_cards: "Cartões vermelhos",
  fouls: "Faltas", offsides: "Foras de jogo",
} as const;
export type PlayerStatistics = { player: Player } & Record<keyof typeof PLAYER_LABELS, number>;
export const RANKING_LABELS = { goals: "Melhores marcadores", assists: "Mais assistências", shots_total: "Mais remates",
  yellow_cards: "Mais cartões amarelos", red_cards: "Mais cartões vermelhos" } as const;
export interface RankingEntry { player_id: number; name: string; value: number }
export interface PlayerStatisticsResponse {
  context: RosterContext;
  scope: { competitive: "FINISHED"; events: "ALL_MATCHES_WITH_EVENTS"; callups: "ALL_MATCHES_INCLUDING_SCHEDULED" };
  players: PlayerStatistics[];
  rankings: Record<keyof typeof RANKING_LABELS, RankingEntry[]>;
}
export interface SeasonStatistics extends PlayerStatisticsResponse {
  total_matches: number; matches_with_events: number; total_events: number; comparison: Comparison;
  competitive: { matches: number; wins: number; draws: number; losses: number; goals_for: number; goals_against: number; goal_difference: number };
}
export const statisticsApi = {
  match: (id: number) => request<MatchStatistics>(`/matches/${id}/stats`),
  season: () => request<SeasonStatistics>("/statistics/season"),
  players: () => request<PlayerStatisticsResponse>("/statistics/players"),
};
