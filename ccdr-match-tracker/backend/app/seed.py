"""Explicit, repeatable setup of the first season and club (no demo players)."""
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_engine
from app.models import Season, Team
from app.roster import CLUB_NAME, SEASON_NAME


def main() -> None:
    with Session(get_engine()) as db:
        season = db.scalar(select(Season).where(Season.name == SEASON_NAME))
        if season is None:
            season = Season(name=SEASON_NAME, starts_on=date(2026, 7, 1), ends_on=date(2027, 6, 30))
            db.add(season)
        team = db.scalar(select(Team).where(Team.name == CLUB_NAME))
        if team is None:
            team = Team(name=CLUB_NAME)
            db.add(team)
        db.commit()
        print(f"season_id={season.id}; team_id={team.id}")


if __name__ == "__main__":
    main()
