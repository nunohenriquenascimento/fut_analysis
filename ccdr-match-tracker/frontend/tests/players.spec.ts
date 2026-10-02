import { expect, test } from "./auth-fixture";
import type { Player } from "../lib/api";

for (const width of [360, 1280]) {
  test(`Plantel: lifecycle, errors and pending requests at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 800 });
    let rows: Player[] = [];
    let writes = 0;
    let failure = 0;
    let contextFailure = true;
    let releaseWrite: (() => void) | undefined;
    let pauseWrite = false;
    let releaseContext!: () => void;
    const contextReady = new Promise<void>((resolve) => { releaseContext = resolve; });
    await page.route("**/players**", async (route) => {
      const request = route.request();
      if (request.isNavigationRequest() || !request.url().includes(":8000/")) return route.continue();
      const url = new URL(request.url());
      if (url.pathname === "/players/context") {
        await contextReady;
        return route.fulfill({ status: contextFailure ? 404 : 200, json: contextFailure
          ? { detail: "Plantel não configurado. Execute python -m app.seed no backend." }
          : { season_id: 17, season_name: "2026/27", team_id: 23, team_name: "CCDR Vila Cortez do Mondego" } });
      }
      if (request.method() === "GET") {
        expect(url.searchParams.get("season_id")).toBe("17");
        expect(url.searchParams.get("team_id")).toBe("23");
        return route.fulfill({ json: rows });
      }
      writes++;
      if (pauseWrite) await new Promise<void>((resolve) => { releaseWrite = resolve; });
      if (failure) return route.fulfill({ status: failure, json: { detail: failure === 409 ? "Número já atribuído." : "Dados inválidos." } });
      const body = request.postDataJSON();
      if (request.method() === "POST") {
        expect(body.season_id).toBe(17);
        expect(body.team_id).toBe(23);
        const row = { ...body, id: rows.length + 1, is_active: true, created_at: "2026-10-01T12:00:00Z" };
        rows.push(row);
        return route.fulfill({ status: 201, json: row });
      }
      const id = Number(url.pathname.split("/").pop());
      rows = rows.map((row) => row.id === id ? { ...row, ...body } : row);
      return route.fulfill({ json: rows.find((row) => row.id === id) });
    });
    await page.goto("/players");
    await expect(page.getByText("A carregar o plantel…", { exact: true })).toBeVisible();
    releaseContext();
    await expect(page.getByRole("main").getByRole("alert")).toContainText("Plantel não configurado");
    contextFailure = false;
    await page.getByRole("button", { name: "Tentar novamente" }).click();
    await expect(page.getByText("Ainda não existem jogadores.", { exact: false })).toBeVisible();
    await page.getByLabel("Nome", { exact: true }).fill("João Silva");
    await page.getByLabel("Número", { exact: true }).fill("8");
    await page.getByLabel("Posição principal").selectOption("MC");
    pauseWrite = true;
    await page.getByRole("button", { name: "Adicionar jogador", exact: true }).click();
    await expect(page.getByRole("button", { name: "A guardar…" })).toBeDisabled();
    await expect.poll(() => writes).toBe(1);
    await page.locator("form").evaluate((form) => {
      form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
      form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
    });
    expect(writes).toBe(1);
    pauseWrite = false;
    releaseWrite!();
    await expect(page.getByRole("heading", { name: "João Silva", exact: true })).toBeVisible();
    await page.getByRole("button", { name: "Editar", exact: true }).click();
    await page.getByLabel("Nome", { exact: true }).fill("João Editado");
    await page.getByLabel("Número", { exact: true }).fill("10");
    await page.getByLabel("Posição principal").selectOption("UNIVERSAL");
    await page.getByRole("button", { name: "Guardar alterações" }).click();
    await expect(page.locator("article")).toContainText("João Editado");
    await expect(page.locator("article")).toContainText("UNIVERSAL");
    await expect(page.locator("article")).toContainText("10");
    await page.getByRole("button", { name: "Desativar", exact: true }).click();
    await expect(page.locator("article")).toContainText("Inativo");
    await page.getByRole("button", { name: "Ativar", exact: true }).click();
    await expect(page.locator("article")).toContainText("Ativo");
    for (const status of [409, 422, 503]) {
      failure = status;
      await page.getByRole("button", { name: "Editar", exact: true }).click();
      await page.getByRole("button", { name: "Guardar alterações" }).click();
      await expect(page.getByRole("main").getByRole("alert")).toContainText(status === 409 ? "Número já atribuído" : status === 422 ? "Verifique o nome" : "base de dados está indisponível");
      await expect(page.getByLabel("Nome", { exact: true })).toHaveValue("João Editado");
      await page.getByRole("button", { name: "Cancelar edição" }).click();
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await page.route("**/players/context", (route) => route.abort());
    await page.reload();
    await expect(page.getByRole("main").getByRole("alert")).toContainText("Não foi possível contactar o servidor");
  });
}
