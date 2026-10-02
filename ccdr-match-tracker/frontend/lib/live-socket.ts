import { API_URL } from "./api";

export type LiveMessageType = "live.snapshot" | "live.state_changed" | "live.event_created" | "live.event_updated" | "live.event_deleted" | "live.match_updated" | "live.cancelled" | "live.ping";
export interface LiveMessage { type: LiveMessageType; version: 1; match_id: number; actor_id: number | null; data: Record<string, unknown> }
export type SocketStatus = "connected" | "reconnecting" | "offline";
const types = new Set<string>(["live.snapshot", "live.state_changed", "live.event_created", "live.event_updated", "live.event_deleted", "live.match_updated", "live.cancelled", "live.ping"]);

export function liveSocketUrl(matchId: number): string {
  const url = new URL(`${API_URL}/ws/matches/${matchId}/live`);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  return url.toString();
}

export function connectLiveSocket(matchId: number, callbacks: {
  onUpdate: (message?: LiveMessage) => void; onStatus: (status: SocketStatus) => void;
}) {
  let stopped = false;
  let socket: WebSocket | null = null;
  let attempt = 0;
  let retry: ReturnType<typeof setTimeout> | undefined;
  let watchdog: ReturnType<typeof setTimeout> | undefined;
  function pulse() {
    clearTimeout(watchdog);
    watchdog = setTimeout(() => socket?.close(), 45_000);
  }
  function schedule() {
    if (stopped || retry) return;
    callbacks.onStatus(attempt >= 3 ? "offline" : "reconnecting");
    const delay = Math.min(30_000, 1000 * 2 ** Math.min(attempt++, 5));
    retry = setTimeout(() => { retry = undefined; open(); }, delay + Math.random() * delay * .2);
  }
  function open() {
    if (stopped) return;
    callbacks.onStatus(attempt >= 3 ? "offline" : "reconnecting");
    try { socket = new WebSocket(liveSocketUrl(matchId)); }
    catch { schedule(); return; }
    const current = socket;
    current.onopen = () => { if (!stopped) { callbacks.onStatus("connected"); pulse(); } };
    current.onmessage = (event) => {
      if (stopped) return;
      let message: LiveMessage;
      try { message = JSON.parse(event.data); } catch { return; }
      if (!message || message.version !== 1 || message.match_id !== matchId || !types.has(message.type)) return;
      pulse(); attempt = 0;
      if (message.type === "live.ping") { if (current.readyState === WebSocket.OPEN) current.send("pong"); }
      else callbacks.onUpdate(message);
    };
    current.onerror = () => { /* onclose owns the retry; never block HTTP writes. */ };
    current.onclose = (event) => {
      clearTimeout(watchdog);
      if (stopped) return;
      if ([4401, 4403, 4404, 4409, 1008].includes(event.code)) {
        stopped = true; callbacks.onStatus("offline"); callbacks.onUpdate();
        if (event.code === 4401) window.dispatchEvent(new Event("ccdr:unauthenticated"));
      } else schedule();
    };
  }
  function resume() {
    if (stopped || document.visibilityState === "hidden") return;
    callbacks.onUpdate();
    if (!socket || socket.readyState === WebSocket.CLOSED) {
      clearTimeout(retry); retry = undefined; open();
    }
  }
  window.addEventListener("online", resume);
  document.addEventListener("visibilitychange", resume);
  open();
  return () => {
    stopped = true; clearTimeout(retry); clearTimeout(watchdog);
    window.removeEventListener("online", resume); document.removeEventListener("visibilitychange", resume);
    if (socket) { socket.onclose = null; socket.onmessage = null; socket.onopen = null; socket.close(); }
  };
}
