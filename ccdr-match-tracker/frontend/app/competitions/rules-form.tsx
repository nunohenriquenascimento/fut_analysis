"use client";

import { useRef, useState } from "react";
import { PrimaryButton, SecondaryButton } from "@/components/ui";
import { competitionsApi, competitionError, TIEBREAKERS, type CompetitionRules, type Tiebreaker } from "@/lib/competitions";
import { ErrorNotice } from "./competition-ui";

export function RulesFields({ value, onChange }: { value: CompetitionRules; onChange: (value: CompetitionRules) => void }) {
  function move(index: number, direction: number) {
    const next = [...value.tiebreakers];
    [next[index], next[index + direction]] = [next[index + direction], next[index]];
    onChange({ ...value, tiebreakers: next });
  }
  return <div className="space-y-4">
    <p className="text-sm text-muted">Política provisória. A ordem dos critérios é explícita; nenhum desempate é considerado oficial.</p>
    <div className="grid grid-cols-3 gap-3">{([["win", "Vitória"], ["draw", "Empate"], ["loss", "Derrota"]] as const).map(([key, label]) =>
      <label key={key} className="text-sm">{label}<input className="form-field mt-1" type="number" min={0} max={100} required value={value[key]}
        onChange={(e) => onChange({ ...value, [key]: e.target.value === "" ? "" : Number(e.target.value) } as CompetitionRules)} /></label>)}</div>
    <p className="font-semibold">Critérios de desempate, por ordem</p>
    {value.tiebreakers.length === 0 && <p className="text-sm text-muted">Sem critérios configurados. A igualdade de pontos permanece por resolver.</p>}
    <ol className="space-y-2">{value.tiebreakers.map((criterion, index) => <li key={criterion} className="rounded-xl border border-border p-3 space-y-2">
      <p>{index + 1}. {TIEBREAKERS[criterion]}</p><div className="flex flex-wrap gap-2">
        <SecondaryButton disabled={index === 0} aria-label={`Subir ${TIEBREAKERS[criterion]}`} onClick={() => move(index, -1)}>↑ Subir</SecondaryButton>
        <SecondaryButton disabled={index === value.tiebreakers.length - 1} aria-label={`Descer ${TIEBREAKERS[criterion]}`} onClick={() => move(index, 1)}>↓ Descer</SecondaryButton>
        <SecondaryButton aria-label={`Retirar ${TIEBREAKERS[criterion]}`} onClick={() => onChange({ ...value, tiebreakers: value.tiebreakers.filter((key) => key !== criterion) })}>Retirar</SecondaryButton>
      </div></li>)}</ol>
    <label className="block text-sm">Adicionar critério<select className="form-field mt-1" value="" onChange={(e) => { if (e.target.value) onChange({ ...value, tiebreakers: [...value.tiebreakers, e.target.value as Tiebreaker] }); }}>
      <option value="">Escolher critério…</option>{(Object.keys(TIEBREAKERS) as Tiebreaker[]).filter((key) => !value.tiebreakers.includes(key)).map((key) => <option value={key} key={key}>{TIEBREAKERS[key]}</option>)}
    </select></label>
  </div>;
}

export default function RulesForm({ competitionId, initial }: { competitionId: number; initial: CompetitionRules }) {
  const [rules, setRules] = useState(initial), [error, setError] = useState("");
  const [busy, setBusy] = useState(false), [saved, setSaved] = useState(false);
  const locked = useRef(false);
  return <form className="card space-y-4" onSubmit={async (event) => {
    event.preventDefault(); if (locked.current) return; locked.current = true; setBusy(true); setError(""); setSaved(false);
    try { const result = await competitionsApi.rules(competitionId, rules); setRules(result.rules); setSaved(true); }
    catch (reason) { setError(competitionError(reason)); }
    finally { locked.current = false; setBusy(false); }
  }}><h2 className="section-header">Configurar pontuação e desempates</h2>
    <fieldset disabled={busy} className="space-y-4"><RulesFields value={rules} onChange={(next) => { setRules(next); setSaved(false); }} />
      <PrimaryButton type="submit">{busy ? "A guardar…" : "Guardar configuração"}</PrimaryButton></fieldset>
    {saved && <p role="status" className="text-success">Configuração guardada. A classificação continua provisória.</p>}
    {error && <ErrorNotice message={error} />}
  </form>;
}
