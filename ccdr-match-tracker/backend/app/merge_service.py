"""Read-only merge plan and transactional application of that exact plan."""
import hashlib
import hmac
import json
import secrets
import time

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import live_service as live
from app.enums import MatchStatus
from app.match_service import get_match
from app.merge_schemas import MergeGame, MergePreview, MergeSelection, MergeSquad, TransferEvent
from app.models import CompetitionFixture, Match, MatchEvent, MatchSquad, Player
from app.live_schemas import EventRead
from app.schemas import MatchRead, PlayerRead
from app.statistics_service import comparison

# Single-process lifecycle, matching the current Live hub. Restart invalidates previews.
PREVIEW_KEY = secrets.token_bytes(32)
PREVIEW_TTL = 1800


def lock_games(db: Session, selection: MergeSelection) -> tuple[Match, Match]:
    if selection.principal_id == selection.continuation_id:
        raise HTTPException(409, "O principal e a continuação têm de ser jogos diferentes.")
    games = {match_id: get_match(db, match_id, lock=True)
             for match_id in sorted([selection.principal_id, selection.continuation_id])}
    return games[selection.principal_id], games[selection.continuation_id]


def squad(db: Session, match: Match) -> list[MergeSquad]:
    rows = db.execute(select(MatchSquad, Player).join(Player, Player.id == MatchSquad.player_id)
                      .where(MatchSquad.match_id == match.id).order_by(MatchSquad.player_id))
    return [MergeSquad(id=row.id, player=PlayerRead.model_validate(player), is_starter=row.is_starter)
            for row, player in rows]


def snapshot(db: Session, match: Match) -> MergeGame:
    rows = live.events(db, match.id)
    return MergeGame(match=MatchRead.model_validate(match), score=live.score(rows),
                     elapsed_seconds=match.elapsed_seconds, period=live.period(match),
                     event_count=len(rows), squad=squad(db, match))


def plan(db: Session, principal: Match, continuation: Match, selection: MergeSelection) -> MergePreview:
    a, b = snapshot(db, principal), snapshot(db, continuation)
    original, incoming = live.events(db, principal.id), live.events(db, continuation.id)
    conflicts, warnings = [], []
    if db.scalar(select(CompetitionFixture.id).where(CompetitionFixture.internal_match_id == continuation.id)) is not None:
        conflicts.append("A continuação está ligada ao calendário da competição e não pode ser absorvida.")
    if principal.season_id != continuation.season_id:
        conflicts.append("Os jogos pertencem a épocas diferentes.")
    if principal.team_id != continuation.team_id:
        conflicts.append("Os jogos pertencem a equipas principais diferentes.")
    if principal.status not in {MatchStatus.FINISHED, MatchStatus.SECOND_HALF}:
        conflicts.append("O principal deve estar terminado ou na segunda parte com relógio parado.")
    for game in [principal, continuation]:
        if game.clock_started_at is not None:
            conflicts.append(f"O relógio do jogo #{game.id} está em curso. Pare-o antes de obter o preview.")
        if game.status in {MatchStatus.SCHEDULED, MatchStatus.CANCELLED, MatchStatus.FIRST_HALF}:
            conflicts.append(f"O jogo #{game.id} não tem um estado elegível para a fusão.")
    if principal.opponent_id != continuation.opponent_id:
        warnings.append(f"Adversários diferentes: {principal.opponent_name} / {continuation.opponent_name}. Será mantido o principal.")
    if principal.matchday != continuation.matchday:
        warnings.append("Jornadas diferentes. Será mantida a jornada do principal.")
    if principal.kickoff_at != continuation.kickoff_at:
        warnings.append("Datas/horas diferentes. Será mantida a data/hora do principal; a diferença não conta como tempo jogado.")
    if principal.is_home != continuation.is_home or principal.venue != continuation.venue:
        warnings.append("Casa/fora ou local diferentes. Serão mantidos os metadados do principal.")
    periods = {row.period for row in incoming}
    if 1 in periods:
        warnings.append("Os eventos da 1.ª parte da continuação serão explicitamente convertidos para a 2.ª parte do principal.")
    if len(periods) > 1:
        warnings.append("A continuação tem eventos em vários períodos. Todos serão convertidos para a 2.ª parte; confirme que representam apenas tempo posterior ao encerramento.")
    if not incoming:
        warnings.append("A continuação não tem eventos. Apenas o tempo e a convocatória serão reconciliados.")
    a_players = {row.player.id: row for row in a.squad}
    b_players = {row.player.id: row for row in b.squad}
    for player_id in a_players.keys() & b_players.keys():
        if a_players[player_id].is_starter != b_players[player_id].is_starter:
            warnings.append(f"Titular/suplente diferente para {a_players[player_id].player.name}. Será mantida a função no principal.")
    for game, rows, selected in [(principal, original, a_players), (continuation, incoming, b_players)]:
        if game.elapsed_seconds < 0:
            conflicts.append(f"Tempo acumulado inválido no jogo #{game.id}.")
        for row in rows:
            if row.period not in {1, 2} or not 0 <= row.elapsed_seconds <= game.elapsed_seconds:
                conflicts.append(f"O evento #{row.id} tem período/tempo incompatível com o relógio do jogo #{game.id}.")
            for player_id in {row.player_id, row.related_player_id} - {None}:
                if player_id not in selected:
                    conflicts.append(f"O evento #{row.id} referencia um jogador fora da convocatória de origem.")
        for entry in selected.values():
            if entry.player.team_id != game.team_id or entry.player.season_id != game.season_id:
                conflicts.append(f"O jogador #{entry.player.id} não pertence à equipa/época do jogo #{game.id}.")
    total = principal.elapsed_seconds + continuation.elapsed_seconds
    if total > 2147483647:
        conflicts.append("O tempo total excede o limite suportado.")
    return MergePreview(principal=a, continuation=b, final_status=selection.final_status,
        transfers=[TransferEvent(original=EventRead.model_validate(row),
                                 new_elapsed_seconds=principal.elapsed_seconds + row.elapsed_seconds)
                   for row in sorted(incoming, key=lambda row: (row.elapsed_seconds, row.id))],
        continuation_only_players=[row for row in b.squad if row.player.id not in a_players],
        predicted_score=live.score(original + incoming), predicted_elapsed_seconds=total,
        warnings=warnings, conflicts=conflicts, can_merge=not conflicts)


def fingerprint(db: Session, principal: Match, continuation: Match, preview: MergePreview) -> str:
    # Include every stored column, not only the visible preview. Detect notes, authors,
    # squad roles/timestamps, metadata and event changes while waiting for confirmation.
    def columns(row):
        return {column.name: getattr(row, column.name) for column in row.__table__.columns}
    stored = []
    for game in [principal, continuation]:
        stored.append({"match": columns(game), "events": [columns(row) for row in live.events(db, game.id)],
                       "squad": [columns(row) for row in db.scalars(select(MatchSquad)
                                 .where(MatchSquad.match_id == game.id).order_by(MatchSquad.player_id))]})
    encoded = json.dumps({"preview": preview.model_dump(mode="json"), "stored": stored},
                         default=str, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def signature(issued: str, digest: str, actor_id: int) -> str:
    return hmac.new(PREVIEW_KEY, f"{issued}:{digest}:{actor_id}".encode(), hashlib.sha256).hexdigest()


def token(digest: str, actor_id: int) -> str:
    issued = str(int(time.time()))
    return f"{issued}.{digest}.{signature(issued, digest, actor_id)}"


def verify_token(value: str, digest: str, actor_id: int) -> None:
    try:
        issued, previous, signed = value.split(".")
        valid = (0 <= time.time() - int(issued) <= PREVIEW_TTL
                 and hmac.compare_digest(signed, signature(issued, previous, actor_id))
                 and hmac.compare_digest(previous, digest))
    except (ValueError, TypeError):
        valid = False
    if not valid:
        raise HTTPException(409, "O preview expirou ou os jogos mudaram. Obtenha e confirme um novo preview.")


def apply(db: Session, principal: Match, continuation: Match, preview: MergePreview) -> None:
    originals = live.events(db, principal.id)
    incoming = live.events(db, continuation.id)
    comparison_before = comparison(originals + incoming)
    expected_events = {row.id: EventRead.model_validate(row).model_dump() for row in originals}
    for transfer in preview.transfers:
        expected_events[transfer.original.id] = {**transfer.original.model_dump(),
            "match_id": principal.id, "period": 2, "elapsed_seconds": transfer.new_elapsed_seconds}
    expected = {row.original.id: row for row in preview.transfers}
    for row in incoming:
        row.match_id = principal.id
        row.period = 2
        row.elapsed_seconds = expected[row.id].new_elapsed_seconds
    existing = {row.player_id for row in db.scalars(select(MatchSquad).where(MatchSquad.match_id == principal.id))}
    for row in db.scalars(select(MatchSquad).where(MatchSquad.match_id == continuation.id)):
        if row.player_id in existing:
            db.delete(row)
        else:
            row.match_id = principal.id
    principal.elapsed_seconds = preview.predicted_elapsed_seconds
    principal.clock_started_at = None
    principal.status = MatchStatus(preview.final_status)
    db.flush()
    combined = live.events(db, principal.id)
    if (len(combined) != preview.principal.event_count + preview.continuation.event_count
            or live.score(combined) != preview.predicted_score
            or comparison(combined) != comparison_before
            or {row.id: EventRead.model_validate(row).model_dump() for row in combined} != expected_events
            or live.events(db, continuation.id)):
        raise HTTPException(409, "A validação dos eventos/resultado falhou. Nenhum jogo foi unido.")
    reconciled = {row.player.id: row.is_starter for row in squad(db, principal)}
    desired = {row.player.id: row.is_starter for row in preview.continuation.squad}
    desired.update({row.player.id: row.is_starter for row in preview.principal.squad})
    if reconciled != desired:
        raise HTTPException(409, "A validação da convocatória falhou. Nenhum jogo foi unido.")
    # Only the now-empty continuation is removed. Unrecognised FKs cause rollback.
    db.delete(continuation)
    db.flush()
