// Real browser -> Next -> FastAPI -> disposable PostgreSQL. No HTTP mocks.
const { chromium, expect } = require(process.cwd() + "/node_modules/@playwright/test");
const assert = require("node:assert/strict");
const path = require("node:path");
(async () => {
  const browser = await chromium.launch({ channel: "msedge" });
  try {
    const page = await browser.newPage({ viewport: { width: Number(process.env.BROWSER_WIDTH), height: 850 } });
    page.setDefaultTimeout(12000);
    const base = `/competitions/${process.env.BROWSER_COMPETITION_ID}/fpf`;
    await page.goto(process.env.BROWSER_ORIGIN + "/login?next=" + base);
    await page.getByLabel("Email", { exact: true }).fill("fpf-browser@test.local");
    await page.getByLabel("Password", { exact: true }).fill(process.env.BROWSER_PASSWORD);
    await page.getByRole("button", { name: "Entrar", exact: true }).click();
    await expect(page).toHaveURL(process.env.BROWSER_ORIGIN + base);
    await page.getByLabel("Ficheiros HTML FPF").setInputFiles([
      path.join(process.env.FPF_FIXTURES, "competition_30369_season_106.html"),
      path.join(process.env.FPF_FIXTURES, "match_2682548.html"),
      path.join(process.env.FPF_FIXTURES, "fixture_677921.html"),
      path.join(process.env.FPF_FIXTURES, "fixture_677922.html"),
    ]);
    await page.getByLabel("URL de origem FPF: fixture_677921.html").fill("https://resultados.fpf.pt/Competition/GetClassificationAndMatchesByFixture?fixtureId=677921");
    await page.getByLabel("URL de origem FPF: fixture_677922.html").fill("https://resultados.fpf.pt/Competition/GetClassificationAndMatchesByFixture?fixtureId=677922");
    await page.getByRole("button", { name: "Validar e identificar ficheiros" }).click();
    const mapping = JSON.parse(process.env.BROWSER_TEAM_MAP);
    for (const [name, id] of Object.entries(mapping)) await page.getByRole("combobox", { name: `Equipa FPF: ${name}`, exact: true }).selectOption(String(id));
    await page.getByLabel("Jornada da ficha #2682548").selectOption("677922");
    for (let iteration = 0; iteration < 2; iteration++) {
      await page.getByRole("button", { name: "Rever diferenças e ligações" }).click();
      await expect(page.getByRole("button", { name: "Confirmar importação FPF" })).toBeDisabled();
      await page.getByLabel("Escreva SINCRONIZAR FPF para confirmar").fill("SINCRONIZAR FPF");
      await page.getByRole("button", { name: "Confirmar importação FPF" }).click();
      await expect(page.getByRole("status").filter({ hasText: "Captura aplicada" })).toBeVisible();
      await expect(page.getByRole("status").filter({ hasText: "Captura aplicada" })).toContainText(
        iteration === 0 ? "12 criados, 0 atualizados, 0 ignorados, 0 rejeitados" : "0 criados, 0 atualizados, 12 ignorados, 0 rejeitados");
    }
    await expect(page.getByRole("region", { name: "Classificação oficial FPF" }).locator("tbody tr")).toHaveCount(8);
    const appliedSeries = page.getByRole("region", { name: /Série FPF/ }).filter({
      has: page.getByRole("region", { name: "Classificação oficial FPF", exact: true }),
    });
    await expect(appliedSeries.getByText("Ainda não importada", { exact: true })).toHaveCount(11);
    const sheets = page.getByRole("region", { name: "Fichas oficiais", exact: true });
    await sheets.getByText(/Ficha oficial #2682548/).click();
    await expect(sheets.getByRole("region", { name: "Eventos oficiais 2682548" })).toContainText("69'");
    const cid = process.env.BROWSER_COMPETITION_ID;
    // Navigate after import: each local screen must fetch the newly persisted fixtures.
    await page.goto(process.env.BROWSER_ORIGIN + `/competitions/${cid}/calendar`);
    await expect(page.getByRole("region", { name: "Calendário", exact: true })).toContainText("Seia Fc");
    await expect(page.getByRole("region", { name: "Calendário", exact: true })).toContainText("2 – 1");
    await expect(page.getByRole("region", { name: "Calendário", exact: true })).toContainText("4 – 0");
    await expect(page.getByRole("region", { name: "Calendário", exact: true })).toContainText("1 nov 16:00");
    await page.goto(process.env.BROWSER_ORIGIN + `/competitions/${cid}/results`);
    await expect(page.getByRole("region", { name: "Jornada 2", exact: true })).toContainText("2 – 1");
    await expect(page.getByRole("region", { name: "Jornada 2", exact: true })).toContainText("3 – 3");
    await expect(page.getByRole("region", { name: "Jornada 2", exact: true })).toContainText("1 – 4");
    await expect(page.getByRole("region", { name: "Jornada 1", exact: true })).toContainText("5 – 0");
    await expect(page.getByRole("region", { name: "Jornada 1", exact: true })).toContainText("0 – 1");
    await page.goto(process.env.BROWSER_ORIGIN + `/competitions/${cid}`);
    await expect(page.getByText("Jogos terminados: 8.", { exact: false })).toBeVisible();
    const standings = page.getByRole("table", { name: "Pontos e estatísticas do campeonato" });
    const seia = standings.locator("tbody tr").filter({ hasText: "Seia Fc" });
    await expect(seia.locator("td").nth(1)).toHaveText("3");
    const aguiar = standings.locator("tbody tr").filter({ hasText: "Adrc Aguiar Beira" });
    await expect(aguiar.locator("td").nth(1)).toHaveText("6");
    // Finish the complete calendar using bounded real-HTML batches, then replay all sources.
    const sources = JSON.parse(process.env.BROWSER_CALENDAR_SOURCES);
    async function importBatch(batch) {
      await page.goto(process.env.BROWSER_ORIGIN + base);
      await expect(page.getByRole("region", { name: "Classificação oficial FPF" }).locator("tbody tr")).toHaveCount(8);
      await page.getByLabel("Ficheiros HTML FPF").setInputFiles(batch.map(source => path.join(process.env.FPF_FIXTURES, source.file)));
      for (const source of batch) await page.getByLabel(`URL de origem FPF: ${source.file}`).fill(source.url);
      await page.getByRole("button", { name: "Validar e identificar ficheiros" }).click();
      for (const [name, id] of Object.entries(mapping)) await page.getByRole("combobox", { name: `Equipa FPF: ${name}`, exact: true }).selectOption(String(id));
      await page.getByRole("button", { name: "Rever diferenças e ligações" }).click();
      await page.getByLabel("Escreva SINCRONIZAR FPF para confirmar").fill("SINCRONIZAR FPF");
      await page.getByRole("button", { name: "Confirmar importação FPF" }).click();
      await expect(page.getByRole("status").filter({ hasText: "Captura aplicada" })).toBeVisible();
    }
    const remaining = sources.filter(source => ![677921,677922].includes(source.fixture_id));
    await importBatch(remaining.slice(0,8));
    await expect(page.getByRole("status").filter({hasText:"Captura aplicada"})).toContainText("32 criados");
    await importBatch(remaining.slice(8));
    await expect(page.getByRole("status").filter({hasText:"Captura aplicada"})).toContainText("12 criados");
    async function calendarLinks() {
      await page.goto(process.env.BROWSER_ORIGIN + `/competitions/${cid}/calendar`);
      await expect(page.locator(".fixture-card")).toHaveCount(56);
      return await page.locator(".fixture-card").evaluateAll(cards => cards.map(card => card.getAttribute("href")));
    }
    const localIds = await calendarLinks();
    for (let start=0; start<sources.length; start+=8) {
      await importBatch(sources.slice(start,start+8));
      await expect(page.getByRole("status").filter({hasText:"Captura aplicada"})).toContainText("0 criados, 0 atualizados");
    }
    assert.deepEqual(await calendarLinks(), localIds);
    const expectedGames = JSON.parse(process.env.BROWSER_CALENDAR_GAMES);
    async function verifyGames(container, games) {
      for (const game of games) {
        const card = container.locator(".fixture-card").filter({hasText:`Jornada ${game.matchday}`})
          .filter({hasText:game.home_name}).filter({hasText:game.away_name});
        await expect(card).toHaveCount(1);
        const internal = game.matchday===3 && game.home_name==="V. Cortez Mondego-Guarda";
        const score = internal ? "1 – 0" : game.home_goals===null ? "–" : `${game.home_goals} – ${game.away_goals}`;
        await expect(card.getByLabel("Resultado", {exact:true})).toHaveText(score);
        if (!internal && game.match_id!==2682548) await expect(card).toContainText(game.schedule_text);
        if (game.match_id===2682548) await expect(card).toContainText("2026");
      }
    }
    await verifyGames(page.getByRole("region", {name:"Calendário",exact:true}),expectedGames);
    await page.goto(process.env.BROWSER_ORIGIN + `/competitions/${cid}/results`);
    await expect(page.locator(".fixture-card")).toHaveCount(56);
    for (let day=1;day<=14;day++) {
      const region=page.getByRole("region",{name:`Jornada ${day}`,exact:true});
      await expect(region.locator(".fixture-card")).toHaveCount(4);
      await verifyGames(region,expectedGames.filter(game=>game.matchday===day));
    }
    await page.goto(process.env.BROWSER_ORIGIN + `/competitions/${cid}`);
    await expect(page.getByText("Jogos terminados: 8.",{exact:false})).toBeVisible();
    await expect(page.getByRole("table",{name:"Pontos e estatísticas do campeonato"}).locator("tbody tr").filter({hasText:"Adrc Aguiar Beira"}).locator("td").nth(1)).toHaveText("6");
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await page.close();
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
