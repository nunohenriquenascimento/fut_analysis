import Link from "next/link";
import type { ButtonHTMLAttributes, HTMLAttributes, ReactNode } from "react";
import type { MatchStatus } from "@/lib/api";
import { MATCH_STATUS } from "@/lib/matches";

export function PageContainer({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <main id="main-content" tabIndex={-1} className={`page-container ${className}`}>{children}</main>;
}
export function PageHeader({ title, backHref = "/", backLabel = "Início", description }: { title: string; backHref?: string; backLabel?: string; description?: string }) {
  return <header className="page-header"><Link href={backHref} className="back-link">← {backLabel}</Link><h1>{title}</h1>{description && <p>{description}</p>}</header>;
}
export function Card({ className = "", ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={`card ${className}`} {...props} />;
}
type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement>;
function Button({ className = "", variant, ...props }: ButtonProps & { variant: string }) {
  return <button type="button" className={`button button-${variant} ${className}`} {...props} />;
}
export function PrimaryButton(props: ButtonProps) { return <Button variant="primary" {...props} />; }
export function SecondaryButton(props: ButtonProps) { return <Button variant="secondary" {...props} />; }
export function DangerButton(props: ButtonProps) { return <Button variant="danger" {...props} />; }
export function StatusBadge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "success" | "warning" | "danger" | "live" }) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}
export function MatchStatusBadge({ status }: { status: MatchStatus }) {
  const tone = status === "CANCELLED" ? "danger" : status === "FINISHED" ? "success" : status === "SCHEDULED" ? "neutral" : "live";
  return <StatusBadge tone={tone}>{MATCH_STATUS[status]}</StatusBadge>;
}
export function EmptyState({ children }: { children: ReactNode }) { return <Card className="empty-state"><p>{children}</p></Card>; }
export function LoadingState({ children }: { children: ReactNode }) { return <p role="status" className="loading-state"><span aria-hidden="true" className="loading-dot" />{children}</p>; }
export function SectionHeader({ children, id }: { children: ReactNode; id?: string }) { return <h2 id={id} className="section-header">{children}</h2>; }
