"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { api, ApiError, type AuthUser, type UserRole } from "@/lib/api";
import { useAuth } from "@/components/auth-provider";
import { PageContainer, PageHeader, PrimaryButton, SecondaryButton, LoadingState, StatusBadge } from "@/components/ui";

export default function UsersPage() {
  const { isAdmin, user: self } = useAuth();
  const [rows, setRows] = useState<AuthUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [editing, setEditing] = useState<AuthUser | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("VIEWER");
  const [active, setActive] = useState(true);
  const [reload, setReload] = useState(0);
  const locked = useRef(false);
  useEffect(() => {
    let cancelled = false;
    if (!isAdmin) return;
    api.users().then((users) => { if (!cancelled) { setRows(users); setError(""); } })
      .catch((reason) => { if (!cancelled) setError(reason instanceof ApiError ? reason.message : "Não foi possível carregar os utilizadores."); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [isAdmin, reload]);
  function open(user: AuthUser | null) {
    setEditing(user); setName(user?.name ?? ""); setEmail(user?.email ?? ""); setPassword("");
    setRole(user?.role ?? "VIEWER"); setActive(user?.is_active ?? true); setFormOpen(true); setError(""); setNotice("");
  }
  async function save(event: FormEvent) {
    event.preventDefault();
    if (locked.current) return;
    locked.current = true; setBusy(true); setError("");
    try {
      const fields = { name, email, role, is_active: active };
      if (editing) {
        // Submit only changes, so editing one's name does not revoke the session.
        const changes = Object.fromEntries(Object.entries(fields).filter(([key, value]) => editing[key as keyof AuthUser] !== value));
        await api.updateUser(editing.id, { ...changes, ...(password ? { password } : {}) });
      } else await api.createUser({ ...fields, password });
      setPassword(""); setFormOpen(false); setNotice("Utilizador guardado.");
      if (editing?.id === self?.id) await api.me();
      setReload((value) => value + 1);
    } catch (reason) { setError(reason instanceof ApiError ? reason.message : "Não foi possível guardar o utilizador."); }
    finally { locked.current = false; setBusy(false); }
  }
  if (!isAdmin) return <PageContainer><h1>Acesso reservado ao ADMIN</h1></PageContainer>;
  return <PageContainer><div className="page-content space-y-6">
    <PageHeader title="Utilizadores" description="Gestão de contas e permissões" />
    {loading && <LoadingState>A carregar utilizadores…</LoadingState>}
    {error && <p role="alert" className="text-error">{error}</p>}
    {notice && <p role="status" className="text-success">{notice}</p>}
    {!formOpen && <PrimaryButton disabled={busy || loading} onClick={() => open(null)}>Criar utilizador</PrimaryButton>}
    {formOpen && <form className="card space-y-4" onSubmit={save}>
      <h2 className="text-xl font-semibold">{editing ? "Editar utilizador" : "Novo utilizador"}</h2>
      <fieldset disabled={busy} className="space-y-4">
        <label className="block">Nome<input className="form-field mt-2" value={name} required maxLength={120} onChange={(e) => setName(e.target.value)} /></label>
        <label className="block">Email<input className="form-field mt-2" type="email" value={email} required maxLength={254} onChange={(e) => setEmail(e.target.value)} /></label>
        <label className="block">{editing ? "Nova password (opcional)" : "Password"}<input className="form-field mt-2" type="password" autoComplete="new-password" value={password} required={!editing} minLength={12} maxLength={128} onChange={(e) => setPassword(e.target.value)} /></label>
        <label className="block">Papel<select className="form-field mt-2" value={role} onChange={(e) => setRole(e.target.value as UserRole)}>{["ADMIN", "COACH", "VIEWER"].map((value) => <option key={value}>{value}</option>)}</select></label>
        <label className="flex items-center gap-2"><input type="checkbox" checked={active} onChange={(e) => setActive(e.target.checked)} />Conta ativa</label>
        <p className="text-sm text-muted">Alterações de password, email, papel ou atividade terminam as sessões dessa conta. O último ADMIN ativo fica protegido.</p>
        <div className="flex flex-wrap gap-3"><PrimaryButton type="submit">Guardar utilizador</PrimaryButton><SecondaryButton onClick={() => { setFormOpen(false); setPassword(""); }}>Cancelar edição</SecondaryButton></div>
      </fieldset>
    </form>}
    <section aria-label="Contas" className="space-y-3">{rows.map((user) => <article className="card space-y-2" key={user.id}>
      <h2 className="break-words text-lg font-semibold">{user.name}</h2><p className="break-words">{user.email}</p><p>{user.role}</p>
      <StatusBadge tone={user.is_active ? "success" : "neutral"}>{user.is_active ? "Ativo" : "Inativo"}</StatusBadge>
      <div><SecondaryButton disabled={busy || loading} onClick={() => open(user)}>Editar {user.name}</SecondaryButton></div>
    </article>)}</section>
    <SecondaryButton disabled={busy || loading} onClick={() => { setLoading(true); setReload((value) => value + 1); }}>Atualizar utilizadores</SecondaryButton>
  </div></PageContainer>;
}
