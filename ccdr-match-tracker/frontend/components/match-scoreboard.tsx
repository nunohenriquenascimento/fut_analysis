import type { ReactNode } from "react";
import type { Match } from "@/lib/api";
import { CLUB } from "@/lib/brand";
import { TeamCrest } from "./media";
import { MatchStatusBadge } from "./ui";

export default function MatchScoreboard({ match, score, teamName = CLUB.name, children, compact = false }: {
  match: Match; score?: { us: number; opponent: number }; teamName?: string; children?: ReactNode; compact?: boolean;
}) {
  return <div className={`match-scoreboard ${compact ? "scoreboard-compact" : ""}`}>
    <div className="scoreboard-teams"><div><TeamCrest name={teamName} path={match.team_crest_path} club /><span>{teamName}</span></div><span className="versus" aria-hidden="true">vs</span><div><TeamCrest name={match.opponent_name} path={match.opponent_crest_path} /><span>{match.opponent_name}</span></div></div>
    {score && <p aria-label="Resultado" className="score-value">{score.us} – {score.opponent}</p>}
    {children}
    <MatchStatusBadge status={match.status} />
  </div>;
}
