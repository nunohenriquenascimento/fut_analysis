"use client";

import { useAuth } from "@/components/auth-provider";

import { DangerButton, PrimaryButton, SecondaryButton } from "@/components/ui";
import { useRouter } from "next/navigation";
import ManagementDialog from "./management-dialog";

import Link from "next/link";
import { PageContainer } from "@/components/ui";
import { useEffect, useRef, useState } from "react";
import { api, ApiError, type Match, type SquadPlayer, type SquadRole } from "@/lib/api";
import { matchDate, matchError } from "@/lib/matches";
import { PlayerAvatar } from "@/components/media";
import { StatusBadge, SectionHeader, LoadingState } from "@/components/ui";
import MatchScoreboard from "@/components/match-scoreboard";
import MatchForm, { type MatchFields } from "../match-form";

export default function MatchDetail({ matchId }: { matchId: number }) {
  const { canEdit, isAdmin } = useAuth();
  const router = useRouter();
  const [management, setManagement] = useState<"delete" | "cancel" | "force" | null>(null);
  const [managementError, setManagementError] = useState("");
  const [match, setMatch] = useState<Match | null>(null);
  const [squad, setSquad] = useState<SquadPlayer[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [editing, setEditing] = useState(false);
  const [reload, setReload] = useState(0);
  const locked = useRef(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        if (!Number.isInteger(matchId) || matchId < 1 || matchId > 2147483647) throw new Error("invalid id");
        const [game, rows] = await Promise.all([api.match(matchId), api.squad(matchId)]);
        if (!cancelled) { setMatch(game); setSquad(rows); setLoadError(""); }
      } catch (reason) {
        if (!cancelled) setLoadError(!Number.isInteger(matchId) || matchId < 1 || matchId > 2147483647 ? "Jogo não encontrado." : matchError(reason));
      } finally { if (!cancelled) setLoading(false); }
    }
    void load();
    return () => { cancelled = true; };
  }, [matchId, reload]);

  async function mutate(operation: () => Promise<void>, message: string) {
    if (locked.current || loading) return;
    locked.current = true; setBusy(true); setError(""); setNotice("");
    try { await operation(); setNotice(message); }
    catch (reason) { setError(matchError(reason)); }
    finally { locked.current = false; setBusy(false); }
  }

  async function saveMatch(fields: MatchFields) {
    await mutate(async () => { await api.updateMatch(matchId, fields); setMatch(await api.match(matchId)); setEditing(false); }, "Jogo atualizado.");
  }

  async function saveSquad() {
    await mutate(async () => {
      const selected = squad.filter((row) => row.role !== "NAO_CONVOCADO")
        .map((row) => ({ player_id: row.player.id, is_starter: row.role === "TITULAR" }));
      setSquad(await api.saveSquad(matchId, selected));
      setMatch(await api.match(matchId));
    }, "Convocatória guardada.");
  }

  function choose(playerId: number, role: SquadRole) {
    setSquad((rows) => rows.map((row) => row.player.id === playerId ? { ...row, role } : row));
    setNotice(""); setError("");
  }

  async function confirmManagement() {
    if (!management || locked.current || loading) return;
    locked.current = true; setBusy(true); setManagementError(""); setNotice("");
    try {
      if (management === "delete" || management === "force") {
        if (management === "force") await api.forceDeleteMatch(matchId);
        else await api.deleteMatch(matchId);
        setManagement(null); setMatch(null);
        router.replace("/matches");
      } else {
        setMatch(await api.cancelMatch(matchId));
        setManagement(null); setNotice("Jogo cancelado. O histórico foi preservado.");
      }
    } catch (reason) {
      setManagementError(reason instanceof ApiError && reason.status === 409 && management === "delete"
        ? "O jogo já não pode ser eliminado com segurança. Recarregue o detalhe e use Cancelar jogo para preservar o histórico."
        : matchError(reason));
      if (reason instanceof ApiError && reason.status === 409) {
        try { setMatch(await api.match(matchId)); } catch { /* Keep the failure and current detail visible. */ }
      }
    } finally { locked.current = false; setBusy(false); }
  }

  const starters = squad.filter((row) => row.role === "TITULAR").length;
  const substitutes = squad.filter((row) => row.role === "SUPLENTE").length;

  return <PageContainer className="">
    <div className="page-content space-y-6">
      <Link href="/matches" className="inline-flex min-h-11 items-center text-sm text-muted">← Jogos</Link>
      {loading && <LoadingState>A carregar o jogo…</LoadingState>}
      {loadError && <div role="alert" className="rounded-xl border border-error p-4 text-error">
        <p>{loadError}</p><SecondaryButton disabled={loading} className="" onClick={() => { setLoading(true); setReload((n) => n + 1); }}>Tentar novamente</SecondaryButton>
      </div>}
      {match && <>
        <header className="card match-sheet">
          <p className="matchday-label">{match.matchday === null ? "Jornada por definir" : `Jornada ${match.matchday}`}</p>
          <h1 className="sr-only">{match.opponent_name}</h1>
          <MatchScoreboard match={match} score={match.status === "SCHEDULED" ? undefined : match.score} />
          <p className="mt-3">{matchDate(match.kickoff_at)}</p>
          <p className="mt-1 text-muted">{match.is_home ? "Casa" : "Fora"} · {match.venue ?? "Local por definir"}</p>
        </header>
        <div className="grid gap-3 sm:grid-cols-2"><Link href={`/matches/${matchId}/stats`} className="button button-secondary">Ver estatísticas</Link>
        <Link href={`/matches/${matchId}/live`} className="button button-primary">Abrir Jogo ao Vivo</Link></div>
        {canEdit && (editing ? <MatchForm match={match} busy={busy || loading} onSave={saveMatch} onCancel={() => setEditing(false)} />
          : <SecondaryButton disabled={busy || loading} onClick={() => { setEditing(true); setNotice(""); setError(""); }} className="w-full">Editar jogo</SecondaryButton>)}
        {error && <p role="alert" className="rounded-xl border border-error p-4 text-error">{error}</p>}
        {notice && <p role="status" className="text-success">{notice}</p>}
        {isAdmin && (match.can_cancel || match.can_delete) && <section className="card space-y-3" aria-labelledby="management-section-title">
          <SectionHeader id="management-section-title">Gestão do jogo</SectionHeader>
          <div className="grid gap-3 sm:grid-cols-2">
            {match.can_cancel && <SecondaryButton disabled={busy || loading} onClick={() => { setManagement("cancel"); setManagementError(""); }}>Cancelar jogo</SecondaryButton>}
            {match.can_delete && <DangerButton disabled={busy || loading} onClick={() => { setManagement("delete"); setManagementError(""); }}>Eliminar jogo</DangerButton>}
          </div>
        </section>}
        {isAdmin && <section className="card space-y-3 border-error" aria-labelledby="force-section-title">
          <SectionHeader id="force-section-title">Eliminação destrutiva</SectionHeader>
          <p className="text-sm">Para limpar jogos de teste ou criados por engano. Apaga definitivamente o jogo, convocatória, eventos e histórico associado.</p>
          <DangerButton disabled={busy || loading} onClick={() => { setManagement("force"); setManagementError(""); }}>Eliminar jogo e dados associados</DangerButton>
        </section>}
        {isAdmin && management && <ManagementDialog action={management} busy={busy} error={managementError} onClose={() => { setManagement(null); setManagementError(""); }} onConfirm={() => void confirmManagement()} />}
        <section aria-labelledby="squad-title" aria-busy={busy || loading} className="space-y-4">
          <SectionHeader id="squad-title">Convocatória</SectionHeader>
          <div aria-live="polite" aria-label="Contadores da convocatória" className="rounded-xl border border-border p-4 text-sm">
            <p>Titulares: {starters}</p><p>Suplentes: {substitutes}</p><p>Total convocados: {starters + substitutes}</p>
          </div>
          <fieldset disabled={!canEdit || busy || loading} className="min-w-0 space-y-3 disabled:opacity-60">
            <legend className="sr-only">Selecionar jogadores</legend>
            {squad.length === 0 && <p className="text-muted">Não existem jogadores ativos no plantel nem jogadores já convocados.</p>}
            {squad.map(({ player, role }) => <div key={player.id} className={`card squad-${role.toLowerCase()}`}>
              <div className="flex items-center gap-3"><PlayerAvatar name={player.name} photoPath={player.photo_path} number={player.shirt_number} /><div className="min-w-0">
              <p className="break-words font-semibold">{player.shirt_number ?? "—"} · {player.name}</p>
              <p className="mt-1 text-sm text-muted">{player.position}{!player.is_active && " · Inativo — convocatória preservada"}</p>
              </div></div>
              <div className="mt-3"><StatusBadge tone={role === "TITULAR" ? "success" : role === "SUPLENTE" ? "warning" : "neutral"}>{role === "NAO_CONVOCADO" ? "Não convocado" : role === "TITULAR" ? "Titular" : "Suplente"}</StatusBadge></div>
              {canEdit && <select aria-label={`Convocatória de ${player.name}`} value={role} onChange={(event) => choose(player.id, event.target.value as SquadRole)} className="mt-3 min-h-12 w-full rounded-xl border border-border bg-surface px-3 text-base">
                <option value="NAO_CONVOCADO">Não convocado</option><option value="TITULAR">Titular</option><option value="SUPLENTE">Suplente</option>
              </select>}
            </div>)}
            {canEdit && <PrimaryButton onClick={() => void saveSquad()} className="w-full">{busy ? "A guardar…" : "Guardar convocatória"}</PrimaryButton>}
          </fieldset>
        </section>
      </>}
    </div>
  </PageContainer>;
}
