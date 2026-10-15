BEGIN;

-- Running upgrade 0006 -> 0007

CREATE TABLE competitions (
    id SERIAL NOT NULL, 
    season_id INTEGER NOT NULL, 
    internal_team_id INTEGER NOT NULL, 
    name VARCHAR(120) NOT NULL, 
    rules JSON NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    CONSTRAINT pk_competitions PRIMARY KEY (id), 
    CONSTRAINT uq_competitions_season_id UNIQUE (season_id, name), 
    CONSTRAINT fk_competitions_season_id_seasons FOREIGN KEY(season_id) REFERENCES seasons (id), 
    CONSTRAINT fk_competitions_internal_team_id_teams FOREIGN KEY(internal_team_id) REFERENCES teams (id)
);

CREATE TABLE competition_teams (
    competition_id INTEGER NOT NULL, 
    team_id INTEGER NOT NULL, 
    CONSTRAINT pk_competition_teams PRIMARY KEY (competition_id, team_id), 
    CONSTRAINT fk_competition_teams_competition_id_competitions FOREIGN KEY(competition_id) REFERENCES competitions (id), 
    CONSTRAINT fk_competition_teams_team_id_teams FOREIGN KEY(team_id) REFERENCES teams (id)
);

CREATE TABLE competition_fixtures (
    id SERIAL NOT NULL, 
    competition_id INTEGER NOT NULL, 
    external_key VARCHAR(120) NOT NULL, 
    matchday INTEGER NOT NULL, 
    home_team_id INTEGER NOT NULL, 
    away_team_id INTEGER NOT NULL, 
    kickoff_at TIMESTAMP WITH TIME ZONE, 
    venue VARCHAR(160), 
    internal_match_id INTEGER, 
    home_goals INTEGER, 
    away_goals INTEGER, 
    source VARCHAR(500) NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    CONSTRAINT pk_competition_fixtures PRIMARY KEY (id), 
    CONSTRAINT uq_fixture_external_key UNIQUE (competition_id, external_key), 
    CONSTRAINT uq_fixture_pair_matchday UNIQUE (competition_id, matchday, home_team_id, away_team_id), 
    CONSTRAINT uq_competition_fixtures_internal_match_id UNIQUE (internal_match_id), 
    CONSTRAINT ck_competition_fixtures_fixture_different_teams CHECK (home_team_id <> away_team_id), 
    CONSTRAINT ck_competition_fixtures_fixture_positive_matchday CHECK (matchday > 0), 
    CONSTRAINT ck_competition_fixtures_fixture_valid_score CHECK ((home_goals IS NULL AND away_goals IS NULL) OR (home_goals >= 0 AND away_goals >= 0 AND home_goals IS NOT NULL AND away_goals IS NOT NULL)), 
    CONSTRAINT ck_competition_fixtures_fixture_internal_no_score CHECK (internal_match_id IS NULL OR (home_goals IS NULL AND away_goals IS NULL)), 
    CONSTRAINT fk_competition_fixtures_competition_id_competitions FOREIGN KEY(competition_id) REFERENCES competitions (id), 
    CONSTRAINT fk_competition_fixtures_home_team_id_teams FOREIGN KEY(home_team_id) REFERENCES teams (id), 
    CONSTRAINT fk_competition_fixtures_away_team_id_teams FOREIGN KEY(away_team_id) REFERENCES teams (id), 
    CONSTRAINT fk_competition_fixtures_internal_match_id_matches FOREIGN KEY(internal_match_id) REFERENCES matches (id)
);

UPDATE alembic_version SET version_num='0007' WHERE alembic_version.version_num = '0006';

COMMIT;

