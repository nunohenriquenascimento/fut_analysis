"use client";

import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { api, ApiError, setCsrfToken, type AuthState, type AuthUser } from "@/lib/api";
import { LoadingState, PageContainer, SecondaryButton } from "./ui";

type AuthContextValue = { user: AuthUser | null; canEdit: boolean; isAdmin: boolean; accept: (state: AuthState) => void; logout: () => Promise<void> };
const AuthContext = createContext<AuthContextValue | null>(null);
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("AuthProvider em falta");
  return context;
}

export default function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const path = usePathname();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checked, setChecked] = useState(false);
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);
  const generation = useRef(0);
  const publicPage = path === "/login";

  useEffect(() => {
    let active = true;
    function unauthenticated() {
      if (!active) return;
      generation.current += 1;
      setUser(null); setCsrfToken(null); setChecked(true); setError("");
      if (path !== "/login") router.replace(`/login?next=${encodeURIComponent(path)}`);
    }
    async function check() {
      const version = generation.current;
      try {
        const state = await api.me();
        if (active && version === generation.current) { setUser(state.user); setCsrfToken(state.csrf_token); setError(""); setChecked(true); }
      } catch (reason) {
        if (!active || version !== generation.current) return;
        if (reason instanceof ApiError && reason.status === 401) unauthenticated();
        else { setError("Não foi possível validar a sessão. Verifique a ligação ao servidor."); setChecked(true); }
      }
    }
    window.addEventListener("ccdr:unauthenticated", unauthenticated);
    void check();
    const timer = window.setInterval(() => void check(), 60_000);
    return () => { active = false; window.clearInterval(timer); window.removeEventListener("ccdr:unauthenticated", unauthenticated); };
  }, [path, retry, router]);

  function accept(state: AuthState) { generation.current += 1; setUser(state.user); setCsrfToken(state.csrf_token); setChecked(true); setError(""); }
  async function logout() {
    await api.logout();
    generation.current += 1; setUser(null); setCsrfToken(null); router.replace("/login");
  }
  const isAdmin = user?.role === "ADMIN";
  const canEdit = isAdmin || user?.role === "COACH";
  return <AuthContext.Provider value={{ user, canEdit, isAdmin, accept, logout }}>
    {publicPage ? children : !checked ? <PageContainer><LoadingState>A validar sessão…</LoadingState></PageContainer>
      : error ? <PageContainer><p role="alert">{error}</p><SecondaryButton onClick={() => setRetry((value) => value + 1)}>Tentar novamente</SecondaryButton></PageContainer>
      : !user ? <PageContainer><LoadingState>A abrir o login…</LoadingState></PageContainer>
      : path.startsWith("/users") && !isAdmin ? <PageContainer><h1>Acesso reservado ao ADMIN</h1></PageContainer>
      : children}
  </AuthContext.Provider>;
}
