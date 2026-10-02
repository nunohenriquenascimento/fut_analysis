from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.statistics_schemas import MatchStatistics, PlayerStatisticsResponse, SeasonStatistics
from app.statistics_service import match_statistics, season_statistics

router = APIRouter(tags=["statistics"])
Database = Annotated[Session, Depends(get_db)]


@router.get("/matches/{match_id}/stats", response_model=MatchStatistics)
def match_stats(match_id: int, db: Database):
    return match_statistics(db, match_id)


@router.get("/statistics/season", response_model=SeasonStatistics)
def season_stats(db: Database):
    return season_statistics(db)


@router.get("/statistics/players", response_model=PlayerStatisticsResponse)
def player_stats(db: Database):
    result = season_statistics(db)
    return PlayerStatisticsResponse(context=result.context, scope=result.scope, players=result.players, rankings=result.rankings)
