"use client";

import { useEffect, useRef, useState } from "react";
import { DangerButton, SecondaryButton } from "@/components/ui";

export default function ManagementDialog({ action, busy, error, onClose, onConfirm }: {
  action: "delete" | "cancel" | "force"; busy: boolean; error: string; onClose: () => void; onConfirm: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [confirmed, setConfirmed] = useState(false);
  const [confirmation, setConfirmation] = useState("");
  const forced = action === "force";
  const deleting = action !== "cancel";
  useEffect(() => { dialog.current?.showModal(); }, []);
  return <dialog ref={dialog} aria-labelledby="management-title" aria-describedby="management-description"
    onCancel={(event) => { event.preventDefault(); if (!busy) onClose(); }}
    className="fixed inset-0 m-auto max-h-[90dvh] w-[calc(100%-2rem)] max-w-md overflow-y-auto rounded-2xl border border-border bg-surface p-5 text-foreground backdrop:bg-overlay">
    <h2 id="management-title" className="text-xl font-bold">{forced ? "Eliminar jogo e dados associados" : deleting ? "Eliminar jogo" : "Cancelar jogo"}</h2>
    <p id="management-description" className="my-4">{forced
      ? "Esta ação é permanente: apaga o jogo, toda a convocatória, todos os eventos, o resultado e o histórico do relógio. O jogo deixará de contribuir para as estatísticas. Jogadores, equipas, época, utilizadores e outros jogos serão preservados."
      : deleting
      ? "A eliminação é permanente e não pode ser desfeita. O servidor voltará a verificar se o jogo não tem histórico."
      : "O jogo ficará cancelado e continuará consultável. A convocatória, os eventos e o resultado histórico serão preservados. O relógio será parado e o jogo ficará excluído de jogos competitivos, vitórias, empates e derrotas."}</p>
    <fieldset disabled={busy} className="space-y-4">
      {deleting && <label className="flex min-h-11 items-center gap-3"><input type="checkbox" checked={confirmed} onChange={(event) => setConfirmed(event.target.checked)} />Confirmo que quero eliminar permanentemente este jogo.</label>}
      {forced && <label className="block">Escreva ELIMINAR para confirmar novamente<input className="form-field mt-2" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} autoComplete="off" spellCheck={false} /></label>}
      {error && <p role="alert" className="text-error">{error}</p>}
      <div className="grid gap-3"><DangerButton disabled={busy || (deleting && !confirmed) || (forced && confirmation !== "ELIMINAR")} onClick={onConfirm}>{busy ? "A processar…" : forced ? "Confirmar eliminação de todos os dados" : deleting ? "Confirmar eliminação" : "Confirmar cancelamento"}</DangerButton>
        <SecondaryButton disabled={busy} onClick={onClose}>Voltar ao jogo</SecondaryButton></div>
    </fieldset>
  </dialog>;
}
