from pathlib import Path

import pytest

from app.fpf_parser import FPFHTMLInvalid, Tree, parse_competition, parse_match, parse_fixture

FIXTURES = Path(__file__).parent / "fixtures/fpf"


@pytest.fixture
def competition_html():
    return (FIXTURES / "competition_30369_season_106.html").read_text(encoding="utf-8-sig")


@pytest.fixture
def match_html():
    return (FIXTURES / "match_2682548.html").read_text(encoding="utf-8-sig")


def test_real_competition_identity_standings_and_all_rounds(competition_html):
    data = parse_competition(competition_html)
    assert (data["competition_id"], data["season_id"], data["season"]) == (30369, 106, "2026-2027")
    assert data["name"] == "LIGA FUTEBOL SUB-19 DAPPIN"
    series, = data["series"]
    assert series["series_id"] == 99718
    assert len(series["standings"]) == 8
    assert series["standings"][0] == dict(name="Adrc Aguiar Beira", rank=1, played=2,
        wins=2, draws=0, losses=0, goals_for=9, goals_against=1, points=6, goal_difference=8)
    assert series["standings"][-1]["name"] == "V. Cortez Mondego-Guarda"
    assert len(series["rounds"]) == 14
    assert [r["matchday"] for r in series["rounds"]] == list(range(1, 15))
    assert series["rounds"][0]["fixture_id"] == 677921
    assert series["rounds"][-1]["fixture_id"] == 677934
    assert [r["fixture_id"] for r in series["rounds"] if r["current"]] == [677923]


def test_real_calendar_has_only_visible_round_and_no_invented_dates_or_scores(competition_html):
    data = parse_competition(competition_html)
    games = data["series"][0]["matches"]
    assert data["coverage"] == "visible_round_only" and len(games) == 4
    ours = next(g for g in games if g["home_name"] == "V. Cortez Mondego-Guarda")
    assert (ours["away_name"], ours["matchday"], ours["venue"], ours["schedule_text"]) == (
        "Guarda Fc", 3, "Campo 3 Maio", "17 out 16:00")
    assert all(g["home_goals"] is None and g["away_goals"] is None and g["match_id"] is None for g in games)


def test_real_match_identity_score_place_and_clubs(match_html):
    data = parse_match(match_html)
    assert (data["match_id"], data["competition_id"], data["season_id"]) == (2682548, 30369, 106)
    assert data["home"] == dict(club_id=2475, name="Seia Fc")
    assert data["away"] == dict(club_id=3264, name="V. Cortez Mondego-Guarda")
    assert (data["home_goals"], data["away_goals"]) == (2, 1)
    assert (data["date"], data["time"], data["venue"]) == ("2026-10-10", "16:00", "Estadio Municipal Seia")


def test_real_match_rosters_ids_and_optional_absence(match_html):
    data = parse_match(match_html)
    assert [len(data["lineups"][side][group]) for side in ("home", "away") for group in ("starters", "substitutes")] == [11, 5, 11, 7]
    assert data["lineups"]["home"]["starters"][0]["player_id"] == 4764314
    assert data["lineups"]["home"]["starters"][0]["shirt_number"] == 1
    # A goal-count icon must not become part of a player's name.
    assert data["lineups"]["home"]["substitutes"][2]["name"] == "Martim Oliveira"
    missing_id = parse_match(match_html.replace('/Player/Logo/4764314', '/Images/unknown.png'))
    assert missing_id["lineups"]["home"]["starters"][0]["player_id"] is None


def test_real_goals_cards_and_substitutions_are_official_only(match_html):
    data = parse_match(match_html)
    goals = [e for e in data["events"] if e["type"] == "goal"]
    assert [e["minute"] for e in goals] == [13, 46, 69]
    assert [e["player"]["side"] for e in goals] == ["away", "home", "home"]
    assert goals[-1]["player"]["player_id"] == 4777877
    assert len([e for e in data["events"] if e["type"] == "yellow_card"]) == 3
    assert len([e for e in data["events"] if e["type"] == "red_card"]) == 1
    changes = [e for e in data["events"] if e["type"] == "substitution"]
    assert len(changes) == 8
    assert changes[0]["player_in"]["name"] == "Martim Reis"
    assert changes[0]["player_out"]["name"] == "João Lourenço"
    assert changes[-1]["minute"] == 90 and changes[-1]["added_minute"] == 1
    assert not any("recorded_by_id" in e or "elapsed_seconds" in e for e in data["events"])


def test_staff_and_referees_do_not_guess_ambiguous_team_markup(match_html):
    data = parse_match(match_html)
    assert len(data["staff"]) == 5 and len(data["officials"]) == 3
    assert data["staff"][0]["role"] == "Treinador Principal"
    assert all(p["side"] is None for p in data["staff"])
    assert len(data["warnings"]) == 2
    assert data["officials"][0] == dict(role="Arbitro", name="Rodrigo Goncalves")


@pytest.mark.parametrize("parser", [parse_competition, parse_match])
@pytest.mark.parametrize("html", ["", "<html>Unavailable</html>", "<html><script>fake</script></html>"])
def test_invalid_or_unavailable_html_is_not_empty_success(parser, html):
    with pytest.raises(FPFHTMLInvalid):
        parser(html)


def test_rejects_identity_and_column_drift(competition_html):
    for modified in (competition_html.replace('value="30369"', 'value="1"'),
                     competition_html.replace('>PTS</div>', '>UNKNOWN</div>')):
        with pytest.raises(FPFHTMLInvalid):
            parse_competition(modified)


def test_absent_optional_date_remains_unknown(match_html):
    root = Tree(match_html).root
    node, = root.all(cls="info-time-place")
    # Change the observed selector only; absence is distinct from malformed content.
    data = parse_match(match_html.replace('info-time-place', 'missing-time-place'))
    assert data["date"] is None and data["time"] is None and data["venue"] is None


def test_match_identity_mismatch_is_rejected(match_html):
    with pytest.raises(FPFHTMLInvalid):
        parse_match(match_html.replace('name="Request.MatchId" type="hidden" value="2682548"',
                                     'name="Request.MatchId" type="hidden" value="1"'))


def test_absent_lineup_is_distinguished_from_an_empty_reported_roster(match_html):
    parsed = parse_match(match_html.replace('Equipas Iniciais', 'Unavailable lineup'))
    assert parsed["availability"]["starters"] is False
    assert parsed["lineups"]["home"]["starters"] == []


def test_round_result_wrapped_in_match_link_requires_fpf_identity():
    html = '''<meta property="og:url" content="https://resultados.fpf.pt/Competition/GetClassificationAndMatchesByFixture?fixtureId=677922">
    <div id="matches"><a class="game-link" href="/Match/GetMatchInformation?matchId=2682548">
    <div class="game"><div class="home-team">Seia Fc</div><div class="text-center">2 - 1</div>
    <div class="away-team">V. Cortez Mondego-Guarda</div></div></a></div>'''
    game, = parse_fixture(html)["matches"]
    assert (game["match_id"], game["home_goals"], game["away_goals"]) == (2682548, 2, 1)
    with pytest.raises(FPFHTMLInvalid):
        parse_fixture(html.replace("/Match/GetMatchInformation?matchId=2682548", "/unknown"))
    with pytest.raises(FPFHTMLInvalid):
        parse_fixture(html.replace('2 - 1', 'Adiado'))
