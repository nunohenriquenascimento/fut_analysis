"use client";

import { useEffect, useRef, useState } from "react";
import { api, ApiError, type Match } from "@/lib/api";
import { mergeApi, type MergeGame, type MergePreview, type MergeStatus } from "@/lib/merge";
import { EVENT_LABELS, formatClock, timelineText } from "@/lib/live";
import { MATCH_STATUS, matchDate, matchError } from "@/lib/matches";
import { DangerButton, SecondaryButton } from "@/components/ui";

function GameSummary({ game, title }: { game: MergeGame; title: string }) {
  return <section className="min-w-0 rounded-xl border border-border p-3" aria-label={title}>
    <h3 className="font-bold">{title} #{game.match.id}</h3>
    <p>{game.match.opponent_name} · Jornada {game.match.matchday ?? "por definir"}</p>
    <p className="text-sm">{matchDate(game.match.kickoff_at)} · {game.match.is_home ? "Casa" : "Fora"} · {game.match.venue ?? "Local por definir"}</p>
    <p>{MATCH_STATUS[game.match.status]} · {game.score.us} – {game.score.opponent}</p>
    <p>{formatClock(game.elapsed_seconds)} ({game.elapsed_seconds} s) · {game.period ?? "—"}.ª parte · {game.event_count} eventos</p>
    <h4 className="mt-2 font-semibold">Convocatória</h4>
    <ul className="text-sm">{game.squad.map(row => <li key={row.id}>{row.player.name} · {row.is_starter ? "Titular" : "Suplente"}</li>)}</ul>
    {!game.squad.length && <p className="text-sm text-muted">Sem convocados.</p>}
  </section>;
}

export default function MergeDialog({ principal, onClose, onMerged }: {
  principal: Match; onClose: () => void; onMerged: (id: number) => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const locked = useRef(false);
  const [candidates, setCandidates] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [continuation, setContinuation] = useState("");
  const [finalStatus, setFinalStatus] = useState<MergeStatus>("FINISHED");
  const [preview, setPreview] = useState<MergePreview | null>(null);
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);
  useEffect(() => { dialog.current?.showModal(); }, []);
  useEffect(() => {
    let active = true;
    api.seasonMatches(principal).then(rows => {
      if (active) { setCandidates(rows.filter(row => row.id !== principal.id)); setError(""); }
    }).catch(reason => { if (active) setError(matchError(reason)); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [principal, retry]);
  const selection = { principal_id: principal.id, continuation_id: Number(continuation), final_status: finalStatus };
  function invalidate() { setPreview(null); setConfirmation(""); setError(""); }
  async function getPreview() {
    if (locked.current || !continuation) return;
    locked.current = true; setBusy(true); invalidate();
    try { setPreview(await mergeApi.preview(selection)); }
    catch (reason) { setError(matchError(reason)); }
    finally { locked.current = false; setBusy(false); }
  }
  async function execute() {
    if (locked.current || !preview?.can_merge || !preview.preview_token || confirmation !== "UNIR JOGOS") return;
    locked.current = true; setBusy(true); setError("");
    try {
      const result = await mergeApi.execute(selection, preview.preview_token, confirmation);
      onMerged(result.match.id);
    } catch (reason) {
      setError(matchError(reason));
      if (reason instanceof ApiError && [404, 409].includes(reason.status)) { setPreview(null); setConfirmation(""); }
    } finally { locked.current = false; setBusy(false); }
  }
  return <dialog ref={dialog} aria-labelledby="merge-title" aria-describedby="merge-description"
    onCancel={event => { event.preventDefault(); if (!busy) onClose(); }}
    className="fixed inset-0 m-auto max-h-[90dvh] w-[calc(100%-2rem)] max-w-3xl overflow-y-auto rounded-2xl border border-border bg-background p-4 text-foreground backdrop:bg-overlay">
    <h2 id="merge-title" className="text-xl font-bold">Unir jogo de continuação</h2>
    <p id="merge-description" className="my-3 text-sm">O jogo principal #{principal.id} será mantido. Os eventos e o tempo da continuação serão incorporados; o registo da continuação será eliminado. Revê o preview antes de confirmar.</p>
    <fieldset disabled={busy || loading} className="space-y-4">
      <p className="text-sm font-semibold">Principal: #{principal.id} · {principal.opponent_name} · Jornada {principal.matchday ?? "—"}</p>
      <label className="block text-sm">Jogo de continuação<select className="form-field mt-2" value={continuation} onChange={event => { setContinuation(event.target.value); invalidate(); }}>
        <option value="">Selecionar jogo da mesma equipa e época</option>
        {candidates.map(game => <option key={game.id} value={game.id}>#{game.id} · {game.opponent_name} · J{game.matchday ?? "—"} · {matchDate(game.kickoff_at)} · {MATCH_STATUS[game.status]}</option>)}
      </select></label>
      <label className="block text-sm">Estado final<select className="form-field mt-2" value={finalStatus} onChange={event => { setFinalStatus(event.target.value as MergeStatus); invalidate(); }}>
        <option value="FINISHED">FINISHED — jogo terminado</option>
        <option value="SECOND_HALF">SECOND_HALF — 2.ª parte com relógio parado</option>
      </select></label>
      <SecondaryButton disabled={!continuation || busy || loading} onClick={() => void getPreview()} className="w-full">{busy ? "A processar…" : "Obter preview"}</SecondaryButton>
    </fieldset>
    {loading && <p role="status" className="my-3">A carregar jogos…</p>}
    {error && <div role="alert" className="my-3 text-error"><p>{error}</p>{!candidates.length && !loading && <SecondaryButton onClick={() => { setLoading(true); setRetry(value => value + 1); }}>Tentar novamente</SecondaryButton>}</div>}
    {preview && <section aria-label="Preview da união" className="my-4 space-y-4">
      <div className="grid gap-3 sm:grid-cols-2"><GameSummary game={preview.principal} title="Jogo principal" /><GameSummary game={preview.continuation} title="Jogo continuação" /></div>
      {!!preview.conflicts.length && <div role="alert" className="rounded-xl border border-error p-3"><h3 className="font-bold">Conflitos que impedem a união</h3><ul className="list-disc pl-5">{preview.conflicts.map((message, index) => <li key={index}>{message}</li>)}</ul></div>}
      {!!preview.warnings.length && <div className="rounded-xl border border-warning p-3"><h3 className="font-bold">Avisos — confirma antes de unir</h3><ul className="list-disc pl-5">{preview.warnings.map((message, index) => <li key={index}>{message}</li>)}</ul></div>}
      <p className="font-semibold">Resultado previsto: {preview.predicted_score.us} – {preview.predicted_score.opponent}</p>
      <p>Tempo final previsto: {formatClock(preview.predicted_elapsed_seconds)} ({preview.predicted_elapsed_seconds} s). {preview.final_status === "FINISHED" ? "Jogo terminado." : "2.ª parte com cronómetro parado."}</p>
      <section aria-label="Jogadores apenas na continuação"><h3 className="font-bold">Jogadores apenas na continuação</h3><p className="text-sm">Serão incorporados com a função histórica da continuação. Nos jogadores comuns prevalece a função do principal.</p>
        <ul>{preview.continuation_only_players.map(row => <li key={row.id}>{row.player.name} · {row.is_starter ? "Titular" : "Suplente"}</li>)}</ul>
        {!preview.continuation_only_players.length && <p>Nenhum.</p>}
      </section>
      <section aria-label="Eventos a transferir"><h3 className="font-bold">Eventos a transferir ({preview.transfers.length})</h3>
        <ol className="space-y-3">{preview.transfers.map(row => <li key={row.original.id} className="break-words rounded-xl border border-border p-3 text-sm">
          <p>#{row.original.id} · {EVENT_LABELS[row.original.event_type]} · {timelineText(row.original, preview.continuation.squad.map(entry => entry.player))}</p>
          <p>{row.original.period}.ª parte · {formatClock(row.original.elapsed_seconds)} → {row.new_period}.ª parte · {formatClock(row.new_elapsed_seconds)}</p>
          <p>{row.original.elapsed_seconds} s → {row.new_elapsed_seconds} s · Autor: {row.original.recorded_by_id ?? "não registado"}</p>
          {row.original.notes && <p>{row.original.notes}</p>}
        </li>)}</ol>
      </section>
      {preview.can_merge && preview.preview_token && <label className="block text-sm">Escreve UNIR JOGOS para confirmar este preview e os avisos<input disabled={busy} className="form-field mt-2" autoComplete="off" spellCheck={false} value={confirmation} onChange={event => setConfirmation(event.target.value)} /></label>}
      <DangerButton disabled={busy || !preview.can_merge || !preview.preview_token || confirmation !== "UNIR JOGOS"} onClick={() => void execute()} className="w-full">{busy ? "A unir…" : "Confirmar união dos jogos"}</DangerButton>
    </section>}
    <SecondaryButton disabled={busy} autoFocus onClick={onClose} className="mt-3 w-full">Voltar ao jogo</SecondaryButton>
  </dialog>;
}
