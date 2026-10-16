"use client";

import Link from "next/link";
import { MatchStatusBadge, SecondaryButton } from "@/components/ui";
import { TeamCrest } from "@/components/media";
import { fixtureDate, type CompetitionFixture, type CompetitionTeam } from "@/lib/competitions";

export function ErrorNotice({ message, retry }: { message: string; retry?: () => void }) {
  return <div role="alert" className="rounded-xl border border-error bg-error-surface p-4 text-error space-y-3"><p>{message}</p>
    {retry && <SecondaryButton onClick={retry}>Tentar novamente</SecondaryButton>}</div>;
}

export function ProvisionalNotice() {
  return <aside className="rounded-xl border border-warning bg-warning-surface p-4 space-y-1">
    <h2 className="font-bold text-warning">Classificação provisória</h2>
    <p className="text-sm">O regulamento de 2026/2027 ainda não foi validado. Os critérios são configuráveis e os empates podem permanecer por resolver.</p>
  </aside>;
}

export function ChampionshipNav({ id, active, canEdit }: { id: number; active: string; canEdit: boolean }) {
  const items = [["", "Classificação"], ["/results", "Resultados"], ["/calendar", "Calendário"], ["/teams", "Equipas"], ["/fpf", "FPF · Oficial"],
    ...(canEdit ? [["/manage", "Gestão"]] : [])];
  return <nav className="competition-nav" aria-label="Campeonato">{items.map(([suffix, label]) =>
    <Link key={suffix} href={`/competitions/${id}${suffix}`} aria-current={active === suffix ? "page" : undefined}>{label}</Link>)}</nav>;
}

export function FixtureCards({ fixtures, teams, competitionId }: { fixtures: CompetitionFixture[]; teams: CompetitionTeam[]; competitionId: number }) {
  const byId = new Map(teams.map((team) => [team.id, team]));
  return <div className="grid gap-3 md:grid-cols-2">{fixtures.map((fixture) => {
    const home = byId.get(fixture.home_team_id), away = byId.get(fixture.away_team_id);
    return <Link key={fixture.id} href={`/competitions/${competitionId}/fixtures/${fixture.id}`} className="card fixture-card block">
      <div className="flex flex-wrap items-center justify-between gap-2"><span className="matchday-label">Jornada {fixture.matchday}</span><MatchStatusBadge status={fixture.status} /></div>
      <div className="fixture-teams my-4">
        <div><TeamCrest name={home?.name ?? "Equipa"} path={home?.crest_path} size="sm" /><span>{home?.name ?? `Equipa #${fixture.home_team_id}`}</span></div>
        <strong className="tabular-nums" aria-label="Resultado">{fixture.status === "SCHEDULED" || fixture.status === "CANCELLED" ? "–" : `${fixture.home_goals ?? "–"} – ${fixture.away_goals ?? "–"}`}</strong>
        <div><TeamCrest name={away?.name ?? "Equipa"} path={away?.crest_path} size="sm" /><span>{away?.name ?? `Equipa #${fixture.away_team_id}`}</span></div>
      </div>
      <p className="text-sm text-muted">{fixture.kickoff_at ? fixtureDate(fixture.kickoff_at) : fixture.schedule_text ? `Data parcial FPF: ${fixture.schedule_text}` : fixtureDate(null)}</p>
      <p className="mt-2 text-sm text-secondary">{fixture.internal_match_id === null ? "Jogo externo · Ver detalhes e origem" : "Nosso jogo · Resultado dos eventos internos"}</p>
    </Link>;
  })}</div>;
}
