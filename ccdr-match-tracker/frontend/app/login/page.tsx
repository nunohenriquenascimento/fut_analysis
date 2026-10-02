"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/components/auth-provider";
import { PageContainer, PrimaryButton } from "@/components/ui";
import { TeamCrest } from "@/components/media";
import { CLUB } from "@/lib/brand";

export default function LoginPage() {
  const router = useRouter();
  const { accept } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setBusy(true); setError("");
    try {
      accept(await api.login(email, password)); setPassword("");
      const next = new URLSearchParams(window.location.search).get("next");
      const safe = next && next.startsWith("/") && !next.startsWith("//") && !next.includes("\\") && !next.startsWith("/login") ? next : "/";
      router.replace(safe);
    } catch (reason) { setError(reason instanceof ApiError ? reason.message : "Não foi possível contactar o servidor."); }
    finally { setBusy(false); }
  }
  return <PageContainer><div className="mx-auto max-w-md space-y-6">
    <div className="flex items-center gap-4"><TeamCrest name={CLUB.name} club /><div><h1 className="text-2xl font-bold">Iniciar sessão</h1><p>{CLUB.name} · Sub-19</p></div></div>
    <form onSubmit={submit} className="card space-y-4">
      <fieldset disabled={busy} className="space-y-4">
        <label className="block">Email<input className="form-field mt-2" type="email" autoComplete="username" required maxLength={254} value={email} onChange={(e) => setEmail(e.target.value)} /></label>
        <label className="block">Password<input className="form-field mt-2" type="password" autoComplete="current-password" required maxLength={128} value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        <PrimaryButton type="submit" className="w-full">{busy ? "A entrar…" : "Entrar"}</PrimaryButton>
      </fieldset>
      {error && <p role="alert" className="text-error">{error}</p>}
    </form>
  </div></PageContainer>;
}
