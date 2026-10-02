// Diagnostic allowlist: never pass bodies, response payloads or Error objects.
export function authDebug(path: string, phase: "request" | "response" | "fetch_error", details?: {
  status?: number; request_id?: string | null;
}) {
  if (process.env.NEXT_PUBLIC_AUTH_DEBUG !== "true" || typeof window === "undefined") return;
  const browser = navigator.userAgent;
  const family = /Edg/.test(browser) ? "Edge" : /Firefox|FxiOS/.test(browser) ? "Firefox" : /Chrome|CriOS/.test(browser) ? "Chrome" : /Safari/.test(browser) ? "Safari" : "Other";
  console.info("AUTH_DEBUG", { timestamp: new Date().toISOString(), path, phase,
    user_agent: `${/Mobile|Android|iPhone|iPad/.test(browser) ? "Mobile" : "Desktop"} ${family}`,
    online: navigator.onLine, origin: window.location.origin, credentials: "include",
    ...(details?.status !== undefined ? { status: details.status } : {}),
    ...(details?.request_id && /^[a-f0-9]{32}$/.test(details.request_id) ? { request_id: details.request_id } : {}),
    ...(phase === "fetch_error" ? { reason: "fetch_failed" } : {}),
  });
}

export function authApiOrigin(value: string) {
  if (process.env.NEXT_PUBLIC_AUTH_DEBUG !== "true" || typeof window === "undefined") return;
  // Print only a credential-free origin, never query/path or the raw config.
  try { console.info("AUTH_DEBUG_API", { api_origin: new URL(value, window.location.origin).origin }); }
  catch { console.info("AUTH_DEBUG_API", { reason: "invalid_api_url" }); }
}
