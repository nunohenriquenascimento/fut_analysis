"""Match statistics backed by the existing service, with no HTTP/model access."""
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.ai.schemas import (
    AuthorizedMatchContext, DataLimitation, EvidenceSource, MatchEvidenceScope,
    MatchStatisticsEvidence, MatchStatisticsInput,
)
from app.enums import MatchStatus
from app.models import Match
from app.statistics_service import match_statistics


def get_match_statistics(
    match_id: int, *, context: AuthorizedMatchContext, engine: Engine,
) -> MatchStatisticsEvidence:
    """Read one authorized game in an owned, read-only PostgreSQL snapshot.

    Only ``match_id`` belongs in a future tool's argument schema. ``context``
    and ``engine`` must be injected by trusted server code; a context dictionary
    is deliberately not accepted. There is no role override or implicit scope.

    The caller's sessions are never reused or flushed. The session closes with
    rollback (also on failure), without committing. REPEATABLE READ keeps the
    authorization check and all statistics queries on the same snapshot.
    """
    arguments = MatchStatisticsInput(match_id=match_id)
    if not isinstance(context, AuthorizedMatchContext):
        raise TypeError("context must be a server-created AuthorizedMatchContext")
    if engine.dialect.name != "postgresql":
        raise ValueError("Match evidence requires a read-only PostgreSQL transaction")

    with engine.connect().execution_options(isolation_level="REPEATABLE READ") as connection:
        with Session(bind=connection, autoflush=False) as db:
            db.execute(text("SET TRANSACTION READ ONLY"))
            authorized_id = db.scalar(select(Match.id).where(
                Match.id == arguments.match_id,
                Match.team_id == context.team_id,
                Match.season_id == context.season_id,
            ))
            if authorized_id is None:
                # Do not reveal whether an out-of-scope game exists.
                raise HTTPException(404, "Jogo não encontrado.")

            statistics = match_statistics(db, authorized_id)
            limitations = [
                DataLimitation(code="UNVERIFIED_COVERAGE", description=(
                    "Os valores refletem apenas os eventos registados; a completude da recolha "
                    "não é verificada, mesmo num jogo terminado. Zero registos não comprova ausência de ações."
                )),
                DataLimitation(code="RECORDED_SHOTS_ONLY", description=(
                    "Remates totais = à baliza + fora + bloqueados. Os golos não acrescentam remates."
                )),
                DataLimitation(code="NO_PLAYER_MINUTES", description=(
                    "Não são calculados minutos jogados nem métricas por 90 minutos."
                )),
            ]
            if statistics.total_events == 0:
                limitations.append(DataLimitation(code="NO_EVENTS", description=(
                    "Não existem eventos registados neste jogo; o resultado derivado 0–0 "
                    "não confirma um resultado observado."
                )))
            if not statistics.is_final:
                limitations.append(DataLimitation(code="NON_FINAL_MATCH", description=(
                    "O jogo não está terminado; os valores não representam estatísticas finais."
                )))
            if statistics.match.status == MatchStatus.CANCELLED:
                limitations.append(DataLimitation(code="CANCELLED_MATCH", description=(
                    "O jogo está cancelado; os eventos preservados não representam um resultado competitivo final."
                )))

            return MatchStatisticsEvidence(
                scope=MatchEvidenceScope(
                    match_id=authorized_id, team_id=context.team_id, season_id=context.season_id,
                ),
                statistics=statistics,
                queried_at=datetime.now(timezone.utc),
                sources=[
                    EvidenceSource(entity="matches", record_ids=[authorized_id]),
                    EvidenceSource(entity="match_events", record_ids=[row.id for row in statistics.timeline]),
                    EvidenceSource(entity="players", record_ids=[row.id for row in statistics.players]),
                    EvidenceSource(entity="teams", record_ids=[statistics.match.team_id, statistics.match.opponent_id]),
                ],
                limitations=limitations,
            )
