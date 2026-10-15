"""FPF capture preview/import on the existing competition; ADMIN writes only."""
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import Field, model_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import current_user, require_admin
from app.competition_service import get_competition
from app.database import get_db
from app.fpf_parser import FPFHTMLInvalid, Tree, parse_competition, parse_match
from app.fpf_source import FPFClient, FPFSourceUnavailable
from app.fpf_sync import apply_fpf, prepare_fpf
from app.schemas import InputModel

Positive = Annotated[int, Field(strict=True, gt=0, le=2_147_483_647)]
HTML = Annotated[str, Field(min_length=1, max_length=2_000_000)]


class FPFCapture(InputModel):
    competition_html: HTML | None = None
    series_id: Positive
    team_mapping: dict[str, Positive] = Field(min_length=2, max_length=64)
    match_htmls: list[HTML] = Field(default_factory=list, max_length=8)
    match_rounds: dict[str, Positive] = Field(default_factory=dict, max_length=64)
    internal_match_links: dict[str, Positive] = Field(default_factory=dict, max_length=64)
    expected_state: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")] | None = None

    @model_validator(mode="after")
    def bounded_html(self):
        sizes = [len(html.encode("utf-8")) for html in [self.competition_html, *self.match_htmls] if html is not None]
        if any(size > 2_000_000 for size in sizes) or sum(sizes) > 4_000_000:
            raise ValueError("Máximo 2 MB por ficheiro HTML e 4 MB por lote.")
        return self


class FPFApply(FPFCapture):
    confirmation: Literal["SINCRONIZAR FPF"]


class FPFRefresh(InputModel):
    confirmation: Literal["SINCRONIZAR FPF"]


class FPFDocument(InputModel):
    name: Annotated[str, Field(min_length=1, max_length=160)]
    html: HTML


class FPFDocuments(InputModel):
    files: list[FPFDocument] = Field(min_length=1, max_length=9)

    @model_validator(mode="after")
    def bounded_html(self):
        sizes = [len(file.html.encode("utf-8")) for file in self.files]
        if any(size > 2_000_000 for size in sizes) or sum(sizes) > 4_000_000:
            raise ValueError("Máximo 2 MB por ficheiro HTML e 4 MB por lote.")
        return self


router = APIRouter(tags=["competitions"], dependencies=[Depends(current_user)])
Database = Annotated[Session, Depends(get_db)]


@router.post("/competitions/{competition_id}/fpf/documents", dependencies=[Depends(require_admin)])
def inspect_documents(competition_id: int, payload: FPFDocuments, db: Database):
    get_competition(db, competition_id)
    if sum(len(file.html.encode("utf-8")) for file in payload.files) > 4_000_000:
        raise HTTPException(422, "O lote HTML excede 4 MB.")
    documents = []
    seen = set()
    for file in payload.files:
        try:
            if not file.name.lower().endswith((".html", ".htm")):
                raise FPFHTMLInvalid("Selecione ficheiros HTML.")
            root = Tree(file.html).root
            urls = [n.attrs.get("content", "") for n in root.all(tag="meta") if n.attrs.get("property") == "og:url"]
            if any("/Competition/Details?" in url for url in urls):
                kind, data = "competition", parse_competition(file.html)
            elif any("/Match/GetMatchInformation?" in url for url in urls):
                kind, data = "match", parse_match(file.html)
            elif root.all(id="classification") and root.all(id="matches"):
                documents.append(dict(name=file.name, kind="fixture", supported=False, data=None,
                    error="Jornada identificada; formato AJAX ainda não validado. Não será importada."))
                continue
            else:
                raise FPFHTMLInvalid("Documento desconhecido ou página de indisponibilidade; não importar.")
            identity = (kind, data.get("match_id") if kind == "match" else (data["competition_id"], data["season_id"]))
            if identity in seen:
                raise FPFHTMLInvalid("Documento repetido no lote.")
            seen.add(identity)
            documents.append(dict(name=file.name, kind=kind, supported=True, data=data, error=None))
        except (FPFHTMLInvalid, ValueError):
            documents.append(dict(name=file.name, kind="invalid", supported=False, data=None,
                                  error="HTML inválido, identidade contraditória ou estrutura não suportada."))
    return dict(documents=documents)


@router.get("/competitions/{competition_id}/fpf")
def read_fpf(competition_id: int, db: Database):
    snapshot = get_competition(db, competition_id).fpf_data
    return dict(source="FPF", available=snapshot is not None, snapshot=snapshot,
                note="Captura oficial separada da classificação local provisória e dos eventos internos.")


def prepare(db, competition, payload, **kwargs):
    try:
        return prepare_fpf(db, competition, payload, **kwargs)
    except FPFHTMLInvalid as error:
        raise HTTPException(422, str(error)) from None


@router.post("/competitions/{competition_id}/fpf/preview", dependencies=[Depends(require_admin)])
def preview_fpf(competition_id: int, payload: FPFCapture, db: Database):
    return prepare(db, get_competition(db, competition_id), payload)


def apply(db, competition, plan):
    try:
        return apply_fpf(db, competition, plan)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Conflito com jogos existentes; nenhuma alteração FPF aplicada.") from None


@router.put("/competitions/{competition_id}/fpf", dependencies=[Depends(require_admin)])
def import_fpf(competition_id: int, payload: FPFApply, db: Database):
    competition = get_competition(db, competition_id, lock=True)
    return apply(db, competition, prepare(db, competition, payload))


@router.post("/competitions/{competition_id}/fpf/sync", dependencies=[Depends(require_admin)])
def sync_fpf(competition_id: int, payload: FPFRefresh, db: Database):
    # Network access happens before acquiring the write lock; revalidate mapping afterwards.
    previous = get_competition(db, competition_id).fpf_data
    if previous is None:
        raise HTTPException(409, "Primeiro reveja e associe uma captura FPF.")
    competition_fpf, season_fpf, series = previous["identity"]
    try:
        document = FPFClient().competition(competition_fpf, season_fpf)
    except FPFSourceUnavailable as error:
        raise HTTPException(503, f"FPF indisponível ({error.reason}); última captura preservada.") from None
    db.expire_all()
    competition = get_competition(db, competition_id, lock=True)
    capture = FPFCapture(competition_html=document.html, series_id=series,
                         team_mapping=previous["team_mapping"], internal_match_links=previous.get("internal_match_links", {}))
    return apply(db, competition, prepare(db, competition, capture, mode="http"))
