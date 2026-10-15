"use client";

import { useEffect, useRef, useState } from "react";
import { competitionsApi, competitionError, type CompetitionTeam, type ParticipantsPlan } from "@/lib/competitions";
import { LoadingState, PrimaryButton, SecondaryButton } from "@/components/ui";
import { ErrorNotice } from "./competition-ui";

export default function ParticipantsForm({ competitionId, internalTeamId, initial, onSaved }: {
  competitionId: number; internalTeamId: number; initial: CompetitionTeam[]; onSaved: (teams: CompetitionTeam[]) => void;
}) {
  const [available, setAvailable] = useState<CompetitionTeam[]>([]), [current, setCurrent] = useState(initial);
  const [selected, setSelected] = useState(initial.map((team) => team.id));
  const [plan, setPlan] = useState<ParticipantsPlan | null>(null), [confirmation, setConfirmation] = useState("");
  const [loading, setLoading] = useState(true), [busy, setBusy] = useState(false);
  const [error, setError] = useState(""), [success, setSuccess] = useState("");
  const [reload, setReload] = useState(0);
  const locked = useRef(false);
  useEffect(() => {
    let active = true;
    Promise.all([competitionsApi.teams(), competitionsApi.participants(competitionId)]).then(([all, members]) => {
      if (active) { setAvailable(all); setCurrent(members); setSelected(members.map((team) => team.id)); setError(""); }
    }).catch((reason) => { if (active) setError(competitionError(reason)); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [competitionId, reload]);
  const selection = { team_ids: selected, expected_team_ids: current.map((team) => team.id) };
  return <section className="card space-y-4" aria-label="Gestão de participantes">
    <h2 className="section-header">Gerir participantes · ADMIN</h2>
    <p className="text-sm text-muted">Reveja e confirme as alterações antes de gravar. Retirar uma participação não elimina a equipa. Jogos dependentes impedem a remoção.</p>
    {loading ? <LoadingState>A carregar equipas disponíveis…</LoadingState> : <>
      <SecondaryButton disabled={busy} onClick={() => { setPlan(null); setConfirmation(""); setSuccess(""); setLoading(true); setReload((n) => n + 1); }}>Atualizar lista de participantes</SecondaryButton>
      <fieldset disabled={busy} className="space-y-3"><legend className="font-semibold mb-2">Participantes selecionados ({selected.length})</legend>
        <div className="grid gap-2 sm:grid-cols-2">{available.map((team) => <label key={team.id} className="participant-option">
          <input type="checkbox" disabled={team.id === internalTeamId} checked={selected.includes(team.id)} onChange={(event) => {
            setSelected((ids) => event.target.checked ? [...ids, team.id] : ids.filter((id) => id !== team.id));
            setPlan(null); setConfirmation(""); setError(""); setSuccess("");
          }} /><span>{team.name}{team.id === internalTeamId && " · Nossa equipa"}</span>
        </label>)}</div>
        <PrimaryButton onClick={async () => {
          if (locked.current) return; locked.current = true; setBusy(true); setError(""); setSuccess(""); setPlan(null); setConfirmation("");
          try { setPlan(await competitionsApi.previewParticipants(competitionId, selection)); }
          catch (reason) { setError(competitionError(reason)); }
          finally { locked.current = false; setBusy(false); }
        }}>{busy ? "A verificar…" : "Rever alteração de participantes"}</PrimaryButton>
      </fieldset>
      {plan && <div className="border-t border-border pt-4 space-y-3">
        <h3 className="font-bold">Revisão de participantes</h3>
        <p>Adicionar: {plan.added.map((team) => team.name).join(", ") || "Nenhuma equipa"}</p>
        <p>Retirar: {plan.removed.map((team) => team.name).join(", ") || "Nenhuma equipa"}</p>
        {plan.conflicts.map((conflict) => <p key={conflict} role="alert" className="text-error">{conflict}</p>)}
        {plan.can_apply && plan.added.length + plan.removed.length > 0 && <>
          <label className="block">Escreva ALTERAR PARTICIPANTES para confirmar<input className="form-field mt-1" disabled={busy} value={confirmation} onChange={(event) => setConfirmation(event.target.value)} autoComplete="off" /></label>
          <PrimaryButton disabled={busy || confirmation !== "ALTERAR PARTICIPANTES"} onClick={async () => {
            if (locked.current) return; locked.current = true; setBusy(true); setError("");
            try {
              const teams = await competitionsApi.updateParticipants(competitionId, { ...selection, confirmation: "ALTERAR PARTICIPANTES" });
              setCurrent(teams); setSelected(teams.map((team) => team.id)); onSaved(teams); setPlan(null); setConfirmation(""); setSuccess("Participantes atualizados.");
            } catch (reason) { setError(competitionError(reason)); setPlan(null); setConfirmation(""); }
            finally { locked.current = false; setBusy(false); }
          }}>{busy ? "A guardar…" : "Confirmar alteração de participantes"}</PrimaryButton>
        </>}
      </div>}
    </>}
    {error && <ErrorNotice message={error} />}{success && <p role="status" className="text-success">{success}</p>}
  </section>;
}
