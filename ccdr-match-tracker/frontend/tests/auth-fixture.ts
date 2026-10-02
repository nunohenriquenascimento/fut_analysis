import { test as base, expect } from "@playwright/test";

// Existing business-flow regressions run as ADMIN. Authentication scenarios
// import Playwright directly and exercise login, expiry and each role.
export const test = base.extend({
  page: async ({ page }, runFixture) => {
    await page.route("**/auth/me", (route) => route.fulfill({ json: {
      user: { id: 1, name: "Admin", email: "admin@test.local", role: "ADMIN", is_active: true }, csrf_token: "test-csrf",
    } }));
    await runFixture(page);
  },
});
export { expect };
