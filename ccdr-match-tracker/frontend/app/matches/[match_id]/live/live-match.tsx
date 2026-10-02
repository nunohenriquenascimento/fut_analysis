"use client";

import { useAuth } from "@/components/auth-provider";

import Link from "next/link";
import { PageContainer } from "@/components/ui";
import { useCallback, useEffect, useRef, useState } from "react";
import { useLiveSocket } from "@/lib/use-live-socket";
import { ApiError } from "@/lib/api";
import { PrimaryButton, SecondaryButton, DangerButton, LoadingState, SectionHeader } from "@/components/ui";
import MatchScoreboard from "@/components/match-scoreboard";
import { EVENT_LABELS, NEXT_ACTION, formatClock, liveApi, timelineText, type EventFields, type EventTeam, type EventType, type LiveState, type MatchEvent } from "@/lib/live";
import EventDialog, { DeleteDialog } from "./event-dialog";

const EVENT_GROUPS: { title: string; events: EventType[] }[] = [
  { title: "Ofensivos", events: ["GOAL", "SHOT_ON_TARGET", "SHOT_OFF_TARGET", "SHOT_BLOCKED", "OFFSIDE"] },
  { title: "Bolas paradas", events: ["CORNER", "FREE_KICK", "PENALTY"] },
  { title: "Disciplina", events: ["FOUL", "YELLOW_CARD", "RED_CARD"] },
  { title: "Defensivos", events: ["OWN_GOAL", "SAVE"] },
  { title: "Substituição", events: ["SUBSTITUTION"] },
];
const QUICK = new Set<EventType>(["CORNER", "FREE_KICK", "PENALTY"]);
function errorText(error: unknown) {
  if (error instanceof ApiError) return error.status === 422 ? "Verifique os dados do evento." : error.message;
  return "Não foi possível contactar o servidor. Recarregue o estado antes de repetir a gravação.";
}

function Clock({ state }: { state: LiveState }) {
  const [seconds, setSeconds] = useState(state.clock_elapsed_seconds);
  useEffect(() => {
    const anchor = performance.now();
    const running = state.match.status === "FIRST_HALF" || state.match.status === "SECOND_HALF";
    // Backend timestamp supplies the snapshot; monotonic browser time only interpolates it.
    const serverNow = Date.parse(state.server_now);
    const start = state.match.clock_started_at ? Date.parse(state.match.clock_started_at) : serverNow;
    const base = running ? state.match.elapsed_seconds + Math.max(0, Math.floor((serverNow - start) / 1000)) : state.clock_elapsed_seconds;
    const tick = () => setSeconds(base + (running ? Math.floor((performance.now() - anchor) / 1000) : 0));
    tick();
    const timer = window.setInterval(tick, 250);
    return () => window.clearInterval(timer);
  }, [state]);
  return <p aria-label="Cronómetro" className="font-mono text-5xl font-bold tabular-nums">{formatClock(seconds)}</p>;
}

export default function LiveMatch({ matchId }: { matchId: number }) {
  const { canEdit } = useAuth();
  const [state, setState] = useState<LiveState | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [draft, setDraft] = useState<(EventFields & { id?: number }) | null>(null);
  const [deleting, setDeleting] = useState<MatchEvent | null>(null);
  const [reload, setReload] = useState(0);
  const locked = useRef(false);
  const generation = useRef(0);
  const refreshing = useRef(false);
  const pending = useRef(false);
  const mounted = useRef(false);
  const [syncError, setSyncError] = useState("");
  const invalidate = useCallback(() => { generation.current++; }, []);

  const refreshRealtime = useCallback(async () => {
    pending.current = true;
    if (refreshing.current || locked.current || !mounted.current) return;
    refreshing.current = true;
    try {
      while (pending.current && !locked.current && mounted.current) {
        pending.current = false;
        const version = ++generation.current;
        try {
          const current = await liveApi.get(matchId);
          if (mounted.current && version === generation.current && !locked.current) { setState(current); setSyncError(""); }
        } catch (reason) {
          if (mounted.current && version === generation.current) {
            if (reason instanceof ApiError && reason.status === 404) { setState(null); setError("Jogo não encontrado."); }
            else setSyncError("Não foi possível atualizar o estado em tempo real. Use Atualizar estado para tentar novamente.");
          }
          break;
        }
      }
    } finally { refreshing.current = false; }
  }, [matchId]);
  const socketStatus = useLiveSocket(matchId, () => void refreshRealtime());

  useEffect(() => {
    mounted.current = true;
    let cancelled = false;
    const version = ++generation.current;
    async function load() {
      try {
        if (!Number.isInteger(matchId) || matchId < 1 || matchId > 2147483647) { if (!cancelled) setError("Jogo não encontrado."); return; }
        const current = await liveApi.get(matchId);
        if (!cancelled && version === generation.current) { setState(current); setError(""); setSyncError(""); }
      } catch (reason) { if (!cancelled) setError(errorText(reason)); }
      finally { if (!cancelled) setLoading(false); }
    }
    void load();
    return () => { cancelled = true; mounted.current = false; invalidate(); };
  }, [matchId, reload, invalidate]);

  async function mutate(operation: () => Promise<LiveState>, message: string) {
    if (locked.current || loading) return;
    locked.current = true; setBusy(true); setError(""); setNotice("");
    generation.current++;
    try {
      setState(await operation()); setDraft(null); setDeleting(null); setNotice(message);
    } catch (reason) { setError(errorText(reason)); }
    finally { locked.current = false; setBusy(false); if (pending.current) void refreshRealtime(); }
  }

  function selectEvent(event_type: EventType, team: EventTeam) {
    const fields: EventFields = { event_type, team, player_id: null, related_player_id: null };
    setError(""); setNotice("");
    if (team === "OPPONENT" || QUICK.has(event_type)) void mutate(() => liveApi.createEvent(matchId, fields), "Evento registado.");
    else setDraft(fields);
  }

  const running = state?.match.status === "FIRST_HALF" || state?.match.status === "SECOND_HALF";
  const action = state ? NEXT_ACTION[state.match.status] : undefined;
  return <PageContainer className="live-page">
    <div className="page-content space-y-6">
      <Link href={`/matches/${matchId}`} className="inline-flex min-h-11 items-center text-sm text-muted">← Detalhe do jogo</Link>
      {loading && <LoadingState>A carregar o jogo ao vivo…</LoadingState>}
      <p role="status" className="text-sm text-muted" aria-label="Ligação em tempo real">{socketStatus === "connected" ? "🟢 Tempo real ligado" : socketStatus === "reconnecting" ? "🟡 A reconectar" : "🔴 Sem tempo real"}</p>
      {syncError && <p className="text-sm text-warning">{syncError}</p>}
      {error && !draft && !deleting && <p role="alert" className="rounded-xl border border-error p-3 text-error">{error}</p>}
      <SecondaryButton disabled={loading || busy || !!draft || !!deleting} onClick={() => { setLoading(true); setNotice(""); setReload((value) => value + 1); }}>Atualizar estado</SecondaryButton>
      {state && <>
        <header className="live-scorecard sticky top-0 z-10 rounded-2xl border border-border p-3 text-center">
          <h1 className="sr-only">Jogo ao Vivo · {state.match.opponent_name}</h1>
          <MatchScoreboard match={state.match} score={state.score}><Clock state={state} /></MatchScoreboard>
        </header>
        {canEdit && action && <PrimaryButton disabled={loading || busy} onClick={() => void mutate(() => liveApi.transition(matchId, action.status), "Estado do jogo atualizado.")} className="w-full">{busy ? "A guardar…" : action.label}</PrimaryButton>}
        {notice && <p role="status" className="text-sm text-success">{notice}</p>}
        {!running && <p className="text-sm text-muted">O registo de novos acontecimentos está disponível durante as partes em curso.</p>}
        {canEdit && <div className="grid grid-cols-2 gap-2">
          {(["US", "OPPONENT"] as EventTeam[]).map((team) => <section key={team} aria-label={team === "US" ? "Nossa equipa" : "Adversário"} className="min-w-0">
            <h2 className="mb-2 text-center text-xs font-bold tracking-wide">{team === "US" ? "NOSSA EQUIPA" : "ADVERSÁRIO"}</h2>
            {EVENT_GROUPS.filter((group) => team === "US" || group.title !== "Substituição").map((group) => <div className="event-group" key={group.title}>
              <h3>{group.title}</h3><div className="grid grid-cols-2 gap-1.5">
              {group.events.map((type) => <button key={type} type="button" disabled={!running || busy || loading}
                onClick={() => selectEvent(type, team)} className={`min-h-16 rounded-xl px-1 text-xs font-semibold disabled:opacity-40 ${group.events.length === 1 ? "col-span-2" : ""} ${team === "US" ? "event-button-us" : "event-button-opponent"}`}>
                {EVENT_LABELS[type]}
              </button>)}
              </div></div>)}
          </section>)}
        </div>}
        <section aria-labelledby="timeline-title" className="space-y-3 pb-8">
          <SectionHeader id="timeline-title">Acontecimentos</SectionHeader>
          {state.events.length === 0 && <p className="text-muted">Ainda não existem acontecimentos.</p>}
          <ol className="space-y-3">
            {[...state.events].sort((a, b) => a.period - b.period || a.elapsed_seconds - b.elapsed_seconds || a.id - b.id).map((event) => <li key={event.id} className="timeline-item rounded-xl border border-border p-3">
              <div className="flex items-center gap-3"><span className="timeline-marker">{Math.floor(event.elapsed_seconds / 60)}′</span><div><p className="text-xs text-muted">{event.period}.ª parte · {formatClock(event.elapsed_seconds)}</p><p className="text-xs font-semibold text-secondary">{event.team === "US" ? "Nossa equipa" : "Adversário"} · {EVENT_LABELS[event.event_type]}</p></div></div>
              <p className="mt-1 break-words text-sm">{timelineText(event, state.squad)}</p>
              {event.notes && <p className="mt-1 text-sm text-muted">{event.notes}</p>}
              {canEdit && <div className="mt-2 grid grid-cols-2 gap-2">
                <SecondaryButton disabled={busy || loading} onClick={() => { setError(""); setDraft(event); }}>Editar</SecondaryButton>
                <DangerButton disabled={busy || loading} onClick={() => { setError(""); setDeleting(event); }}>Eliminar</DangerButton>
              </div>}
            </li>)}
          </ol>
        </section>
        {canEdit && draft && <EventDialog initial={draft} squad={state.squad} busy={busy} error={error} onClose={() => { setDraft(null); setError(""); }} onSave={(fields) => mutate(
          () => draft.id ? liveApi.updateEvent(matchId, draft.id, fields) : liveApi.createEvent(matchId, fields), draft.id ? "Evento atualizado." : "Evento registado.",
        )} />}
        {canEdit && deleting && <DeleteDialog event={deleting} busy={busy} error={error} onClose={() => { setDeleting(null); setError(""); }} onConfirm={() => void mutate(() => liveApi.deleteEvent(matchId, deleting.id), "Evento eliminado.")} />}
      </>}
    </div>
  </PageContainer>;
}
