"use client";

import { useAuth } from "@/components/auth-provider";

import { PrimaryButton, SecondaryButton, PageHeader, StatusBadge, LoadingState, EmptyState, PageContainer } from "@/components/ui";
import { PlayerAvatar } from "@/components/media";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { api, ApiError, PLAYER_POSITIONS, type Player, type PlayerPosition, type RosterContext } from "@/lib/api";

type PlayerFields = { name: string; shirt_number: number; position: PlayerPosition; photo_path: string | null };

function errorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 422) return "Verifique o nome, o número (1 a 99), a posição e o caminho público da foto do jogador.";
    if (error.status === 503) return "A base de dados está indisponível. Tente novamente dentro de instantes.";
    return error.message;
  }
  return "Não foi possível contactar o servidor. Verifique a ligação e tente novamente.";
}

function PlayerForm({ player, busy, onSave, onCancel }: {
  player: Player | null;
  busy: boolean;
  onSave: (fields: PlayerFields) => Promise<void>;
  onCancel: () => void;
}) {
  const [name, setName] = useState(player?.name ?? "");
  const [number, setNumber] = useState(player?.shirt_number?.toString() ?? "");
  const [position, setPosition] = useState<PlayerPosition>(player?.position ?? "GR");
  const [photo, setPhoto] = useState(player?.photo_path ?? "");
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const shirtNumber = Number(number);
    if (!name.trim() || name.trim().length > 120 || !Number.isInteger(shirtNumber) || shirtNumber < 1 || shirtNumber > 99 || !PLAYER_POSITIONS.includes(position)) {
      setError("Preencha o nome, um número inteiro entre 1 e 99 e uma posição válida.");
      return;
    }
    setError("");
    await onSave({ name: name.trim(), shirt_number: shirtNumber, position, photo_path: photo.trim() || null });
  }

  const inputClass = "form-field mt-2";
  return (
    <form onSubmit={submit} className="rounded-2xl border border-border bg-surface p-5" aria-labelledby="player-form-title">
      <h2 id="player-form-title" className="mb-4 text-xl font-semibold">{player ? `Editar ${player.name}` : "Adicionar jogador"}</h2>
      <fieldset disabled={busy} className="space-y-4 disabled:opacity-60">
        <label className="block text-sm">Nome
          <input name="name" required maxLength={120} value={name} onChange={(event) => setName(event.target.value)} className={inputClass} autoComplete="off" />
        </label>
        <div className="grid grid-cols-2 gap-3">
          <label className="block text-sm">Número
            <input name="shirt_number" type="number" inputMode="numeric" required min={1} max={99} step={1} value={number} onChange={(event) => setNumber(event.target.value)} className={inputClass} />
          </label>
          <label className="block text-sm">Posição principal
            <select name="position" value={position} onChange={(event) => setPosition(event.target.value as PlayerPosition)} className={inputClass}>
              {PLAYER_POSITIONS.map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
          </label>
        </div>
        <label className="block text-sm">Caminho da foto (opcional)
          <input value={photo} onChange={(event) => setPhoto(event.target.value)} maxLength={500} placeholder="/players/jogador-8.webp" className={inputClass} aria-describedby="photo-help" />
        </label>
        <p id="photo-help" className="text-xs text-muted">Use o caminho da imagem já colocada na pasta pública.</p>
        {error && <p role="alert" className="text-sm text-error">{error}</p>}
        <PrimaryButton type="submit" className="w-full">
          {busy ? "A guardar…" : player ? "Guardar alterações" : "Adicionar jogador"}
        </PrimaryButton>
        <SecondaryButton type="button" onClick={onCancel} className="w-full">{player ? "Cancelar edição" : "Fechar formulário"}</SecondaryButton>
      </fieldset>
    </form>
  );
}

export default function PlayersPage() {
  const { canEdit } = useAuth();
  const [context, setContext] = useState<RosterContext | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [actionError, setActionError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const locked = useRef(false);
  const [editing, setEditing] = useState<Player | null>(null);
  const [adding, setAdding] = useState(false);
  const [formVersion, setFormVersion] = useState(0);
  const [reload, setReload] = useState(0);
  const formArea = useRef<HTMLElement>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const roster = await api.rosterContext();
        const rows = await api.rosterPlayers(roster);
        if (!cancelled) {
          setContext(roster);
          setPlayers(rows);
          setLoadError("");
        }
      } catch (error) {
        if (!cancelled) setLoadError(errorMessage(error));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => { cancelled = true; };
  }, [reload]);

  function refresh() {
    setLoading(true);
    setReload((value) => value + 1);
  }

  async function mutate(operation: () => Promise<Player>, message: string) {
    if (locked.current || !context || loading) return;
    locked.current = true;
    setBusy(true);
    setActionError("");
    setNotice("");
    try {
      const saved = await operation();
      // Use the persisted response immediately, even if the following refresh fails.
      setPlayers((rows) => [...rows.filter((row) => row.id !== saved.id), saved]);
      setEditing(null);
      setAdding(false);
      setFormVersion((value) => value + 1);
      setNotice(message);
      refresh();
    } catch (error) {
      setActionError(errorMessage(error));
    } finally {
      locked.current = false;
      setBusy(false);
    }
  }

  async function save(fields: PlayerFields) {
    if (!context) return;
    await mutate(
      () => editing ? api.updatePlayer(editing.id, fields) : api.createPlayer({ ...fields, team_id: context.team_id, season_id: context.season_id }),
      editing ? "Jogador atualizado." : "Jogador adicionado ao plantel.",
    );
  }

  function edit(player: Player) {
    setEditing(player);
    setActionError("");
    setNotice("");
    formArea.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  const sortedPlayers = [...players].sort((a, b) => (a.shirt_number ?? 100) - (b.shirt_number ?? 100) || a.name.localeCompare(b.name, "pt"));
  return (
    <PageContainer className="wide-page">
      <div className="page-content space-y-6">
        <PageHeader title="Plantel" description={`${context?.team_name ?? "CCDR Vila Cortez do Mondego"} · Sub-19 · ${context?.season_name ?? "2026/27"}`} />

        {loading && <LoadingState>A carregar o plantel…</LoadingState>}
        {loadError && <div role="alert" className="rounded-xl border border-error p-4 text-error">
          <p>{loadError}</p>
          {players.length > 0 && <p className="mt-2 text-sm">A lista apresentada pode estar desatualizada.</p>}
          <SecondaryButton type="button" disabled={loading || busy} onClick={refresh} className="mt-2">Tentar novamente</SecondaryButton>
        </div>}

        {canEdit && context && <section ref={formArea} className="scroll-mt-4">
          {editing || adding || players.length === 0 ? <PlayerForm key={`${editing?.id ?? "new"}-${formVersion}`} player={editing} busy={busy || loading} onSave={save} onCancel={() => { setEditing(null); setAdding(false); }} />
            : <PrimaryButton disabled={busy || loading} onClick={() => setAdding(true)}>Adicionar jogador</PrimaryButton>}
        </section>}
        {actionError && <p role="alert" className="rounded-xl border border-error p-4 text-error">{actionError}</p>}
        {notice && <p role="status" className="text-success">{notice}</p>}

        <section aria-label="Jogadores" aria-busy={loading} className="roster-grid space-y-3">
          {!loading && !loadError && players.length === 0 && <EmptyState>Ainda não existem jogadores. {canEdit ? "Adicione o primeiro jogador acima." : "Peça à equipa técnica para adicionar jogadores."}</EmptyState>}
          {sortedPlayers.map((player) => <article key={player.id} className={`card player-card ${!player.is_active ? "player-inactive" : ""}`}>
            <div className="flex items-center gap-4">
              <PlayerAvatar name={player.name} photoPath={player.photo_path} number={player.shirt_number} />
              <div className="min-w-0 flex-1">
                <h2 className="break-words text-lg font-semibold">{player.name}</h2>
                <p className="mb-2 text-sm text-muted"><span className="player-number">#{player.shirt_number ?? "—"}</span> · {player.position}</p>
                <StatusBadge tone={player.is_active ? "success" : "neutral"}>{player.is_active ? "Ativo" : "Inativo"}</StatusBadge>
              </div>
            </div>
            {canEdit && <div className="mt-4 grid grid-cols-2 gap-3">
              <SecondaryButton disabled={busy || loading} onClick={() => edit(player)}>Editar</SecondaryButton>
              <SecondaryButton disabled={busy || loading} onClick={() => void mutate(() => api.updatePlayer(player.id, { is_active: !player.is_active }), player.is_active ? "Jogador desativado. Os dados foram preservados." : "Jogador ativado.")}>
                {player.is_active ? "Desativar" : "Ativar"}
              </SecondaryButton>
            </div>}
          </article>)}
        </section>
      </div>
    </PageContainer>
  );
}
