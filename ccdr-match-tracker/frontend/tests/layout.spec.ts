import { expect, test } from "./auth-fixture";
import type { Page } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import { join } from "node:path";
import type { Match, Player, RosterContext } from "../lib/api";
import type { LiveState } from "../lib/live";
import type { EventTotals, SeasonStatistics } from "../lib/statistics";

const timestamp = "2026-10-02T12:00:00Z";
const context: RosterContext = { season_id: 17, team_id: 23, season_name: "2026/27", team_name: "CCDR Vila Cortez do Mondego", team_crest_path: "/clubs/ccdr-vila-cortez/crest.png" };
const players: Player[] = [
  { id: 7, name: "João Silva", position: "MC", shirt_number: 8, is_active: true, photo_path: "/players/jogador-8.webp", season_id: 17, team_id: 23, created_at: timestamp },
  { id: 8, name: "Álvaro Gonçalves", position: "PL", shirt_number: 9, is_active: false, photo_path: null, season_id: 17, team_id: 23, created_at: timestamp },
];
const match: Match = { id: 31, season_id: 17, team_id: 23, opponent_id: 24, opponent_name: "Adversário com um nome longo para testar o telemóvel", matchday: 3, kickoff_at: timestamp, is_home: true, venue: "Campo de Vila Cortez", status: "SECOND_HALF", elapsed_seconds: 3804, clock_started_at: timestamp, created_at: timestamp, team_crest_path: context.team_crest_path, opponent_crest_path: "/teams/adversario.png", score: { us: 2, opponent: 1 } };
const zero: EventTotals = { goals: 0, shots_on_target: 0, shots_off_target: 0, shots_blocked: 0, shots_total: 0, corners: 0, free_kicks: 0, fouls: 0, offsides: 0, penalties: 0, yellow_cards: 0, red_cards: 0, saves: 0 };
const comparison = { us: { ...zero, goals: 2 }, opponent: { ...zero, goals: 1 } };
const live: LiveState = { match, score: match.score!, server_now: timestamp, clock_elapsed_seconds: 3804, period: 2, events: [{ id: 1, match_id: 31, event_type: "GOAL", team: "US", player_id: 7, related_player_id: 8, period: 2, elapsed_seconds: 3660, created_at: timestamp }], squad: players };
const season: SeasonStatistics = {
  context, scope: { competitive: "FINISHED", events: "ALL_MATCHES_WITH_EVENTS", callups: "ALL_MATCHES_INCLUDING_SCHEDULED" }, total_matches: 1, matches_with_events: 1, total_events: 1,
  competitive: { matches: 0, wins: 0, draws: 0, losses: 0, goals_for: 0, goals_against: 0, goal_difference: 0 }, comparison,
  players: players.map((player, index) => ({ player, matches_called_up: 1, matches_started: index === 0 ? 1 : 0, goals: index === 0 ? 1 : 0, assists: index === 1 ? 1 : 0, shots_on_target: 0, shots_off_target: 0, shots_blocked: 0, shots_total: 0, yellow_cards: 0, red_cards: 0, fouls: 0, offsides: 0 })),
  rankings: { goals: [{ player_id: 7, name: players[0].name, value: 1 }], assists: [{ player_id: 8, name: players[1].name, value: 1 }], shots_total: [], yellow_cards: [], red_cards: [] },
};
const pixel = Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aV1kAAAAASUVORK5CYII=", "base64");

async function mock(page: Page, broken = false) {
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (["/clubs/ccdr-vila-cortez/crest.png", "/teams/adversario.png", "/players/jogador-8.webp"].includes(url.pathname)) {
      return route.fulfill(broken ? { status: 404, body: "" } : { contentType: "image/png", body: pixel });
    }
    if (url.port !== "8000") return route.continue();
    const path = url.pathname;
    const data = path === "/auth/me" ? { user: { id: 1, name: "Admin", email: "admin@test.local", role: "ADMIN", is_active: true }, csrf_token: "test-csrf" } : path === "/players/context" ? context : path === "/players" ? players : path === "/matches" ? [match, { ...match, id: 32, opponent_name: "Equipa sem emblema", opponent_crest_path: null, status: "SCHEDULED", score: undefined }]
      : path === "/matches/31" ? match : path === "/matches/31/squad" ? players.map((player, index) => ({ player, role: index ? "SUPLENTE" : "TITULAR" }))
      : path === "/matches/31/live" ? live : path === "/matches/31/stats" ? { match, team_name: context.team_name, score: match.score, is_final: false, total_events: 1, comparison, timeline: live.events, players }
      : path === "/statistics/season" ? season : null;
    return route.fulfill({ status: data ? 200 : 404, json: data ?? { detail: "Não encontrado" } });
  });
}

async function fits(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  const smallTargets = await page.locator("main button:visible, main select:visible").evaluateAll((elements) => elements.filter((el) => el.getBoundingClientRect().height < 44).map((el) => el.textContent));
  expect(smallTargets).toEqual([]);
}

for (const width of [360, 390, 430, 768, 1280]) {
  test(`Layout e media: todas as páginas a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 850 });
    await mock(page);
    const preview = join("artifacts", "layout", String(width));
    await mkdir(preview, { recursive: true });
    await page.goto("/");
    await expect(page.getByRole("heading", { name: context.team_name, exact: true })).toBeVisible();
    await expect(page.getByRole("main").getByRole("link")).toHaveCount(5);
    await expect(page.getByRole("main").getByRole("img", { name: `Emblema de ${context.team_name}` })).toBeVisible();
    // Keyboard navigation starts with a visible skip link and reaches the content.
    await page.keyboard.press("Tab");
    await expect(page.getByRole("link", { name: "Saltar para o conteúdo" })).toBeFocused();
    await page.keyboard.press("Enter");
    await expect(page.getByRole("main")).toBeFocused();
    await fits(page);
    await page.screenshot({ path: join(preview, "home.png"), fullPage: true });

    await page.goto("/players");
    await expect(page.locator("article")).toHaveCount(2);
    await expect(page.locator("article").first().locator("img")).toHaveAttribute("src", "/players/jogador-8.webp");
    await expect(page.locator("article").last().getByRole("img")).toHaveText("ÁG");
    await expect(page.locator("article").last()).toContainText("Inativo");
    await expect(page.getByLabel("Nome", { exact: true })).toHaveCount(0);
    await page.getByRole("button", { name: "Adicionar jogador", exact: true }).click();
    await expect(page.getByLabel("Caminho da foto (opcional)")).toBeVisible();
    await page.getByRole("button", { name: "Fechar formulário" }).click();
    await fits(page);
    await page.screenshot({ path: join(preview, "players.png"), fullPage: true });

    await page.goto("/matches");
    const games = page.getByRole("region", { name: "Jogos", exact: true });
    await expect(games.getByLabel("Resultado")).toHaveText("2 – 1");
    await expect(games.locator('img[src="/teams/adversario.png"]')).toBeVisible();
    await expect(games.getByRole("img", { name: "Emblema de Equipa sem emblema" })).toHaveText("—");
    await fits(page);
    await page.screenshot({ path: join(preview, "matches.png"), fullPage: true });

    await page.goto("/matches/31");
    await expect(page.getByLabel("Contadores da convocatória")).toContainText("Titulares: 1");
    await expect(page.getByRole("region", { name: "Convocatória", exact: true }).locator("img")).toHaveAttribute("src", "/players/jogador-8.webp");
    await page.getByLabel(`Convocatória de ${players[1].name}`).selectOption("NAO_CONVOCADO");
    await expect(page.getByLabel("Contadores da convocatória")).toContainText("Total convocados: 1");
    await fits(page);
    await page.screenshot({ path: join(preview, "squad.png"), fullPage: true });

    await page.goto("/matches/31/live");
    await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("2 – 1");
    await expect(page.getByLabel("Cronómetro")).toContainText("63:");
    const own = page.getByRole("region", { name: "Nossa equipa", exact: true });
    await expect(own.getByRole("heading", { name: "Ofensivos", exact: true })).toBeVisible();
    await fits(page);
    await page.screenshot({ path: join(preview, "live.png"), fullPage: true });
    await own.getByRole("button", { name: "Golo", exact: true }).click();
    await page.getByRole("dialog").getByRole("combobox", { name: "Marcador", exact: true }).selectOption("7");
    await expect(page.getByRole("dialog").getByRole("img", { name: "Foto de João Silva" })).toBeVisible();
    await page.getByLabel("Assistência (opcional)").selectOption("8");
    await expect(page.getByRole("dialog").getByRole("img", { name: "Foto de Álvaro Gonçalves" })).toHaveText("ÁG");
    await fits(page);
    await page.getByRole("dialog").getByRole("button", { name: "Cancelar", exact: true }).click();

    await page.goto("/statistics");
    const scorers = page.getByRole("region", { name: "Melhores marcadores", exact: true });
    await expect(scorers.locator("img")).toHaveAttribute("src", "/players/jogador-8.webp");
    await expect(page.getByRole("region", { name: "Mais assistências", exact: true }).getByRole("img")).toHaveText("ÁG");
    await page.locator("summary").filter({ hasText: "João Silva" }).click();
    await expect(page.locator("details[open]").locator("img")).toBeVisible();
    await fits(page);
    await page.screenshot({ path: join(preview, "statistics.png"), fullPage: true });

    await page.goto("/matches/31/stats");
    await expect(page.getByRole("heading", { name: "Estatísticas do jogo", exact: true })).toBeVisible();
    await expect(page.getByRole("main").locator('img[src="/teams/adversario.png"]')).toBeVisible();
    await expect(page.getByRole("region", { name: "Timeline resumida" })).toContainText("Assistência: Álvaro Gonçalves");
    await fits(page);
    await page.screenshot({ path: join(preview, "match-statistics.png"), fullPage: true });
  });
}

test("Media: ficheiros em falta e contraste da paleta em 360px", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 850 });
  await mock(page, true);
  await page.goto("/players");
  await expect(page.locator("article").first().getByRole("img")).toHaveText("JS");
  await expect(page.locator("article").first().locator("img")).toHaveCount(0);
  await expect(page.getByRole("banner").getByRole("img")).toHaveText("—");
  await fits(page);
  const ratios = await page.evaluate(() => {
    const css = getComputedStyle(document.documentElement);
    const luminance = (token: string) => {
      const raw = css.getPropertyValue(token).trim().slice(1);
      // The production CSS minifier shortens white to #fff.
      const hex = raw.length === 3 ? [...raw].map((digit) => digit + digit).join("") : raw;
      const rgb = [0, 2, 4].map((offset) => parseInt(hex.slice(offset, offset + 2), 16) / 255).map((value) => value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4);
      return rgb[0] * .2126 + rgb[1] * .7152 + rgb[2] * .0722;
    };
    return [["--foreground", "--background"], ["--muted", "--surface"], ["--muted", "--surface-raised"], ["--on-secondary", "--secondary"], ["--secondary", "--secondary-surface"], ["--on-accent", "--accent"], ["--on-primary", "--primary"], ["--success", "--success-surface"], ["--warning", "--warning-surface"], ["--error", "--error-surface"]].map(([a, b]) => {
      const first = luminance(a), second = luminance(b);
      return (Math.max(first, second) + .05) / (Math.min(first, second) + .05);
    });
  });
  for (const ratio of ratios) expect(ratio).toBeGreaterThanOrEqual(4.5);
  await page.goto("/matches/31/stats");
  await expect(page.getByRole("main").getByRole("img", { name: `Emblema de ${match.opponent_name}` })).toHaveText("—");
  await fits(page);
});
