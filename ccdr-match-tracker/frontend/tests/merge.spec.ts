import { expect, test } from "./auth-fixture";
import type { MergeGame, MergePreview } from "../lib/merge";
import type { Match, Player } from "../lib/api";

const created = "2026-10-04T14:00:00Z";
const player: Player = { id: 7, name: "Jogador teste", position: "MC", shirt_number: 7, season_id: 1, team_id: 1, is_active: true, created_at: created };
const principal: Match = { id: 31, season_id: 1, team_id: 1, opponent_id: 2, opponent_name: "Seia", matchday: 3,
  kickoff_at: created, is_home: true, venue: "Campo", status: "FINISHED", elapsed_seconds: 3780, clock_started_at: null,
  created_at: created, score: { us: 1, opponent: 0 }, can_cancel: true, can_delete: false };
const continuation: Match = { ...principal, id: 32, opponent_id: 3, opponent_name: "Seia FC", matchday: 4, elapsed_seconds: 900 };
function game(match: Match): MergeGame {
  return { match, score: match.score!, elapsed_seconds: match.elapsed_seconds, period: 2, event_count: 1,
    squad: [{ id: match.id, player, is_starter: match.id === 31 }] };
}
const preview: MergePreview = {
  principal: game(principal), continuation: game(continuation), final_status: "FINISHED", preview_token: "signed-preview",
  predicted_score: { us: 2, opponent: 0 }, predicted_elapsed_seconds: 4680, continuation_only_players: [], can_merge: true,
  conflicts: [], warnings: ["Adversários diferentes: Seia / Seia FC. Será mantido o principal.", "Jornadas diferentes.", "Os eventos da 1.ª parte serão convertidos para a 2.ª parte."],
  transfers: [{ original: { id: 18, match_id: 32, event_type: "GOAL", team: "US", player_id: 7, related_player_id: null,
    recorded_by_id: 1, notes: "Golo histórico", elapsed_seconds: 270, period: 1, created_at: created }, new_period: 2, new_elapsed_seconds: 4050 }],
};

for (const width of [360, 390]) {
  test(`ADMIN revê preview e confirma união a ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 850 });
    let previews = 0, executions = 0;
    let stale = true;
    let merged = false;
    await page.route("**/matches**", route => {
      const request = route.request();
      if (request.isNavigationRequest() || !request.url().includes(":8000/")) return route.continue();
      const path = new URL(request.url()).pathname;
      if (path === "/matches/merge/preview") {
        previews++;
        expect(request.postDataJSON()).toEqual({ principal_id: 31, continuation_id: 32, final_status: request.postDataJSON().final_status });
        return route.fulfill({ json: { ...preview, final_status: request.postDataJSON().final_status } });
      }
      if (path === "/matches/merge") {
        executions++;
        expect(request.postDataJSON().confirmation).toBe("UNIR JOGOS");
        expect(request.postDataJSON().preview_token).toBe("signed-preview");
        expect(request.postDataJSON()).not.toHaveProperty("transfers");
        if (stale) { stale = false; return route.fulfill({ status: 409, json: { detail: "Os jogos mudaram. Obtenha um novo preview." } }); }
        merged = true;
        return route.fulfill({ json: { match: principal } });
      }
      if (path.endsWith("/squad")) return route.fulfill({ json: [{ player, role: "TITULAR" }] });
      if (path === "/matches/31") return route.fulfill({ json: { ...principal, score: merged ? preview.predicted_score : principal.score } });
      return route.fulfill({ json: [principal, continuation] });
    });
    await page.goto("/matches/31");
    await page.getByRole("button", { name: "Unir jogo de continuação", exact: true }).click();
    const dialog = page.getByRole("dialog");
    await expect(dialog.getByRole("button", { name: "Obter preview", exact: true })).toBeDisabled();
    await expect(dialog.getByRole("button", { name: "Confirmar união dos jogos", exact: true })).toHaveCount(0);
    await dialog.getByRole("combobox", { name: "Jogo de continuação", exact: true }).selectOption("32");
    await dialog.getByRole("button", { name: "Obter preview", exact: true }).click();
    await expect(dialog.getByRole("region", { name: "Preview da união", exact: true })).toBeVisible();
    await expect(dialog).toContainText("Resultado previsto: 2 – 0");
    await expect(dialog).toContainText("78:00 (4680 s)");
    await expect(dialog).toContainText("04:30 → 2.ª parte · 67:30");
    await expect(dialog).toContainText("Seia / Seia FC");
    await expect(dialog).toContainText("Autor: 1");
    const confirmation = dialog.getByRole("textbox", { name: /Escreve UNIR JOGOS/ });
    await confirmation.fill("UNIR");
    await expect(dialog.getByRole("button", { name: "Confirmar união dos jogos", exact: true })).toBeDisabled();
    expect(executions).toBe(0);
    await confirmation.fill("UNIR JOGOS");
    await expect(dialog.getByRole("button", { name: "Confirmar união dos jogos", exact: true })).toBeEnabled();
    await dialog.screenshot({ path: `artifacts/merge/preview-${width}.png` });
    expect(await dialog.evaluate(element => element.scrollWidth <= element.clientWidth)).toBe(true);
    // Changing final status requires a fresh preview and fresh confirmation.
    await dialog.getByRole("combobox", { name: "Estado final", exact: true }).selectOption("SECOND_HALF");
    await expect(dialog.getByRole("region", { name: "Preview da união", exact: true })).toHaveCount(0);
    await dialog.getByRole("button", { name: "Obter preview", exact: true }).click();
    await confirmation.fill("UNIR JOGOS");
    await dialog.getByRole("button", { name: "Confirmar união dos jogos", exact: true }).click();
    await expect(dialog.getByRole("alert")).toContainText("Os jogos mudaram");
    await expect(dialog.getByRole("region", { name: "Preview da união", exact: true })).toHaveCount(0);
    await dialog.getByRole("button", { name: "Obter preview", exact: true }).click();
    await confirmation.fill("UNIR JOGOS");
    await dialog.getByRole("button", { name: "Confirmar união dos jogos", exact: true }).click();
    await expect(dialog).toHaveCount(0);
    await expect(page.getByLabel("Resultado", { exact: true })).toHaveText("2 – 0");
    expect(previews).toBe(3); expect(executions).toBe(2);
  });
}

for (const role of ["COACH", "VIEWER"] as const) {
  test(`${role} não tem ação de união`, async ({ page }) => {
    await page.route("**/auth/me", route => route.fulfill({ json: { user: { id: 2, name: role, email: "test@test.local", role, is_active: true }, csrf_token: "test" } }));
    await page.route("**/matches/31**", route => {
      if (route.request().isNavigationRequest()) return route.continue();
      return route.fulfill({ json: route.request().url().endsWith("/squad") ? [] : principal });
    });
    await page.goto("/matches/31");
    await expect(page.getByRole("heading", { name: "Convocatória", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Unir jogo de continuação", exact: true })).toHaveCount(0);
  });
}

test("Preview com conflitos bloqueia execução", async ({ page }) => {
  let executions = 0;
  await page.route("**/matches**", route => {
    if (route.request().isNavigationRequest()) return route.continue();
    const path = new URL(route.request().url()).pathname;
    if (path.endsWith("/merge/preview")) return route.fulfill({ json: { ...preview, can_merge: false, preview_token: null, conflicts: ["O relógio está em curso."] } });
    if (path.endsWith("/merge")) executions++;
    return route.fulfill({ json: path.endsWith("/squad") ? [] : path === "/matches/31" ? principal : [principal, continuation] });
  });
  await page.goto("/matches/31");
  await page.getByRole("button", { name: "Unir jogo de continuação", exact: true }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("combobox", { name: "Jogo de continuação", exact: true }).selectOption("32");
  await dialog.getByRole("button", { name: "Obter preview", exact: true }).click();
  await expect(dialog.getByRole("alert")).toContainText("O relógio está em curso.");
  await expect(dialog.getByRole("button", { name: "Confirmar união dos jogos", exact: true })).toBeDisabled();
  await expect(dialog.getByRole("textbox")).toHaveCount(0);
  await dialog.getByRole("button", { name: "Voltar ao jogo", exact: true }).click();
  expect(executions).toBe(0);
});
