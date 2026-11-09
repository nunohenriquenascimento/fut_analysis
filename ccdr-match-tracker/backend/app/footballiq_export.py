"""Núcleo de exportação FootballIQ v1, sem HTTP nem autorização inventada.

A leitura devolve um rascunho sem authorized_scope. A emissão real está bloqueada
até existir autorização por recurso. Nenhum método altera entidades ou tabelas.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal
from zoneinfo import ZoneInfo

from sqlalchemy import Select, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.enums import EventTeam, EventType, MatchStatus
from app.live_service import score
from app.models import (
    Competition,
    CompetitionFixture,
    Match,
    MatchEvent,
    MatchSquad,
    Player,
)

JsonObject = dict[str, Any]
QUALITY_CATEGORIES = (
    "score_events",
    "shots",
    "cards",
    "substitutions",
    "other_events",
    "player_attribution",
    "squad",
)
AUTHORIZATION_BLOCKER = (
    "O Tracker não dispõe de autorização por clube/equipa para matches:export. "
    "O rascunho não é um pacote v1 autorizado para consumo real."
)


def _positive_id(value: int) -> None:
    if type(value) is not int or value <= 0:
        raise ValueError("IDs internos devem ser inteiros positivos, sem booleanos.")


def _text(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Identidade/nome não pode ficar vazio.")
    return value.strip()


def _utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("Datetime deve incluir timezone explícito.")
    return value.astimezone(UTC)


def _instant(value: datetime) -> str:
    return _utc(value).isoformat().replace("+00:00", "Z")


def _digest(value: object) -> str:
    # Canonicalização local v1: UTF-8, chaves ordenadas e sem espaços/NaN.
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ExportSettings:
    """Configuração explícita da instalação, sem ler .env ou obter credenciais."""

    source_instance_id: str
    timezone: str

    def __post_init__(self) -> None:
        """Valida a identidade estável e a zona de apresentação fornecidas."""
        if _text(self.source_instance_id) != self.source_instance_id:
            raise ValueError(
                "source_instance_id deve ser canónico, sem espaços exteriores."
            )
        ZoneInfo(self.timezone)


@dataclass(frozen=True)
class ExportSelection:
    """Determina o âmbito de leitura; IDs aqui não são prova de autorização."""

    team_id: int
    season_id: int
    as_of: datetime
    competition_scope: Literal["all", "single"]
    competition_id: int | None

    def __post_init__(self) -> None:
        """Exige equipa, época, data e opção competitiva sem defaults implícitos."""
        _positive_id(self.team_id)
        _positive_id(self.season_id)
        _utc(self.as_of)
        if self.competition_scope not in {"all", "single"}:
            raise ValueError("competition_scope deve ser all ou single.")
        if (self.competition_scope == "single") != (self.competition_id is not None):
            raise ValueError("competition_id deve existir apenas em single.")
        if self.competition_id is not None:
            _positive_id(self.competition_id)


@dataclass(frozen=True)
class ExportDraft:
    """Conteúdo não autorizado; não contém scope nem snapshot_version de pacote.

    selection_version identifica apenas seleção/conteúdo, não permissões.
    Este objeto não deve ser servido a clientes não autorizados.
    """

    content: JsonObject
    selection_version: str
    authorization_blocker: str = AUTHORIZATION_BLOCKER


class AuthorizationUnavailable(PermissionError):
    """Indica que não é possível emitir legitimamente um pacote completo."""


def emit_authorized_package(*_args: object, **_kwargs: object) -> JsonObject:
    """Recusa emissão real, sem consultar bases ou aceitar scopes do chamador."""
    raise AuthorizationUnavailable(AUTHORIZATION_BLOCKER)


def recent_matches_query(selection: ExportSelection) -> Select:
    """Limita jogos antes de carregar eventos; EXISTS evita duplicação por fixtures."""
    query = select(Match).where(
        Match.team_id == selection.team_id,
        Match.season_id == selection.season_id,
        Match.status == MatchStatus.FINISHED,
        Match.kickoff_at <= _utc(selection.as_of),
    )
    if selection.competition_scope == "single":
        linked = (
            select(CompetitionFixture.id)
            .where(
                CompetitionFixture.internal_match_id == Match.id,
                CompetitionFixture.competition_id == selection.competition_id,
            )
            .exists()
        )
        query = query.where(linked)
    return query.order_by(Match.kickoff_at.desc(), Match.id.desc()).limit(5)


def _player(player_id: int, players: Mapping[int, Player], match: Match) -> JsonObject:
    player = players.get(player_id)
    if player is None or player.id != player_id:
        raise ValueError("Referência a uma inscrição inexistente ou inconsistente.")
    _positive_id(player.id)
    if player.team_id != match.team_id or player.season_id != match.season_id:
        raise ValueError("Inscrição fora da equipa/época do jogo.")
    return {
        "source_player_id": str(player.id),
        "team_id": str(player.team_id),
        "season_id": str(player.season_id),
        "name": _text(player.name),
    }


def _match_content(
    match: Match,
    events: Sequence[MatchEvent],
    squads: Sequence[MatchSquad],
    players: Mapping[int, Player],
    fixture: CompetitionFixture | None,
    competitions: Mapping[int, Competition],
    settings: ExportSettings,
) -> JsonObject:
    home, away = (
        (match.team, match.opponent) if match.is_home else (match.opponent, match.team)
    )
    if (
        home.id == away.id
        or match.team.id != match.team_id
        or match.opponent.id != match.opponent_id
    ):
        raise ValueError("Identidade das equipas inconsistente.")
    competition_id = None
    references = []
    if fixture is not None:
        competition = competitions.get(fixture.competition_id)
        if competition is None or (
            competition.season_id,
            competition.internal_team_id,
            fixture.home_team_id,
            fixture.away_team_id,
            fixture.matchday,
        ) != (match.season_id, match.team_id, home.id, away.id, match.matchday):
            raise ValueError("Ligação de competição/fixture desatualizada.")
        if fixture.home_goals is not None or fixture.away_goals is not None:
            raise ValueError(
                "Fixture interno não pode manter outro resultado armazenado."
            )
        competition_id = str(competition.id)
        references.append({"resource": "competition_fixture", "id": str(fixture.id)})
    recorded_squad = []
    squad_player_ids = set()
    for entry in sorted(squads, key=lambda row: row.id):
        _positive_id(entry.id)
        if entry.match_id != match.id or entry.player_id in squad_player_ids:
            raise ValueError("Convocatória duplicada ou associada a outro jogo.")
        squad_player_ids.add(entry.player_id)
        if type(entry.is_starter) is not bool:
            raise ValueError("Titularidade inválida.")
        recorded_squad.append(
            {
                "source_squad_id": str(entry.id),
                "player": _player(entry.player_id, players, match),
                "is_starter": entry.is_starter,
            }
        )
    exported_events = []
    seen = set()
    ordered_events = sorted(
        events, key=lambda row: (row.period, row.elapsed_seconds, row.id)
    )
    for event in ordered_events:
        _positive_id(event.id)
        if event.match_id != match.id or event.id in seen:
            raise ValueError("Evento duplicado ou de outro jogo.")
        seen.add(event.id)
        if event.team not in {
            EventTeam.US,
            EventTeam.OPPONENT,
        } or event.event_type not in set(EventType):
            raise ValueError("Equipa/tipo de evento desconhecido.")
        if type(event.period) is not int or event.period not in {1, 2}:
            raise ValueError("Período fora do contrato v1.")
        if type(event.elapsed_seconds) is not int or event.elapsed_seconds < 0:
            raise ValueError("Tempo acumulado inválido.")
        if event.related_player_id is not None and event.event_type not in {
            EventType.GOAL,
            EventType.SUBSTITUTION,
        }:
            raise ValueError("Segundo jogador não permitido neste evento.")
        if event.player_id is not None and event.player_id == event.related_player_id:
            raise ValueError("Os dois jogadores do evento devem ser diferentes.")
        event_players = []
        for player_id in (event.player_id, event.related_player_id):
            if player_id is None:
                event_players.append(None)
            else:
                if event.team != EventTeam.US or player_id not in squad_player_ids:
                    raise ValueError(
                        "Jogador de evento fora da convocatória/equipa interna."
                    )
                event_players.append(_player(player_id, players, match))
        exported_events.append(
            {
                "source_event_id": str(event.id),
                "source_match_id": str(match.id),
                "event_type": str(event.event_type),
                "team_id": str(
                    match.team_id if event.team == EventTeam.US else match.opponent_id
                ),
                "period": event.period,
                "elapsed_seconds": event.elapsed_seconds,
                "minute": event.elapsed_seconds // 60,
                "player": event_players[0],
                "related_player": event_players[1],
            }
        )
    result = score(list(ordered_events))
    has_goal_records = any(
        row.event_type in {EventType.GOAL, EventType.OWN_GOAL} for row in ordered_events
    )
    # Só preservamos uma contagem observada, nunca um resultado certificado.
    home_goals, away_goals = (
        (result.us, result.opponent) if match.is_home else (result.opponent, result.us)
    )
    payload = {
        "source_match_id": str(match.id),
        "team_id": str(match.team_id),
        "season_id": str(match.season_id),
        "competition_id": competition_id,
        "kickoff_at": _instant(match.kickoff_at),
        "timezone": settings.timezone,
        "status": "FINISHED",
        "home_team": {"team_id": str(home.id), "name": _text(home.name)},
        "away_team": {"team_id": str(away.id), "name": _text(away.name)},
        "score": {
            "home_goals": home_goals if has_goal_records else None,
            "away_goals": away_goals if has_goal_records else None,
            "status": "unverified",
            "provenance": {
                "method": "events",
                "reference_ids": [
                    f"event:{row.id}"
                    for row in ordered_events
                    if row.event_type in {EventType.GOAL, EventType.OWN_GOAL}
                ],
                "verified_at": None,
            },
        },
        "events": exported_events,
        "squad": recorded_squad or None,
        "quality": {
            name: {"status": "unknown", "evidence": None, "assessed_at": None}
            for name in QUALITY_CATEGORIES
        },
        "updated_at": None,
        "source_reference": {"resource": "internal_match", "id": str(match.id)},
        "external_references": references,
    }
    payload["data_version"] = _digest(
        {
            "hash_version": 1,
            "source_system": "match_tracker",
            "source_instance_id": settings.source_instance_id,
            "match": payload,
        }
    )
    return payload


def build_export_draft(
    selection: ExportSelection,
    settings: ExportSettings,
    *,
    matches: Sequence[Match],
    events: Sequence[MatchEvent],
    squads: Sequence[MatchSquad],
    players: Mapping[int, Player],
    fixtures: Sequence[CompetitionFixture],
    competitions: Mapping[int, Competition],
    exported_at: datetime,
) -> ExportDraft:
    """Transforma apenas os jogos previamente selecionados, sem mutar ORM.

    Não filtra ou reordena jogos para esconder erros do produtor e não aceita
    um sexto jogo. Eventos/convocatórias podem chegar fora de ordem e são
    serializados numa ordem estável. Um scope de autorização não é fabricado.
    """
    exported_at = _utc(exported_at)
    if len(matches) > 5:
        raise ValueError(
            "A seleção deve limitar a cinco antes de carregar os detalhes."
        )
    ids = [match.id for match in matches]
    if len(ids) != len(set(ids)):
        raise ValueError("Jogos duplicados.")
    order = [(_utc(match.kickoff_at), match.id) for match in matches]
    if order != sorted(order, reverse=True):
        raise ValueError("Jogos fora da ordenação kickoff/id numérico.")
    selected_ids = set(ids)
    linked: dict[int, CompetitionFixture] = {}
    for fixture in fixtures:
        if fixture.internal_match_id not in selected_ids:
            raise ValueError("Fixture não pertence aos jogos selecionados.")
        if fixture.internal_match_id in linked:
            raise ValueError("Mais de um fixture associado ao mesmo jogo interno.")
        linked[fixture.internal_match_id] = fixture
    grouped_events: dict[int, list[MatchEvent]] = {mid: [] for mid in ids}
    grouped_squads: dict[int, list[MatchSquad]] = {mid: [] for mid in ids}
    for rows, groups in ((events, grouped_events), (squads, grouped_squads)):
        row_ids = [row.id for row in rows]
        if len(row_ids) != len(set(row_ids)):
            raise ValueError("IDs de eventos/convocatórias duplicados na instalação.")
        for row in rows:
            if row.match_id not in selected_ids:
                raise ValueError("Detalhes de um jogo não selecionado.")
            groups[row.match_id].append(row)
    payloads = []
    for match in matches:
        for value in (match.id, match.team_id, match.opponent_id, match.season_id):
            _positive_id(value)
        if type(match.is_home) is not bool:
            raise ValueError("is_home deve ser booleano.")
        if (match.team_id, match.season_id, match.status) != (
            selection.team_id,
            selection.season_id,
            MatchStatus.FINISHED,
        ):
            raise ValueError("Jogo fora da equipa/época/estado selecionados.")
        if _utc(match.kickoff_at) > min(_utc(selection.as_of), exported_at):
            raise ValueError("Kickoff posterior ao limite temporal.")
        fixture = linked.get(match.id)
        if selection.competition_scope == "single" and (
            fixture is None or fixture.competition_id != selection.competition_id
        ):
            raise ValueError("Jogo fora da competição selecionada.")
        payloads.append(
            _match_content(
                match,
                grouped_events[match.id],
                grouped_squads[match.id],
                players,
                fixture,
                competitions,
                settings,
            )
        )
    content = {
        "schema_version": "1.0",
        "source_system": "match_tracker",
        "source_instance_id": settings.source_instance_id,
        "exported_at": _instant(exported_at),
        "selection": {
            "team_id": str(selection.team_id),
            "season_id": str(selection.season_id),
            "competition_scope": selection.competition_scope,
            "competition_id": str(selection.competition_id)
            if selection.competition_id
            else None,
            "as_of": _instant(selection.as_of),
            "limit": 5,
            "returned_count": len(payloads),
            "order": "kickoff_at_desc_source_match_id_numeric_desc",
        },
        "matches": payloads,
    }
    version_input = {
        key: value for key, value in content.items() if key != "exported_at"
    }
    return ExportDraft(content=content, selection_version=_digest(version_input))


def compute_snapshot_version(
    draft: ExportDraft, declared_scope: Mapping[str, str]
) -> str:
    """Calcula o hash com scope declarado, sem o autenticar nem emitir um pacote.

    Útil para testar o contrato com scopes explicitamente fictícios. Em produção
    o scope terá de provir de uma futura política de autorização por recurso.
    """
    content = {
        key: value for key, value in draft.content.items() if key != "exported_at"
    }
    if _digest(content) != draft.selection_version:
        raise ValueError("Rascunho alterado depois do cálculo da seleção.")
    for match in draft.content["matches"]:
        payload = {key: value for key, value in match.items() if key != "data_version"}
        expected = _digest(
            {
                "hash_version": 1,
                "source_system": "match_tracker",
                "source_instance_id": draft.content["source_instance_id"],
                "match": payload,
            }
        )
        if match["data_version"] != expected:
            raise ValueError("Versão do jogo não corresponde ao conteúdo do rascunho.")
    scope = dict(declared_scope)
    if set(scope) != {"scope_id", "club_id", "team_id", "permission"}:
        raise ValueError("Scope declarado incompleto ou com campos inesperados.")
    if (
        scope["team_id"] != draft.content["selection"]["team_id"]
        or scope["permission"] != "matches:export"
    ):
        raise ValueError("Scope declarado incompatível com a seleção.")
    for value in scope.values():
        _text(value)
    return _digest(
        {
            "hash_version": 1,
            "source_system": draft.content["source_system"],
            "source_instance_id": draft.content["source_instance_id"],
            "authorized_scope": scope,
            "selection": draft.content["selection"],
            "matches": [
                {"id": row["source_match_id"], "version": row["data_version"]}
                for row in draft.content["matches"]
            ],
        }
    )


def read_export_draft(
    engine: Engine,
    selection: ExportSelection,
    settings: ExportSettings,
    *,
    exported_at: datetime,
) -> ExportDraft:
    """Lê PostgreSQL num snapshot REPEATABLE READ e READ ONLY, sem autoflush.

    Recebe uma Engine explicitamente fornecida, sem abrir ligações no import.
    Usa ligação/transação próprias, sem reutilizar sessões com alterações locais.
    Só deve ser chamado por código interno confiável; não autoriza o team_id.
    """
    _utc(exported_at)
    if engine.dialect.name != "postgresql":
        raise ValueError(
            "A leitura consistente exige PostgreSQL; não há fallback SQLite."
        )
    with engine.connect() as connection:
        connection = connection.execution_options(isolation_level="REPEATABLE READ")
        with connection.begin():
            connection.exec_driver_sql("SET TRANSACTION READ ONLY")
            with Session(
                bind=connection,
                autoflush=False,
                expire_on_commit=False,
                join_transaction_mode="rollback_only",
            ) as db:
                matches = list(db.scalars(recent_matches_query(selection)))
                ids = [match.id for match in matches]
                events = (
                    list(
                        db.scalars(
                            select(MatchEvent).where(MatchEvent.match_id.in_(ids))
                        )
                    )
                    if ids
                    else []
                )
                squads = (
                    list(
                        db.scalars(
                            select(MatchSquad).where(MatchSquad.match_id.in_(ids))
                        )
                    )
                    if ids
                    else []
                )
                fixtures = (
                    list(
                        db.scalars(
                            select(CompetitionFixture).where(
                                CompetitionFixture.internal_match_id.in_(ids)
                            )
                        )
                    )
                    if ids
                    else []
                )
                player_ids = {
                    value
                    for row in events
                    for value in (row.player_id, row.related_player_id)
                    if value is not None
                }
                player_ids.update(row.player_id for row in squads)
                players = (
                    {
                        row.id: row
                        for row in db.scalars(
                            select(Player).where(Player.id.in_(player_ids))
                        )
                    }
                    if player_ids
                    else {}
                )
                competition_ids = {row.competition_id for row in fixtures}
                competitions = (
                    {
                        row.id: row
                        for row in db.scalars(
                            select(Competition).where(
                                Competition.id.in_(competition_ids)
                            )
                        )
                    }
                    if competition_ids
                    else {}
                )
                return build_export_draft(
                    selection,
                    settings,
                    matches=matches,
                    events=events,
                    squads=squads,
                    players=players,
                    fixtures=fixtures,
                    competitions=competitions,
                    exported_at=exported_at,
                )
