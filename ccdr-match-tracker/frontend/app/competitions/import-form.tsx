"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import { competitionError, competitionsApi, type FixtureInput } from "@/lib/competitions";
import { PrimaryButton, SecondaryButton } from "@/components/ui";
import { ErrorNotice } from "./competition-ui";

export default function ImportForm({ competitionId }: { competitionId: number }) {
  const [text, setText] = useState(""), [preview, setPreview] = useState<{ fixtures: FixtureInput[] } | null>(null);
  const [error, setError] = useState(""), [success, setSuccess] = useState("");
  const [busy, setBusy] = useState(false);
  const locked = useRef(false);
  function change(value: string) { setText(value); setPreview(null); setError(""); setSuccess(""); }
  return <section className="card space-y-4" aria-label="Importação de resultados">
    <h2 className="section-header">Importar resultados externos</h2>
    <p className="text-sm text-muted">Importação por chave externa, até 200 jogos por lote. Uma chave existente atualiza o mesmo jogo. O lote completo é validado pelo servidor antes de ser gravado.</p>
    <p className="rounded-xl bg-secondary-surface p-3 text-sm">Os nossos jogos exigem ligação por <code>internal_match_id</code>, sem golos importados. O resultado interno continua a ser obtido dos eventos.</p>
    <details><summary className="min-h-12 py-3 font-semibold">Formato JSON e exemplo</summary>
      <p className="text-sm text-muted mb-2">Substitua os IDs pelos participantes desta competição; não são dados reais.</p>
      <pre className="competition-json">{JSON.stringify({ fixtures: [{ external_key: "j1-exemplo", matchday: 1, home_team_id: 2, away_team_id: 3, home_goals: 2, away_goals: 1, source: "Referência do boletim oficial" }] }, null, 2)}</pre>
      <p className="mt-3 text-sm">Também aceita <code>kickoff_at</code> com fuso horário e <code>venue</code>. Para agendar sem resultado, omita ambos os golos.</p>
    </details>
    <label className="block">Ficheiro JSON<input className="form-field py-3 mt-1" type="file" accept="application/json,.json" disabled={busy} onChange={async (event) => {
      const file = event.target.files?.[0]; if (!file || locked.current) return;
      change("");
      if (file.size > 1_000_000) { setError("O ficheiro excede 1 MB. Divida a importação em lotes."); return; }
      locked.current = true; setBusy(true);
      try { change(await file.text()); } catch { setError("Não foi possível ler o ficheiro."); }
      finally { locked.current = false; setBusy(false); }
    }} /></label>
    <label className="block">Conteúdo JSON<textarea className="form-field competition-json mt-1" rows={12} disabled={busy} value={text} onChange={(event) => change(event.target.value)} spellCheck={false} /></label>
    {preview ? <div className="space-y-3 border-t border-border pt-4">
      <h3 className="font-bold">Rever lote: {preview.fixtures.length} jogo(s)</h3>
      <p className="text-sm">A revisão abaixo não grava dados. Confirme as chaves, equipas e origens. O servidor verificará as referências e impedirá alterações aos resultados internos.</p>
      <pre className="competition-json max-h-80 overflow-y-auto" aria-label="Lote em revisão">{JSON.stringify(preview, null, 2)}</pre>
      <div className="flex flex-wrap gap-2"><PrimaryButton disabled={busy} onClick={async () => {
        if (locked.current) return; locked.current = true; setBusy(true); setError(""); setSuccess("");
        try { const result = await competitionsApi.import(competitionId, preview); setSuccess(`Importação concluída: ${result.imported} jogo(s).`); setPreview(null); }
        catch (reason) { setError(competitionError(reason)); }
        finally { locked.current = false; setBusy(false); }
      }}>{busy ? "A importar…" : "Confirmar importação"}</PrimaryButton><SecondaryButton disabled={busy} onClick={() => setPreview(null)}>Voltar à edição</SecondaryButton></div>
    </div> : <PrimaryButton disabled={busy || !text.trim()} onClick={() => {
      setError(""); setSuccess("");
      try {
        const parsed: unknown = JSON.parse(text);
        if (!parsed || typeof parsed !== "object" || !("fixtures" in parsed) || !Array.isArray(parsed.fixtures) || parsed.fixtures.length < 1 || parsed.fixtures.length > 200) {
          setError('Use um objeto JSON com "fixtures": [...] e entre 1 e 200 jogos.'); return;
        }
        setPreview(parsed as { fixtures: FixtureInput[] });
      } catch { setError("JSON inválido. Verifique as aspas, vírgulas e parênteses."); }
    }}>Rever importação</PrimaryButton>}
    {error && <ErrorNotice message={error} />}
    {success && <div role="status" className="space-y-2"><p className="text-success">{success}</p><Link href={`/competitions/${competitionId}/results`} className="button button-secondary">Consultar resultados atualizados</Link></div>}
  </section>;
}
