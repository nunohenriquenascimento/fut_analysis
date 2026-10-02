import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";
import ts from "typescript";

function compiled(file: string) {
  return ts.transpileModule(readFileSync(file, "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText;
}

test("Configuração Vercel exige uma API HTTPS pública", () => {
  const code = compiled("next.config.ts");
  for (const url of [undefined, "http://api.club.pt", "https://localhost", "https://127.0.0.1", "https://user:password@api.club.pt", "https://api.club.pt/path", "https://api.club.pt?token=secret", "invalid"]) {
    expect(() => runInNewContext(code, { exports: {}, process: { env: { VERCEL: "1", NEXT_PUBLIC_API_URL: url } }, URL })).toThrow();
  }
  expect(() => runInNewContext(code, { exports: {}, process: { env: { VERCEL: "1", NEXT_PUBLIC_API_URL: "https://api.club.pt" } }, URL })).not.toThrow();
  expect(() => runInNewContext(code, { exports: {}, process: { env: {} }, URL })).not.toThrow();
});

test("URL Live deriva WSS de HTTPS sem identidade na query", () => {
  const exports: { liveSocketUrl?: (id: number) => string } = {};
  runInNewContext(compiled("lib/live-socket.ts"), { exports, require: () => ({ API_URL: "https://api.club.pt" }), URL, Set });
  expect(exports.liveSocketUrl!(31)).toBe("wss://api.club.pt/ws/matches/31/live");
});
