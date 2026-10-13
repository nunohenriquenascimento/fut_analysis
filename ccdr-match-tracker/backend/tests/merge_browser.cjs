// Real ADMIN preview and merge against isolated PostgreSQL, HTTP and WebSockets.
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
    const source = `/matches/${process.env.BROWSER_CONTINUATION_ID}`;
    await page.goto(origin + "/login?next=" + base);
    await page.getByLabel("Email", { exact: true }).fill("socket-admin@test.local");
    await page.getByLabel("Password", { exact: true }).fill(process.env.BROWSER_PASSWORD);
    await page.getByRole("button", { name: "Entrar", exact: true }).click();
    await expect(page).toHaveURL(origin + base);
    async function api(path) {
      return page.evaluate(async path => {
        const response = await fetch("http://localhost:8000" + path, { credentials: "include" });
        return { status: response.status, data: await response.json() };
      }, path);
    }
    const before = (await api(base + "/live")).data;
    const continuation = (await api(source + "/live")).data;
    const statsBefore = (await api("/statistics/season")).data;
    const spectator = await context.newPage();
    await spectator.goto(origin + base + "/live");
    await expect(spectator.getByLabel("Ligação em tempo real")).toContainText("Tempo real ligado");
    await page.getByRole("button", { name: "Unir jogo de continuação", exact: true }).click();
    const dialog = page.getByRole("dialog");
    await dialog.getByRole("combobox", { name: "Jogo de continuação", exact: true }).selectOption(process.env.BROWSER_CONTINUATION_ID);
    await dialog.getByRole("button", { name: "Obter preview", exact: true }).click();
    await expect(dialog.getByRole("region", { name: "Preview da união", exact: true })).toBeVisible();
    await expect(dialog).toContainText("Resultado previsto: 2 – 1");
    await expect(dialog).toContainText("78:00 (4680 s)");
    await expect(dialog).toContainText("04:30 → 2.ª parte · 67:30");
    assert.deepEqual((await api(base + "/live")).data.events, before.events);
    assert.deepEqual((await api(source + "/live")).data.events, continuation.events);
    await expect(dialog.getByRole("button", { name: "Confirmar união dos jogos", exact: true })).toBeDisabled();
    await dialog.getByRole("textbox", { name: /Escreve UNIR JOGOS/ }).fill("UNIR JOGOS");
    await dialog.screenshot({ path: `artifacts/merge/real-preview-${process.env.BROWSER_WIDTH}.png` });
    assert.equal(await dialog.evaluate(element => element.scrollWidth <= element.clientWidth), true);
    await dialog.getByRole("button", { name: "Confirmar união dos jogos", exact: true }).click();
    await expect(dialog).toHaveCount(0);
    await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("2 – 1");
    await expect(spectator.getByLabel("Resultado", { exact: true })).toHaveText("2 – 1");
    await expect(spectator.getByLabel("Cronómetro")).toHaveText("78:00");
    await expect(spectator.getByRole("region", { name: "Acontecimentos" }).getByRole("listitem")).toHaveCount(5);
    const final = (await api(base + "/live")).data;
    assert.equal(final.match.id, before.match.id);
    assert.equal(final.match.elapsed_seconds, 4680);
    assert.equal(final.match.clock_started_at, null);
    assert.equal(final.match.status, "FINISHED");
    assert.deepEqual(final.events[0], before.events[0]);
    for (const original of continuation.events) {
      const moved = final.events.find(row => row.id === original.id);
      assert.deepEqual(moved, { ...original, match_id: before.match.id, period: 2, elapsed_seconds: 3780 + original.elapsed_seconds });
    }
    assert.equal((await api(source)).status, 404);
    const stats = (await api("/statistics/season")).data;
    assert.equal(stats.total_matches, statsBefore.total_matches - 1);
    assert.equal(stats.competitive.matches, 1);
    assert.equal(stats.competitive.wins, 1);
    assert.equal(stats.competitive.goals_for, 2);
    assert.equal(stats.competitive.goals_against, 1);
    assert.deepEqual(stats.comparison, statsBefore.comparison);
    assert.deepEqual(stats.rankings, statsBefore.rankings);
    assert.equal(stats.players[0].matches_called_up, 1);
    assert.equal(stats.players[0].matches_started, 1);
    await page.goto(origin + base + "/stats");
    await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("2 – 1");
    await expect(page.getByRole("region", { name: "Timeline resumida" }).getByRole("listitem")).toHaveCount(5);
    await context.close();
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
