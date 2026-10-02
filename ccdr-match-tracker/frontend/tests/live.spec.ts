import { expect, test } from "./auth-fixture";
import type { EventFields, LiveState, MatchEvent, TransitionStatus } from "../lib/live";

for (const width of [360, 1280]) {
  test(`Jogo ao Vivo: relógio, eventos, resultado e transições a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 850 });
    let offset = 0;
    let writes = 0;
    let deletes = 0;
    let nextId = 1;
    let releaseSave!: () => void;
    let pauseSave = true;
    let rows: MatchEvent[] = [];
    const now = () => new Date(Date.now() + offset).toISOString();
    const state: LiveState = {
      match: { id: 31, season_id: 17, team_id: 23, opponent_id: 24, opponent_name: "Adversário de teste",
        matchday: 1, kickoff_at: now(), is_home: true, venue: "Campo", status: "SCHEDULED", elapsed_seconds: 0,
        clock_started_at: null, created_at: now() },
      server_now: now(), clock_elapsed_seconds: 0, period: null, score: { us: 0, opponent: 0 }, events: [],
      squad: ["Jorge", "Jajão"].map((name, index) => ({ id: index + 1, name, shirt_number: index + 7,
        team_id: 23, season_id: 17, position: "MC", is_active: true, created_at: now() })),
    };
    function snapshot() {
      state.server_now = now();
      state.clock_elapsed_seconds = state.match.elapsed_seconds + (state.match.clock_started_at
        ? Math.max(0, Math.floor((Date.parse(now()) - Date.parse(state.match.clock_started_at)) / 1000)) : 0);
      state.events = rows;
      state.score = { us: 0, opponent: 0 };
      for (const row of rows) {
        if (row.event_type === "GOAL" || row.event_type === "OWN_GOAL") {
          if ((row.team === "US") === (row.event_type === "GOAL")) state.score.us++;
          else state.score.opponent++;
        }
      }
      return structuredClone(state);
    }
    await page.route("**/matches/31**", async (route) => {
      const request = route.request();
      if (request.isNavigationRequest() || !request.url().includes(":8000/")) return route.continue();
      const path = new URL(request.url()).pathname;
      if (path.endsWith("/squad")) return route.fulfill({ json: state.squad.map((player) => ({ player, role: "TITULAR" })) });
      if (path === "/matches/31") return route.fulfill({ json: state.match });
      if (path.endsWith("/transition")) {
        snapshot();
        const target = request.postDataJSON().status as TransitionStatus;
        state.match.elapsed_seconds = state.clock_elapsed_seconds;
        state.match.status = target;
        state.match.clock_started_at = target === "FIRST_HALF" || target === "SECOND_HALF" ? now() : null;
        state.period = target === "FIRST_HALF" || target === "HALF_TIME" ? 1 : 2;
      } else if (request.method() === "POST") {
        writes++;
        const fields: EventFields = request.postDataJSON();
        expect(fields).not.toHaveProperty("elapsed_seconds");
        expect(fields).not.toHaveProperty("period");
        if (pauseSave) await new Promise<void>((resolve) => { releaseSave = resolve; });
        snapshot();
        rows.push({ ...fields, id: nextId++, match_id: 31, period: state.period!, elapsed_seconds: state.clock_elapsed_seconds, created_at: now() });
      } else if (request.method() === "PATCH") {
        const id = Number(path.split("/").pop());
        rows = rows.map((row) => row.id === id ? { ...row, ...request.postDataJSON() } : row);
      } else if (request.method() === "DELETE") {
        deletes++;
        rows = rows.filter((row) => row.id !== Number(path.split("/").pop()));
      }
      return route.fulfill({ status: request.method() === "POST" && path.endsWith("/events") ? 201 : 200, json: snapshot() });
    });

    await page.goto("/matches/31");
    await page.getByRole("link", { name: "Abrir Jogo ao Vivo" }).click();
    await expect(page.getByRole("heading", { name: /Jogo ao Vivo ·/ })).toBeVisible();
    await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("0 – 0");
    await expect(page.getByLabel("Cronómetro")).toHaveText("00:00");
    const ours = page.getByRole("region", { name: "Nossa equipa", exact: true });
    const theirs = page.getByRole("region", { name: "Adversário", exact: true });
    await expect(ours.getByRole("button", { name: "Golo", exact: true })).toBeDisabled();
    await page.getByRole("button", { name: "Iniciar 1.ª parte", exact: true }).click();
    await expect(page.getByText("1.ª parte", { exact: true })).toBeVisible();
    await expect(page.getByLabel("Cronómetro")).not.toHaveText("00:00");
    offset = 65000;
    await page.reload();
    await expect(page.getByLabel("Cronómetro")).toHaveText(/^01:0[5-9]$/);
    await ours.getByRole("button", { name: "Golo", exact: true }).click();
    const dialog = page.getByRole("dialog");
    await dialog.getByRole("combobox", { name: "Marcador", exact: true }).selectOption("1");
    await dialog.getByLabel("Assistência (opcional)").selectOption("2");
    await dialog.getByRole("button", { name: "Guardar evento" }).click();
    await expect(dialog.getByRole("button", { name: "A guardar…" })).toBeDisabled();
    await expect.poll(() => writes).toBe(1);
    await dialog.locator("form").evaluate((form) => form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true })));
    expect(writes).toBe(1);
    pauseSave = false; releaseSave();
    await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("1 – 0");
    const timeline = page.getByRole("region", { name: "Acontecimentos" });
    await expect(timeline).toContainText("Golo — Jorge — Assistência: Jajão");
    await theirs.getByRole("button", { name: "Remate à baliza", exact: true }).click();
    await expect(timeline).toContainText("Remate à baliza — Adversário");
    await theirs.getByRole("button", { name: "Golo", exact: true }).click();
    await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("1 – 1");
    const goal = timeline.getByRole("listitem").filter({ hasText: "Golo — Jorge" });
    await goal.getByRole("button", { name: "Editar", exact: true }).click();
    await dialog.getByLabel("Tipo de evento").selectOption("SHOT_OFF_TARGET");
    await dialog.getByRole("button", { name: "Guardar evento" }).click();
    await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("0 – 1");
    await expect(timeline).toContainText("Remate fora — Jorge");
    const opponentGoal = timeline.getByRole("listitem").filter({ hasText: "Golo — Adversário" });
    await opponentGoal.getByRole("button", { name: "Eliminar", exact: true }).click();
    await expect(dialog.getByRole("heading", { name: "Eliminar evento?" })).toBeVisible();
    await dialog.getByRole("button", { name: "Cancelar", exact: true }).click();
    expect(deletes).toBe(0);
    await opponentGoal.getByRole("button", { name: "Eliminar", exact: true }).click();
    await dialog.getByRole("button", { name: "Confirmar eliminação" }).click();
    await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("0 – 0");
    await expect(timeline.getByRole("listitem")).toHaveCount(2);
    await page.getByRole("button", { name: "Terminar 1.ª parte", exact: true }).click();
    await expect(page.getByText("Intervalo", { exact: true })).toBeVisible();
    const stopped = await page.getByLabel("Cronómetro").textContent();
    offset += 15 * 60 * 1000;
    await page.reload();
    await expect(page.getByLabel("Cronómetro")).toHaveText(stopped!);
    await page.getByRole("button", { name: "Iniciar 2.ª parte", exact: true }).click();
    await ours.getByRole("button", { name: "Substituição", exact: true }).click();
    await dialog.getByLabel("Jogador que sai").selectOption("1");
    await dialog.getByLabel("Jogador que entra").selectOption("2");
    await dialog.getByRole("button", { name: "Guardar evento" }).click();
    await expect(timeline).toContainText("Substituição — Jorge — Entra: Jajão");
    await page.getByRole("button", { name: "Terminar jogo", exact: true }).click();
    await expect(page.getByText("Terminado", { exact: true })).toBeVisible();
    await expect(ours.getByRole("button", { name: "Golo", exact: true })).toBeDisabled();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  });
}

test("Jogo ao Vivo: jogo inexistente não apresenta controlos", async ({ page }) => {
  await page.route("**/matches/999/live", (route) => route.request().isNavigationRequest() ? route.continue()
    : route.fulfill({ status: 404, json: { detail: "Jogo não encontrado." } }));
  await page.goto("/matches/999/live");
  await expect(page.getByRole("main").getByRole("alert")).toHaveText("Jogo não encontrado.");
  await expect(page.getByRole("button", { name: "Iniciar 1.ª parte" })).toHaveCount(0);
});

test("Jogo ao Vivo: erro de gravação preserva o marcador e permite corrigir", async ({ page }) => {
  const state: LiveState = {
    match: { id: 31, season_id: 17, team_id: 23, opponent_id: 24, opponent_name: "Adversário", matchday: 1,
      kickoff_at: "2026-10-04T14:00:00Z", is_home: true, venue: "Campo", status: "FIRST_HALF", elapsed_seconds: 0,
      clock_started_at: "2026-10-04T14:00:00Z", created_at: "2026-10-01T12:00:00Z" },
    server_now: "2026-10-04T14:01:00Z", clock_elapsed_seconds: 60, period: 1,
    score: { us: 0, opponent: 0 }, events: [],
    squad: [{ id: 1, name: "Jorge", shirt_number: 7, team_id: 23, season_id: 17, position: "MC", is_active: true, created_at: "2026-10-01T12:00:00Z" }],
  };
  await page.route("**/matches/31/**", (route) => {
    if (route.request().isNavigationRequest() || !route.request().url().includes(":8000/")) return route.continue();
    return route.request().method() === "POST" ? route.fulfill({ status: 409, json: { detail: "O jogador não faz parte da convocatória do jogo." } }) : route.fulfill({ json: state });
  });
  await page.goto("/matches/31/live");
  await page.getByRole("region", { name: "Nossa equipa" }).getByRole("button", { name: "Golo", exact: true }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("combobox", { name: "Marcador", exact: true }).selectOption("1");
  await dialog.getByRole("button", { name: "Guardar evento" }).click();
  await expect(dialog.getByRole("alert")).toContainText("não faz parte da convocatória");
  await expect(dialog.getByRole("combobox", { name: "Marcador", exact: true })).toHaveValue("1");
  await expect(dialog.getByRole("button", { name: "Guardar evento" })).toBeEnabled();
  await dialog.getByRole("button", { name: "Cancelar", exact: true }).click();
  await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("0 – 0");
});
