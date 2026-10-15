"use client";

import { type FPFCompetition, type FPFMatch, type FPFSnapshot, type FPFStanding } from "@/lib/fpf";

export function OfficialTable({ rows, label = "Classificação oficial FPF" }: { rows: FPFStanding[]; label?: string }) {
  return <div className="standings-scroll" role="region" aria-label={label} tabIndex={0}>
    <table className="standings-table"><caption>Classificação publicada pela FPF na captura</caption>
      <thead><tr>{["Pos.", "Equipa", "Pts", "J", "V", "E", "D", "GM", "GS", "DG"].map((label) => <th scope="col" key={label}>{label}</th>)}</tr></thead>
      <tbody>{rows.map((row) => <tr key={row.name}><td>{row.rank}</td><th scope="row">{row.name}</th>
        {[row.points, row.played, row.wins, row.draws, row.losses, row.goals_for, row.goals_against, row.goal_difference].map((n, index) => <td key={index}>{n}</td>)}</tr>)}</tbody>
    </table>
  </div>;
}

const eventNames: Record<string, string> = { goal: "Golo", yellow_card: "Amarelo", red_card: "Vermelho", substitution: "Substituição" };
export function OfficialMatch({ match, anchor = true }: { match: FPFMatch; anchor?: boolean }) {
  return <details className="card" id={anchor ? `fpf-match-${match.match_id}` : undefined}><summary className="min-h-12 py-3 font-semibold break-words">
    Ficha oficial #{match.match_id} · {match.home.name} {match.home_goals}–{match.away_goals} {match.away.name}
  </summary><div className="space-y-4 mt-3">
    <p>{match.date ?? "Data não disponível"} · {match.time ?? "Hora não disponível"} · {match.venue ?? "Estádio não disponível"}</p>
    <p className="rounded-xl bg-secondary-surface p-3 text-sm">Dados oficiais da captura. Não são eventos, jogadores ou convocatórias internas do Match Tracker.</p>
    <div className="grid gap-4 md:grid-cols-2">{(["home", "away"] as const).map((side) => <section key={side} aria-label={`Plantel oficial ${match[side].name}`} className="space-y-3 min-w-0">
      <h3 className="font-bold">{match[side].name}</h3>{(["starters", "substitutes"] as const).map((group) => <div key={group}><h4 className="font-semibold">{group === "starters" ? "Titulares" : "Suplentes"}</h4>
        {match.availability?.[group] === false ? <p>Não disponível na captura.</p> : <ul className="space-y-2">{match.lineups[side][group].map((p, i) => <li key={`${p.player_id}-${i}`} className="break-words">#{p.shirt_number} {p.name} <span className="text-sm text-muted">FPF: {p.player_id ?? "não disponível"}</span></li>)}</ul>}</div>)}
    </section>)}</div>
    <section aria-label={`Eventos oficiais ${match.match_id}`}><h3 className="font-bold mb-2">Eventos oficiais</h3>{match.availability?.events === false ? <p>Não disponíveis na captura.</p> : <ul className="space-y-2">{match.events.map((event, i) => <li key={i} className="break-words">
      {event.minute_text} · {eventNames[event.type] ?? event.type} · {event.type === "substitution" ? `Entra ${event.player_in?.name ?? "não disponível"}; sai ${event.player_out?.name ?? "não disponível"}` : event.player?.name ?? "Jogador não disponível"}
    </li>)}</ul>}</section>
    <section><h3 className="font-bold">Equipa técnica</h3>{match.staff.length ? <ul className="space-y-2">{match.staff.map((p, i) => <li key={i}>{p.role}: {p.name} · {p.side === "home" ? match.home.name : p.side === "away" ? match.away.name : "Equipa não atribuída pela marcação da fonte"}</li>)}</ul> : <p>Não disponível na captura.</p>}</section>
    <section><h3 className="font-bold">Arbitragem</h3>{match.officials.length ? <ul>{match.officials.map((p, i) => <li key={i}>{p.role}: {p.name}</li>)}</ul> : <p>Não disponível na captura.</p>}</section>
    {match.warnings.map((warning) => <p className="text-warning" key={warning}>{warning}</p>)}
  </div></details>;
}

export function OfficialCompetition({ document, snapshot, preview = false }: { document: FPFCompetition; snapshot?: FPFSnapshot; preview?: boolean }) {
  return <div className="space-y-5"><p className="font-semibold">{document.name} · {document.season} · Competição {document.competition_id} · Época FPF {document.season_id}</p>
    {document.series.map((series) => <section className="space-y-4" key={series.series_id} aria-label={`Série FPF ${series.series_id}`}>
      <h2 className="section-header">Classificação oficial · Série {series.series_id}</h2><OfficialTable rows={series.standings} label={preview ? "Classificação FPF em revisão" : "Classificação oficial FPF"} />
      <h2 className="section-header">Jornadas oficiais</h2><p className="text-sm text-muted">Um link de jornada identificado não significa que os seus jogos já foram importados.</p>
      <div className="grid gap-3 sm:grid-cols-2">{series.rounds.map((round) => {
        const capture = snapshot?.round_captures?.[`${series.series_id}:${round.fixture_id}`];
        const games = capture?.matches ?? series.matches.filter((g) => g.fixture_id === round.fixture_id);
        return <details className="card" key={round.fixture_id}><summary className="min-h-12 py-3">Jornada {round.matchday} · <span className={games.length ? "text-secondary" : "text-warning"}>{games.length ? capture?.complete === false ? "Captura parcial" : "Dados disponíveis" : "Ainda não importada"}</span></summary>
          {!games.length ? <p className="text-muted">Calendário e resultados ainda não disponíveis nesta captura.</p> : <ul className="space-y-3">{games.map((game, i) => <li key={i} className="space-y-1 break-words">
            <p className="font-semibold">{game.home_name} · {game.home_goals === null ? "Resultado não disponível" : `${game.home_goals}–${game.away_goals}`} · {game.away_name}</p>
            <p className="text-sm">{game.schedule_text ?? "Data não disponível no calendário"} · {game.venue ?? "Estádio não disponível"}</p>
            {game.match_id && snapshot?.match_sheets[String(game.match_id)] && <a className="button button-secondary" href={`#fpf-match-${game.match_id}`}>Consultar ficha oficial</a>}
          </li>)}</ul>}
        </details>;
      })}</div>
    </section>)}
  </div>;
}
