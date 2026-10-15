"""Read public FPF HTML without retries, authentication or database writes.

Only the two competition routes confirmed in the source are used. Table and
match parsing must be based on captured HTML, never on an assumed JSON API.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import re
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


ORIGIN = "https://resultados.fpf.pt"
FIXTURE_PATH = "/Competition/GetClassificationAndMatchesByFixture"
MAX_HTML_BYTES = 2_000_000


class FPFSourceUnavailable(Exception):
    """Sanitized source error; callers must retain the last successful snapshot."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__("Fonte FPF indisponível: " + reason)


class FPFHTMLInvalid(ValueError):
    pass


@dataclass(frozen=True)
class FPFHTML:
    url: str
    html: str
    sha256: str
    fetched_at: datetime


def _positive_id(value: int) -> int:
    if type(value) is not int or not 1 <= value <= 2_147_483_647:
        raise ValueError("Identificador FPF inválido.")
    return value


class _NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # A login, security challenge or changed destination is not competition HTML.
        return None


class FPFClient:
    def __init__(self, *, timeout: float = 10, opener=None):
        if not 0 < timeout <= 30:
            raise ValueError("Timeout FPF inválido.")
        self.timeout = timeout
        self.opener = opener if opener is not None else build_opener(ProxyHandler({}), _NoRedirects())

    def competition(self, competition_id: int, season_id: int) -> FPFHTML:
        return self._get("/Competition/Details", {
            "competitionId": _positive_id(competition_id), "seasonId": _positive_id(season_id),
        })

    def fixture(self, fixture_id: int) -> FPFHTML:
        return self._get(FIXTURE_PATH, {"fixtureId": _positive_id(fixture_id)})

    def match(self, match_id: int) -> FPFHTML:
        return self._get("/Match/GetMatchInformation", {"matchId": _positive_id(match_id)})

    def _get(self, path: str, params: dict[str, int]) -> FPFHTML:
        url = ORIGIN + path + "?" + urlencode(params)
        request = Request(url, headers={"Accept": "text/html", "Accept-Encoding": "identity"}, method="GET")
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                if response.status != 200:
                    raise FPFSourceUnavailable("access_denied" if response.status == 403 else "http_error")
                if response.geturl() != url:
                    raise FPFSourceUnavailable("unexpected_destination")
                if response.headers.get_content_type() != "text/html":
                    raise FPFSourceUnavailable("unexpected_content_type")
                if response.headers.get("Content-Encoding", "identity").lower() != "identity":
                    raise FPFSourceUnavailable("unexpected_encoding")
                raw = response.read(MAX_HTML_BYTES + 1)
                if not raw or len(raw) > MAX_HTML_BYTES:
                    raise FPFSourceUnavailable("invalid_size")
                try:
                    html = raw.decode(response.headers.get_content_charset() or "utf-8", errors="strict")
                except (LookupError, UnicodeError):
                    raise FPFSourceUnavailable("invalid_encoding") from None
                if "ip address has been banned" in html.casefold():
                    raise FPFSourceUnavailable("access_denied")
                return FPFHTML(url, html, hashlib.sha256(raw).hexdigest(), datetime.now(timezone.utc))
        except HTTPError as error:
            error.close()
            raise FPFSourceUnavailable("access_denied" if error.code == 403 else "http_error") from None
        except (URLError, TimeoutError, OSError):
            raise FPFSourceUnavailable("connection_failed") from None


class _FixtureLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids: list[int] = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        candidates = []
        for key, value in attrs:
            if key not in {"href", "data-ajax-url"} or not value:
                continue
            try:
                url = urlsplit(urljoin(ORIGIN + "/Competition/Details", value))
                if (url.scheme != "https" or url.hostname != "resultados.fpf.pt"
                        or url.port not in {None, 443} or url.username is not None
                        or url.password is not None or url.path != FIXTURE_PATH):
                    continue
                values = parse_qs(url.query, keep_blank_values=True).get("fixtureId", [])
                if len(values) != 1 or not re.fullmatch(r"[1-9][0-9]{0,9}", values[0]):
                    raise FPFHTMLInvalid("Link de jornada FPF inválido.")
                candidates.append(_positive_id(int(values[0])))
            except FPFHTMLInvalid:
                raise
            except ValueError:
                raise FPFHTMLInvalid("Link de jornada FPF inválido.") from None
        if len(set(candidates)) > 1:
            raise FPFHTMLInvalid("Link de jornada FPF contraditório.")
        for fixture_id in candidates:
            if fixture_id not in self.ids:
                self.ids.append(fixture_id)


def discover_fixture_ids(html: str) -> tuple[int, ...]:
    """Discover links in source order, including dynamically assigned future IDs."""
    if len(html.encode("utf-8")) > MAX_HTML_BYTES:
        raise FPFHTMLInvalid("HTML FPF demasiado grande.")
    parser = _FixtureLinks()
    parser.feed(html)
    parser.close()
    if not parser.ids:
        raise FPFHTMLInvalid("HTML sem links de jornadas FPF; não sincronizar.")
    return tuple(parser.ids)
