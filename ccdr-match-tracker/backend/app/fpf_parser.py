"""Parse the supplied FPF HTML captures; no scripts, HTTP or internal events."""
from dataclasses import dataclass, field
from datetime import datetime
from html.parser import HTMLParser
import re
import unicodedata
from urllib.parse import parse_qs, urlsplit

from app.fpf_source import FPFHTMLInvalid, MAX_HTML_BYTES, ORIGIN, discover_fixture_ids


@dataclass
class Node:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)
    parent: object = field(default=None, repr=False)

    def has(self, cls):
        return cls in self.attrs.get("class", "").split()

    def all(self, *, tag=None, cls=None, id=None):
        result = []
        for child in self.children:
            if isinstance(child, Node):
                if ((tag is None or child.tag == tag) and (cls is None or child.has(cls))
                        and (id is None or child.attrs.get("id") == id)):
                    result.append(child)
                result.extend(child.all(tag=tag, cls=cls, id=id))
        return result

    def text(self):
        return " ".join(" ".join(c.text() if isinstance(c, Node) else c for c in self.children).split())


class Tree(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        if not html or len(html.encode("utf-8")) > MAX_HTML_BYTES:
            raise FPFHTMLInvalid("HTML vazio ou demasiado grande.")
        self.root = Node("root")
        self.stack = [self.root]
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        if len(self.stack) > 128:
            raise FPFHTMLInvalid("HTML demasiado profundo.")
        node = Node(tag, dict(attrs), parent=self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, text):
        if self.stack[-1].tag not in {"script", "style"}:
            self.stack[-1].children.append(text)


def one(nodes, label):
    if len(nodes) != 1:
        raise FPFHTMLInvalid(f"Elemento FPF ausente ou ambíguo: {label}.")
    return nodes[0]


def number(text):
    if not re.fullmatch(r"[0-9]{1,10}", text) or int(text) > 2_147_483_647:
        raise FPFHTMLInvalid("Número FPF inválido.")
    return int(text)


def identity_url(url, path, fields):
    split = urlsplit(url)
    if split.scheme and (split.scheme != "https" or split.netloc != "resultados.fpf.pt"):
        raise FPFHTMLInvalid("Origem FPF inválida.")
    if split.path != path:
        raise FPFHTMLInvalid("Rota FPF inválida.")
    query = parse_qs(split.query)
    result = {}
    for field in fields:
        values = query.get(field, [])
        if len(values) != 1 or not values[0].isascii() or not values[0].isdigit() or int(values[0]) <= 0:
            raise FPFHTMLInvalid("Identidade FPF inválida.")
        result[field] = int(values[0])
    return result


def canonical(root, path, fields):
    meta = one([n for n in root.all(tag="meta") if n.attrs.get("property") == "og:url"], "og:url")
    return identity_url(meta.attrs.get("content", ""), path, fields)


def fixture_source(url):
    try:
        split = urlsplit(url)
    except ValueError:
        raise FPFHTMLInvalid("URL de origem da jornada inválido.") from None
    query = parse_qs(split.query, keep_blank_values=True)
    if (split.scheme != "https" or split.netloc != "resultados.fpf.pt" or split.fragment
            or set(query) != {"fixtureId"} or len(query["fixtureId"]) != 1):
        raise FPFHTMLInvalid("URL de origem da jornada inválido.")
    return identity_url(url, "/Competition/GetClassificationAndMatchesByFixture", ["fixtureId"])["fixtureId"]


def bind_fixture(document, fixture, series_id=None):
    candidates = [(series, r) for series in document["series"] for r in series["rounds"]
                  if r["fixture_id"] == fixture["fixture_id"] and (series_id is None or series["series_id"] == series_id)]
    series, round_info = one(candidates, "associação entre origem, competição, época, série e jornada")
    expected = {r["name"] for r in series["standings"]}
    observed = [name for game in fixture["matches"] for name in (game["home_name"], game["away_name"])]
    if set(observed) != expected or len(observed) != len(expected):
        raise FPFHTMLInvalid("A jornada tem de conter exatamente um jogo por equipa da série confirmada.")
    return dict(competition_id=document["competition_id"], season_id=document["season_id"],
                series_id=series["series_id"], matchday=round_info["matchday"])


def parse_games(root, names, fixture_id, matchday):
    rows = [{"name": name} for name in names]
    matches = []
    for game in one(root.all(id="matches"), "jogos").all(cls="game"):
        home = one(game.all(cls="home-team"), "casa").text()
        away = one(game.all(cls="away-team"), "fora").text()
        if home not in {r["name"] for r in rows} or away not in {r["name"] for r in rows} or home == away:
            raise FPFHTMLInvalid("Participantes do jogo inválidos.")
        links = [game, *game.all(tag="a")]
        if game.parent.tag == "a" and len(game.parent.all(cls="game")) == 1:
            links.append(game.parent)
        ids = {identity_url(n.attrs["href"], "/Match/GetMatchInformation", ["matchId"])["matchId"]
               for n in links if "/Match/GetMatchInformation?" in n.attrs.get("href", "")}
        if len(ids) > 1:
            raise FPFHTMLInvalid("Identificadores contraditórios no jogo.")
        schedule = game.all(cls="game-schedule")
        scores = game.all(cls="score")
        score_nodes = [n for score in scores for n in score.children if isinstance(n, Node)
                       and not n.has("game-schedule") and re.fullmatch(r"[0-9]{1,3}\s*[-–]\s*[0-9]{1,3}", n.text())]
        if not scores:
            score_nodes = [n for n in game.all(cls="text-center")
                       if re.fullmatch(r"[0-9]{1,3}\s*[-–]\s*[0-9]{1,3}", n.text())]
        if len(schedule) > 1 or (schedule and score_nodes and not scores):
            raise FPFHTMLInvalid("Jogo com horário e resultado contraditórios.")
        if (scores and len(score_nodes) != 1) or len(score_nodes) > 1 or (score_nodes and not ids):
            raise FPFHTMLInvalid("Resultado sem ID FPF ou formato não suportado.")
        if not score_nodes and len(schedule) != 1:
            raise FPFHTMLInvalid("Resultado sem ID FPF ou formato não suportado.")
        goals = re.split(r"\s*[-–]\s*", score_nodes[0].text()) if score_nodes else None
        siblings = game.parent.children
        index = siblings.index(game)
        stadium = next((s.text() for s in siblings[index + 1:] if isinstance(s, Node)), None)
        next_node = next((s for s in siblings[index + 1:] if isinstance(s, Node)), None)
        stadium = stadium if next_node is not None and next_node.has("game-list-stadium") else None
        matches.append(dict(home_name=home, away_name=away, home_goals=int(goals[0]) if goals else None, away_goals=int(goals[1]) if goals else None,
                            schedule_text=(schedule[0].text() or None) if schedule else None, venue=stadium,
                            match_id=next(iter(ids), None), fixture_id=fixture_id, matchday=matchday))
    return matches


def parse_fixture(html, *, source_url=None):
    root = Tree(html).root
    meta = [n for n in root.all(tag="meta") if n.attrs.get("property") == "og:url"]
    if source_url is None:
        fixture_id = canonical(root, "/Competition/GetClassificationAndMatchesByFixture", ["fixtureId"])["fixtureId"]
    else:
        fixture_id = fixture_source(source_url)
        if meta and canonical(root, "/Competition/GetClassificationAndMatchesByFixture", ["fixtureId"])["fixtureId"] != fixture_id:
            raise FPFHTMLInvalid("URL declarado contradiz a identidade da jornada no HTML.")
        one(root.all(id="classification"), "classificação da jornada")
    games = one(root.all(id="matches"), "jogos")
    names = [n.text() for n in games.all(cls="home-team") + games.all(cls="away-team")]
    if not names or len(names) != len(set(names)):
        raise FPFHTMLInvalid("Jornada vazia ou participantes repetidos.")
    return dict(fixture_id=fixture_id, matches=parse_games(root, names, fixture_id, None))


def parse_competition(html):
    root = Tree(html).root
    ids = canonical(root, "/Competition/Details", ["competitionId", "seasonId"])
    hidden = one(root.all(id="Competition_Id"), "Competition_Id")
    if number(hidden.attrs.get("value", "")) != ids["competitionId"]:
        raise FPFHTMLInvalid("Identidades da competição contraditórias.")
    option = one([n for n in one(root.all(id="SeasonId"), "SeasonId").all(tag="option")
                  if "selected" in n.attrs], "época selecionada")
    if number(option.attrs.get("value", "")) != ids["seasonId"]:
        raise FPFHTMLInvalid("Épocas contraditórias.")
    scope = one(root.all(id="competitionId"), "competitionId")
    name = one(scope.all(tag="h2"), "nome da competição").text()
    series = []
    for section in scope.all(cls="game-results"):
        series_match = re.fullmatch(r"htmlSerieId_([0-9]+)", section.attrs.get("id", ""))
        if not series_match:
            raise FPFHTMLInvalid("Série sem identificador.")
        classification = one(section.all(id="classification"), "classificação")
        headings = [n.text() for n in one(classification.all(cls="game-header"), "cabeçalho").children if isinstance(n, Node)]
        if headings != ["POS", "", "JGS", "V", "E", "D", "GM", "GS", "PTS"]:
            raise FPFHTMLInvalid("Colunas de classificação desconhecidas.")
        rows = []
        for row in classification.all(cls="classification"):
            cells = [c.text() for c in row.children if isinstance(c, Node) and c.tag == "div"]
            if len(cells) != 9 or not cells[1]:
                raise FPFHTMLInvalid("Linha de classificação incompleta.")
            values = dict(zip(["rank", "played", "wins", "draws", "losses", "goals_for", "goals_against", "points"],
                              [number(cells[0]), *map(number, cells[2:])]))
            if values["played"] != values["wins"] + values["draws"] + values["losses"]:
                raise FPFHTMLInvalid("Estatísticas de classificação inconsistentes.")
            rows.append(dict(name=cells[1], **values, goal_difference=values["goals_for"] - values["goals_against"]))
        if not rows or len({r["name"] for r in rows}) != len(rows):
            raise FPFHTMLInvalid("Participantes ausentes ou repetidos.")
        rounds = []
        for link in one(section.all(cls="game-nav-slider"), "jornadas").all(tag="a"):
            query = identity_url(link.attrs.get("href", ""), "/Competition/GetClassificationAndMatchesByFixture", ["fixtureId"])
            rounds.append(dict(fixture_id=query["fixtureId"], matchday=number(link.text()), current=link.has("current")))
        if len({r["fixture_id"] for r in rounds}) != len(rounds) or len({r["matchday"] for r in rounds}) != len(rounds):
            raise FPFHTMLInvalid("Jornadas repetidas.")
        current = one([r for r in rounds if r["current"]], "jornada atual")
        matches = parse_games(section, {r["name"] for r in rows}, current["fixture_id"], current["matchday"])
        series.append(dict(series_id=int(series_match[1]), standings=rows, rounds=rounds, matches=matches))
    if not series or set(discover_fixture_ids(html)) != {r["fixture_id"] for s in series for r in s["rounds"]}:
        raise FPFHTMLInvalid("Séries/jornadas incompletas.")
    return dict(competition_id=ids["competitionId"], season_id=ids["seasonId"], name=name,
                season=option.text(), series=series, coverage="visible_round_only")


def _person_id(node):
    ids = [int(m[1]) for img in node.all(tag="img")
           if (m := re.fullmatch(r"/Player/Logo/([0-9]+)", img.attrs.get("src", "")))]
    return one(ids, "identificador de pessoa") if ids else None


def _key(name):
    return " ".join("".join(c for c in unicodedata.normalize("NFD", name) if not unicodedata.combining(c)).casefold().split())


def _minute(text):
    m = re.fullmatch(r"\s*(\d+)'\s*(?:\+\s*(\d+)'?)?\s*", text)
    if not m:
        raise FPFHTMLInvalid("Minuto inválido.")
    return dict(minute=int(m[1]), added_minute=int(m[2]) if m[2] else 0, minute_text=text)


def parse_match(html):
    root = Tree(html).root
    ids = canonical(root, "/Match/GetMatchInformation", ["matchId"])
    hidden = root.all(id="Request_MatchId")
    if hidden and number(one(hidden, "MatchId").attrs.get("value", "")) != ids["matchId"]:
        raise FPFHTMLInvalid("Identidades da ficha contraditórias.")
    comp = identity_url(one(root.all(id="competitionDetails"), "competição").attrs.get("href", ""),
                        "/Competition/Details", ["competitionId", "seasonId"])
    resume = one(root.all(cls="game-resume"), "resumo")
    clubs = []
    for image in resume.all(tag="img"):
        m = re.fullmatch(r"/Club/Logo/([0-9]+)", image.attrs.get("src", ""))
        if m:
            clubs.append(dict(club_id=int(m[1]), name=image.attrs.get("alt", "")))
    if len(clubs) != 2 or clubs[0]["club_id"] == clubs[1]["club_id"] or not all(c["name"] for c in clubs):
        raise FPFHTMLInvalid("Equipas da ficha incompletas.")
    scores = [re.fullmatch(r"(\d+)\s*-\s*(\d+)", n.text()) for n in resume.all(tag="strong")]
    score = one([m for m in scores if m], "resultado")
    time_nodes = root.all(cls="info-time-place")
    date, clock, venue = None, None, None
    if time_nodes:
        text = one(time_nodes, "data/hora/local").text()
        m = re.fullmatch(r"Data:\s*(\d{2}-\d{2}-\d{4})\s+Hora:\s*(\d{2}:\d{2})\s+Estádio:\s*(.*)", text)
        if not m:
            raise FPFHTMLInvalid("Data/hora/local em formato desconhecido.")
        try:
            date = datetime.strptime(m[1], "%d-%m-%Y").date().isoformat()
            clock = datetime.strptime(m[2], "%H:%M").strftime("%H:%M")
        except ValueError:
            raise FPFHTMLInvalid("Data/hora inválidas.") from None
        venue = m[3] or None
    lineups = dict(home=dict(starters=[], substitutes=[]), away=dict(starters=[], substitutes=[]))
    staff, officials, warnings = [], [], []
    available = set()
    for section in root.all(tag="section"):
        titles = section.all(cls="title-bar")
        if len(titles) != 1:
            continue
        title = titles[0].text()
        available.add(title)
        if title in {"Equipas Iniciais", "Suplentes"}:
            for team in section.all(cls="lineup-team"):
                side = "home" if team.has("home-team") else "away" if team.has("away-team") else None
                if side is None:
                    raise FPFHTMLInvalid("Plantel sem equipa.")
                for player in team.all(cls="player"):
                    shirt = one(player.all(tag="strong"), "camisola").text()
                    # Direct text excludes the photo's goal-count badges.
                    name = " ".join(c for c in player.children if isinstance(c, str)).strip()
                    name = " ".join(name.split())
                    if not name:
                        raise FPFHTMLInvalid("Jogador sem nome.")
                    lineups[side]["starters" if title == "Equipas Iniciais" else "substitutes"].append(
                        dict(player_id=_person_id(player), shirt_number=number(shirt), name=name,
                             lookup_name=re.sub(r"\s*\(GR\)$", "", name)))
        elif title in {"Treinadores", "Dirigentes"}:
            teams = section.all(cls="lineup-team")
            ambiguous = len(teams) != 2 or [t.has("away-team") for t in teams] != [False, True]
            if ambiguous:
                warnings.append(f"{title}: marcação de equipa ambígua; lado não atribuído.")
            for index, team in enumerate(teams):
                for person in team.all(cls="player"):
                    spans = [n for n in person.children if isinstance(n, Node) and n.tag == "span"]
                    if len(spans) != 2:
                        raise FPFHTMLInvalid("Equipa técnica incompleta.")
                    staff.append(dict(category=title, role=spans[0].text(), name=spans[1].text(),
                                      person_id=_person_id(person), side=None if ambiguous else ("home" if index == 0 else "away"),
                                      column=index + 1))
        elif title == "Equipa de arbitragem":
            for person in section.all(cls="player"):
                officials.append(dict(role=one(person.all(tag="strong"), "função árbitro").text(),
                                      name=one(person.all(tag="span"), "nome árbitro").text()))
    roster = [(side, p) for side, groups in lineups.items() for group in groups.values() for p in group]
    ids_present = [p["player_id"] for _, p in roster if p["player_id"] is not None]
    if len(ids_present) != len(set(ids_present)):
        raise FPFHTMLInvalid("Jogadores repetidos na ficha.")
    def resolve(name):
        found = [(side, p) for side, p in roster if _key(p["lookup_name"]) == _key(name)]
        return dict(name=name, player_id=found[0][1]["player_id"] if len(found) == 1 else None,
                    side=found[0][0] if len(found) == 1 else None)
    events = []
    icons = {"icon-goal.png": "goal", "icon-yellow-card.png": "yellow_card",
             "icon-red-card.png": "red_card", "icon-substitution.png": "substitution"}
    for period, wrapper in enumerate(root.all(cls="timeline-wrapper"), 1):
        for item in wrapper.all(cls="timeline-item"):
            images = [n.attrs.get("src", "").rsplit("/", 1)[-1] for n in item.all(tag="img")]
            kinds = [icons[i] for i in images if i in icons]
            if not kinds:
                if any(i not in {"icon-start.png", "icon-end.png"} for i in images):
                    warnings.append("Ícone de evento desconhecido; não convertido.")
                continue
            kind = one(kinds, "tipo de evento")
            minute = one(item.all(cls="top-tag"), "minuto").text()
            event = dict(type=kind, period=period, **_minute(minute))
            if kind == "substitution":
                incoming = resolve(one(item.all(cls="in"), "jogador que entra").text())
                outgoing = resolve(one(item.all(cls="out"), "jogador que sai").text())
                if incoming["side"] and outgoing["side"] and incoming["side"] != outgoing["side"]:
                    raise FPFHTMLInvalid("Substituição entre equipas diferentes.")
                event.update(player_in=incoming, player_out=outgoing)
            else:
                event.update(player=resolve(one(item.all(tag="strong"), "jogador do evento").text()))
            events.append(event)
    goals = [event for event in events if event["type"] == "goal"]
    if goals and all(event["player"]["side"] is not None for event in goals):
        counts = tuple(sum(event["player"]["side"] == side for event in goals) for side in ("home", "away"))
        if counts != (int(score[1]), int(score[2])):
            warnings.append("Resultado e golos da timeline não reconciliados; conservar ambos sem criar eventos internos.")
    return dict(match_id=ids["matchId"], competition_id=comp["competitionId"], season_id=comp["seasonId"],
                home=clubs[0], away=clubs[1], home_goals=int(score[1]), away_goals=int(score[2]),
                date=date, time=clock, venue=venue, lineups=lineups, events=events,
                staff=staff, officials=officials, warnings=warnings,
                availability=dict(starters="Equipas Iniciais" in available, substitutes="Suplentes" in available,
                                  events=bool(root.all(cls="timeline-wrapper")), staff=bool({"Treinadores", "Dirigentes"} & available),
                                  officials="Equipa de arbitragem" in available),
                source_url=f"{ORIGIN}/Match/GetMatchInformation?matchId={ids['matchId']}")
