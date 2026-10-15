"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { CLUB } from "@/lib/brand";
import { TeamCrest } from "./media";
import { useAuth } from "./auth-provider";
import { useState } from "react";

export default function AppHeader() {
  const path = usePathname();
  const { user, isAdmin, logout } = useAuth();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  if (path === "/login") return null;
  return <header className="app-header">
    <a className="skip-link" href="#main-content">Saltar para o conteúdo</a>
    <div className="app-header-inner">
      <Link href="/" className="club-brand" aria-label="CCDR Sub-19 · Início"><TeamCrest name={CLUB.name} club size="sm" /><span><strong>{CLUB.shortName}</strong><small>{CLUB.squad} · Época {CLUB.season}</small></span></Link>
      <nav aria-label="Navegação principal">{[["/players", "Plantel"], ["/matches", "Jogos"], ["/competitions", "Campeonato"], ["/statistics", "Estatísticas"]].map(([href, title]) => <Link key={href} href={href} aria-current={path.startsWith(href) ? "page" : undefined}>{title}</Link>)}</nav>
      {user && <div className="flex flex-wrap items-center gap-2 text-sm"><span>{user.name} · {user.role}</span>{isAdmin && <Link href="/users" className="button button-secondary">Utilizadores</Link>}
        <button className="button button-secondary" disabled={busy} onClick={async () => { setBusy(true); setError(""); try { await logout(); } catch { setError("Não foi possível terminar a sessão. Tente novamente."); } finally { setBusy(false); } }}>Sair</button>{error && <p role="alert">{error}</p>}</div>}
    </div>
  </header>;
}
