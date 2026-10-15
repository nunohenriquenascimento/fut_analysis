import { expect, test } from "./auth-fixture";
import type { Page } from "@playwright/test";
import type { Competition, CompetitionFixture, CompetitionTeam, ParticipantsSelection, Standings } from "../lib/competitions";

const rules = { win: 3, draw: 1, loss: 0, tiebreakers: [] };
const competition: Competition = { id: 1, name: "Liga Dappin 2026/2027", season_id: 17, internal_team_id: 23, rules, provisional: true };
const teams: CompetitionTeam[] = [
  { id: 23, name: "CCDR Vila Cortez do Mondego", crest_path: null, created_at: "2026-10-01T12:00:00Z" },
  { id: 24, name: "Adversário com nome bastante comprido", crest_path: null, created_at: "2026-10-01T12:00:00Z" },
  { id: 25, name: "Visitantes", crest_path: null, created_at: "2026-10-01T12:00:00Z" },
];
const fixtures: CompetitionFixture[] = [
  { id: 11, competition_id: 1, external_key: "externo-j1", matchday: 1, home_team_id: 24, away_team_id: 25,
    kickoff_at: "2026-10-15T14:00:00Z", venue: "Campo visitante", source: "Boletim oficial — edição 1", home_goals: 2, away_goals: 1, internal_match_id: null, status: "FINISHED", created_at: "2026-10-01T12:00:00Z" },
  { id: 12, competition_id: 1, external_key: "nosso-j2", matchday: 2, home_team_id: 23, away_team_id: 24,
    kickoff_at: null, venue: null, source: "Calendário oficial", home_goals: 0, away_goals: 0, internal_match_id: 31, status: "SCHEDULED", created_at: "2026-10-01T12:00:00Z" },
];
const standings: Standings = { provisional: true, warning: "Regulamento por validar.", rules, completed_fixtures: 1,
  // Deliberately use server-provided points/rank which cannot be inferred from the fixtures.
  rows: teams.map((team) => ({ team_id: team.id, name: team.name, rank: 2, unresolved_tie: true, points: 99,
    played: 1, wins: 0, draws: 1, losses: 0, goals_for: 2, goals_against: 2, goal_difference: 0 })) };

async function mock(page: Page, role = "ADMIN") {
  const state = { competitions: [structuredClone(competition)], teams: structuredClone(teams), fixtures: structuredClone(fixtures),
    imports: [] as unknown[], writes: [] as { method: string; path: string; body: unknown }[], failImport: 0, failCreate: false, failRead: false,
    members: structuredClone(teams), staleParticipants: false, participantConflict: false };
  await page.route("http://localhost:8000/**", async (route) => {
    const request = route.request(), url = new URL(request.url()), path = url.pathname, method = request.method();
    const body = method === "POST" || method === "PUT" ? request.postDataJSON() : null;
    if (body) state.writes.push({ method, path, body });
    if (path === "/auth/me") return route.fulfill({ json: { user: { id: 1, name: role, email: "test@test.local", role, is_active: true }, csrf_token: "test-csrf" } });
    if (path === "/players/context") return route.fulfill({ json: { team_id: 23, season_id: 17, season_name: "2026/27", team_name: teams[0].name } });
    if (path === "/teams") {
      if (method === "POST") { const row = { ...teams[1], id: 26, name: body.name }; state.teams.push(row); return route.fulfill({ status: 201, json: row }); }
      return route.fulfill({ json: Number(url.searchParams.get("offset")) > 0 ? [] : state.teams });
    }
    if (path === "/competitions") {
      if (method === "POST") {
        if (state.failCreate) return route.fulfill({ status: 409, json: { detail: "Competição já existente nesta época." } });
        const row = { ...competition, ...body }; state.competitions = [row]; return route.fulfill({ status: 201, json: row });
      }
      if (state.failRead) return route.fulfill({ status: 503, json: { detail: "Indisponível" } });
      return route.fulfill({ json: Number(url.searchParams.get("offset")) > 0 ? [] : state.competitions });
    }
    if (path === "/competitions/1/teams/preview") {
      const selection = body as ParticipantsSelection;
      if (state.staleParticipants) return route.fulfill({ status: 409, json: { detail: "Os participantes foram alterados. Atualize a lista." } });
      const added = state.teams.filter((team) => selection.team_ids.includes(team.id) && !state.members.some((member) => member.id === team.id));
      const removed = state.members.filter((team) => !selection.team_ids.includes(team.id));
      return route.fulfill({ json: { current_team_ids: state.members.map((team) => team.id), proposed_team_ids: selection.team_ids, added, removed,
        can_apply: !state.participantConflict, conflicts: state.participantConflict ? ["Existem jogos dependentes. Não é possível retirar a equipa."] : [] } });
    }
    if (path === "/competitions/1/teams") {
      if (method === "PUT") {
        if (state.staleParticipants) return route.fulfill({ status: 409, json: { detail: "Os participantes foram alterados. Atualize a lista." } });
        if (state.participantConflict) return route.fulfill({ status: 409, json: { detail: "Existe um jogo novo dependente. Nenhuma alteração foi gravada." } });
        state.members = state.teams.filter((team) => body.team_ids.includes(team.id));
      }
      return route.fulfill({ json: state.members });
    }
    if (path === "/competitions/1/standings") return route.fulfill({ json: standings });
    if (path === "/competitions/1/calendar") return route.fulfill({ json: state.fixtures });
    if (path === "/competitions/1/matchdays") return route.fulfill({ json: [1, 2].map((matchday) => ({ matchday, fixtures: state.fixtures.filter((row) => row.matchday === matchday) })) });
    if (path === "/competitions/1/rules") { state.competitions[0].rules = body; return route.fulfill({ json: { ...competition, rules: body } }); }
    if (path === "/competitions/1/fixtures/import") {
      state.imports.push(body);
      if (state.failImport === 422) return route.fulfill({ status: 422, json: { detail: [{ loc: ["body", "fixtures", 0, "source"], msg: "Field required" }] } });
      if (state.failImport === 409) return route.fulfill({ status: 409, json: { detail: "Resultados internos não podem ser substituídos." } });
      for (const row of body.fixtures) {
        const index = state.fixtures.findIndex((existing) => existing.external_key === row.external_key);
        if (index >= 0) state.fixtures[index] = { ...state.fixtures[index], ...row, status: "FINISHED" };
      }
      return route.fulfill({ json: { imported: body.fixtures.length } });
    }
    return route.fulfill({ status: 404, json: { detail: "Não encontrado" } });
  });
  return state;
}

async function fits(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  expect(await page.locator("main button:visible, main select:visible").evaluateAll((items) => items.filter((item) => item.getBoundingClientRect().height < 44).map((item) => item.textContent))).toEqual([]);
}

for (const width of [360, 390, 1280]) {
  test(`Campeonato: classificação, jornadas, calendário e equipas a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 850 });
    await mock(page, "VIEWER");
    await page.goto("/competitions");
    await page.getByRole("link", { name: /Liga Dappin/ }).click();
    await expect(page.getByRole("heading", { name: "Classificação provisória", exact: true })).toBeVisible();
    await expect(page.getByRole("cell", { name: "99", exact: true })).toHaveCount(3);
    await expect(page.getByText("Empate por resolver", { exact: true })).toHaveCount(3);
    await fits(page);
    await page.getByRole("navigation", { name: "Campeonato", exact: true }).getByRole("link", { name: "Resultados" }).click();
    await expect(page.getByRole("region", { name: "Jornada 1", exact: true })).toBeVisible();
    await page.getByLabel("Jornada", { exact: true }).selectOption("2");
    await expect(page.getByRole("region", { name: "Jornada 1", exact: true })).toHaveCount(0);
    await expect(page.getByText("Data por definir")).toBeVisible();
    await fits(page);
    await page.getByRole("navigation", { name: "Campeonato", exact: true }).getByRole("link", { name: "Calendário" }).click();
    await expect(page.locator(".fixture-card")).toHaveCount(2);
    await fits(page);
    await page.locator(".fixture-card").first().click();
    await expect(page.getByText("Boletim oficial — edição 1", { exact: true })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Corrigir resultado externo" })).toHaveCount(0);
    await fits(page);
    await page.getByRole("navigation", { name: "Campeonato", exact: true }).getByRole("link", { name: "Equipas", exact: true }).click();
    await expect(page.getByRole("region", { name: "Participantes" }).getByRole("listitem")).toHaveCount(3);
    await fits(page);
    await page.screenshot({ path: `artifacts/competitions/teams-${width}.png`, fullPage: true });
  });
}

for (const role of ["ADMIN", "COACH", "VIEWER"]) {
  test(`Campeonato: permissões de ${role}`, async ({ page }) => {
    const state = await mock(page, role);
    await page.goto("/competitions");
    await expect(page.getByRole("link", { name: /Liga Dappin/ })).toBeVisible();
    await expect(page.getByRole("button", { name: "Criar competição", exact: true })).toHaveCount(role === "VIEWER" ? 0 : 1);
    await page.goto("/competitions/1/manage");
    if (role === "VIEWER") {
      await expect(page.getByRole("main").getByRole("alert")).toContainText("ADMIN ou COACH");
      await expect(page.getByLabel("Conteúdo JSON")).toHaveCount(0);
    } else await expect(page.getByLabel("Conteúdo JSON")).toBeVisible();
    await expect(page.getByRole("region", { name: "Gestão de participantes", exact: true })).toHaveCount(role === "ADMIN" ? 1 : 0);
    await page.goto("/competitions/1/fixtures/12");
    await expect(page.getByRole("link", { name: "Abrir o nosso jogo" })).toHaveAttribute("href", "/matches/31");
    await expect(page.getByRole("heading", { name: "Corrigir resultado externo" })).toHaveCount(0);
    expect(state.writes).toEqual([]);
  });
}

test("Criar competição e associar participantes, sem perder campos após 409", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 850 });
  const state = await mock(page); state.competitions = []; state.failCreate = true;
  await page.goto("/competitions");
  await page.getByRole("button", { name: "Criar competição", exact: true }).click();
  await page.getByLabel("Nome da competição").fill("Liga distrital");
  await page.getByLabel(teams[1].name, { exact: true }).check();
  await page.getByLabel("Nova equipa adversária").fill("Novo adversário");
  await page.getByRole("button", { name: "Adicionar equipa à seleção" }).click();
  await expect(page.getByLabel("Novo adversário", { exact: true })).toBeChecked();
  await fits(page);
  await page.getByRole("button", { name: "Criar e associar equipas" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("já existente");
  await expect(page.getByLabel("Nome da competição")).toHaveValue("Liga distrital");
  state.failCreate = false;
  await page.getByRole("button", { name: "Criar e associar equipas" }).click();
  await expect(page).toHaveURL(/\/competitions\/1$/);
  const saved = state.writes.filter((row) => row.path === "/competitions").at(-1)!.body;
  expect(saved).toMatchObject({ name: "Liga distrital", season_id: 17, internal_team_id: 23, team_ids: [23, 24, 26], rules });
});

test("Configuração provisória preserva a ordem explícita dos desempates", async ({ page }) => {
  const state = await mock(page);
  await page.goto("/competitions/1/manage");
  await page.getByLabel("Vitória", { exact: true }).fill("2");
  await page.getByLabel("Adicionar critério").selectOption("head_to_head_points");
  await page.getByLabel("Adicionar critério").selectOption("goal_difference");
  await page.getByRole("button", { name: "Subir Diferença de golos global", exact: true }).click();
  await page.getByRole("button", { name: "Guardar configuração" }).click();
  await expect(page.getByRole("status")).toContainText("continua provisória");
  expect(state.writes.at(-1)).toMatchObject({ method: "PUT", path: "/competitions/1/rules", body: { win: 2, draw: 1, loss: 0, tiebreakers: ["goal_difference", "head_to_head_points"] } });
});

test("Importação JSON exige revisão, preserva conteúdo após erros e mostra origem", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 850 });
  const state = await mock(page);
  await page.goto("/competitions/1/manage");
  await page.getByLabel("Conteúdo JSON").fill("{bad");
  await page.getByRole("button", { name: "Rever importação" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("JSON inválido");
  expect(state.imports).toHaveLength(0);
  const body = { fixtures: [{ external_key: "externo-j1", matchday: 1, home_team_id: 24, away_team_id: 25, home_goals: 4, away_goals: 2, source: "Retificação oficial" }] };
  await page.getByLabel("Conteúdo JSON").fill(JSON.stringify(body));
  await page.getByRole("button", { name: "Rever importação" }).click();
  expect(state.imports).toHaveLength(0);
  await fits(page);
  state.failImport = 422;
  await page.getByRole("button", { name: "Confirmar importação" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("fixtures → 0 → source");
  await expect(page.getByLabel("Conteúdo JSON")).toHaveValue(JSON.stringify(body));
  state.failImport = 409;
  await page.getByRole("button", { name: "Confirmar importação" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Resultados internos não podem ser substituídos");
  state.failImport = 0;
  await page.getByRole("button", { name: "Confirmar importação" }).click();
  await expect(page.getByRole("status")).toContainText("Importação concluída: 1");
  await page.getByRole("link", { name: "Consultar resultados atualizados" }).click();
  await page.locator(".fixture-card").first().click();
  await expect(page.getByLabel("Resultado do jogo", { exact: true })).toHaveText("4 – 2");
  await expect(page.getByText("Retificação oficial", { exact: true })).toBeVisible();
  expect(state.writes.every((row) => !row.path.startsWith("/matches"))).toBe(true);
});

test("Importar ficheiro e editar JSON invalida a revisão anterior", async ({ page }) => {
  const state = await mock(page);
  await page.goto("/competitions/1/manage");
  await page.getByLabel("Ficheiro JSON").setInputFiles({ name: "results.json", mimeType: "application/json", buffer: Buffer.from(JSON.stringify({ fixtures: [fixtures[0]] })) });
  await page.getByRole("button", { name: "Rever importação" }).click();
  await expect(page.getByRole("button", { name: "Confirmar importação" })).toBeVisible();
  await page.getByLabel("Conteúdo JSON").fill("{}");
  await expect(page.getByRole("button", { name: "Confirmar importação" })).toHaveCount(0);
  expect(state.imports).toHaveLength(0);
});

test("Correção externa mantém identidade, consulta o servidor e conserva campos após erro", async ({ page }) => {
  const state = await mock(page); state.failImport = 409;
  await page.goto("/competitions/1/fixtures/11");
  await page.getByLabel("Golos da equipa da casa").fill("5");
  await page.getByLabel("Golos da equipa visitante").fill("3");
  await page.getByLabel("Origem da correção").fill("Boletim corrigido");
  await page.getByRole("button", { name: "Guardar resultado externo" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toBeVisible();
  await expect(page.getByLabel("Golos da equipa da casa")).toHaveValue("5");
  state.failImport = 0;
  await page.getByRole("button", { name: "Guardar resultado externo" }).click();
  await expect(page.getByLabel("Resultado do jogo", { exact: true })).toHaveText("5 – 3");
  await expect(page.getByText("Boletim corrigido", { exact: true })).toBeVisible();
  expect(state.imports.at(-1)).toEqual({ fixtures: [{ external_key: "externo-j1", matchday: 1, home_team_id: 24, away_team_id: 25, kickoff_at: fixtures[0].kickoff_at, venue: "Campo visitante", internal_match_id: null, home_goals: 5, away_goals: 3, source: "Boletim corrigido" }] });
});

test("Estados vazios, indisponibilidade, retry e jogo inexistente", async ({ page }) => {
  const state = await mock(page); state.failRead = true;
  await page.goto("/competitions");
  await expect(page.getByRole("main").getByRole("alert")).toContainText("indisponível");
  state.failRead = false; state.competitions = [];
  await page.getByRole("button", { name: "Tentar novamente" }).click();
  await expect(page.getByText("Ainda não existem competições configuradas.")).toBeVisible();
  await page.goto("/competitions/99");
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Competição não encontrada");
  state.competitions = [competition]; state.fixtures = [];
  await page.goto("/competitions/1/calendar");
  await expect(page.getByText("Ainda não existem jogos no calendário.")).toBeVisible();
  await page.goto("/competitions/1/fixtures/999");
  await expect(page.getByText("Jogo não encontrado nesta competição.")).toBeVisible();
});

test("ADMIN revê, confirma e atualiza participantes sem eliminar equipas", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 850 });
  const state = await mock(page);
  state.teams.push({ ...teams[1], id: 26, name: "Equipa disponível" });
  await page.goto("/competitions/1/manage");
  const form = page.getByRole("region", { name: "Gestão de participantes", exact: true });
  await expect(form.getByLabel(/CCDR Vila Cortez.*Nossa equipa/)).toBeDisabled();
  await form.getByLabel("Equipa disponível", { exact: true }).check();
  await form.getByRole("button", { name: "Rever alteração de participantes", exact: true }).click();
  await expect(form.getByText("Adicionar: Equipa disponível", { exact: true })).toBeVisible();
  expect(state.writes.filter((row) => row.method === "PUT")).toHaveLength(0);
  const confirm = form.getByRole("button", { name: "Confirmar alteração de participantes", exact: true });
  await expect(confirm).toBeDisabled();
  await form.getByLabel("Escreva ALTERAR PARTICIPANTES para confirmar").fill("ALTERAR PARTICIPANTES");
  await fits(page);
  await confirm.click();
  await expect(form.getByRole("status")).toHaveText("Participantes atualizados.");
  expect(state.members.map((team) => team.id)).toEqual([23, 24, 25, 26]);
  expect(state.writes.find((row) => row.method === "PUT")).toMatchObject({ path: "/competitions/1/teams", body: {
    team_ids: [23, 24, 25, 26], expected_team_ids: [23, 24, 25], confirmation: "ALTERAR PARTICIPANTES" } });
  await form.getByLabel("Equipa disponível", { exact: true }).uncheck();
  await form.getByRole("button", { name: "Rever alteração de participantes", exact: true }).click();
  await expect(form.getByText("Retirar: Equipa disponível", { exact: true })).toBeVisible();
  await form.getByLabel("Escreva ALTERAR PARTICIPANTES para confirmar").fill("ALTERAR PARTICIPANTES");
  await form.getByRole("button", { name: "Confirmar alteração de participantes", exact: true }).click();
  await expect(form.getByRole("status")).toHaveText("Participantes atualizados.");
  expect(state.members.map((team) => team.id)).toEqual([23, 24, 25]);
  expect(state.teams.some((team) => team.id === 26)).toBe(true);
});

test("Participantes: dependências, revisão invalidada e conflito após preview", async ({ page }) => {
  const state = await mock(page);
  await page.goto("/competitions/1/manage");
  const form = page.getByRole("region", { name: "Gestão de participantes", exact: true });
  await form.getByLabel("Visitantes", { exact: true }).uncheck();
  state.participantConflict = true;
  await form.getByRole("button", { name: "Rever alteração de participantes", exact: true }).click();
  await expect(form.getByRole("alert")).toContainText("jogos dependentes");
  await expect(form.getByRole("button", { name: "Confirmar alteração de participantes", exact: true })).toHaveCount(0);
  state.participantConflict = false;
  await form.getByRole("button", { name: "Rever alteração de participantes", exact: true }).click();
  await form.getByLabel("Visitantes", { exact: true }).check();
  await expect(form.getByLabel("Escreva ALTERAR PARTICIPANTES para confirmar")).toHaveCount(0);
  await form.getByLabel("Visitantes", { exact: true }).uncheck();
  await form.getByRole("button", { name: "Rever alteração de participantes", exact: true }).click();
  await form.getByLabel("Escreva ALTERAR PARTICIPANTES para confirmar").fill("ALTERAR PARTICIPANTES");
  state.staleParticipants = true;
  await form.getByRole("button", { name: "Confirmar alteração de participantes", exact: true }).click();
  await expect(form.getByRole("alert")).toContainText("Atualize a lista");
  await expect(form.getByLabel("Escreva ALTERAR PARTICIPANTES para confirmar")).toHaveCount(0);
  expect(state.members).toHaveLength(3);
});
