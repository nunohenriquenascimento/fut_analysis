import Link from "next/link";
import { CLUB } from "@/lib/brand";
import { TeamCrest } from "@/components/media";
import { PageContainer } from "@/components/ui";

const destinations = [
  { href: "/players", icon: "◎", title: "Plantel", text: "Os jogadores, as posições e a nossa equipa." },
  { href: "/matches", icon: "▦", title: "Jogos", text: "Preparar jornadas e escolher os convocados." },
  { href: "/matches", icon: "◉", title: "Jogo ao Vivo", text: "Escolher jogo e registar cada acontecimento." },
  { href: "/statistics", icon: "▥", title: "Estatísticas", text: "A época, os resultados e os jogadores em números." },
];
export default function Home() {
  return <PageContainer className="wide-page"><div className="page-content">
    <section className="home-hero"><div className="flex items-center gap-4"><TeamCrest name={CLUB.name} club size="lg" /><div><p className="home-kicker">{CLUB.squad}</p><p className="mt-2 text-muted">Época {CLUB.season}</p></div></div><h1>{CLUB.name}</h1><p className="text-muted">A nossa equipa. Cada jogo. Cada momento.</p></section>
    <section aria-label="Áreas da aplicação" className="home-grid space-y-3 md:space-y-0">{destinations.map((item) => <Link href={item.href} key={item.title} className={`home-card ${item.title === "Jogo ao Vivo" ? "home-card-live" : ""}`}><span aria-hidden="true" className="home-icon">{item.icon}</span><span className="min-w-0"><strong>{item.title}</strong><small>{item.text}</small></span></Link>)}</section>
    <footer className="mt-8 text-sm text-muted">CCDR · Sub-19 · 2026/27</footer>
  </div></PageContainer>;
}
