"use client";

import { useAuth } from "@/components/auth-provider";

import { PrimaryButton, SecondaryButton } from "@/components/ui";

import Link from "next/link";
import { PageContainer } from "@/components/ui";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { api, type Match, type RosterContext } from "@/lib/api";
import { matchDate, matchError } from "@/lib/matches";
import { PageHeader, LoadingState, EmptyState } from "@/components/ui";
import MatchScoreboard from "@/components/match-scoreboard";
import MatchForm, { type MatchFields } from "./match-form";

export default function MatchesPage() {
  const { canEdit } = useAuth();
  const router = useRouter();
  const [context, setContext] = useState<RosterContext | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");
  const [creating, setCreating] = useState(false);
  const [busy, setBusy] = useState(false);
  const [reload, setReload] = useState(0);
  const locked = useRef(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const current = await api.rosterContext();
        const rows = await api.seasonMatches(current);
        // Scores already exist on the detail API; no new result calculation.
        const withScores = await Promise.all(rows.map(async (match) => {
          if (match.status === "SCHEDULED") return match;
          try { return await api.match(match.id); } catch { return match; }
        }));
        if (!cancelled) { setContext(current); setMatches(withScores); setError(""); }
      } catch (reason) { if (!cancelled) setError(matchError(reason)); }
      finally { if (!cancelled) setLoading(false); }
    }
    void load();
    return () => { cancelled = true; };
  }, [reload]);

  async function create(fields: MatchFields) {
    if (locked.current || !context || loading) return;
    locked.current = true;
    setBusy(true); setActionError("");
    try {
      const saved = await api.createMatch({ ...fields, season_id: context.season_id, team_id: context.team_id });
      // Hide the form before navigation, preventing another creation if navigation is slow.
      setCreating(false);
      setMatches((rows) => [saved, ...rows]);
      router.push(`/matches/${saved.id}`);
    } catch (reason) { setActionError(matchError(reason)); }
    finally { locked.current = false; setBusy(false); }
  }

  return <PageContainer className="wide-page">
    <div className="page-content space-y-6">
      <PageHeader title="Jogos e jornadas" description={`Sub-19 · ${context?.season_name ?? "2026/27"}`} />
      {loading && <LoadingState>A carregar os jogos…</LoadingState>}
      {error && <div role="alert" className="rounded-xl border border-error p-4 text-error">
        <p>{error}</p><SecondaryButton disabled={loading} className="" onClick={() => { setLoading(true); setReload((value) => value + 1); }}>Tentar novamente</SecondaryButton>
      </div>}
      {canEdit && context && !creating && <PrimaryButton disabled={loading || busy} onClick={() => { setCreating(true); setActionError(""); }} className="w-full">Criar jogo</PrimaryButton>}
      {canEdit && creating && <MatchForm busy={busy || loading} onSave={create} onCancel={() => { setCreating(false); setActionError(""); }} />}
      {actionError && <p role="alert" className="text-error">{actionError}</p>}
      <section aria-label="Jogos" aria-busy={loading} className="matches-grid space-y-3">
        {!loading && !error && matches.length === 0 && <EmptyState>Ainda não existem jogos nesta época.</EmptyState>}
        {matches.map((match) => <Link key={match.id} href={`/matches/${match.id}`} className="card block">
          <p className="matchday-label">{match.matchday === null ? "Jornada por definir" : `Jornada ${match.matchday}`}</p>
          <h2 className="sr-only">{match.opponent_name}</h2>
          <MatchScoreboard match={match} score={match.score} teamName={context?.team_name} compact />
          <p className="mt-2">{matchDate(match.kickoff_at)}</p>
          <p className="mt-1 text-sm text-muted">{match.is_home ? "Casa" : "Fora"}</p>
        </Link>)}
      </section>
    </div>
  </PageContainer>;
}
