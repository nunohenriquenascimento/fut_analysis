"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api, type RosterContext } from "@/lib/api";
import { competitionError, competitionsApi, type CompetitionRules, type CompetitionTeam } from "@/lib/competitions";
import { LoadingState, PrimaryButton, SecondaryButton } from "@/components/ui";
import { ErrorNotice } from "./competition-ui";
import { RulesFields } from "./rules-form";

export default function CompetitionCreateForm({ onCancel }: { onCancel: () => void }) {
  const router = useRouter();
  const [context, setContext] = useState<RosterContext | null>(null), [teams, setTeams] = useState<CompetitionTeam[]>([]);
  const [selected, setSelected] = useState<number[]>([]), [name, setName] = useState("");
  const [rules, setRules] = useState<CompetitionRules>({ win: 3, draw: 1, loss: 0, tiebreakers: [] });
  const [loading, setLoading] = useState(true), [error, setError] = useState("");
  const [newTeam, setNewTeam] = useState(""), [busy, setBusy] = useState(false), [reload, setReload] = useState(0);
  const locked = useRef(false);
  useEffect(() => {
    let active = true;
    Promise.all([api.rosterContext(), competitionsApi.teams()]).then(([ctx, rows]) => {
      if (active) { setContext(ctx); setTeams(rows); setSelected([ctx.team_id]); setError(""); }
    }).catch((reason) => { if (active) setError(competitionError(reason)); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [reload]);
  if (loading) return <LoadingState>A preparar competição…</LoadingState>;
  if (!context) return <ErrorNotice message={error} retry={() => { setLoading(true); setReload((n) => n + 1); }} />;
  return <section className="card space-y-5" aria-label="Nova competição">
    <h2 className="section-header">Nova competição</h2><p className="text-muted">{context.season_name} · {context.team_name}</p>
    <form className="space-y-4" onSubmit={async (event) => {
      event.preventDefault(); if (locked.current) return; locked.current = true; setBusy(true); setError("");
      try {
        const row = await competitionsApi.create({ name, season_id: context.season_id, internal_team_id: context.team_id, team_ids: selected, rules });
        router.push(`/competitions/${row.id}`);
        // Keep locked until navigation: no duplicate creations on a slow device.
      } catch (reason) { setError(competitionError(reason)); locked.current = false; setBusy(false); }
    }}><fieldset disabled={busy} className="space-y-4">
      <label className="block">Nome da competição<input className="form-field mt-1" required maxLength={120} value={name} onChange={(e) => setName(e.target.value)} /></label>
      <fieldset className="space-y-2"><legend className="font-semibold mb-2">Equipas participantes ({selected.length})</legend>
        <p className="text-sm text-muted">Associe as equipas nesta criação. Os IDs ficam disponíveis para preparar a importação de jogos.</p>
        <div className="grid gap-2 sm:grid-cols-2">{teams.map((team) => <label key={team.id} className="participant-option">
          <input type="checkbox" checked={selected.includes(team.id)} disabled={team.id === context.team_id} onChange={(e) => setSelected((current) => e.target.checked ? [...current, team.id] : current.filter((id) => id !== team.id))} />
          <span>{team.name}{team.id === context.team_id && " · Nossa equipa"}</span></label>)}</div>
      </fieldset>
      <RulesFields value={rules} onChange={setRules} />
      <div className="flex flex-wrap gap-2"><PrimaryButton type="submit">{busy ? "A criar…" : "Criar e associar equipas"}</PrimaryButton><SecondaryButton onClick={onCancel}>Fechar formulário</SecondaryButton></div>
    </fieldset></form>
    <form className="border-t border-border pt-4 space-y-3" onSubmit={async (event) => {
      event.preventDefault(); if (locked.current) return; locked.current = true; setBusy(true); setError("");
      try { const team = await competitionsApi.createTeam(newTeam); setTeams((rows) => [...rows, team]); setSelected((rows) => [...rows, team.id]); setNewTeam(""); }
      catch (reason) { setError(competitionError(reason)); }
      finally { locked.current = false; setBusy(false); }
    }}><label className="block">Nova equipa adversária<input className="form-field mt-1" required disabled={busy} maxLength={120} value={newTeam} onChange={(e) => setNewTeam(e.target.value)} /></label>
      <SecondaryButton type="submit" disabled={busy}>Adicionar equipa à seleção</SecondaryButton>
    </form>
    {error && <ErrorNotice message={error} />}
  </section>;
}
