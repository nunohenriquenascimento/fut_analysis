"""Explicit operator source associations; round numbers always come from competition HTML."""
from pathlib import Path

from app.fpf_parser import bind_fixture, parse_competition, parse_fixture

FIXTURES = Path(__file__).parent / 'fixtures/fpf'
SOURCES = {
    677921: 'fixture_677921.html',
    677922: 'fixture_677922.html',
    677924: 'fixtureId=677924.html',
    677925: 'fixture_677925.html',
    677926: 'fixture_677926.html',
    677927: 'fixture_677927.html',
    677928: 'fixture_677928.html',
    677929: 'fixture_677929.html',
    677930: 'fixture_677930.html',
    677931: 'fixture_677931.html',
    677932: 'fixture_677932.html',
    677933: 'fixture_677933.html',
    677934: 'fixture_677934.html',
}


def calendar_data():
    competition = parse_competition((FIXTURES/'competition_30369_season_106.html').read_text(encoding='utf-8-sig'))
    series = next(s for s in competition['series'] if s['series_id'] == 99718)
    games = [dict(g) for g in series['matches']]
    documents = []
    for fixture_id, filename in SOURCES.items():
        url = f'https://resultados.fpf.pt/Competition/GetClassificationAndMatchesByFixture?fixtureId={fixture_id}'
        html = (FIXTURES/filename).read_text(encoding='utf-8-sig')
        parsed = parse_fixture(html, source_url=url)
        context = bind_fixture(competition, parsed, 99718)
        games.extend(dict(game, matchday=context['matchday']) for game in parsed['matches'])
        documents.append(dict(html=html, source_url=url, competition_id=competition['competition_id'],
                              season_id=competition['season_id'], series_id=context['series_id']))
    return competition, games, documents
