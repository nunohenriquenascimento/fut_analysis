"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/components/auth-provider";
import { api, type Match } from "@/lib/api";
import { competitionsApi, type Competition, type CompetitionTeam } from "@/lib/competitions";
import { fpfApi, fpfError, type FPFCapture, type FPFDocument, type FPFFile, type FPFPreview, type FPFRead } from "@/lib/fpf";
import { LoadingState, PrimaryButton, SecondaryButton } from "@/components/ui";
import { ErrorNotice } from "./competition-ui";
import { OfficialCompetition, OfficialMatch } from "./fpf-view";

export default function FPFSection({ competition }: { competition: Competition }) {
  const { isAdmin } = useAuth();
  const [data, setData] = useState<FPFRead | null>(null), [error, setError] = useState(""), [lookupError, setLookupError] = useState("");
  const [loading, setLoading] = useState(true), [reload, setReload] = useState(0), [busy, setBusy] = useState(false), [success, setSuccess] = useState("");
  const [teams, setTeams] = useState<CompetitionTeam[]>([]), [matches, setMatches] = useState<Match[]>([]);
  const [files, setFiles] = useState<FPFFile[]>([]), [documents, setDocuments] = useState<FPFDocument[]>([]);
  const [seriesId, setSeriesId] = useState(0), [mapping, setMapping] = useState<Record<string, number>>({});
  const [rounds, setRounds] = useState<Record<string, number>>({}), [links, setLinks] = useState<Record<string, number>>({});
  const [preview, setPreview] = useState<FPFPreview | null>(null), [pending, setPending] = useState<FPFPreview["pending_internal_links"]>([]), [confirmation, setConfirmation] = useState("");
  const locked = useRef(false);
  const revision = useRef(0), readGeneration = useRef(0);
  useEffect(() => {
    let active = true;
    const started = revision.current, generation = ++readGeneration.current;
    fpfApi.read(competition.id).then((result) => {
      if (!active || generation !== readGeneration.current) return;
      setData(result);
      if (started === revision.current) {
        setError(""); setMapping(result.snapshot?.team_mapping ?? {});
        setLinks(result.snapshot?.internal_match_links ?? {}); setSeriesId(result.snapshot?.identity[2] ?? 0);
      }
    }).catch((reason) => { if (active && generation === readGeneration.current) setError(fpfError(reason)); }).finally(() => { if (active && generation === readGeneration.current) setLoading(false); });
    if (isAdmin) Promise.all([competitionsApi.teams(), api.seasonMatches({ season_id: competition.season_id, team_id: competition.internal_team_id })]).then(([all, games]) => {
      if (active) { setTeams(all); setMatches(games); setLookupError(""); }
    }).catch((reason) => { if (active) setLookupError(fpfError(reason)); });
    return () => { active = false; };
  }, [competition.id, competition.season_id, competition.internal_team_id, isAdmin, reload]);
  function invalidate() { revision.current++; setPreview(null); setConfirmation(""); setSuccess(""); }
  const incoming = documents.find((doc) => doc.kind === "competition");
  const document = incoming?.kind === "competition" ? incoming.data : data?.snapshot?.competition;
  const series = document?.series.find((item) => item.series_id === seriesId);
  const matchDocs = documents.filter((doc): doc is Extract<FPFDocument, { kind: "match" }> => doc.kind === "match");
  const valid = documents.length > 0 && documents.every((doc) => doc.supported) && documents.filter((doc) => doc.kind === "competition").length <= 1;
  function payload(): FPFCapture | null {
    if (!valid || !series || series.standings.some((row) => !mapping[row.name])) return null;
    return { ...(incoming?.kind === "competition" ? { competition_html: files[documents.indexOf(incoming)].html } : {}), series_id: seriesId,
      fixture_htmls: documents.filter((doc) => doc.kind === "fixture" && doc.supported).map((doc) => {
        const file = files[documents.indexOf(doc)];
        return file.source_url ? { html: file.html, source_url: file.source_url,
          competition_id: document!.competition_id, season_id: document!.season_id, series_id: seriesId } : file.html;
      }),
      team_mapping: Object.fromEntries(series.standings.map((row) => [row.name, mapping[row.name]])),
      match_htmls: documents.flatMap((doc, i) => doc.kind === "match" ? [files[i].html] : []), match_rounds: rounds, internal_match_links: links };
  }
  const ready = payload();
  return <section className="space-y-5" aria-label="Integração FPF">
    <div className="card space-y-3"><h2 className="section-header">Fonte oficial FPF</h2>
      <p className="text-warning">Ligação automática não confirmada · HTTP 403 observado. Importação de HTML disponível.</p>
      <p>Referência: competição 30369 · época 2026/27 (106).</p>
      <p>Última captura disponível: {data?.snapshot ? new Date(data.snapshot.imported_at).toLocaleString("pt-PT", { timeZone: "Europe/Lisbon" }) : "Ainda não importada"}.</p>
      <p className="text-sm text-muted">Esta é a data de importação. A captura pode conter dados anteriores. {data?.snapshot?.mode === "http" ? "Última captura obtida por HTTP; não é monitorização da ligação atual." : "A importação de ficheiros não comprova sincronização automática."}</p>
      <div className="flex flex-wrap gap-2"><span className="badge badge-success">FPF · dados oficiais da captura</span><Link className="button button-secondary" href={`/competitions/${competition.id}`}>Consultar classificação local provisória</Link></div>
      <SecondaryButton disabled={busy} onClick={() => { invalidate(); setLoading(true); setReload((n) => n + 1); }}>Atualizar captura disponível</SecondaryButton>
    </div>
    {loading && <LoadingState>A carregar captura FPF…</LoadingState>}
    {error && <ErrorNotice message={error} />}
    {data?.snapshot ? <><OfficialCompetition document={data.snapshot.competition} snapshot={data.snapshot} />
      <section className="space-y-3" aria-label="Fichas oficiais"><h2 className="section-header">Fichas oficiais disponíveis</h2>
        {Object.values(data.snapshot.match_sheets).length ? Object.values(data.snapshot.match_sheets).map((match) => <OfficialMatch key={match.match_id} match={match} />) : <p>Sem fichas importadas.</p>}
      </section></> : !loading && <p className="card text-muted">Dados oficiais ainda não disponíveis. Os dados locais continuam acessíveis.</p>}
    {isAdmin ? <section className="card space-y-4" aria-label="Importar HTML FPF">
      <h2 className="section-header">Importar HTML FPF · ADMIN</h2>
      <p>Selecione a competição, páginas de jornada ou fichas de jogo (até nove ficheiros). Máximo 2 MB por ficheiro e 4 MB por lote. O HTML é analisado como texto e nunca executado.</p>
      {lookupError && <ErrorNotice message={`Mapeamento indisponível: ${lookupError}`} />}
      <fieldset disabled={busy} className="space-y-4">
        <label className="block">Ficheiros HTML FPF<input type="file" accept=".html,.htm,text/html" multiple className="form-field mt-1 py-3" onChange={async (event) => {
          const chosen = Array.from(event.target.files ?? []); if (locked.current) return;
          invalidate(); setDocuments([]); setFiles([]); setPending([]); setRounds({}); setError("");
          if (!chosen.length) return;
          if (chosen.length > 9 || chosen.some((file) => !/\.html?$/i.test(file.name) || file.name.length > 160 || !file.size || file.size > 2_000_000) || chosen.reduce((n, file) => n + file.size, 0) > 4_000_000) {
            setError("Selecione até nove ficheiros HTML válidos: máximo 2 MB por ficheiro e 4 MB por lote."); return;
          }
          locked.current = true; setBusy(true);
          try { setFiles(await Promise.all(chosen.map(async (file) => ({ name: file.name, html: await file.text() })))); }
          catch { setError("Não foi possível ler os ficheiros."); }
          finally { locked.current = false; setBusy(false); }
        }} /></label>
        {files.map((file, index) => <label className="block" key={`${file.name}-${index}`}>URL de origem FPF: {file.name}
          <input type="url" className="form-field mt-1" value={file.source_url ?? ""} placeholder="https://resultados.fpf.pt/Competition/GetClassificationAndMatchesByFixture?fixtureId=…"
            onChange={(event) => { const value = event.target.value.trim(); invalidate(); setDocuments([]); setPending([]);
              setFiles((old) => old.map((item, i) => i === index ? { ...item, source_url: value || undefined } : item)); }} />
          <span className="text-sm text-muted">Obrigatório para fragmentos de jornada sem identidade no HTML. Copie o URL do pedido original; a jornada será validada pela competição.</span>
        </label>)}
        <PrimaryButton disabled={!files.length} onClick={async () => {
          if (locked.current) return; locked.current = true; setBusy(true); invalidate(); setError("");
          try {
            const result = await fpfApi.inspect(competition.id, files); setDocuments(result.documents);
            const initial = result.documents.find((doc) => doc.kind === "competition");
            if (initial?.kind === "competition") setSeriesId(initial.data.series[0]?.series_id ?? 0);
          } catch (reason) { setError(fpfError(reason)); }
          finally { locked.current = false; setBusy(false); }
        }}>Validar e identificar ficheiros</PrimaryButton>
        {documents.map((doc, i) => <div key={`${doc.name}-${i}`} className="rounded-xl border border-border p-3 break-words"><strong>{doc.name}</strong> · {doc.kind === "competition" ? "Competição" : doc.kind === "match" ? "Ficha de jogo" : doc.kind === "fixture" ? "Jornada" : "Inválido"}
          {!doc.supported ? <p role="alert" className="text-error">{doc.error}</p> : doc.kind === "competition" ? <p>{doc.data.name} · {doc.data.season} · {doc.data.series.reduce((n, s) => n + s.standings.length, 0)} equipas</p> : doc.kind === "fixture" ? <p>{doc.data.matchday ? `Jornada ${doc.data.matchday} · ` : ""}FPF #{doc.data.fixture_id} · {doc.data.matches.length} jogos identificados</p> : <p>{doc.data.home.name} {doc.data.home_goals}–{doc.data.away_goals} {doc.data.away.name} · #{doc.data.match_id}</p>}
        </div>)}
        {documents.filter((doc) => doc.kind === "competition").length > 1 && <p role="alert">Selecione apenas uma captura da competição por lote.</p>}
        {documents.some((doc) => !doc.supported) && <p className="text-error">{documents.filter((doc) => !doc.supported).length} ficheiro(s) rejeitado(s). Nenhum jogo foi aplicado; corrija os ficheiros antes de confirmar.</p>}
        {valid && !document && <p role="alert">Importe primeiro o HTML da competição para poder associar esta ficha.</p>}
        {valid && document && <div className="space-y-4">
          {incoming?.kind === "competition" && <details className="card"><summary className="min-h-12 py-3 font-semibold">Dados extraídos da competição · Ainda não aplicados</summary><OfficialCompetition document={incoming.data} preview /></details>}
          <label className="block">Série FPF<select className="form-field mt-1" value={seriesId} onChange={(e) => { setSeriesId(Number(e.target.value)); setMapping({}); setLinks({}); setPending([]); invalidate(); }}>
            {document.series.map((s) => <option key={s.series_id} value={s.series_id}>Série {s.series_id}</option>)}
          </select></label>
          <h3 className="font-bold">Mapear equipas para registos existentes</h3>
          <p className="text-sm text-muted">Nenhuma equipa é criada automaticamente. A nossa equipa deve ser associada ao registo interno correto.</p>
          <div className="grid gap-3 sm:grid-cols-2">{series?.standings.map((row) => <label key={row.name} className="block min-w-0">Equipa FPF: {row.name}<select className="form-field mt-1" value={mapping[row.name] ?? ""} onChange={(e) => { setMapping((old) => ({ ...old, [row.name]: Number(e.target.value) })); setLinks({}); setPending([]); invalidate(); }}>
            <option value="">Selecionar equipa interna</option>{teams.map((team) => <option key={team.id} value={team.id}>{team.name} · #{team.id}</option>)}
          </select></label>)}</div>
          {matchDocs.map((doc) => <div key={doc.data.match_id} className="space-y-3"><OfficialMatch match={doc.data} anchor={false} /><label className="block">Jornada da ficha #{doc.data.match_id}<select className="form-field mt-1" value={rounds[String(doc.data.match_id)] ?? ""} onChange={(e) => {
            const key = String(doc.data.match_id); setRounds((old) => { const next = { ...old }; if (e.target.value) next[key] = Number(e.target.value); else delete next[key]; return next; }); invalidate();
          }}><option value="">Selecionar jornada para importar o jogo local</option>{series?.rounds.map((r) => <option key={r.fixture_id} value={r.fixture_id}>Jornada {r.matchday}</option>)}</select></label></div>)}
          {pending.map((item) => <label key={item.external_key} className="block">Jogo interno: {item.official.home_name} / {item.official.away_name} · Jornada {item.official.matchday}<select className="form-field mt-1" value={links[item.external_key] ?? ""} onChange={(e) => {
            setLinks((old) => { const next = { ...old }; if (e.target.value) next[item.external_key] = Number(e.target.value); else delete next[item.external_key]; return next; }); invalidate();
          }}><option value="">Sem ligação · conservar apenas na captura oficial</option>{matches.filter((match) => match.matchday === item.official.matchday).map((match) => <option key={match.id} value={match.id}>#{match.id} · {match.opponent_name} · {match.is_home ? "Casa" : "Fora"} · {match.status}</option>)}</select></label>)}
          <PrimaryButton disabled={!ready || !!lookupError} onClick={async () => {
            if (!ready || locked.current) return; locked.current = true; setBusy(true); invalidate(); setError("");
            try { const result = await fpfApi.preview(competition.id, ready); setPreview(result); setPending((old) => [...new Map([...old, ...result.pending_internal_links].map((p) => [p.external_key, p])).values()]); }
            catch (reason) { setError(fpfError(reason)); }
            finally { locked.current = false; setBusy(false); }
          }}>Rever diferenças e ligações</PrimaryButton>
        </div>}
        {preview && ready && <section className="space-y-4 border-t border-border pt-4" aria-label="Revisão FPF">
          <h3 className="font-bold">Diferenças antes de aplicar</h3>
          <p>Participantes a associar: {preview.add_participants.length}. Jogos internos pendentes: {preview.pending_internal_links.length}.</p>
          {preview.summary && <p>Criar: {preview.summary.created} · Atualizar: {preview.summary.updated} · Ignorar: {preview.summary.ignored} · Rejeitar: {preview.summary.rejected}</p>}
          {preview.ignored?.map((item) => <p role="alert" key={item.match_id}>Ficha #{item.match_id}: {item.reason}</p>)}
          {preview.pending_internal_links.map((item) => <p role="alert" key={item.external_key}>{item.reason}</p>)}
          <p className="text-sm text-muted">Os links das jornadas não contêm os jogos. Importe o HTML de cada jornada ou as fichas com jornada confirmada. A classificação local usa apenas jogos importados, não os totais da tabela oficial.</p>
          {preview.add_participants.length > 0 && <ul>{preview.add_participants.map((id) => <li key={id}>{teams.find((team) => team.id === id)?.name ?? `Equipa #${id}`}</li>)}</ul>}
          <ul className="space-y-3">{preview.changes.map((change) => <li key={change.external_key} className="rounded-xl border border-border p-3 break-words">
            <strong>{change.action === "create" ? "Criar jogo externo/ligação" : change.action === "update" ? "Atualizar jogo" : "Sem alterações"}</strong> · Jornada {change.after.matchday}<br />
            {teams.find((team) => team.id === change.after.home_team_id)?.name} / {teams.find((team) => team.id === change.after.away_team_id)?.name}<br />
            Resultado: {change.before ? `${change.before.home_goals ?? "–"}–${change.before.away_goals ?? "–"}` : "Sem registo local"} → {change.after.home_goals === null || change.after.home_goals === undefined ? "Sem golos importados" : `${change.after.home_goals}–${change.after.away_goals}`}<br />
            Local: {change.before?.venue ?? "Não disponível"} → {change.after.venue ?? "Não disponível"}
            <p className="text-xs text-muted break-all">Origem: {change.before?.source ?? "Sem registo"} → {change.after.source}</p>
          </li>)}</ul>
          <details className="card"><summary className="min-h-12 py-3 font-semibold">Diferenças na classificação oficial</summary><ul className="space-y-2">{preview.snapshot.competition.series.flatMap((s) => s.standings.map((row) => {
            const previous = preview.standings_before.find((old) => old.series_id === s.series_id)?.standings.find((old) => old.name === row.name);
            return <li key={`${s.series_id}-${row.name}`} className="space-y-1"><strong>{row.name}</strong><div className="flex flex-wrap gap-x-3 gap-y-1 text-sm">{([
              ["rank", "Posição"], ["played", "Jogos"], ["wins", "Vitórias"], ["draws", "Empates"], ["losses", "Derrotas"], ["goals_for", "GM"], ["goals_against", "GS"], ["points", "Pontos"],
            ] as const).map(([field, label]) => <span key={field}>{label}: {previous?.[field] ?? "sem captura"} → {row[field]}</span>)}</div></li>;
          }))}</ul></details>
          <p className="text-sm text-muted">Eventos, convocatórias e resultados internos permanecem independentes. Os jogos pendentes não criam jogos internos.</p>
          <label className="block">Escreva SINCRONIZAR FPF para confirmar<input className="form-field mt-1" value={confirmation} onChange={(e) => setConfirmation(e.target.value)} autoComplete="off" /></label>
          <PrimaryButton disabled={confirmation !== "SINCRONIZAR FPF"} onClick={async () => {
            if (locked.current) return; locked.current = true; setBusy(true); setError("");
            try {
              const result = await fpfApi.apply(competition.id, { ...ready, expected_state: preview.state_token }, confirmation);
              setSuccess(result.summary ? `Captura aplicada: ${result.summary.created} criados, ${result.summary.updated} atualizados, ${result.summary.ignored} ignorados, ${result.summary.rejected} rejeitados. ${result.ignored?.map((item) => `Ficha #${item.match_id}: ${item.reason}`).join(" ") ?? ""}` : `Captura aplicada: ${result.imported} jogo(s); ${result.pending_internal_links.length} ligação(ões) interna(s) pendente(s).`); setPreview(null); setConfirmation("");
              readGeneration.current++;
              try { setData(await fpfApi.read(competition.id)); setLoading(false); } catch { setError("A captura foi aplicada, mas a leitura falhou. Atualize a captura disponível."); }
            } catch (reason) { setError(fpfError(reason)); setPreview(null); setConfirmation(""); }
            finally { locked.current = false; setBusy(false); }
          }}>Confirmar importação FPF</PrimaryButton>
        </section>}
      </fieldset>
      {success && <p role="status" className="text-success">{success}</p>}
    </section> : <p className="card text-muted">Importar capturas FPF requer ADMIN. A consulta permanece disponível.</p>}
  </section>;
}
