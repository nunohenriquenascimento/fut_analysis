import { expect, test, type Page } from "@playwright/test";

function account(role: "ADMIN" | "COACH" | "VIEWER") { return { id: 1, name: role, email: `${role.toLowerCase()}@test.local`, role, is_active: true }; }
const csrf = "server-issued-csrf";
async function data(page: Page) {
  await page.route("**/players**", (route) => route.request().isNavigationRequest() ? route.continue() : route.fulfill({ json: route.request().url().endsWith("/context")
    ? { season_id: 1, team_id: 1, season_name: "2026/27", team_name: "CCDR Vila Cortez do Mondego" }
    : [{ id: 1, name: "Jogador", shirt_number: 8, position: "MC", is_active: true, season_id: 1, team_id: 1, created_at: "2026-10-02T12:00:00Z" }] }));
  const match = { id: 31, season_id: 1, team_id: 1, opponent_id: 2, opponent_name: "Adversário", matchday: 1, kickoff_at: "2026-10-04T14:00:00Z", is_home: true, venue: null, status: "FIRST_HALF", elapsed_seconds: 10, clock_started_at: "2026-10-02T12:00:00Z", created_at: "2026-10-02T12:00:00Z", score: { us: 0, opponent: 0 } };
  await page.route("**/matches**", (route) => {
    if (route.request().isNavigationRequest()) return route.continue();
    const path = new URL(route.request().url()).pathname;
    return route.fulfill({ json: path.endsWith("/live") ? { match, score: match.score, server_now: "2026-10-02T12:00:10Z", clock_elapsed_seconds: 10, period: 1, events: [{ id: 1, event_type: "CORNER", team: "OPPONENT", period: 1, elapsed_seconds: 5, player_id: null, related_player_id: null }], squad: [] }
      : path.endsWith("/squad") ? [] : path === "/matches" ? [match] : match });
  });
}

test("Login, erro de credenciais, redirect seguro e logout a 360px", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  let authenticated = false;
  let attempts = 0;
  await page.route("**/auth/**", (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path === "/auth/login") {
      expect(route.request().postDataJSON()).toEqual({ email: "admin@test.local", password: "Test-password-2026!" });
      expect(route.request().headers()["x-requested-with"]).toBe("CCDR");
      if (++attempts === 1) return route.fulfill({ status: 401, json: { detail: "Email ou password inválidos." } });
      authenticated = true;
    } else if (path === "/auth/logout") {
      expect(route.request().headers()["x-csrf-token"]).toBe(csrf);
      authenticated = false;
      return route.fulfill({ status: 204 });
    }
    return route.fulfill({ status: authenticated ? 200 : 401, json: authenticated ? { user: account("ADMIN"), csrf_token: csrf } : { detail: "Sessão inexistente ou expirada." } });
  });
  await data(page);
  await page.goto("/players");
  await expect(page).toHaveURL(/\/login\?next=/);
  await expect(page.getByRole("button", { name: "Adicionar jogador" })).toHaveCount(0);
  await page.getByLabel("Email", { exact: true }).fill("admin@test.local");
  await page.getByLabel("Password", { exact: true }).fill("Test-password-2026!");
  await page.getByRole("button", { name: "Entrar", exact: true }).click();
  await expect(page.getByRole("main").getByRole("alert")).toHaveText("Email ou password inválidos.");
  await page.getByRole("button", { name: "Entrar", exact: true }).click();
  await expect(page).toHaveURL(/\/players$/);
  await expect(page.getByRole("button", { name: "Adicionar jogador" })).toBeVisible();
  expect(await page.evaluate(() => Object.keys(localStorage))).toEqual([]);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.getByRole("button", { name: "Sair", exact: true }).click();
  await expect(page).toHaveURL(/\/login$/);
});

for (const role of ["ADMIN", "COACH", "VIEWER"] as const) {
  test(`Permissões visuais de ${role}: Plantel, Jogos, Live e contas`, async ({ page }) => {
    await page.route("**/auth/me", (route) => route.fulfill({ json: { user: account(role), csrf_token: csrf } }));
    await data(page);
    await page.goto("/players");
    await expect(page.getByRole("heading", { name: "Jogador", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Adicionar jogador" })).toHaveCount(role === "VIEWER" ? 0 : 1);
    await expect(page.getByRole("button", { name: "Editar", exact: true })).toHaveCount(role === "VIEWER" ? 0 : 1);
    await expect(page.getByRole("link", { name: "Utilizadores", exact: true })).toHaveCount(role === "ADMIN" ? 1 : 0);
    await page.goto("/matches");
    await expect(page.getByRole("heading", { name: "Jogos e jornadas" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Criar jogo" })).toHaveCount(role === "VIEWER" ? 0 : 1);
    await page.goto("/matches/31");
    await expect(page.getByRole("heading", { name: "Convocatória", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Editar jogo" })).toHaveCount(role === "VIEWER" ? 0 : 1);
    await expect(page.getByRole("button", { name: "Guardar convocatória" })).toHaveCount(role === "VIEWER" ? 0 : 1);
    await page.goto("/matches/31/live");
    await expect(page.getByRole("heading", { name: "Acontecimentos" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Terminar 1.ª parte" })).toHaveCount(role === "VIEWER" ? 0 : 1);
    await expect(page.getByRole("button", { name: "Eliminar", exact: true })).toHaveCount(role === "VIEWER" ? 0 : 1);
    if (role !== "ADMIN") {
      await page.goto("/users");
      await expect(page.getByRole("heading", { name: "Acesso reservado ao ADMIN" })).toBeVisible();
    }
  });
}

test("Sessão expirada redireciona sem apresentar dados protegidos", async ({ page }) => {
  await page.route("**/auth/me", (route) => route.fulfill({ json: { user: account("VIEWER"), csrf_token: csrf } }));
  await page.route("**/players/context", (route) => route.fulfill({ status: 401, json: { detail: "Sessão expirada." } }));
  await page.goto("/players");
  await expect(page).toHaveURL(/\/login/);
  await expect(page.getByRole("heading", { name: "Iniciar sessão" })).toBeVisible();
});

test("Resposta antiga de sessão não invalida um login recente nem permite redirect externo", async ({ page }) => {
  let release!: () => void;
  let first = true;
  const pending = new Promise<void>((resolve) => { release = resolve; });
  await page.route("**/auth/me", async (route) => {
    if (first) { first = false; await pending; return route.fulfill({ status: 401, json: { detail: "Sessão anterior expirada." } }); }
    return route.fulfill({ json: { user: account("ADMIN"), csrf_token: csrf } });
  });
  await page.route("**/auth/login", (route) => route.fulfill({ json: { user: account("ADMIN"), csrf_token: csrf } }));
  await page.goto("/login?next=https%3A%2F%2Fevil.example");
  await page.getByLabel("Email", { exact: true }).fill("admin@test.local");
  await page.getByLabel("Password", { exact: true }).fill("Test-password-2026!");
  await page.getByRole("button", { name: "Entrar", exact: true }).click();
  release();
  await expect(page).toHaveURL("http://localhost:3100/");
  await expect(page.getByRole("heading", { name: "CCDR Vila Cortez do Mondego", exact: true })).toBeVisible();
});

test("ADMIN cria, edita e desativa contas; conflito do último ADMIN", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await page.route("**/auth/me", (route) => route.fulfill({ json: { user: account("ADMIN"), csrf_token: csrf } }));
  const users = [account("ADMIN")];
  await page.route("**/users**", (route) => {
    if (route.request().isNavigationRequest() || new URL(route.request().url()).port !== "8000") return route.continue();
    expect(route.request().headers()["x-csrf-token"]).toBe(csrf);
    const method = route.request().method();
    if (method === "GET") return route.fulfill({ json: users });
    const body = route.request().postDataJSON();
    if (method === "POST") {
      users.push({ ...body, id: 2 });
      return route.fulfill({ status: 201, json: users[1] });
    }
    const id = Number(new URL(route.request().url()).pathname.split("/").at(-1));
    if (id === 1 && body.is_active === false) return route.fulfill({ status: 409, json: { detail: "Não pode desativar ou despromover o último ADMIN ativo." } });
    Object.assign(users.find((user) => user.id === id)!, body);
    return route.fulfill({ json: users.find((user) => user.id === id) });
  });
  await page.goto("/users");
  await page.getByRole("button", { name: "Criar utilizador" }).click();
  await page.getByLabel("Nome", { exact: true }).fill("Treinador");
  await page.getByLabel("Email", { exact: true }).fill("coach@test.local");
  await page.getByLabel("Password", { exact: true }).fill("Test-password-2026!");
  await page.getByRole("combobox", { name: "Papel" }).selectOption("COACH");
  await page.getByRole("button", { name: "Guardar utilizador" }).click();
  await expect(page.getByRole("heading", { name: "Treinador", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Editar Treinador" }).click();
  await page.getByLabel("Conta ativa").uncheck();
  await page.getByRole("button", { name: "Guardar utilizador" }).click();
  await expect(page.getByText("Inativo", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Editar ADMIN", exact: true }).click();
  await page.getByLabel("Conta ativa").uncheck();
  await page.getByRole("button", { name: "Guardar utilizador" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("último ADMIN ativo");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});
