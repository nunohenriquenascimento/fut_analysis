// Browser journey against the real app. No HTTP or WebSocket mocks.
const { chromium, expect } = require(process.cwd() + "/node_modules/@playwright/test");
const assert = require("node:assert/strict");

(async () => {
  const browser = await chromium.launch({ channel: "msedge" });
  try {
    const context = await browser.newContext({ viewport: { width: Number(process.env.BROWSER_WIDTH), height: 850 } });
    context.setDefaultTimeout(10000);
    const page = await context.newPage();
    const origin = process.env.BROWSER_ORIGIN;
    const base = `/matches/${process.env.BROWSER_MATCH_ID}`;
    await page.goto(origin + "/login?next=" + base + "/live");
    await page.getByLabel("Email", { exact: true }).fill("socket-coach@test.local");
    await page.getByLabel("Password", { exact: true }).fill(process.env.BROWSER_PASSWORD);
    await page.getByRole("button", { name: "Entrar", exact: true }).click();
    await expect(page).toHaveURL(origin + base + "/live");

    async function api(path, method = "GET", body) {
      return page.evaluate(async ({ path, method, body }) => {
        const auth = await fetch("http://localhost:8000/auth/me", { credentials: "include" }).then(r => r.json());
        const response = await fetch("http://localhost:8000" + path, { method, credentials: "include",
          headers: { "Content-Type": "application/json", "X-CSRF-Token": auth.csrf_token },
          body: body === undefined ? undefined : JSON.stringify(body) });
        if (!response.ok) throw new Error(`${path}: ${response.status}`);
        return response.json();
      }, { path, method, body });
    }
    await api(base + "/squad", "PUT", { players: [{ player_id: Number(process.env.BROWSER_PLAYER_ID), is_starter: true }] });
    await page.getByRole("button", { name: "Atualizar estado", exact: true }).click();
    const second = await context.newPage();
    await second.goto(origin + base + "/live");
    for (const device of [page, second]) await expect(device.getByLabel("Ligação em tempo real")).toContainText("Tempo real ligado");
    await page.getByRole("button", { name: "Iniciar 1.ª parte", exact: true }).click();
    await expect(page.getByLabel("Cronómetro")).not.toHaveText("00:00");
    await page.getByRole("button", { name: "Terminar 1.ª parte", exact: true }).click();
    await page.getByRole("button", { name: "Iniciar 2.ª parte", exact: true }).click();
    const theirs = page.getByRole("region", { name: "Adversário", exact: true });
    for (const label of ["Golo", "Amarelo", "Remate à baliza"]) await theirs.getByRole("button", { name: label, exact: true }).click();
    const ours = page.getByRole("region", { name: "Nossa equipa", exact: true });
    await ours.getByRole("button", { name: "Golo", exact: true }).click();
    await page.getByRole("dialog").getByRole("combobox", { name: "Marcador", exact: true }).selectOption(process.env.BROWSER_PLAYER_ID);
    await page.getByRole("dialog").getByRole("button", { name: "Guardar evento", exact: true }).click();
    await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("1 – 1");
    await expect(second.getByLabel("Resultado", { exact: true })).toHaveText("1 – 1");
    async function finish() {
      await page.getByRole("button", { name: "Terminar 2.ª Parte", exact: true }).click();
      await expect(page.getByRole("dialog")).toContainText("Esta ação termina o jogo e fecha o cronómetro.");
      await page.getByRole("dialog").getByRole("button", { name: "Terminar jogo", exact: true }).click();
      await expect(page.getByText("Terminado", { exact: true })).toBeVisible();
    }
    await finish();
    await expect(second.getByText("Terminado", { exact: true })).toBeVisible();
    const before = await api(base + "/live");
    const squadBefore = await api(base + "/squad");
    assert.equal((await api("/statistics/season")).competitive.matches, 1);
    await page.waitForTimeout(1200);
    await page.getByRole("button", { name: "Reabrir jogo", exact: true }).click();
    await page.getByRole("dialog").getByRole("button", { name: "Reabrir jogo", exact: true }).click();
    for (const device of [page, second]) {
      await expect(device.getByRole("button", { name: "Retomar 2.ª Parte", exact: true })).toBeVisible();
      await expect(device.getByText("Terminado", { exact: true })).toHaveCount(0);
      await expect(device.getByRole("region", { name: "Acontecimentos" }).getByRole("listitem")).toHaveCount(4);
      await expect(device.getByLabel("Resultado", { exact: true })).toHaveText("1 – 1");
    }
    const reopened = await api(base + "/live");
    assert.equal(reopened.match.clock_started_at, null);
    assert.equal(reopened.clock_elapsed_seconds, before.clock_elapsed_seconds);
    assert.deepEqual(reopened.events, before.events);
    assert.deepEqual(await api(base + "/squad"), squadBefore);
    assert.equal((await api("/statistics/season")).competitive.matches, 0);
    const stopped = await page.getByLabel("Cronómetro").textContent();
    await page.waitForTimeout(1200);
    await expect(page.getByLabel("Cronómetro")).toHaveText(stopped);
    assert.equal((await api(base + "/live")).clock_elapsed_seconds, before.clock_elapsed_seconds);
    await page.getByRole("button", { name: "Retomar 2.ª Parte", exact: true }).click();
    await expect(page.getByLabel("Cronómetro")).not.toHaveText(stopped);
    await theirs.getByRole("button", { name: "Golo", exact: true }).click();
    await finish();
    const final = await api(base + "/live");
    assert.deepEqual(final.events.slice(0, 4), before.events);
    assert.deepEqual(final.score, { us: 1, opponent: 2 });
    const season = await api("/statistics/season");
    assert.equal(season.competitive.matches, 1);
    assert.equal(season.competitive.goals_for, 1);
    assert.equal(season.competitive.goals_against, 2);
    await page.goto(origin + base + "/stats");
    await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("1 – 2");
    await expect(page.getByRole("region", { name: "Timeline resumida" }).getByRole("listitem")).toHaveCount(5);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await page.goto(origin + "/statistics");
    await expect(page.getByRole("region", { name: "Resumo competitivo" }).locator("dd").first()).toHaveText("1");
    await context.close();
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
