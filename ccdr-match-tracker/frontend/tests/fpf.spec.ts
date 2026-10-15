import { test, expect, type Page } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
import type { FPFCompetition, FPFMatch, FPFSnapshot, FPFCapture, FPFPreview } from "../lib/fpf";

const backend = resolve(__dirname, "../../backend");
const captures = resolve(backend, "tests/fixtures/fpf");
// Real captures parsed by the production Python parser. HTTP is mocked in this
// suite; a separate backend/browser test exercises the real HTTP flow.
const source = JSON.parse(execFileSync(resolve(backend, ".venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python"), ["-c", `
import json
from pathlib import Path
from app.fpf_parser import parse_competition,parse_match
p=Path('tests/fixtures/fpf')
print(json.dumps({'competition':parse_competition((p/'competition_30369_season_106.html').read_text(encoding='utf-8-sig')),'match':parse_match((p/'match_2682548.html').read_text(encoding='utf-8-sig'))}))
`], { cwd: backend, encoding: "utf8" })) as { competition: FPFCompetition; match: FPFMatch };
const competition = { id: 1, name: "Liga Dappin", season_id: 17, internal_team_id: 23, provisional: true, rules: { win: 3, draw: 1, loss: 0, tiebreakers: [] } };
const teams = source.competition.series[0].standings.map((r, i) => ({ id: r.name === "V. Cortez Mondego-Guarda" ? 23 : 100 + i, name: r.name, crest_path: null, created_at: "2026-10-15T10:00:00Z" }));
const mapping = Object.fromEntries(teams.map((t) => [t.name, t.id]));
const own = source.competition.series[0].matches.find((m) => m.home_name === "V. Cortez Mondego-Guarda")!;
const ownKey = `fpf:106:30369:99718:677923:23:${mapping['Guarda Fc']}`;
function snapshot(): FPFSnapshot {
  return { identity: [30369, 106, 99718], competition: structuredClone(source.competition), team_mapping: mapping,
    match_sheets: { "2682548": structuredClone(source.match) }, mode: "captured_html", imported_at: "2026-10-15T10:00:00Z",
    source_url: "https://resultados.fpf.pt/Competition/Details?competitionId=30369&seasonId=106", internal_match_links: {},
    round_captures: { "99718:677923": { series_id: 99718, fixture_id: 677923, matchday: 3, complete: true, matches: source.competition.series[0].matches } } };
}
async function mock(page: Page, role = "ADMIN", available = false, delayRead?: Promise<void>) {
  const state = { data: available ? snapshot() : null as FPFSnapshot | null, applies: 0, inspections: 0, conflict: false, unsupported: false };
  await page.route("http://localhost:8000/**", async (route) => {
    const req = route.request(), path = new URL(req.url()).pathname, method = req.method();
    if (path === "/auth/me") return route.fulfill({ json: { user: { id: 1, name: role, email: "test@test.local", role, is_active: true }, csrf_token: "test-csrf" } });
    if (path === "/competitions") return route.fulfill({ json: [competition] });
    if (path === "/competitions/1/teams" || path === "/teams") return route.fulfill({ json: teams });
    if (path === "/matches") return route.fulfill({ json: [{ id: 31, matchday: 3, opponent_name: "Guarda Fc", opponent_id: mapping['Guarda Fc'], is_home: true, status: "SCHEDULED" }] });
    if (path === "/competitions/1/fpf" && method === "GET") { await delayRead; return route.fulfill({ json: { source: "FPF", available: !!state.data, snapshot: state.data, note: "Captura oficial separada" } }); }
    if (path === "/competitions/1/fpf/documents") {
      state.inspections++;
      const body = req.postDataJSON() as { files: { name: string }[] };
      return route.fulfill({ json: { documents: body.files.map((f) => f.name.includes("competition")
        ? { name: f.name, kind: "competition", supported: true, data: source.competition }
        : f.name.includes("match_") ? { name: f.name, kind: "match", supported: true, data: source.match }
        : { name: f.name, kind: state.unsupported ? "fixture" : "invalid", supported: false, data: null, error: state.unsupported ? "Jornada identificada; formato AJAX ainda não validado. Não será importada." : "HTML inválido ou indisponível." }) } });
    }
    if (path === "/competitions/1/fpf/preview") {
      const body = req.postDataJSON() as FPFCapture;
      const fixtures = source.competition.series[0].matches.filter((g) => g !== own && g.home_name !== own.home_name).map((g) => ({
        external_key: `fpf:${g.home_name}`, matchday: 3, home_team_id: mapping[g.home_name], away_team_id: mapping[g.away_name],
        source: snapshot().source_url, home_goals: null, away_goals: null, venue: g.venue, internal_match_id: null,
      }));
      const plan: FPFPreview = { snapshot: snapshot(), fixtures, state_token: "f".repeat(64), add_participants: [],
        pending_internal_links: body.internal_match_links[ownKey] ? [] : [{ external_key: ownKey, official: own, reason: "internal_match_link_required" }],
        changes: fixtures.map((f) => ({ external_key: f.external_key, action: state.data ? "unchanged" : "create", before: state.data ? f : null, after: f })),
        standings_before: state.data?.competition.series ?? [] };
      return route.fulfill({ json: plan });
    }
    if (path === "/competitions/1/fpf" && method === "PUT") {
      if (state.conflict) return route.fulfill({ status: 409, json: { detail: "Os dados mudaram após o preview. Reveja as diferenças." } });
      const body = req.postDataJSON() as FPFCapture & { confirmation: string };
      expect(body.confirmation).toBe("SINCRONIZAR FPF"); expect(body.expected_state).toBe("f".repeat(64));
      state.data = snapshot(); state.applies++;
      return route.fulfill({ json: { imported: 3, pending_internal_links: [] } });
    }
    return route.fulfill({ status: 404, json: { detail: "Not found" } });
  });
  return state;
}
async function selectCaptures(page: Page) {
  await page.getByLabel("Ficheiros HTML FPF").setInputFiles([resolve(captures, "competition_30369_season_106.html"), resolve(captures, "match_2682548.html")]);
  await page.getByRole("button", { name: "Validar e identificar ficheiros" }).click();
}
async function mapTeams(page: Page) {
  for (const team of teams) await page.getByRole("combobox", { name: `Equipa FPF: ${team.name}`, exact: true }).selectOption(String(team.id));
}

for (const role of ["COACH", "VIEWER"]) test(`FPF consulta oficial e permissões ${role}`, async ({ page }) => {
  await mock(page, role, true); await page.goto("/competitions/1/fpf");
  await expect(page.getByRole("heading", { name: "FPF · Fonte oficial", exact: true })).toBeVisible();
  await expect(page.getByRole("region", { name: "Classificação oficial FPF" }).locator("tbody tr")).toHaveCount(8);
  await expect(page.getByText("Ainda não importada", { exact: true })).toHaveCount(13);
  await expect(page.getByLabel("Ficheiros HTML FPF")).toHaveCount(0);
  await page.getByText(/Ficha oficial #2682548/).click();
  await expect(page.getByRole("region", { name: "Eventos oficiais 2682548" })).toContainText("13'");
  await expect(page.getByRole("region", { name: "Eventos oficiais 2682548" })).toContainText("69'");
});

for (const width of [360, 390]) test(`FPF importação HTML real, mapeamento, confirmação e repetição ${width}px`, async ({ page }) => {
  await page.setViewportSize({ width, height: 850 }); const state = await mock(page);
  await page.goto("/competitions/1/fpf"); await selectCaptures(page); await mapTeams(page);
  await page.getByRole("button", { name: "Rever diferenças e ligações" }).click();
  await expect(page.getByRole("region", { name: "Revisão FPF" })).toContainText("Jogos internos pendentes: 1");
  const link = page.getByLabel(/Jogo interno:.*Jornada 3/);
  await link.selectOption("31"); await expect(page.getByRole("button", { name: "Confirmar importação FPF" })).toHaveCount(0);
  await page.getByRole("button", { name: "Rever diferenças e ligações" }).click();
  await expect(page.getByRole("button", { name: "Confirmar importação FPF" })).toBeDisabled();
  await page.getByLabel("Escreva SINCRONIZAR FPF para confirmar").fill("SINCRONIZAR FPF");
  await page.getByRole("button", { name: "Confirmar importação FPF" }).click();
  await expect(page.getByRole("status").filter({ hasText: "Captura aplicada" })).toBeVisible();
  expect(state.applies).toBe(1);
  await page.getByRole("button", { name: "Rever diferenças e ligações" }).click();
  await expect(page.getByRole("region", { name: "Revisão FPF" })).toContainText("Sem alterações");
  await page.getByLabel("Escreva SINCRONIZAR FPF para confirmar").fill("SINCRONIZAR FPF");
  await page.getByRole("button", { name: "Confirmar importação FPF" }).click();
  await expect.poll(() => state.applies).toBe(2);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test("FPF conflitos preservam captura e invalidam confirmação; HTML nunca é executado", async ({ page }) => {
  const state = await mock(page, "ADMIN", true); await page.goto("/competitions/1/fpf");
  await selectCaptures(page); await page.getByRole("button", { name: "Rever diferenças e ligações" }).click();
  state.conflict = true;
  await page.getByLabel("Escreva SINCRONIZAR FPF para confirmar").fill("SINCRONIZAR FPF");
  await page.getByRole("button", { name: "Confirmar importação FPF" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("dados mudaram");
  await expect(page.getByRole("region", { name: "Classificação oficial FPF" }).locator("tbody tr")).toHaveCount(8);
  await page.getByLabel("Ficheiros HTML FPF").setInputFiles({ name: "invalid.html", mimeType: "text/html", buffer: Buffer.from('<script>window.__fpfExecuted=true</script>') });
  await page.getByRole("button", { name: "Validar e identificar ficheiros" }).click();
  await expect(page.getByText("HTML inválido ou indisponível.", { exact: true })).toBeVisible();
  expect(await page.evaluate(() => "__fpfExecuted" in window)).toBe(false);
  expect(state.applies).toBe(0);
});

test("FPF recusa ficheiro excessivo e explica jornada ainda não suportada", async ({ page }) => {
  const state = await mock(page); await page.goto("/competitions/1/fpf");
  await page.getByLabel("Ficheiros HTML FPF").setInputFiles({ name: "big.html", mimeType: "text/html", buffer: Buffer.alloc(2_000_001, 120) });
  await expect(page.getByRole("main").getByRole("alert")).toContainText("máximo 2 MB"); expect(state.inspections).toBe(0);
  state.unsupported = true;
  await page.getByLabel("Ficheiros HTML FPF").setInputFiles({ name: "fixture.html", mimeType: "text/html", buffer: Buffer.from('<div id="classification"></div><div id="matches"></div>') });
  await page.getByRole("button", { name: "Validar e identificar ficheiros" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("formato AJAX ainda não validado");
  await expect(page.getByRole("button", { name: "Rever diferenças e ligações" })).toHaveCount(0);
});

test("FPF resposta inicial tardia não repõe os mapeamentos já revistos", async ({ page }) => {
  let release!: () => void;
  const barrier = new Promise<void>((resolve) => { release = resolve; });
  await mock(page, "ADMIN", false, barrier);
  await page.goto("/competitions/1/fpf"); await selectCaptures(page); await mapTeams(page);
  await page.getByRole("button", { name: "Rever diferenças e ligações" }).click();
  release();
  await expect(page.getByRole("region", { name: "Revisão FPF" })).toBeVisible();
  await expect(page.getByRole("combobox", { name: `Equipa FPF: ${teams[0].name}`, exact: true })).toHaveValue(String(teams[0].id));
});
