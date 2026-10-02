import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";
import ts from "typescript";

function compiled(file: string) {
  return ts.transpileModule(readFileSync(file, "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText;
}

test("API relativa inclui cookie e WebSocket usa host da página sem /api", async () => {
  const calls: { url: string; credentials?: RequestCredentials }[] = [];
  const exports: { API_URL?: string; request?: (path: string) => Promise<unknown> } = {};
  runInNewContext(compiled("lib/api.ts"), { exports, process: { env: { NEXT_PUBLIC_API_URL: "/api" } },
    require: () => ({ authDebug: () => {}, authApiOrigin: () => {} }),
    fetch: async (url: string, options: RequestInit) => {
      calls.push({ url, credentials: options.credentials });
      return { ok: true, status: 200, headers: { get: () => null }, json: async () => ({}) };
    } });
  await exports.request!("/auth/me");
  expect(calls).toEqual([{ url: "/api/auth/me", credentials: "include" }]);
  const socket: { liveSocketUrl?: (id: number) => string } = {};
  runInNewContext(compiled("lib/live-socket.ts"), { exports: socket, require: () => exports,
    window: { location: { origin: "https://club.up.railway.app" } }, URL, Set });
  expect(socket.liveSocketUrl!(31)).toBe("wss://club.up.railway.app/ws/matches/31/live");
});
