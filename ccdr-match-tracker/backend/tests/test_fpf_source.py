"""Transport/discovery tests. Synthetic HTML is explicitly not an FPF capture."""
from email.message import Message
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest

from app.fpf_source import (
    FPFClient, FPFHTMLInvalid, FPFSourceUnavailable, MAX_HTML_BYTES, ORIGIN, discover_fixture_ids,
)


class Response(BytesIO):
    def __init__(self, raw, url, *, status=200, content_type="text/html; charset=utf-8"):
        super().__init__(raw)
        self.status = status
        self.url = url
        self.headers = Message()
        self.headers["Content-Type"] = content_type

    def geturl(self):
        return self.url


class Opener:
    def __init__(self, response=None, error=None):
        self.response, self.error, self.calls = response, error, []

    def open(self, request, *, timeout):
        self.calls.append((request.full_url, request.get_method(), timeout))
        if self.error:
            raise self.error
        return self.response


def test_fetches_html_and_records_source_without_assuming_json():
    url = ORIGIN + "/Competition/GetClassificationAndMatchesByFixture?fixtureId=677921"
    opener = Opener(Response("<p>Classificação</p>".encode(), url))
    document = FPFClient(opener=opener).fixture(677921)
    assert document.html == "<p>Classificação</p>"
    assert document.url == url and len(document.sha256) == 64
    assert document.fetched_at.tzinfo is not None
    assert opener.calls == [(url, "GET", 10)]


def test_competition_uses_confirmed_route():
    url = ORIGIN + "/Competition/Details?competitionId=30369&seasonId=106"
    opener = Opener(Response(b"<html></html>", url))
    assert FPFClient(opener=opener).competition(30369, 106).url == url


@pytest.mark.parametrize("error,reason", [
    (HTTPError(ORIGIN, 403, "private error text", Message(), BytesIO()), "access_denied"),
    (HTTPError(ORIGIN, 500, "private error text", Message(), BytesIO()), "http_error"),
    (URLError("private error text"), "connection_failed"),
    (TimeoutError("private error text"), "connection_failed"),
])
def test_unavailable_source_is_sanitized_and_not_retried(error, reason):
    opener = Opener(error=error)
    with pytest.raises(FPFSourceUnavailable) as caught:
        FPFClient(opener=opener).fixture(677921)
    assert caught.value.reason == reason
    assert "private error text" not in str(caught.value)
    assert len(opener.calls) == 1


@pytest.mark.parametrize("raw,content_type,reason", [
    (b"{}", "application/json", "unexpected_content_type"),
    (b"", "text/html", "invalid_size"),
    (b"x" * (MAX_HTML_BYTES + 1), "text/html", "invalid_size"),
    (b"\xff", "text/html; charset=utf-8", "invalid_encoding"),
    (b"IP address has been banned", "text/html", "access_denied"),
], ids=["json", "empty", "oversize", "invalid-utf8", "blocked-page"])
def test_rejects_unusable_response(raw, content_type, reason):
    url = ORIGIN + "/Competition/GetClassificationAndMatchesByFixture?fixtureId=677921"
    with pytest.raises(FPFSourceUnavailable) as caught:
        FPFClient(opener=Opener(Response(raw, url, content_type=content_type))).fixture(677921)
    assert caught.value.reason == reason


@pytest.mark.parametrize("identifier", [True, 0, -1, "677921", 2_147_483_648])
def test_rejects_invalid_identifiers_without_http(identifier):
    opener = Opener()
    with pytest.raises(ValueError):
        FPFClient(opener=opener).fixture(identifier)
    assert not opener.calls


def test_discovers_links_dynamically_and_deduplicates_synthetic_html():
    html = '''<a data-ajax="true" href="/Competition/GetClassificationAndMatchesByFixture?fixtureId=9&amp;x=1"><span>Jornada</span></a>
      <A HREF="https://resultados.fpf.pt/Competition/GetClassificationAndMatchesByFixture?fixtureId=42">2</A>
      <a href="/Competition/GetClassificationAndMatchesByFixture?fixtureId=9">1</a>
      <a href="https://other.example/Competition/GetClassificationAndMatchesByFixture?fixtureId=99">Ignore</a>'''
    assert discover_fixture_ids(html) == (9, 42)


def test_discovers_relative_ajax_url_without_assuming_id_ranges():
    assert discover_fixture_ids('<a data-ajax-url="GetClassificationAndMatchesByFixture?fixtureId=987654">Jornada</a>') == (987654,)


@pytest.mark.parametrize("html", [
    "<html>Unavailable</html>",
    '<a href="/Competition/GetClassificationAndMatchesByFixture?fixtureId=0">Invalid</a>',
    '<a href="/Competition/GetClassificationAndMatchesByFixture?fixtureId=9&amp;fixtureId=42">Ambiguous</a>',
    '<a href="/Competition/GetClassificationAndMatchesByFixture?fixtureId=9" data-ajax-url="/Competition/GetClassificationAndMatchesByFixture?fixtureId=42">Conflict</a>',
])
def test_refuses_missing_invalid_or_contradictory_fixture_links(html):
    with pytest.raises(FPFHTMLInvalid):
        discover_fixture_ids(html)


def test_discovery_with_operator_supplied_real_competition_html():
    capture = Path(__file__).parent / "fixtures/fpf/competition_30369_season_106.html"
    ids = discover_fixture_ids(capture.read_text(encoding="utf-8-sig"))
    assert len(ids) == 14  # This specific competition has 14 rounds, per operator.
    assert 677921 in ids
