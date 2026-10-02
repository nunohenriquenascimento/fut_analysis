"use client";

import Link from "next/link";
import { PageContainer } from "@/components/ui";
import { useEffect, useState } from "react";
import ComparisonTable from "@/app/statistics/comparison-table";
import { MATCH_STATUS, matchError } from "@/lib/matches";
import MatchScoreboard from "@/components/match-scoreboard";
import { LoadingState, SecondaryButton } from "@/components/ui";
import { timelineText } from "@/lib/live";
import { statisticsApi, type MatchStatistics as Statistics } from "@/lib/statistics";

export default function MatchStatistics({ matchId }: { matchId: number }) {
  const [data, setData] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);
  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        if (!Number.isInteger(matchId) || matchId < 1 || matchId > 2147483647) { if (!cancelled) setError("Jogo não encontrado."); return; }
        const result = await statisticsApi.match(matchId);
        if (!cancelled) { setData(result); setError(""); }
      } catch (reason) { if (!cancelled) setError(matchError(reason)); }
      finally { if (!cancelled) setLoading(false); }
    }
    void load();
    return () => { cancelled = true; };
  }, [matchId, reload]);
  return <PageContainer className=""><div className="page-content space-y-6">
    <Link href={`/matches/${matchId}`} className="inline-flex min-h-11 items-center text-sm text-muted">← Detalhe do jogo</Link>
    <h1 className="text-3xl font-bold">Estatísticas do jogo</h1>
    <SecondaryButton disabled={loading} onClick={() => { setLoading(true); setReload((n) => n + 1); }}>Atualizar estatísticas</SecondaryButton>
    {loading && <LoadingState>A carregar estatísticas…</LoadingState>}
    {error && <p role="alert" className="rounded-xl border border-error p-4 text-error">{error}{data && " Os dados apresentados podem estar desatualizados."}</p>}
    {data && <>
      <header className="card match-sheet text-center">
        <p className="mt-3 text-sm text-muted">{data.is_final ? "Resultado final" : "Resultado atual"} · {MATCH_STATUS[data.match.status]}</p>
        <MatchScoreboard match={data.match} score={data.score} teamName={data.team_name} />
      </header>
      <p className="text-sm">Total de eventos: <strong>{data.total_events}</strong></p>
      <ComparisonTable data={data.comparison} us={data.team_name} opponent={data.match.opponent_name} />
      <p className="text-xs text-muted">Remates totais = à baliza + fora + bloqueados. Os golos não acrescentam remates.</p>
      <section aria-labelledby="timeline-title" className="space-y-3">
        <h2 id="timeline-title" className="text-xl font-semibold">Timeline resumida</h2>
        {data.timeline.length === 0 && <p className="text-muted">Ainda não existem acontecimentos neste jogo.</p>}
        <ol className="space-y-2">{data.timeline.map((event) => <li key={event.id} className="rounded-xl bg-surface p-3">
          <p className="text-xs text-muted">{event.period}.ª parte</p>
          <p className="mt-1 break-words text-sm">{timelineText(event, data.players)}</p>
        </li>)}</ol>
      </section>
    </>}
  </div></PageContainer>;
}
