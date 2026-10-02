"use client";

import { PrimaryButton, SecondaryButton } from "@/components/ui";

import { useState, type FormEvent } from "react";
import type { Match, MatchCreate } from "@/lib/api";
import { localDateFields } from "@/lib/matches";

export type MatchFields = Omit<MatchCreate, "season_id" | "team_id">;
const inputClass = "form-field mt-2";

export default function MatchForm({ match, busy, onSave, onCancel }: {
  match?: Match; busy: boolean; onSave: (fields: MatchFields) => Promise<void>; onCancel: () => void;
}) {
  const [matchday, setMatchday] = useState(match?.matchday?.toString() ?? "");
  const [opponent, setOpponent] = useState(match?.opponent_name ?? "");
  const initialDate = localDateFields(match?.kickoff_at);
  const [date, setDate] = useState(initialDate.date);
  const [time, setTime] = useState(initialDate.time);
  const [home, setHome] = useState(match?.is_home ?? true);
  const [venue, setVenue] = useState(match?.venue ?? "");
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const number = Number(matchday);
    const kickoff = new Date(`${date}T${time}`);
    const parsed = Number.isNaN(kickoff.getTime()) ? null : localDateFields(kickoff.toISOString());
    if (!Number.isInteger(number) || number < 1 || number > 2147483647 || !opponent.trim() || !parsed || parsed.date !== date || parsed.time !== time) {
      setError("Indique uma jornada positiva, adversário, data e hora válidos.");
      return;
    }
    setError("");
    await onSave({ matchday: number, opponent_name: opponent.trim(), kickoff_at: kickoff.toISOString(),
      is_home: home, venue: venue.trim() || null });
  }

  return <form onSubmit={submit} aria-label={match ? "Editar jogo" : "Criar jogo"} className="rounded-2xl border border-border bg-surface p-5">
    <h2 className="mb-4 text-xl font-semibold">{match ? "Editar jogo" : "Criar jogo"}</h2>
    <fieldset disabled={busy} className="min-w-0 space-y-4 disabled:opacity-60">
      <label className="block text-sm">Jornada
        <input className={inputClass} type="number" inputMode="numeric" min={1} max={2147483647} step={1} required value={matchday} onChange={(e) => setMatchday(e.target.value)} />
      </label>
      <label className="block text-sm">Adversário
        <input className={inputClass} maxLength={160} required value={opponent} onChange={(e) => setOpponent(e.target.value)} />
      </label>
      <label className="block text-sm">Data
        <input className={inputClass} type="date" required value={date} onChange={(e) => setDate(e.target.value)} />
      </label>
      <label className="block text-sm">Hora (fuso do dispositivo)
        <input className={inputClass} type="time" required value={time} onChange={(e) => setTime(e.target.value)} />
      </label>
      <label className="block text-sm">Casa ou fora
        <select className={inputClass} value={home ? "home" : "away"} onChange={(e) => setHome(e.target.value === "home")}>
          <option value="home">Casa</option><option value="away">Fora</option>
        </select>
      </label>
      <label className="block text-sm">Local
        <input className={inputClass} maxLength={160} value={venue} onChange={(e) => setVenue(e.target.value)} />
      </label>
      {error && <p role="alert" className="text-error">{error}</p>}
      <PrimaryButton className="w-full" type="submit">{busy ? "A guardar…" : match ? "Guardar jogo" : "Criar jogo"}</PrimaryButton>
      <SecondaryButton className="w-full" type="button" onClick={onCancel}>Cancelar</SecondaryButton>
    </fieldset>
  </form>;
}
