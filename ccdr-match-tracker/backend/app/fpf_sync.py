"""Map verified HTML onto the current championship without internal writes."""
from datetime import datetime, timezone
import hashlib
import json
from copy import deepcopy

from fastapi import HTTPException
from sqlalchemy import select

from app.competition_api import apply_fixture_import, commit
from app.competition_schemas import FixtureImport
from app.fpf_parser import parse_competition, parse_match
from app.fpf_source import ORIGIN
from app.models import CompetitionFixture, CompetitionTeam, Season, Team


def prepare_fpf(db, competition, payload, *, mode="captured_html"):
    old = competition.fpf_data or {}
    if payload.competition_html is None:
        if not old:
            raise HTTPException(409, "Importe primeiro o HTML da competição.")
        document = deepcopy(old["competition"])
    else:
        document = parse_competition(payload.competition_html)
    series = next((s for s in document["series"] if s["series_id"] == payload.series_id), None)
    if series is None:
        raise HTTPException(409, "Série não encontrada na captura.")
    season = db.get(Season, competition.season_id)
    if document["season"] != f"{season.starts_on.year}-{season.ends_on.year}":
        raise HTTPException(409, "A época FPF não corresponde à época interna.")
    identity = (document["competition_id"], document["season_id"], payload.series_id)
    if old and identity != tuple(old["identity"]):
        raise HTTPException(409, "A competição já está associada a outra origem FPF.")
    names = {r["name"] for r in series["standings"]}
    mapping = payload.team_mapping
    if names != set(mapping) or len(set(mapping.values())) != len(mapping):
        raise HTTPException(409, "Mapeie todas as equipas FPF para IDs internos distintos.")
    if old and old["team_mapping"] != mapping:
        raise HTTPException(409, "O mapeamento FPF existente não pode ser reassociado automaticamente.")
    found = set(db.scalars(select(Team.id).where(Team.id.in_(mapping.values()))))
    if found != set(mapping.values()) or competition.internal_team_id not in found:
        raise HTTPException(409, "Mapeamento incompleto ou nossa equipa ausente.")
    members = set(db.scalars(select(CompetitionTeam.team_id).where(CompetitionTeam.competition_id == competition.id)))
    if members - found:
        raise HTTPException(409, "Há participantes internos fora do mapeamento; nenhuma remoção automática.")
    rounds = {r["fixture_id"]: r["matchday"] for r in series["rounds"]}
    rows = list(series["matches"])
    sheets = dict(old.get("match_sheets", {}))
    for html in payload.match_htmls:
        sheet = parse_match(html)
        if (sheet["competition_id"], sheet["season_id"]) != identity[:2]:
            raise HTTPException(409, "Ficha de outra competição/época.")
        if {sheet["home"]["name"], sheet["away"]["name"]} - names:
            raise HTTPException(409, "Ficha com equipas fora do mapeamento.")
        key = str(sheet["match_id"])
        sheets[key] = sheet
        round_id = payload.match_rounds.get(key)
        if round_id is not None:
            if round_id not in rounds:
                raise HTTPException(409, "A jornada indicada não consta da captura.")
            rows.append(dict(home_name=sheet["home"]["name"], away_name=sheet["away"]["name"],
                             home_goals=sheet["home_goals"], away_goals=sheet["away_goals"],
                             matchday=rounds[round_id], fixture_id=round_id, venue=sheet["venue"],
                             match_id=sheet["match_id"], schedule_text=None))
    if set(payload.match_rounds) - set(sheets):
        raise HTTPException(409, "Ligação de jornada sem ficha verificada.")
    source = f"{ORIGIN}/Competition/Details?competitionId={identity[0]}&seasonId={identity[1]}"
    links = {**old.get("internal_match_links", {}), **payload.internal_match_links}
    proposed, pending = {}, []
    for row in rows:
        home, away = mapping[row["home_name"]], mapping[row["away_name"]]
        key = f"fpf:{identity[1]}:{identity[0]}:{payload.series_id}:{row['fixture_id']}:{home}:{away}"
        internal = links.get(key)
        ours = competition.internal_team_id in {home, away}
        if ours and internal is None:
            pending.append(dict(external_key=key, reason="internal_match_link_required", official=row))
            continue
        if not ours and internal is not None:
            raise HTTPException(409, "Ligação interna num jogo externo.")
        fixture = dict(external_key=key, matchday=row["matchday"], home_team_id=home, away_team_id=away,
                       internal_match_id=internal, home_goals=None if ours else row["home_goals"],
                       away_goals=None if ours else row["away_goals"], venue=row["venue"],
                       source=source if row["match_id"] is None else f"{ORIGIN}/Match/GetMatchInformation?matchId={row['match_id']}")
        if key in proposed and proposed[key] != fixture:
            raise HTTPException(409, "Capturas contraditórias para o mesmo jogo; reveja o lote.")
        proposed[key] = fixture
    existing = {r.external_key: r for r in db.scalars(select(CompetitionFixture).where(CompetitionFixture.competition_id == competition.id))}
    for key, fixture in proposed.items():
        if key in existing:
            previous = existing[key]
            if not previous.source.startswith(ORIGIN + "/"):
                raise HTTPException(409, "Existe uma correção manual; a FPF não a substitui silenciosamente.")
            # Unknown capture fields cannot erase metadata already known locally.
            fixture["kickoff_at"] = previous.kickoff_at
            if fixture["venue"] is None:
                fixture["venue"] = previous.venue
            if fixture["home_goals"] is None and not fixture["internal_match_id"] and previous.home_goals is not None:
                raise HTTPException(409, "A captura sem resultado não pode apagar um resultado conhecido.")
    state = dict(snapshot=old, members=sorted(members), fixtures=[
        {c.name: getattr(row, c.name) for c in CompetitionFixture.__table__.columns}
        for row in sorted(existing.values(), key=lambda item: item.id)])
    state_token = hashlib.sha256(json.dumps(state, default=str, sort_keys=True).encode()).hexdigest()
    if payload.expected_state is not None and payload.expected_state != state_token:
        raise HTTPException(409, "Os dados mudaram após o preview. Reveja as diferenças antes de confirmar.")
    changes = []
    for key, fixture in proposed.items():
        previous = existing.get(key)
        before = {field: getattr(previous, field) for field in fixture} if previous is not None else None
        after = dict(fixture)
        changes.append(dict(external_key=key, action="create" if before is None else "unchanged" if before == after else "update",
                            before=before, after=after))
    if proposed:
        try:
            validated = FixtureImport(fixtures=list(proposed.values()))
        except ValueError:
            raise HTTPException(422, "Campos FPF incompatíveis com o calendário interno; reveja a captura.") from None
        apply_fixture_import(db, competition, validated, validate_only=True, member_ids=found)
    round_captures = deepcopy(old.get("round_captures", {}))
    for source_doc in [old.get("competition"), document]:
        if not source_doc:
            continue
        for source_series in source_doc["series"]:
            for round_info in source_series["rounds"]:
                games = [g for g in source_series["matches"] if g["fixture_id"] == round_info["fixture_id"]]
                if games:
                    observed = [name for g in games for name in (g["home_name"], g["away_name"])]
                    round_captures[f"{source_series['series_id']}:{round_info['fixture_id']}"] = dict(
                        series_id=source_series["series_id"], fixture_id=round_info["fixture_id"], matchday=round_info["matchday"],
                        matches=games, complete=len(observed) == len(source_series["standings"]) and len(set(observed)) == len(observed))
    for row in rows:
        key = f"{payload.series_id}:{row['fixture_id']}"
        capture = round_captures.setdefault(key, dict(series_id=payload.series_id, fixture_id=row["fixture_id"],
                                                     matchday=row["matchday"], matches=[], complete=False))
        pairs = {(game["home_name"], game["away_name"]): game for game in capture["matches"]}
        previous_game = pairs.get((row["home_name"], row["away_name"]))
        if previous_game is None or row["home_goals"] is not None or previous_game["home_goals"] is None:
            pairs[(row["home_name"], row["away_name"])] = row
        capture["matches"] = list(pairs.values())
        observed = [name for game in capture["matches"] for name in (game["home_name"], game["away_name"])]
        capture["complete"] = len(observed) == len(series["standings"]) and len(set(observed)) == len(observed)
    snapshot = dict(identity=list(identity), competition=document, team_mapping=dict(mapping), match_sheets=sheets,
                    internal_match_links=links,
                    source_url=source, mode=mode, coverage="visible_round_only",
                    round_captures=round_captures,
                    html_sha256=hashlib.sha256(payload.competition_html.encode()).hexdigest() if payload.competition_html is not None else old["html_sha256"],
                    imported_at=datetime.now(timezone.utc).isoformat())
    return dict(snapshot=snapshot, fixtures=list(proposed.values()), pending_internal_links=pending,
                add_participants=sorted(found - members), changes=changes, state_token=state_token,
                standings_before=old.get("competition", {}).get("series", []))


def apply_fpf(db, competition, plan):
    for team_id in plan["add_participants"]:
        db.add(CompetitionTeam(competition_id=competition.id, team_id=team_id))
    db.flush()
    if plan["fixtures"]:
        apply_fixture_import(db, competition, FixtureImport(fixtures=plan["fixtures"]), commit_changes=False)
    competition.fpf_data = plan["snapshot"]
    commit(db)
    return dict(imported=len(plan["fixtures"]), pending_internal_links=plan["pending_internal_links"],
                coverage="visible_round_only", mode=plan["snapshot"]["mode"])
