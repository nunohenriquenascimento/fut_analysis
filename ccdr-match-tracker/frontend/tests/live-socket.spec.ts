import { expect, test, type BrowserContext, type Page, type WebSocketRoute } from "@playwright/test";
import type { LiveState, MatchEvent, EventFields } from "../lib/live";

async function liveServer(context: BrowserContext) {
  const sockets = new Set<WebSocketRoute>();
  let connections = 0;
  const state: LiveState = {
    match: { id: 31, season_id: 1, team_id: 1, opponent_id: 2, opponent_name: "Adversário", matchday: 1,
      kickoff_at: new Date().toISOString(), is_home: true, venue: "Campo", status: "FIRST_HALF", elapsed_seconds: 65,
      clock_started_at: new Date().toISOString(), created_at: new Date().toISOString() },
    score: { us: 0, opponent: 0 }, server_now: new Date().toISOString(), clock_elapsed_seconds: 65, period: 1, events: [],
    squad: [{ id: 1, name: "Jorge", shirt_number: 8, position: "MC", team_id: 1, season_id: 1, is_active: true, created_at: new Date().toISOString() }],
  };
  let nextId = 1;
  function snapshot() {
    state.server_now = new Date().toISOString();
    state.score = { us: 0, opponent: 0 };
    for (const row of state.events) {
      if (row.event_type === "GOAL" || row.event_type === "OWN_GOAL") {
        if ((row.team === "US") === (row.event_type === "GOAL")) state.score.us++; else state.score.opponent++;
      }
    }
    return structuredClone(state);
  }
  function notify(type: string) {
    for (const socket of sockets) socket.send(JSON.stringify({ type, version: 1, match_id: 31, actor_id: 1, data: {} }));
  }
  await context.routeWebSocket("**/ws/matches/31/live", (socket) => {
    connections++; sockets.add(socket);
    socket.onClose(() => sockets.delete(socket));
    socket.send(JSON.stringify({ type: "live.snapshot", version: 1, match_id: 31, actor_id: null, data: snapshot() }));
  });
  await context.route("**/auth/me", (route) => route.fulfill({ json: { user: { id: 1, name: "Coach", email: "coach@test.local", role: "COACH", is_active: true }, csrf_token: "socket-csrf" } }));
  await context.route("**/matches/31/**", async (route) => {
    const request = route.request();
    if (request.isNavigationRequest() || new URL(request.url()).port !== "8000") return route.continue();
    const path = new URL(request.url()).pathname;
    const method = request.method();
    let type: string | null = null;
    if (method !== "GET") expect(request.headers()["x-csrf-token"]).toBe("socket-csrf");
    if (path.endsWith("/transition")) {
      state.match.status = request.postDataJSON().status;
      state.match.clock_started_at = state.match.status === "SECOND_HALF" ? new Date().toISOString() : null;
      state.period = state.match.status === "HALF_TIME" ? 1 : 2;
      type = "live.state_changed";
    } else if (method === "POST") {
      const fields: EventFields = request.postDataJSON();
      state.events.push({ ...fields, id: nextId++, match_id: 31, period: state.period!, elapsed_seconds: 65, created_at: new Date().toISOString() });
      type = "live.event_created";
    } else if (method === "PATCH") {
      const id = Number(path.split("/").at(-1));
      Object.assign(state.events.find((row) => row.id === id)!, request.postDataJSON()); type = "live.event_updated";
    } else if (method === "DELETE") {
      state.events = state.events.filter((row) => row.id !== Number(path.split("/").at(-1))); type = "live.event_deleted";
    }
    if (type) { snapshot(); notify(type); }
    return route.fulfill({ status: method === "POST" && path.endsWith("/events") ? 201 : 200, json: snapshot() });
  });
  return { state, snapshot, notify, sockets, connections: () => connections };
}

function theirs(page: Page) { return page.getByRole("region", { name: "Adversário", exact: true }); }
function timeline(page: Page) { return page.getByRole("region", { name: "Acontecimentos" }); }

test("Duas páginas sincronizam eventos, resultado, partes e preservam formulário a 360px", async ({ context }) => {
  const server = await liveServer(context);
  const first = await context.newPage(), second = await context.newPage();
  await Promise.all([first.setViewportSize({ width: 360, height: 800 }), second.setViewportSize({ width: 360, height: 800 })]);
  await Promise.all([first.goto("/matches/31/live"), second.goto("/matches/31/live")]);
  for (const page of [first, second]) await expect(page.getByLabel("Ligação em tempo real")).toContainText("Tempo real ligado");
  await second.getByRole("region", { name: "Nossa equipa", exact: true }).getByRole("button", { name: "Golo", exact: true }).click();
  const draft = second.getByRole("dialog");
  await draft.getByRole("combobox", { name: "Marcador", exact: true }).selectOption("1");
  await theirs(first).getByRole("button", { name: "Golo", exact: true }).click();
  await expect(second.getByLabel("Resultado", { exact: true })).toHaveText("0 – 1");
  await expect(draft).toBeVisible(); await expect(draft.getByRole("combobox", { name: "Marcador", exact: true })).toHaveValue("1");
  await draft.getByRole("button", { name: "Cancelar", exact: true }).click();
  for (const page of [first, second]) await expect(timeline(page).getByRole("listitem")).toHaveCount(1);
  await timeline(first).getByRole("button", { name: "Editar", exact: true }).click();
  await first.getByRole("dialog").getByLabel("Tipo de evento").selectOption("SHOT_OFF_TARGET");
  await first.getByRole("dialog").getByRole("button", { name: "Guardar evento" }).click();
  await expect(second.getByLabel("Resultado", { exact: true })).toHaveText("0 – 0");
  await expect(timeline(second)).toContainText("Remate fora");
  await timeline(first).getByRole("button", { name: "Eliminar", exact: true }).click();
  await first.getByRole("dialog").getByRole("button", { name: "Confirmar eliminação" }).click();
  await expect(timeline(second).getByRole("listitem")).toHaveCount(0);
  await first.getByRole("button", { name: "Terminar 1.ª parte", exact: true }).click();
  await expect(second.getByText("Intervalo", { exact: true })).toBeVisible();
  const clock = await second.getByLabel("Cronómetro").textContent();
  await first.getByRole("button", { name: "Iniciar 2.ª parte", exact: true }).click();
  await expect(second.getByText("2.ª parte", { exact: true })).toBeVisible();
  expect(clock).toMatch(/^01:/);
  // Out-of-order/duplicate invalidations always fetch current server state.
  server.notify("live.event_deleted"); server.notify("live.event_created");
  await expect(timeline(second).getByRole("listitem")).toHaveCount(0);
  server.state.match.status = "CANCELLED"; server.state.match.clock_started_at = null; server.notify("live.cancelled");
  await expect(second.getByText("Cancelado", { exact: true })).toBeVisible();
  expect(await second.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test("Queda do socket reconecta e recupera alterações perdidas sem bloquear HTTP", async ({ context, page }) => {
  const server = await liveServer(context);
  await page.goto("/matches/31/live");
  await expect(page.getByLabel("Ligação em tempo real")).toContainText("Tempo real ligado");
  for (const socket of server.sockets) socket.close({ code: 1012, reason: "Restart" });
  server.sockets.clear();
  await expect(page.getByLabel("Ligação em tempo real")).toContainText("A reconectar");
  await theirs(page).getByRole("button", { name: "Golo", exact: true }).click();
  await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("0 – 1");
  server.state.events.push({ id: 100, match_id: 31, event_type: "GOAL", team: "OPPONENT", player_id: null, related_player_id: null, period: 1, elapsed_seconds: 66, created_at: new Date().toISOString() } as MatchEvent);
  await expect.poll(server.connections).toBeGreaterThan(1);
  await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("0 – 2");
  await expect(page.getByLabel("Ligação em tempo real")).toContainText("Tempo real ligado");
});

test("HTTP continua funcional quando o tempo real está indisponível", async ({ context, page }) => {
  await liveServer(context);
  await page.routeWebSocket("**/ws/matches/31/live", (socket) => socket.close({ code: 4403 }));
  await page.goto("/matches/31/live");
  await expect(page.getByLabel("Ligação em tempo real")).toContainText("Sem tempo real");
  await theirs(page).getByRole("button", { name: "Golo", exact: true }).click();
  await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("0 – 1");
  await page.getByRole("button", { name: "Terminar 1.ª parte", exact: true }).click();
  await expect(page.getByText("Intervalo", { exact: true })).toBeVisible();
});
