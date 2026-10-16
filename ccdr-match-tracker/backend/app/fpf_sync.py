"""Map verified HTML onto the current championship without internal writes."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import hashlib
import json
from copy import deepcopy

from fastapi import HTTPException
from sqlalchemy import select

from app.competition_api import apply_fixture_import, commit
from app.competition_schemas import FixtureImport
from app.fpf_parser import parse_competition, parse_match, parse_fixture, bind_fixture
from app.fpf_source import ORIGIN
from app.models import CompetitionFixture, CompetitionTeam, Season, Team, Match


def validate_results(observations, existing):
    """Only simultaneous captures must agree; persisted results are update context."""
    grouped = {}
    for row, source in observations:
        if row.get("match_id") and row["home_goals"] is not None:
            grouped.setdefault(row["match_id"], []).append(dict(
                source=source, home_goals=row["home_goals"], away_goals=row["away_goals"]))
    conflicts = []
    for match_id, values in grouped.items():
        if len({(v["home_goals"], v["away_goals"]) for v in values}) > 1:
            persisted = [dict(source=f"persisted_fixture:{r.id}", home_goals=r.home_goals,
                              away_goals=r.away_goals) for r in existing.values()
                         if r.source == f"{ORIGIN}/Match/GetMatchInformation?matchId={match_id}"
                         and r.home_goals is not None and r.internal_match_id is None]
            conflicts.append(dict(match_id=match_id, sources=values, persisted=persisted))
    if conflicts:
        raise HTTPException(409, dict(code="FPF_RESULT_CONFLICT",
            message="Resultados FPF contraditórios no mesmo lote. Corrija as capturas e volte a rever a importação. Nenhuma alteração aplicada.",
            conflicts=conflicts))
    return {match_id: (values[0]["home_goals"], values[0]["away_goals"])
            for match_id, values in grouped.items()}


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
    existing = {r.external_key: r for r in db.scalars(select(CompetitionFixture).where(CompetitionFixture.competition_id == competition.id))}
    rows = list(series["matches"])
    observations = [(row, "competition_html") for row in rows] if payload.competition_html is not None else []
    duplicate_errors = []
    uploaded_rounds = {}
    for index, html in enumerate(payload.fixture_htmls):
        if isinstance(html, str):
            fixture_doc = parse_fixture(html)
        else:
            if (html.competition_id, html.season_id, html.series_id) != identity:
                raise HTTPException(409, "Origem da jornada incompatível com competição, época ou série confirmadas.")
            fixture_doc = parse_fixture(html.html, source_url=html.source_url)
            context = bind_fixture(document, fixture_doc, payload.series_id)
            fixture_doc.update(context, source_url=html.source_url)
        observations.extend((row, f"fixture_htmls[{index}]:{fixture_doc['fixture_id']}") for row in fixture_doc["matches"])
        if fixture_doc["fixture_id"] in uploaded_rounds and uploaded_rounds[fixture_doc["fixture_id"]] != fixture_doc:
            duplicate_errors.append("Capturas contraditórias da mesma jornada; lote rejeitado sem alterações.")
        uploaded_rounds[fixture_doc["fixture_id"]] = fixture_doc
        if fixture_doc["fixture_id"] not in rounds:
            raise HTTPException(409, "Jornada fora da série confirmada.")
        for row in fixture_doc["matches"]:
            if {row["home_name"], row["away_name"]} - names:
                raise HTTPException(409, "Jornada com equipas fora do mapeamento.")
            rows.append({**row, "matchday": rounds[fixture_doc["fixture_id"]]})
    sheets = dict(old.get("match_sheets", {}))
    sheet_rounds = {**old.get("match_rounds", {}), **payload.match_rounds}
    ignored = []
    uploaded_sheets = set()
    for index, html in enumerate(payload.match_htmls):
        sheet = parse_match(html)
        observations.append((sheet, f"match_htmls[{index}]:{sheet['match_id']}"))
        if (sheet["competition_id"], sheet["season_id"]) != identity[:2]:
            raise HTTPException(409, "Ficha de outra competição/época.")
        if {sheet["home"]["name"], sheet["away"]["name"]} - names:
            raise HTTPException(409, "Ficha com equipas fora do mapeamento.")
        key = str(sheet["match_id"])
        if key in uploaded_sheets and sheets[key] != sheet:
            duplicate_errors.append("Fichas contraditórias para o mesmo ID FPF.")
        uploaded_sheets.add(key)
        sheets[key] = sheet
    current_results = validate_results(observations, existing)
    if duplicate_errors:
        raise HTTPException(409, duplicate_errors[0])

    def historical_result(row):
        # Replaying saved HTML must never undo a later, verified correction.
        match_id = row.get("match_id")
        result = current_results.get(match_id)
        if result is None and match_id:
            result = next(((r.home_goals, r.away_goals) for r in existing.values()
                           if r.source == f"{ORIGIN}/Match/GetMatchInformation?matchId={match_id}"
                           and r.internal_match_id is None and r.home_goals is not None), None)
        return {**row, "home_goals": result[0], "away_goals": result[1]} if result else row

    if payload.competition_html is None:
        rows[:len(series["matches"])] = [historical_result(row) for row in series["matches"]]
    for key, sheet in sheets.items():
        if key not in uploaded_sheets:
            sheet = historical_result(sheet)
        round_id = sheet_rounds.get(key)
        known = {r["fixture_id"] for r in rows if r.get("match_id") == sheet["match_id"]}
        if not known and round_id is None:
            known = {fid for fid, day in rounds.items() for fixture in existing.values()
                     if fixture.matchday == day and fixture.source == sheet["source_url"]}
        if round_id is None and len(known) == 1:
            round_id = next(iter(known))
            sheet_rounds[key] = round_id
        if round_id is None:
            ignored.append(dict(match_id=sheet["match_id"], reason="Ficha sem jornada confirmada; selecione a jornada para alimentar o calendário e a classificação."))
            continue
        if round_id not in rounds:
            raise HTTPException(409, "A jornada indicada não consta da captura.")
        if known and known != {round_id}:
            raise HTTPException(409, "Jornada da ficha contradiz a jornada do mesmo ID FPF.")
        if key not in uploaded_sheets and any(r.get("match_id") == sheet["match_id"] and r["home_goals"] is not None for r in rows):
            continue
        kickoff = None
        if sheet["date"] and sheet["time"]:
            kickoff = datetime.fromisoformat(f"{sheet['date']}T{sheet['time']}").replace(tzinfo=ZoneInfo("Europe/Lisbon"))
        rows.append(dict(home_name=sheet["home"]["name"], away_name=sheet["away"]["name"],
                         home_goals=sheet["home_goals"], away_goals=sheet["away_goals"],
                         matchday=rounds[round_id], fixture_id=round_id, venue=sheet["venue"],
                         match_id=sheet["match_id"], schedule_text=None, kickoff_at=kickoff.isoformat() if kickoff else None))
    if set(payload.match_rounds) - set(sheets):
        raise HTTPException(409, "Ligação de jornada sem ficha verificada.")
    source = f"{ORIGIN}/Competition/Details?competitionId={identity[0]}&seasonId={identity[1]}"
    links = {**old.get("internal_match_links", {}), **payload.internal_match_links}
    proposed, pending = {}, []
    # Reconcile a visible scheduled row with its detailed sheet; never invent missing rounds.
    merged = {}
    for row in rows:
        pair = (row["matchday"], row["home_name"], row["away_name"])
        previous_row = merged.get(pair)
        if previous_row and previous_row.get("match_id") and row.get("match_id") and previous_row["match_id"] != row["match_id"]:
            raise HTTPException(409, "IDs FPF contraditórios para o mesmo jogo.")
        if previous_row is None or row["home_goals"] is not None:
            merged[pair] = row
    for row in merged.values():
        home, away = mapping[row["home_name"]], mapping[row["away_name"]]
        legacy_key = f"fpf:{identity[1]}:{identity[0]}:{payload.series_id}:{row['fixture_id']}:{home}:{away}"
        match_source = f"{ORIGIN}/Match/GetMatchInformation?matchId={row['match_id']}" if row["match_id"] else None
        matches = [r for r in existing.values() if (match_source and r.source == match_source)
                   or (r.matchday, r.home_team_id, r.away_team_id) == (row["matchday"], home, away)]
        if len(matches) > 1:
            raise HTTPException(409, "Mais de um registo local corresponde ao jogo FPF.")
        previous = matches[0] if matches else None
        key = previous.external_key if previous else f"fpf:match:{row['match_id']}" if row["match_id"] else legacy_key
        if previous and match_source and "/Match/GetMatchInformation?" in previous.source and previous.source != match_source:
            raise HTTPException(409, "O jogo local está associado a outro ID FPF.")
        internal = links.get(key, links.get(legacy_key)) or (previous.internal_match_id if previous else None)
        ours = competition.internal_team_id in {home, away}
        if ours and internal is None:
            candidates = list(db.scalars(select(Match).where(
                Match.season_id == competition.season_id, Match.team_id == competition.internal_team_id,
                Match.matchday == row["matchday"],
                Match.opponent_id == (away if home == competition.internal_team_id else home),
                Match.is_home == (home == competition.internal_team_id))))
            if len(candidates) > 1:
                pending.append(dict(external_key=key, reason="Vários jogos internos compatíveis; confirme a ligação.", official=row))
                continue
            if candidates:
                internal = candidates[0].id
        if not ours and internal is not None:
            raise HTTPException(409, "Ligação interna num jogo externo.")
        if internal:
            links[key] = internal
        fixture = dict(external_key=key, matchday=row["matchday"], home_team_id=home, away_team_id=away,
                       internal_match_id=internal, home_goals=None if internal else row["home_goals"],
                       away_goals=None if internal else row["away_goals"], venue=row["venue"],
                       kickoff_at=datetime.fromisoformat(row["kickoff_at"]) if row.get("kickoff_at") else None,
                       source=match_source or next((doc["source_url"] for doc in uploaded_rounds.values()
                                                   if doc["fixture_id"] == row["fixture_id"] and doc.get("source_url")), source))
        if key in proposed and proposed[key] != fixture:
            raise HTTPException(409, "O mesmo ID FPF identifica jogos incompatíveis.")
        proposed[key] = fixture
    for key, fixture in proposed.items():
        if key in existing:
            previous = existing[key]
            if not previous.source.startswith(ORIGIN + "/"):
                raise HTTPException(409, "Existe uma correção manual; a FPF não a substitui silenciosamente.")
            # Unknown capture fields cannot erase metadata already known locally.
            fixture["kickoff_at"] = fixture["kickoff_at"] or previous.kickoff_at
            if fixture["venue"] is None:
                fixture["venue"] = previous.venue
            if "/Match/GetMatchInformation?" in previous.source and "/Match/GetMatchInformation?" not in fixture["source"]:
                fixture["source"] = previous.source
            if fixture["home_goals"] is None and not fixture["internal_match_id"] and previous.home_goals is not None:
                fixture["home_goals"], fixture["away_goals"] = previous.home_goals, previous.away_goals
                fixture["source"] = previous.source
    state = dict(snapshot=old, members=sorted(members), internal_matches=[
        (m.id, m.matchday, m.opponent_id, m.is_home) for m in db.scalars(select(Match).where(
            Match.season_id == competition.season_id, Match.team_id == competition.internal_team_id).order_by(Match.id))], fixtures=[
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
        apply_fixture_import(db, competition, validated, validate_only=True, member_ids=found, allow_fpf_external=True)
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
        source_doc = uploaded_rounds.get(row["fixture_id"])
        if source_doc and source_doc.get("source_url"):
            capture.update(source_url=source_doc["source_url"], competition_id=identity[0], season_id=identity[1])
        observed = [name for game in capture["matches"] for name in (game["home_name"], game["away_name"])]
        capture["complete"] = len(observed) == len(series["standings"]) and len(set(observed)) == len(observed)
    snapshot = dict(identity=list(identity), competition=document, team_mapping=dict(mapping), match_sheets=sheets,
                    internal_match_links=links, match_rounds=sheet_rounds,
                    source_url=source, mode=mode, coverage="visible_round_only",
                    round_captures=round_captures,
                    html_sha256=hashlib.sha256(payload.competition_html.encode()).hexdigest() if payload.competition_html is not None else old["html_sha256"],
                    imported_at=datetime.now(timezone.utc).isoformat())
    summary = dict(created=sum(c["action"] == "create" for c in changes),
                   updated=sum(c["action"] == "update" for c in changes),
                   ignored=sum(c["action"] == "unchanged" for c in changes) + len(ignored) + len(pending),
                   rejected=0)
    return dict(summary=summary, ignored=ignored, snapshot=snapshot, fixtures=list(proposed.values()), pending_internal_links=pending,
                add_participants=sorted(found - members), changes=changes, state_token=state_token,
                standings_before=old.get("competition", {}).get("series", []))


def apply_fpf(db, competition, plan):
    for team_id in plan["add_participants"]:
        db.add(CompetitionTeam(competition_id=competition.id, team_id=team_id))
    db.flush()
    if plan["fixtures"]:
        apply_fixture_import(db, competition, FixtureImport(fixtures=plan["fixtures"]), commit_changes=False, allow_fpf_external=True)
    competition.fpf_data = plan["snapshot"]
    commit(db)
    return dict(summary=plan["summary"], ignored=plan["ignored"], imported=len(plan["fixtures"]), pending_internal_links=plan["pending_internal_links"],
                coverage="visible_round_only", mode=plan["snapshot"]["mode"])
