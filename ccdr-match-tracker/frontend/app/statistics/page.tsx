"use client";

import { PageHeader, LoadingState, Card, SectionHeader, SecondaryButton } from "@/components/ui";
import { PlayerAvatar } from "@/components/media";
import { PageContainer } from "@/components/ui";
import { useEffect, useState } from "react";
import { matchError } from "@/lib/matches";
import { PLAYER_LABELS, RANKING_LABELS, statisticsApi, type SeasonStatistics } from "@/lib/statistics";
import ComparisonTable from "./comparison-table";

export default function StatisticsPage() {
  const [data, setData] = useState<SeasonStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);
  useEffect(() => {
    let cancelled = false;
    async function load() {
      try { const result = await statisticsApi.season(); if (!cancelled) { setData(result); setError(""); } }
      catch (reason) { if (!cancelled) setError(matchError(reason)); }
      finally { if (!cancelled) setLoading(false); }
    }
    void load();
    return () => { cancelled = true; };
  }, [reload]);

  const competitiveCards = data ? [
    ["Jogos terminados", data.competitive.matches], ["Vitórias", data.competitive.wins],
    ["Empates", data.competitive.draws], ["Derrotas", data.competitive.losses],
    ["Golos marcados", data.competitive.goals_for], ["Golos sofridos", data.competitive.goals_against],
    ["Diferença de golos", data.competitive.goal_difference],
  ] as const : [];

  return <PageContainer className="wide-page"><div className="page-content space-y-6">
    <PageHeader title="Estatísticas" description={`${data?.context.team_name ?? "CCDR Vila Cortez do Mondego"} · ${data?.context.season_name ?? "2026/27"}`} />
    <SecondaryButton disabled={loading} onClick={() => { setLoading(true); setReload((n) => n + 1); }}>Atualizar estatísticas</SecondaryButton>
    {loading && <LoadingState>A carregar estatísticas…</LoadingState>}
    {error && <p role="alert" className="rounded-xl border border-error p-4 text-error">{error}{data && " Os dados apresentados podem estar desatualizados."}</p>}
    {data && <>
      {data.total_matches === 0 && <p role="status" className="rounded-xl border border-border p-4">Ainda não existem jogos nesta época.</p>}
      <section aria-labelledby="competitive-title" className="space-y-3">
        <SectionHeader id="competitive-title">Resumo competitivo</SectionHeader>
        <p className="text-sm text-muted">Apenas jogos terminados. Jogos registados na época: {data.total_matches}.</p>
        <dl className="summary-grid grid grid-cols-2 gap-3 md:grid-cols-4">{competitiveCards.map(([label, value]) => <Card key={label}>
          <dt className="text-sm text-muted">{label}</dt><dd className="mt-1 text-2xl font-bold tabular-nums">{value}</dd>
        </Card>)}</dl>
      </section>
      <section aria-labelledby="activity-title" className="space-y-3">
        <h2 id="activity-title" className="text-xl font-semibold">Atividade da época</h2>
        <p className="text-sm text-muted">Eventos de todos os jogos, incluindo jogos em curso ou cancelados. Os adversários são somados.</p>
        <div className="grid grid-cols-2 gap-3">
          <p className="rounded-xl bg-surface p-4 text-sm">Jogos com eventos <strong className="mt-1 block text-2xl">{data.matches_with_events}</strong></p>
          <p className="rounded-xl bg-surface p-4 text-sm">Total de eventos <strong className="mt-1 block text-2xl">{data.total_events}</strong></p>
        </div>
        <ComparisonTable data={data.comparison} us={data.context.team_name} opponent="Adversários" />
        <p className="text-xs text-muted">Remates totais = à baliza + fora + bloqueados. Os golos não acrescentam remates.</p>
      </section>
      <section aria-labelledby="rankings-title" className="space-y-4">
        <h2 id="rankings-title" className="text-xl font-semibold">Rankings</h2>
        <p className="text-sm text-muted">Eventos de todos os jogos. Empates ordenados por nome; apenas valores superiores a zero.</p>
        <div className="rankings-grid space-y-3 md:space-y-0">{(Object.keys(RANKING_LABELS) as (keyof typeof RANKING_LABELS)[]).map((key) => <section key={key} aria-label={RANKING_LABELS[key]} className="card">
          <h3 className="font-semibold">{RANKING_LABELS[key]}</h3>
          {data.rankings[key].length === 0 ? <p className="mt-2 text-sm text-muted">Sem registos.</p> : <ol className="mt-3 space-y-2">
            {data.rankings[key].map((entry) => <li key={entry.player_id} className="flex items-center gap-3 text-sm"><PlayerAvatar name={entry.name} photoPath={data.players.find((row) => row.player.id === entry.player_id)?.player.photo_path} size="sm" /><span className="min-w-0 flex-1 break-words">{entry.name}</span><strong className="shrink-0 text-xl tabular-nums">{entry.value}</strong></li>)}
          </ol>}
        </section>)}</div>
      </section>
      <section aria-labelledby="players-title" className="space-y-3">
        <h2 id="players-title" className="text-xl font-semibold">Por jogador</h2>
        <p className="text-sm text-muted">Convocado/titular conta todas as convocatórias, incluindo jogos agendados. Inclui jogadores inativos. Não são calculados minutos jogados.</p>
        {data.players.length === 0 && <p className="text-muted">Ainda não existem jogadores nesta época.</p>}
        {data.players.map((row) => <details key={row.player.id} className="player-statistics rounded-xl border border-border p-4">
          <summary className="min-h-12 cursor-pointer break-words font-semibold"><span className="inline-flex items-center gap-3 align-middle"><PlayerAvatar name={row.player.name} photoPath={row.player.photo_path} number={row.player.shirt_number} /><span className="min-w-0">{row.player.name}{!row.player.is_active && " · Inativo"}<small className="mt-1 block text-muted">#{row.player.shirt_number ?? "—"} · {row.player.position}</small></span></span></summary>
          <dl className="mt-3 grid grid-cols-2 gap-3">{(Object.keys(PLAYER_LABELS) as (keyof typeof PLAYER_LABELS)[]).map((key) => <div key={key}>
            <dt className="text-xs text-muted">{PLAYER_LABELS[key]}</dt><dd className="text-lg font-semibold tabular-nums">{row[key]}</dd>
          </div>)}</dl>
        </details>)}
      </section>
    </>}
  </div></PageContainer>;
}
