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
    ]);
    await page.getByRole("button", { name: "Validar e identificar ficheiros" }).click();
    const mapping = JSON.parse(process.env.BROWSER_TEAM_MAP);
    for (const [name, id] of Object.entries(mapping)) await page.getByRole("combobox", { name: `Equipa FPF: ${name}`, exact: true }).selectOption(String(id));
    await page.getByRole("button", { name: "Rever diferenças e ligações" }).click();
    await expect(page.getByRole("region", { name: "Revisão FPF" })).toContainText("Jogos internos pendentes: 1");
    await page.getByLabel(/Jogo interno:.*Jornada 3/).selectOption(process.env.BROWSER_MATCH_ID);
    await expect(page.getByRole("button", { name: "Confirmar importação FPF" })).toHaveCount(0);
    for (let iteration = 0; iteration < 2; iteration++) {
      await page.getByRole("button", { name: "Rever diferenças e ligações" }).click();
      await expect(page.getByRole("button", { name: "Confirmar importação FPF" })).toBeDisabled();
      await page.getByLabel("Escreva SINCRONIZAR FPF para confirmar").fill("SINCRONIZAR FPF");
      await page.getByRole("button", { name: "Confirmar importação FPF" }).click();
      await expect(page.getByRole("status").filter({ hasText: "Captura aplicada" })).toBeVisible();
    }
    await expect(page.getByRole("region", { name: "Classificação oficial FPF" }).locator("tbody tr")).toHaveCount(8);
    const appliedSeries = page.getByRole("region", { name: /Série FPF/ }).filter({
      has: page.getByRole("region", { name: "Classificação oficial FPF", exact: true }),
    });
    await expect(appliedSeries.getByText("Ainda não importada", { exact: true })).toHaveCount(13);
    const sheets = page.getByRole("region", { name: "Fichas oficiais", exact: true });
    await sheets.getByText(/Ficha oficial #2682548/).click();
    await expect(sheets.getByRole("region", { name: "Eventos oficiais 2682548" })).toContainText("69'");
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await page.close();
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
