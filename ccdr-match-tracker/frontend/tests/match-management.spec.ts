import { expect, test } from "./auth-fixture";
import type { Page } from "@playwright/test";

async function setup(page: Page, options: { role?: "ADMIN" | "COACH" | "VIEWER"; eligible?: boolean; conflict?: boolean } = {}) {
  const role = options.role ?? "ADMIN";
  await page.route("**/auth/me", (route) => route.fulfill({ json: {
    user: { id: 1, name: role, email: `${role.toLowerCase()}@test.local`, role, is_active: true }, csrf_token: "server-csrf",
  } }));
  let deleted = false;
  let deleteRequests = 0;
  let forceRequests = 0;
  let cancelRequests = 0;
  const game = { id: 31, season_id: 1, team_id: 1, opponent_id: 2, opponent_name: "Adversário", matchday: 3,
    kickoff_at: "2026-10-04T14:00:00Z", is_home: true, venue: "Campo", status: "SCHEDULED", elapsed_seconds: 0,
    clock_started_at: null, created_at: "2026-10-02T12:00:00Z", score: { us: 2, opponent: 1 }, can_delete: options.eligible ?? true, can_cancel: true };
  await page.route("**/players/context", (route) => route.fulfill({ json: { season_id: 1, team_id: 1, team_name: "CCDR Vila Cortez do Mondego", season_name: "2026/27" } }));
  await page.route("**/matches**", (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (request.isNavigationRequest() || url.port !== "8000") return route.continue();
    if (request.method() !== "GET") expect(request.headers()["x-csrf-token"]).toBe("server-csrf");
    if (request.method() === "DELETE") {
      if (url.pathname.endsWith("/force")) { forceRequests++; expect(request.postDataJSON()).toEqual({ confirmation: "ELIMINAR" }); }
      deleteRequests++;
      if (options.conflict) { game.can_delete = false; return route.fulfill({ status: 409, json: { detail: "Tem convocatória." } }); }
      deleted = true;
      return route.fulfill({ status: 204 });
    }
    if (url.pathname.endsWith("/cancel")) {
      cancelRequests++;
      game.status = "CANCELLED"; game.can_cancel = false; game.can_delete = false;
      return route.fulfill({ json: game });
    }
    return route.fulfill({ json: url.pathname.endsWith("/squad") ? [] : url.pathname === "/matches" ? deleted ? [] : [game] : game });
  });
  return { deletes: () => deleteRequests, forces: () => forceRequests, cancellations: () => cancelRequests };
}

for (const role of ["ADMIN", "COACH", "VIEWER"] as const) {
  test(`Gestão destrutiva: visibilidade de ${role}`, async ({ page }) => {
    await setup(page, { role }); // Even forged true flags must not expose actions to non-admins.
    await page.goto("/matches/31");
    await expect(page.getByRole("heading", { name: "Convocatória", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Eliminar jogo", exact: true })).toHaveCount(role === "ADMIN" ? 1 : 0);
    await expect(page.getByRole("button", { name: "Cancelar jogo", exact: true })).toHaveCount(role === "ADMIN" ? 1 : 0);
    await expect(page.getByRole("button", { name: "Eliminar jogo e dados associados", exact: true })).toHaveCount(role === "ADMIN" ? 1 : 0);
  });
}

test("ADMIN não vê eliminar quando o servidor recusa elegibilidade", async ({ page }) => {
  await setup(page, { eligible: false });
  await page.goto("/matches/31");
  await expect(page.getByRole("button", { name: "Cancelar jogo", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Eliminar jogo", exact: true })).toHaveCount(0);
});

test("Eliminação forçada exige duas confirmações e usa rota separada a 360px", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  const calls = await setup(page, { eligible: false });
  await page.goto("/matches/31");
  await expect(page.getByRole("button", { name: "Eliminar jogo", exact: true })).toHaveCount(0);
  await page.getByRole("button", { name: "Eliminar jogo e dados associados", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Eliminar jogo e dados associados", exact: true });
  await expect(dialog).toContainText("toda a convocatória, todos os eventos");
  const confirm = dialog.getByRole("button", { name: "Confirmar eliminação de todos os dados" });
  await expect(confirm).toBeDisabled();
  await dialog.getByRole("checkbox").check();
  await expect(confirm).toBeDisabled();
  await dialog.getByRole("textbox").fill("eliminar");
  await expect(confirm).toBeDisabled();
  expect(calls.deletes()).toBe(0);
  await dialog.getByRole("textbox").fill("ELIMINAR");
  await confirm.click();
  await expect(page).toHaveURL(/\/matches$/);
  await expect(page.getByText("Ainda não existem jogos nesta época.")).toBeVisible();
  expect(calls.deletes()).toBe(1);
  expect(calls.forces()).toBe(1);
});

test("Eliminar exige confirmação explícita e atualiza lista após redirect a 360px", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  const calls = await setup(page);
  await page.goto("/matches/31");
  await page.getByRole("button", { name: "Eliminar jogo", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Eliminar jogo", exact: true });
  await expect(dialog).toContainText("permanente");
  await expect(dialog.getByRole("button", { name: "Confirmar eliminação" })).toBeDisabled();
  expect(calls.deletes()).toBe(0);
  await dialog.getByRole("button", { name: "Voltar ao jogo" }).click();
  expect(calls.deletes()).toBe(0);
  await page.getByRole("button", { name: "Eliminar jogo", exact: true }).click();
  await dialog.getByRole("checkbox").check();
  await dialog.getByRole("button", { name: "Confirmar eliminação" }).click();
  await expect(page).toHaveURL(/\/matches$/);
  await expect(page.getByText("Ainda não existem jogos nesta época.")).toBeVisible();
  expect(calls.deletes()).toBe(1);
});

test("Cancelamento confirma preservação de histórico e atualiza badge a 360px", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  const calls = await setup(page, { eligible: false });
  await page.goto("/matches/31");
  await page.getByRole("button", { name: "Cancelar jogo", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Cancelar jogo", exact: true });
  await expect(dialog).toContainText("preservados");
  expect(calls.cancellations()).toBe(0);
  await dialog.getByRole("button", { name: "Voltar ao jogo" }).click();
  expect(calls.cancellations()).toBe(0);
  await page.getByRole("button", { name: "Cancelar jogo", exact: true }).click();
  await dialog.getByRole("button", { name: "Confirmar cancelamento" }).click();
  await expect(page.getByText("Cancelado", { exact: true })).toBeVisible();
  await expect(page.getByText("Jogo cancelado. O histórico foi preservado.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Cancelar jogo", exact: true })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Eliminar jogo", exact: true })).toHaveCount(0);
  expect(calls.cancellations()).toBe(1);
});

test("DELETE 409 explica bloqueio, conserva detalhe e atualiza elegibilidade", async ({ page }) => {
  const calls = await setup(page, { conflict: true });
  await page.goto("/matches/31");
  await page.getByRole("button", { name: "Eliminar jogo", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Eliminar jogo", exact: true });
  await dialog.getByRole("checkbox").check();
  await dialog.getByRole("button", { name: "Confirmar eliminação" }).click();
  await expect(dialog.getByRole("alert")).toContainText("já não pode ser eliminado com segurança");
  await dialog.getByRole("button", { name: "Voltar ao jogo" }).click();
  await expect(page).toHaveURL(/\/matches\/31$/);
  await expect(page.getByRole("button", { name: "Eliminar jogo", exact: true })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Cancelar jogo", exact: true })).toBeVisible();
  expect(calls.deletes()).toBe(1);
});
