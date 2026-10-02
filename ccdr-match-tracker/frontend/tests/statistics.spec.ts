import { expect, test } from "./auth-fixture";
import type { EventTotals, MatchStatistics, PlayerStatistics, SeasonStatistics } from "../lib/statistics";

const zero: EventTotals = { goals: 0, shots_on_target: 0, shots_off_target: 0, shots_blocked: 0, shots_total: 0,
  corners: 0, free_kicks: 0, fouls: 0, offsides: 0, penalties: 0, yellow_cards: 0, red_cards: 0, saves: 0 };
const player: PlayerStatistics = {
  player: { id: 7, name: "Jorge", shirt_number: 9, position: "PL", team_id: 23, season_id: 17, is_active: true, created_at: "2026-10-01T12:00:00Z" },
  matches_called_up: 2, matches_started: 1, goals: 1, assists: 0, shots_on_target: 1, shots_off_target: 1,
  shots_blocked: 0, shots_total: 2, yellow_cards: 1, red_cards: 0, fouls: 2, offsides: 1,
};
const season: SeasonStatistics = {
  context: { season_id: 17, team_id: 23, season_name: "2026/27", team_name: "CCDR Vila Cortez do Mondego" },
  scope: { competitive: "FINISHED", events: "ALL_MATCHES_WITH_EVENTS", callups: "ALL_MATCHES_INCLUDING_SCHEDULED" },
  total_matches: 2, matches_with_events: 1, total_events: 6,
  competitive: { matches: 1, wins: 1, draws: 0, losses: 0, goals_for: 1, goals_against: 0, goal_difference: 1 },
  comparison: { us: { ...zero, goals: 1, shots_on_target: 1, shots_off_target: 1, shots_total: 2, corners: 2, yellow_cards: 1 }, opponent: { ...zero } },
  players: [player], rankings: { goals: [{ player_id: 7, name: "Jorge", value: 1 }], assists: [],
    shots_total: [{ player_id: 7, name: "Jorge", value: 2 }], yellow_cards: [{ player_id: 7, name: "Jorge", value: 1 }], red_cards: [] },
};
const match: MatchStatistics = {
  match: { id: 31, season_id: 17, team_id: 23, opponent_id: 24, opponent_name: "Visitantes", matchday: 1,
    kickoff_at: "2026-10-04T14:00:00Z", is_home: true, venue: "Campo", status: "FINISHED", elapsed_seconds: 5400,
    clock_started_at: null, created_at: "2026-10-01T12:00:00Z" },
  team_name: season.context.team_name, score: { us: 1, opponent: 0 }, is_final: true,
  total_events: 1, comparison: { us: { ...zero, goals: 1 }, opponent: { ...zero } },
  players: [player.player], timeline: [{ id: 1, match_id: 31, event_type: "GOAL", team: "US", player_id: 7,
    related_player_id: null, period: 1, elapsed_seconds: 2040, created_at: "2026-10-04T14:34:00Z" }],
};

for (const width of [360, 1280]) {
  test(`Estatísticas: época, rankings, jogador e jogo a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 800 });
    await page.route("**/statistics/season", (route) => route.fulfill({ json: season }));
    await page.route("**/matches/31**", (route) => {
      if (route.request().isNavigationRequest() || !route.request().url().includes(":8000/")) return route.continue();
      const path = new URL(route.request().url()).pathname;
      return route.fulfill({ json: path.endsWith("/stats") ? match : path.endsWith("/squad") ? [] : match.match });
    });
    await page.goto("/");
    await page.getByRole("main").getByRole("link", { name: /Estatísticas/ }).click();
    await expect(page.getByRole("heading", { name: "Estatísticas", exact: true })).toBeVisible();
    const competitive = page.getByRole("region", { name: "Resumo competitivo" });
    await expect(competitive).toContainText("Apenas jogos terminados");
    await expect(competitive.locator("dl > div").filter({ hasText: "Vitórias" }).locator("dd")).toHaveText("1");
    const activity = page.getByRole("region", { name: "Atividade da época" });
    await expect(activity).toContainText("incluindo jogos em curso ou cancelados");
    await expect(activity.getByRole("row", { name: "Remates totais 2 0", exact: true })).toBeVisible();
    await expect(page.getByRole("region", { name: "Melhores marcadores", exact: true })).toContainText("Jorge");
    await expect(page.getByRole("region", { name: "Mais assistências", exact: true })).toContainText("Sem registos.");
    await page.locator("summary").filter({ hasText: "Jorge" }).click();
    const details = page.locator("details").filter({ hasText: "Jorge" });
    await expect(details.locator("dl > div").filter({ hasText: "Jogos convocado" }).locator("dd")).toHaveText("2");
    await expect(details.locator("dl > div").filter({ hasText: "Jogos titular" }).locator("dd")).toHaveText("1");
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await page.goto("/matches/31");
    await page.getByRole("link", { name: "Ver estatísticas", exact: true }).click();
    await expect(page.getByRole("heading", { name: "Estatísticas do jogo", exact: true })).toBeVisible();
    await expect(page.getByText("Resultado final · Terminado")).toBeVisible();
    await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("1 – 0");
    await expect(page.getByRole("columnheader", { name: "Visitantes", exact: true })).toBeVisible();
    await expect(page.getByRole("row", { name: "Remates totais 0 0", exact: true })).toBeVisible();
    await expect(page.getByRole("region", { name: "Timeline resumida" })).toContainText("34' — Golo — Jorge");
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  });
}

test("Estatísticas: loading, falha, retry e época sem dados em 360px", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  let fail = true;
  let release!: () => void;
  const ready = new Promise<void>((resolve) => { release = resolve; });
  const empty: SeasonStatistics = { ...season, total_matches: 0, matches_with_events: 0, total_events: 0,
    competitive: { matches: 0, wins: 0, draws: 0, losses: 0, goals_for: 0, goals_against: 0, goal_difference: 0 },
    comparison: { us: zero, opponent: zero }, players: [],
    rankings: { goals: [], assists: [], shots_total: [], yellow_cards: [], red_cards: [] } };
  await page.route("**/statistics/season", async (route) => {
    await ready;
    return route.fulfill({ status: fail ? 503 : 200, json: fail ? { detail: "Base de dados indisponível." } : empty });
  });
  await page.goto("/statistics");
  await expect(page.getByText("A carregar estatísticas…")).toBeVisible();
  release();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("base de dados está indisponível");
  fail = false;
  await page.getByRole("button", { name: "Atualizar estatísticas" }).click();
  await expect(page.getByText("Ainda não existem jogos nesta época.", { exact: true })).toBeVisible();
  await expect(page.getByText("Ainda não existem jogadores nesta época.", { exact: true })).toBeVisible();
  await expect(page.getByRole("region", { name: "Melhores marcadores", exact: true })).toContainText("Sem registos.");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test("Estatísticas: jogo sem eventos e jogo inexistente", async ({ page }) => {
  let missing = false;
  await page.route("**/matches/31/stats", (route) => {
    if (route.request().isNavigationRequest()) return route.continue();
    return route.fulfill({ status: missing ? 404 : 200, json: missing ? { detail: "Jogo não encontrado." } : {
      ...match, is_final: false, match: { ...match.match, status: "SCHEDULED" }, score: { us: 0, opponent: 0 },
      total_events: 0, timeline: [], players: [], comparison: { us: zero, opponent: zero },
    } });
  });
  await page.goto("/matches/31/stats");
  await expect(page.getByText("Resultado atual · Agendado")).toBeVisible();
  await expect(page.getByText("Ainda não existem acontecimentos neste jogo.")).toBeVisible();
  missing = true;
  await page.reload();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Jogo não encontrado.");
});
