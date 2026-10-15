"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { EmptyState, LoadingState, PageContainer, PageHeader, PrimaryButton } from "@/components/ui";
import { competitionsApi, competitionError, type Competition } from "@/lib/competitions";
import { ErrorNotice } from "./competition-ui";
import CompetitionCreateForm from "./create-form";

export default function CompetitionsPage() {
  const { canEdit } = useAuth();
  const [rows, setRows] = useState<Competition[]>([]);
  const [loading, setLoading] = useState(true), [error, setError] = useState("");
  const [reload, setReload] = useState(0), [creating, setCreating] = useState(false);
  useEffect(() => {
    let active = true;
    competitionsApi.list().then((result) => { if (active) { setRows(result); setError(""); } })
      .catch((reason) => { if (active) setError(competitionError(reason)); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [reload]);
  return <PageContainer className="wide-page"><div className="page-content space-y-6">
    <PageHeader title="Campeonato" description="Classificação, jornadas e equipas participantes." />
    {loading ? <LoadingState>A carregar campeonatos…</LoadingState> : error ? <ErrorNotice message={error} retry={() => { setLoading(true); setReload((n) => n + 1); }} /> : <>
      {canEdit && !creating && <PrimaryButton onClick={() => setCreating(true)}>Criar competição</PrimaryButton>}
      {canEdit && creating && <CompetitionCreateForm onCancel={() => setCreating(false)} />}
      {rows.length === 0 && <EmptyState>Ainda não existem competições configuradas.</EmptyState>}
      <section aria-label="Competições" className="grid gap-3 md:grid-cols-2">{rows.map((row) => <Link href={`/competitions/${row.id}`} className="card block" key={row.id}>
        <h2 className="section-header">{row.name}</h2><span className="badge badge-warning mt-3">Classificação provisória</span>
        <p className="mt-3 text-muted">Ver classificação, resultados e calendário →</p>
      </Link>)}</section>
    </>}
  </div></PageContainer>;
}
