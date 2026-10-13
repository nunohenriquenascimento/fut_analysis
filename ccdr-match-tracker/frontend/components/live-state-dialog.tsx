"use client";

import { useEffect, useRef } from "react";
import { DangerButton, PrimaryButton, SecondaryButton } from "@/components/ui";

export default function LiveStateDialog({ mode, busy, error, onClose, onConfirm }: {
  mode: "finish" | "reopen"; busy: boolean; error: string; onClose: () => void; onConfirm: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => { dialog.current?.showModal(); }, []);
  const ConfirmButton = mode === "finish" ? DangerButton : PrimaryButton;
  return <dialog ref={dialog} aria-labelledby="live-state-title" aria-describedby="live-state-description"
    onCancel={(event) => { event.preventDefault(); if (!busy) onClose(); }}
    className="fixed inset-0 m-auto max-h-[90dvh] w-[calc(100%-2rem)] max-w-md overflow-y-auto rounded-2xl border border-border bg-background p-5 text-foreground backdrop:bg-overlay">
    <h2 id="live-state-title" className="text-xl font-bold">{mode === "finish" ? "Tens a certeza que o jogo terminou?" : "Reabrir este jogo?"}</h2>
    <p id="live-state-description" className="my-4">{mode === "finish" ? "Esta ação termina o jogo e fecha o cronómetro." : "Os eventos e o resultado serão mantidos. O cronómetro ficará parado até escolheres Retomar 2.ª Parte."}</p>
    {error && <p role="alert" className="mb-4 text-error">{error}</p>}
    <SecondaryButton autoFocus disabled={busy} onClick={onClose} className="w-full">Voltar</SecondaryButton>
    <ConfirmButton disabled={busy} onClick={onConfirm} className="mt-4 w-full">{busy ? "A guardar…" : mode === "finish" ? "Terminar jogo" : "Reabrir jogo"}</ConfirmButton>
  </dialog>;
}
