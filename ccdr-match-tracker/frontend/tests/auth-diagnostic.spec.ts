import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";
import ts from "typescript";

function compiled(file: string) {
  return ts.transpileModule(readFileSync(file, "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText;
}

for (const enabled of [false, true]) test(`Diagnóstico auth ${enabled}: include e ausência de secrets`, async () => {
  const logs: unknown[] = [], calls: RequestInit[] = [];
  const diagnostic = {};
  const common = { process: { env: { NEXT_PUBLIC_AUTH_DEBUG: String(enabled), NEXT_PUBLIC_API_URL: "https://api.example.pt" } },
    console: { info: (...args: unknown[]) => logs.push(args) },
    window: { location: { origin: "https://app.example.pt" } },
    navigator: { userAgent: "Mobile Safari SECRET-UA", onLine: true }, URL };
  runInNewContext(compiled("lib/auth-debug.ts"), { ...common, exports: diagnostic });
  const exports: { request?: (path: string, init?: RequestInit) => Promise<unknown> } = {};
  runInNewContext(compiled("lib/api.ts"), { ...common, exports, require: () => diagnostic,
    fetch: async (_url: string, init: RequestInit) => {
      calls.push(init);
      return { ok: true, status: 200, headers: { get: () => "a".repeat(32) }, json: async () => ({ token: "SECRET-RESPONSE", csrf_token: "SECRET-CSRF" }) };
    } });
  for (const path of ["/auth/login", "/auth/me", "/auth/logout"]) {
    await exports.request!(path, { method: path.endsWith("me") ? "GET" : "POST", body: "SECRET-PASSWORD", credentials: "omit" });
  }
  expect(calls.every((call) => call.credentials === "include")).toBe(true);
  expect(logs.length > 0).toBe(enabled);
  const text = JSON.stringify(logs);
  for (const secret of ["SECRET-UA", "SECRET-RESPONSE", "SECRET-CSRF", "SECRET-PASSWORD"]) expect(text).not.toContain(secret);
  if (enabled) { expect(text).toContain("request_id"); expect(text).toContain("Mobile Safari"); expect(text).toContain("/auth/me"); }
});

test("Erro fetch é registado sem mensagem sensível do Error", async () => {
  const logs: unknown[] = [];
  const exports: { authDebug?: (path: string, phase: string) => void } = {};
  runInNewContext(compiled("lib/auth-debug.ts"), { exports,
    process: { env: { NEXT_PUBLIC_AUTH_DEBUG: "true" } },
    window: { location: { origin: "https://app.example.pt" } }, navigator: { userAgent: "Mobile Safari", onLine: false },
    console: { info: (...args: unknown[]) => logs.push(args) } });
  exports.authDebug!("/auth/login", "fetch_error");
  expect(JSON.stringify(logs)).toContain("fetch_failed");
  expect(JSON.stringify(logs)).toContain('"online":false');
});
