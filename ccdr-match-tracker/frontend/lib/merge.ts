import { request, type Match, type Player } from "./api";
import type { LiveState, MatchEvent } from "./live";

export type MergeStatus = "FINISHED" | "SECOND_HALF";
export interface MergeSelection { principal_id: number; continuation_id: number; final_status: MergeStatus }
export interface MergeSquad { id: number; player: Player; is_starter: boolean }
export interface MergeGame {
  match: Match; score: { us: number; opponent: number }; elapsed_seconds: number;
  period: number | null; event_count: number; squad: MergeSquad[];
}
export interface MergePreview {
  principal: MergeGame; continuation: MergeGame; final_status: MergeStatus;
  transfers: { original: MatchEvent; new_period: 2; new_elapsed_seconds: number }[];
  continuation_only_players: MergeSquad[]; predicted_score: { us: number; opponent: number };
  predicted_elapsed_seconds: number; warnings: string[]; conflicts: string[];
  can_merge: boolean; preview_token: string | null;
}
export const mergeApi = {
  preview: (selection: MergeSelection) => request<MergePreview>("/matches/merge/preview", { method: "POST", body: JSON.stringify(selection) }),
  execute: (selection: MergeSelection, preview_token: string, confirmation: string) => request<LiveState>("/matches/merge", {
    method: "POST", body: JSON.stringify({ ...selection, preview_token, confirmation }),
  }),
};
