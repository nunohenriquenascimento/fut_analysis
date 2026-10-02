"use client";

import { useEffect, useRef, useState } from "react";
import { connectLiveSocket, type SocketStatus } from "./live-socket";

export function useLiveSocket(matchId: number, onUpdate: () => void) {
  const [status, setStatus] = useState<SocketStatus>("reconnecting");
  const callback = useRef(onUpdate);
  useEffect(() => { callback.current = onUpdate; }, [onUpdate]);
  useEffect(() => {
    if (!Number.isInteger(matchId) || matchId < 1 || matchId > 2147483647) return;
    return connectLiveSocket(matchId, { onStatus: setStatus, onUpdate: () => callback.current() });
  }, [matchId]);
  return status;
}
