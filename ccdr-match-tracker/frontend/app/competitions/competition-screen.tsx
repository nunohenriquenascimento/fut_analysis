"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { TeamCrest } from "@/components/media";
import { EmptyState, LoadingState, PageContainer, PageHeader, SecondaryButton } from "@/components/ui";
import { competitionsApi, competitionError, TIEBREAKERS, type Competition, type CompetitionFixture, type CompetitionTeam, type Matchday, type Standings } from "@/lib/competitions";
import { ChampionshipNav, ErrorNotice, FixtureCards, ProvisionalNotice } from "./competition-ui";
import FixtureDetail from "./fixture-detail";
import ImportForm from "./import-form";
import RulesForm from "./rules-form";
import ParticipantsForm from "./participants-form";
import FPFSection from "./fpf-section";

export type ChampionshipView = "standings" | "results" | "calendar" | "teams" | "manage" | "fixture" | "fpf";
const titles: Record<ChampionshipView, string> = { standings: "Classificação do campeonato", results: "Resultados por jornada", calendar: "Calendário completo", teams: "Equipas participantes", manage: "Gestão do campeonato", fixture: "Detalhes do jogo", fpf: "FPF · Fonte oficial" };

export default function CompetitionScreen({ competitionId, view = "standings", fixtureId }: { competitionId: number; view?: ChampionshipView; fixtureId?: number }) {
  const { canEdit, isAdmin } = useAuth();
  const [competition, setCompetition] = useState<Competition | null>(null), [teams, setTeams] = useState<CompetitionTeam[]>([]);
  const [standings, setStandings] = useState<Standings | null>(null), [fixtures, setFixtures] = useState<CompetitionFixture[]>([]), [matchdays, setMatchdays] = useState<Matchday[]>([]);
  const [loading, setLoading] = useState(true), [error, setError] = useState(""), [reload, setReload] = useState(0);
  const [matchday, setMatchday] = useState("");
  const denied = view === "manage" && !canEdit;
  useEffect(() => {
    if (denied) return;
    let active = true;
    async function load() {
      try {
        const all = await competitionsApi.list();
        const current = all.find((item) => item.id === competitionId);
        if (!current) throw new Error("not-found");
        const [members, table, calendar, rounds] = await Promise.all([
          competitionsApi.participants(competitionId),
          view === "standings" ? competitionsApi.standings(competitionId) : null,
          view === "calendar" || view === "fixture" ? competitionsApi.calendar(competitionId) : [],
          view === "results" ? competitionsApi.matchdays(competitionId) : [],
        ]);
        if (active) { setCompetition(current); setTeams(members); setStandings(table); setFixtures(calendar); setMatchdays(rounds); setError(""); }
      } catch (reason) { if (active) setError(reason instanceof Error && reason.message === "not-found" ? "Competição não encontrada." : competitionError(reason)); }
      finally { if (active) setLoading(false); }
    }
    void load();
    return () => { active = false; };
  }, [competitionId, view, reload, denied]);
  function refresh() { setLoading(true); setReload((number) => number + 1); }
  const fixture = fixtures.find((item) => item.id === fixtureId);
  return <PageContainer className="wide-page"><div className="page-content space-y-6">
    <PageHeader title={titles[view]} description={competition?.name} backHref="/competitions" backLabel="Campeonatos" />
    {denied ? <p role="alert">A gestão do campeonato requer ADMIN ou COACH.</p> : <>
      <ChampionshipNav id={competitionId} active={view === "standings" ? "" : `/${view}`} canEdit={canEdit} />
      {loading ? <LoadingState>A carregar campeonato…</LoadingState> : error ? <ErrorNotice message={error} retry={refresh} /> : competition && <>
        {view !== "fpf" && <ProvisionalNotice />}
        {view !== "manage" && <SecondaryButton onClick={refresh}>Atualizar dados</SecondaryButton>}
        {view === "standings" && standings && <section aria-label="Classificação" className="space-y-4">
          <p className="text-sm text-muted">{standings.warning} Jogos terminados: {standings.completed_fixtures}.</p>
          <div className="standings-scroll" role="region" aria-label="Tabela de classificação, deslize para ver todas as colunas" tabIndex={0}>
            <table className="standings-table"><caption>Pontos e estatísticas do campeonato</caption>
              <thead><tr>{["Pos.", "Equipa", "Pts", "J", "V", "E", "D", "GM", "GS", "DG"].map((label) => <th scope="col" key={label}>{label}</th>)}</tr></thead>
              <tbody>{standings.rows.map((row) => <tr key={row.team_id} className={row.team_id === competition.internal_team_id ? "our-team" : ""}>
                <td>{row.rank}</td><th scope="row">{row.name}{row.unresolved_tie && <span className="block text-xs text-warning mt-1">Empate por resolver</span>}</th>
                {[row.points, row.played, row.wins, row.draws, row.losses, row.goals_for, row.goals_against, row.goal_difference].map((value, index) => <td key={index}>{value}</td>)}
              </tr>)}</tbody>
            </table>
          </div>
          <p className="text-xs text-muted">Pts: pontos · J: jogos · V: vitórias · E: empates · D: derrotas · GM: golos marcados · GS: golos sofridos · DG: diferença de golos.</p>
          <details className="card"><summary className="min-h-12 py-3 font-semibold">Política de classificação em uso</summary>
            <p>Vitória: {standings.rules.win} · Empate: {standings.rules.draw} · Derrota: {standings.rules.loss} pontos.</p>
            {standings.rules.tiebreakers.length ? <ol className="list-decimal pl-5 mt-3">{standings.rules.tiebreakers.map((key) => <li key={key}>{TIEBREAKERS[key]}</li>)}</ol> : <p className="mt-2">Sem critérios de desempate configurados.</p>}
          </details>
        </section>}
        {view === "results" && <section aria-label="Jornadas" className="space-y-5">
          {matchdays.length === 0 ? <EmptyState>Ainda não existem jornadas.</EmptyState> : <>
            <div><label className="block" htmlFor="competition-matchday">Jornada</label><select id="competition-matchday" className="form-field mt-1" value={matchday} onChange={(event) => setMatchday(event.target.value)}><option value="">Todas as jornadas</option>{matchdays.map((round) => <option value={round.matchday} key={round.matchday}>Jornada {round.matchday}</option>)}</select></div>
            {matchdays.filter((round) => !matchday || String(round.matchday) === matchday).map((round) => <section key={round.matchday} aria-label={`Jornada ${round.matchday}`} className="space-y-3"><h2 className="section-header">Jornada {round.matchday}</h2><FixtureCards fixtures={round.fixtures} teams={teams} competitionId={competitionId} /></section>)}
          </>}
        </section>}
        {view === "calendar" && <section aria-label="Calendário" className="space-y-3"><p className="text-sm text-muted">Todas as jornadas. Horas de Lisboa.</p>{fixtures.length ? <FixtureCards fixtures={fixtures} teams={teams} competitionId={competitionId} /> : <EmptyState>Ainda não existem jogos no calendário.</EmptyState>}</section>}
        {(view === "teams" || view === "manage") && <section aria-label="Participantes" className="space-y-3"><h2 className="section-header">Equipas participantes ({teams.length})</h2><ul className="grid gap-3 sm:grid-cols-2">{teams.map((team) => <li className="card flex gap-3 items-center" key={team.id}>
          <TeamCrest name={team.name} path={team.crest_path} size="sm" /><div className="min-w-0"><p className="font-semibold break-words">{team.name}</p>{team.id === competition.internal_team_id && <span className="text-sm text-secondary">Nossa equipa</span>}{view === "manage" && <p className="text-sm text-muted">ID para importação: {team.id}</p>}</div>
        </li>)}</ul></section>}
        {view === "manage" && <>{isAdmin && <ParticipantsForm competitionId={competitionId} internalTeamId={competition.internal_team_id} initial={teams} onSaved={setTeams} />}<RulesForm competitionId={competitionId} initial={competition.rules} /><ImportForm competitionId={competitionId} /></>}
        {view === "fixture" && (fixture ? <FixtureDetail key={fixture.id} fixture={fixture} teams={teams} canEdit={canEdit} /> : <EmptyState>Jogo não encontrado nesta competição.</EmptyState>)}
        {view === "fpf" && <FPFSection competition={competition} />}
      </>}
    </>}
  </div></PageContainer>;
}
