"use client";

import { DangerButton, PrimaryButton, SecondaryButton } from "@/components/ui";

import { useEffect, useRef, useState, type FormEvent } from "react";
import type { Player } from "@/lib/api";
import { PlayerAvatar } from "@/components/media";
import { EVENT_LABELS, type EventFields, type EventTeam, type EventType, type MatchEvent } from "@/lib/live";

export default function EventDialog({ initial, squad, busy, error, onSave, onClose }: {
  initial: EventFields & { id?: number }; squad: Player[]; busy: boolean; error: string;
  onSave: (fields: EventFields) => Promise<void>; onClose: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [type, setType] = useState(initial.event_type);
  const [team, setTeam] = useState(initial.team);
  const [player, setPlayer] = useState(initial.player_id?.toString() ?? "");
  const [related, setRelated] = useState(initial.related_player_id?.toString() ?? "");
  useEffect(() => { dialog.current?.showModal(); }, []);
  const own = team === "US";
  const goal = type === "GOAL";
  const substitution = type === "SUBSTITUTION";
  const selectedPlayer = squad.find((row) => String(row.id) === player);
  const relatedPlayer = squad.find((row) => String(row.id) === related);
  const inputClass = "form-field mt-2";
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    await onSave({ event_type: type, team, player_id: own && player ? Number(player) : null,
      related_player_id: own && (goal || substitution) && related ? Number(related) : null,
      notes: initial.notes ?? null });
  }
  return <dialog ref={dialog} onCancel={(event) => { event.preventDefault(); if (!busy) onClose(); }} aria-labelledby="event-dialog-title"
    className="fixed inset-0 m-auto max-h-[90dvh] w-[calc(100%-2rem)] max-w-md overflow-y-auto rounded-2xl border border-border bg-background p-5 text-foreground backdrop:bg-overlay">
    <h2 id="event-dialog-title" className="mb-4 text-xl font-bold">{initial.id ? "Editar evento" : EVENT_LABELS[type]}</h2>
    <form onSubmit={submit}>
      <fieldset disabled={busy} className="space-y-4 disabled:opacity-60">
        {initial.id && <>
          <label className="block text-sm">Tipo de evento<select value={type} onChange={(e) => { setType(e.target.value as EventType); setRelated(""); }} className={inputClass}>
            {Object.entries(EVENT_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select></label>
          <label className="block text-sm">Equipa<select value={team} onChange={(e) => { setTeam(e.target.value as EventTeam); setPlayer(""); setRelated(""); }} className={inputClass}>
            <option value="US">Nossa equipa</option><option value="OPPONENT">Adversário</option>
          </select></label>
        </>}
        {own && <label className="block text-sm">{substitution ? "Jogador que sai" : goal ? "Marcador" : "Jogador (opcional)"}
          <select required={goal || substitution} value={player} onChange={(e) => setPlayer(e.target.value)} className={inputClass}>
            <option value="">{goal || substitution ? "Selecionar convocado" : "Sem jogador"}</option>
            {squad.map((row) => <option key={row.id} value={row.id}>{row.shirt_number ?? "—"} · {row.name}</option>)}
          </select>
        </label>}
        {own && selectedPlayer && <div className="flex items-center gap-3"><PlayerAvatar name={selectedPlayer.name} photoPath={selectedPlayer.photo_path} number={selectedPlayer.shirt_number} /><p className="min-w-0 text-sm">{selectedPlayer.name} · {selectedPlayer.position}</p></div>}
        {own && (goal || substitution) && <label className="block text-sm">{substitution ? "Jogador que entra" : "Assistência (opcional)"}
          <select required={substitution} value={related} onChange={(e) => setRelated(e.target.value)} className={inputClass}>
            <option value="">{substitution ? "Selecionar convocado" : "Sem assistência"}</option>
            {squad.map((row) => <option key={row.id} value={row.id} disabled={row.id.toString() === player}>{row.shirt_number ?? "—"} · {row.name}</option>)}
          </select>
        </label>}
        {own && (goal || substitution) && relatedPlayer && <div className="flex items-center gap-3"><PlayerAvatar name={relatedPlayer.name} photoPath={relatedPlayer.photo_path} number={relatedPlayer.shirt_number} /><p className="min-w-0 text-sm">{relatedPlayer.name} · {relatedPlayer.position}</p></div>}
        {own && squad.length === 0 && <p className="text-warning">Não existem convocados. Configure a convocatória no detalhe do jogo.</p>}
        {error && <p role="alert" className="text-error">{error}</p>}
        <PrimaryButton type="submit" className="w-full">{busy ? "A guardar…" : "Guardar evento"}</PrimaryButton>
        <SecondaryButton type="button" onClick={onClose} className="w-full">Cancelar</SecondaryButton>
      </fieldset>
    </form>
  </dialog>;
}

export function DeleteDialog({ event, busy, error, onConfirm, onClose }: {
  event: MatchEvent; busy: boolean; error: string; onConfirm: () => void; onClose: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => { dialog.current?.showModal(); }, []);
  return <dialog ref={dialog} onCancel={(e) => { e.preventDefault(); if (!busy) onClose(); }} aria-labelledby="delete-title" className="fixed inset-0 m-auto w-[calc(100%-2rem)] max-w-md rounded-2xl border border-border bg-background p-5 text-foreground backdrop:bg-overlay">
    <h2 id="delete-title" className="text-xl font-bold">Eliminar evento?</h2>
    <p className="my-4">{EVENT_LABELS[event.event_type]} · {event.team === "US" ? "Nossa equipa" : "Adversário"}. O resultado será recalculado.</p>
    {error && <p role="alert" className="mb-4 text-error">{error}</p>}
    <DangerButton type="button" disabled={busy} onClick={onConfirm} className="w-full">{busy ? "A eliminar…" : "Confirmar eliminação"}</DangerButton>
    <SecondaryButton type="button" disabled={busy} onClick={onClose} className="w-full mt-3">Cancelar</SecondaryButton>
  </dialog>;
}
