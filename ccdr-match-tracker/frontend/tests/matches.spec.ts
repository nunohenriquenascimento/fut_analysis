import { expect, test } from "./auth-fixture";
import type { Match, SquadEntry, SquadPlayer } from "../lib/api";

const baseMatch: Match = {
  id: 31, season_id: 17, team_id: 23, opponent_id: 24, opponent_name: "Clube visitante",
  matchday: 1, kickoff_at: "2026-10-04T14:00:00Z", is_home: true, venue: "Campo municipal",
  status: "SCHEDULED", elapsed_seconds: 0, clock_started_at: null, created_at: "2026-10-01T12:00:00Z",
};
const baseSquad: SquadPlayer[] = ["João", "Miguel", "Pedro"].map((name, index) => ({
  player: { id: index + 1, name, shirt_number: index + 1, position: "MC", season_id: 17,
    team_id: 23, is_active: true, created_at: "2026-10-01T12:00:00Z" }, role: "NAO_CONVOCADO",
}));

for (const width of [360, 1280]) {
  test(`Jogos e convocatórias: criar, editar e guardar a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 800 });
    const games = [{ ...baseMatch }];
    let rows = structuredClone(baseSquad);
    let postCount = 0;
    let putCount = 0;
    let lastSquad: SquadEntry[] = [];
    let releaseCreate!: () => void;
    const createReady = new Promise<void>((resolve) => { releaseCreate = resolve; });
    await page.route("**/players/context", (route) => route.fulfill({ json: {
      season_id: 17, team_id: 23, season_name: "2026/27", team_name: "CCDR Vila Cortez do Mondego",
    } }));
    await page.route("**/matches**", async (route) => {
      const request = route.request();
      if (request.isNavigationRequest() || !request.url().includes(":8000/")) return route.continue();
      const url = new URL(request.url());
      if (url.pathname.endsWith("/squad")) {
        if (request.method() === "PUT") {
          putCount++;
          lastSquad = request.postDataJSON().players;
          rows = rows.map((row) => {
            const entry = lastSquad.find((value) => value.player_id === row.player.id);
            return { ...row, role: entry ? entry.is_starter ? "TITULAR" : "SUPLENTE" : "NAO_CONVOCADO" };
          });
        }
        return route.fulfill({ json: rows });
      }
      if (url.pathname === "/matches") {
        if (request.method() === "POST") {
          postCount++;
          await createReady;
          const body = request.postDataJSON();
          expect(body.season_id).toBe(17); expect(body.team_id).toBe(23);
          expect(body.kickoff_at).toMatch(/Z$/);
          const created = { ...baseMatch, ...body, id: 32, opponent_id: 25 };
          games.push(created);
          return route.fulfill({ status: 201, json: created });
        }
        expect(url.searchParams.get("season_id")).toBe("17");
        expect(url.searchParams.get("team_id")).toBe("23");
        return route.fulfill({ json: games });
      }
      const game = games.find((row) => row.id === Number(url.pathname.split("/").pop()));
      if (!game) return route.fulfill({ status: 404, json: { detail: "Jogo não encontrado." } });
      if (request.method() === "PATCH") Object.assign(game, request.postDataJSON());
      return route.fulfill({ json: game });
    });

    await page.goto("/");
    await page.getByRole("main").getByRole("link", { name: /Jogos Preparar jornadas/ }).click();
    await expect(page.getByRole("heading", { name: "Jogos e jornadas" })).toBeVisible();
    await expect(page.getByRole("link", { name: /Clube visitante/ })).toContainText("Jornada 1");
    await page.getByRole("link", { name: /Clube visitante/ }).click();
    await expect(page.getByRole("heading", { name: "Clube visitante", exact: true })).toBeVisible();
    await page.getByRole("link", { name: "← Jogos" }).click();
    await page.getByRole("button", { name: "Criar jogo", exact: true }).click();
    await page.getByLabel("Jornada", { exact: true }).fill("2");
    await page.getByLabel("Adversário", { exact: true }).fill("Clube novo");
    await page.getByLabel("Data", { exact: true }).fill("2026-10-11");
    await page.getByLabel("Hora (fuso do dispositivo)").fill("15:30");
    await page.getByLabel("Casa ou fora").selectOption("away");
    await page.getByLabel("Local", { exact: true }).fill("Campo visitante");
    await page.getByRole("button", { name: "Criar jogo", exact: true }).click();
    await expect(page.getByRole("button", { name: "A guardar…" })).toBeDisabled();
    await expect.poll(() => postCount).toBe(1);
    await page.locator("form").evaluate((form) => {
      form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
      form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
    });
    expect(postCount).toBe(1);
    releaseCreate();
    await expect(page).toHaveURL(/\/matches\/32$/);
    await expect(page.getByRole("heading", { name: "Clube novo", exact: true })).toBeVisible();
    await expect(page.getByText("Fora · Campo visitante")).toBeVisible();
    await expect(page.getByText("Agendado", { exact: true })).toBeVisible();
    const counters = page.getByLabel("Contadores da convocatória");
    await expect(counters).toContainText("Total convocados: 0");
    await page.getByLabel("Convocatória de João").selectOption("TITULAR");
    await page.getByLabel("Convocatória de Miguel").selectOption("SUPLENTE");
    await expect(counters).toContainText("Titulares: 1");
    await expect(counters).toContainText("Suplentes: 1");
    await expect(counters).toContainText("Total convocados: 2");
    await page.getByRole("button", { name: "Guardar convocatória" }).click();
    await expect(page.getByText("Convocatória guardada.", { exact: true })).toBeVisible();
    expect(lastSquad).toEqual([{ player_id: 1, is_starter: true }, { player_id: 2, is_starter: false }]);
    await page.reload();
    await expect(page.getByLabel("Convocatória de João")).toHaveValue("TITULAR");
    await page.getByLabel("Convocatória de João").selectOption("SUPLENTE");
    await page.getByLabel("Convocatória de Miguel").selectOption("TITULAR");
    await page.getByLabel("Convocatória de Pedro").selectOption("SUPLENTE");
    await expect(counters).toContainText("Total convocados: 3");
    await page.getByRole("button", { name: "Guardar convocatória" }).click();
    await expect(page.getByText("Convocatória guardada.", { exact: true })).toBeVisible();
    await page.getByLabel("Convocatória de João").selectOption("NAO_CONVOCADO");
    await page.getByRole("button", { name: "Guardar convocatória" }).click();
    await expect(page.getByText("Convocatória guardada.", { exact: true })).toBeVisible();
    expect(lastSquad).toEqual([{ player_id: 2, is_starter: true }, { player_id: 3, is_starter: false }]);
    expect(putCount).toBe(3);
    await page.getByRole("button", { name: "Editar jogo", exact: true }).click();
    await page.getByLabel("Jornada", { exact: true }).fill("3");
    await page.getByRole("button", { name: "Guardar jogo", exact: true }).click();
    await expect(page.getByText("Jogo atualizado.", { exact: true })).toBeVisible();
    await expect(page.getByText("Jornada 3", { exact: true })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  });

  test(`Convocatória: loading, histórico inativo e erro sem perder seleção a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 800 });
    let releaseLoad!: () => void;
    const loaded = new Promise<void>((resolve) => { releaseLoad = resolve; });
    let releaseSave!: () => void;
    const saved = new Promise<void>((resolve) => { releaseSave = resolve; });
    let writes = 0;
    const rows = structuredClone(baseSquad);
    rows[0].player.is_active = false; rows[0].role = "TITULAR";
    await page.route("**/matches/31**", async (route) => {
      if (route.request().isNavigationRequest() || !route.request().url().includes(":8000/")) return route.continue();
      await loaded;
      if (route.request().method() === "PUT") {
        writes++;
        await saved;
        return route.fulfill({ status: 409, json: { detail: "Um jogador inativo não pode ser adicionado à convocatória." } });
      }
      return route.fulfill({ json: route.request().url().endsWith("/squad") ? rows : baseMatch });
    });
    await page.goto("/matches/31");
    await expect(page.getByText("A carregar o jogo…")).toBeVisible();
    releaseLoad();
    await expect(page.getByText("MC · Inativo — convocatória preservada")).toBeVisible();
    await page.getByLabel("Convocatória de Miguel").selectOption("SUPLENTE");
    await page.getByRole("button", { name: "Guardar convocatória" }).click();
    await expect(page.getByLabel("Convocatória de Miguel")).toBeDisabled();
    await expect(page.getByRole("button", { name: "A guardar…" })).toBeDisabled();
    await expect.poll(() => writes).toBe(1);
    releaseSave();
    await expect(page.getByRole("main").getByRole("alert")).toContainText("Um jogador inativo");
    await expect(page.getByLabel("Convocatória de Miguel")).toHaveValue("SUPLENTE");
    await expect(page.getByRole("button", { name: "Guardar convocatória" })).toBeEnabled();
    expect(writes).toBe(1);
  });
}
