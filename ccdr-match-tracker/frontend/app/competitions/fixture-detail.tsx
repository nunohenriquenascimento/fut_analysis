"use client";

import Link from "next/link";
import { useRef, useState } from "react";
import { competitionsApi, competitionError, externalCorrection, fixtureDate, type CompetitionFixture, type CompetitionTeam } from "@/lib/competitions";
import { MatchStatusBadge, PrimaryButton } from "@/components/ui";
import { ErrorNotice } from "./competition-ui";

export default function FixtureDetail({ fixture, teams, canEdit }: { fixture: CompetitionFixture; teams: CompetitionTeam[]; canEdit: boolean }) {
  const [current, setCurrent] = useState(fixture);
  const [home, setHome] = useState(fixture.home_goals?.toString() ?? ""), [away, setAway] = useState(fixture.away_goals?.toString() ?? "");
  const [source, setSource] = useState(fixture.source), [busy, setBusy] = useState(false);
  const [error, setError] = useState(""), [success, setSuccess] = useState("");
  const locked = useRef(false);
  const homeName = teams.find((team) => team.id === current.home_team_id)?.name ?? `Equipa #${current.home_team_id}`;
  const awayName = teams.find((team) => team.id === current.away_team_id)?.name ?? `Equipa #${current.away_team_id}`;
  return <article className="space-y-5">
    <div className="card space-y-4">
      <h2 className="section-header">{homeName} · {awayName}</h2>
      <MatchStatusBadge status={current.status} />
      <p className="text-3xl font-bold text-secondary tabular-nums" aria-label="Resultado do jogo">{current.status === "SCHEDULED" || current.status === "CANCELLED" ? "Por disputar" : `${current.home_goals} – ${current.away_goals}`}</p>
      <dl className="space-y-3">
        <div><dt className="text-sm text-muted">Jornada</dt><dd>{current.matchday}</dd></div>
        <div><dt className="text-sm text-muted">Data e hora de Lisboa</dt><dd>{fixtureDate(current.kickoff_at)}</dd></div>
        <div><dt className="text-sm text-muted">Local</dt><dd>{current.venue || "Por definir"}</dd></div>
        <div><dt className="text-sm text-muted">Origem do registo</dt><dd className="break-words whitespace-pre-wrap">{current.source}</dd></div>
        <div><dt className="text-sm text-muted">Chave externa</dt><dd className="break-all">{current.external_key}</dd></div>
      </dl>
      {current.internal_match_id !== null && <div className="space-y-3"><p className="text-sm">Este é um jogo interno. O resultado é derivado dos seus eventos e não pode ser corrigido como resultado externo.</p>
        <Link className="button button-secondary" href={`/matches/${current.internal_match_id}`}>Abrir o nosso jogo</Link></div>}
    </div>
    {canEdit && current.internal_match_id === null && <form className="card space-y-4" onSubmit={async (event) => {
      event.preventDefault(); if (locked.current) return; locked.current = true; setBusy(true); setError(""); setSuccess("");
      try {
        await competitionsApi.import(current.competition_id, { fixtures: [externalCorrection(current, Number(home), Number(away), source)] });
        setSuccess("Resultado externo corrigido. Consulte a classificação para ver os valores atualizados.");
        try {
          const rows = await competitionsApi.calendar(current.competition_id);
          const saved = rows.find((row) => row.id === current.id);
          if (!saved) throw new Error("not-found");
          setCurrent(saved); setHome(saved.home_goals?.toString() ?? ""); setAway(saved.away_goals?.toString() ?? ""); setSource(saved.source);
        } catch { setError("O resultado foi guardado, mas não foi possível atualizar o detalhe. Use Atualizar dados para consultar o estado atual."); }
      } catch (reason) { setError(competitionError(reason)); }
      finally { locked.current = false; setBusy(false); }
    }}><h2 className="section-header">Corrigir resultado externo</h2>
      <fieldset disabled={busy} className="space-y-4"><div className="grid grid-cols-2 gap-3">
        <label>Golos da equipa da casa<input type="number" className="form-field mt-1" min={0} max={999} required value={home} onChange={(event) => { setHome(event.target.value); setSuccess(""); }} /></label>
        <label>Golos da equipa visitante<input type="number" className="form-field mt-1" min={0} max={999} required value={away} onChange={(event) => { setAway(event.target.value); setSuccess(""); }} /></label>
      </div><label className="block">Origem da correção<input className="form-field mt-1" maxLength={500} required value={source} onChange={(event) => { setSource(event.target.value); setSuccess(""); }} /></label>
        <PrimaryButton type="submit">{busy ? "A guardar…" : "Guardar resultado externo"}</PrimaryButton>
      </fieldset>{error && <ErrorNotice message={error} />}{success && <p role="status" className="text-success">{success}</p>}
    </form>}
  </article>;
}
