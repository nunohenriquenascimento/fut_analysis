"""Política proposta e simulável: autorização e certificação sem infraestrutura.

Só usa objetos sintéticos/imutáveis e biblioteca padrão. Não autentica clientes,
consulta pertenças, atribui permissões ou certifica dados operacionais. Não está
ligada a auth.py, ao exportador ou a rotas de produção.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


def _text(value: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("Identificador/evidência deve ser texto canónico não vazio.")


def _aware(value: datetime) -> None:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("O instante deve incluir timezone.")


class Permission(StrEnum):
    """Ações independentes; exportar não implica poder certificar ou corrigir."""

    VIEW_MATCHES = "matches:read"
    RECORD_EVENTS = "events:create"
    CORRECT_EVENTS = "events:correct"
    CERTIFY_RESULT = "results:certify"
    CERTIFY_STATISTICS = "statistics:certify"
    EXPORT_MATCHES = "matches:export"


class ResourceRole(StrEnum):
    """Papéis propostos por equipa/época, sem correspondência com ADMIN global."""

    READER = "reader"
    RECORDER = "recorder"
    REVIEWER = "reviewer"
    EXPORTER = "exporter"


_ROLE_PERMISSIONS = {
    ResourceRole.READER: frozenset({Permission.VIEW_MATCHES}),
    ResourceRole.RECORDER: frozenset(
        {Permission.VIEW_MATCHES, Permission.RECORD_EVENTS}
    ),
    ResourceRole.REVIEWER: frozenset(
        {
            Permission.VIEW_MATCHES,
            Permission.CORRECT_EVENTS,
            Permission.CERTIFY_RESULT,
            Permission.CERTIFY_STATISTICS,
        }
    ),
    ResourceRole.EXPORTER: frozenset(
        {Permission.VIEW_MATCHES, Permission.EXPORT_MATCHES}
    ),
}


@dataclass(frozen=True)
class ResourceScope:
    """Identidade exata do recurso; não admite herança implícita entre equipas."""

    source_instance_id: str
    club_id: str
    team_id: str
    season_id: str

    def __post_init__(self) -> None:
        """Rejeita IDs vazios/ambíguos; a associação real virá do servidor."""
        for value in (
            self.source_instance_id,
            self.club_id,
            self.team_id,
            self.season_id,
        ):
            _text(value)


@dataclass(frozen=True)
class Principal:
    """Snapshot declarado de identidade; a autenticação real fica fora deste módulo."""

    subject_id: str
    authenticated: bool
    active: bool

    def __post_init__(self) -> None:
        """Exige flags booleanas estritas, sem coerções de strings ou números."""
        _text(self.subject_id)
        if type(self.authenticated) is not bool or type(self.active) is not bool:
            raise ValueError("Flags da identidade devem ser booleanas.")


@dataclass(frozen=True)
class Membership:
    """Pertença sintética com papel, validade e eventual revogação temporal."""

    membership_id: str
    subject_id: str
    scope: ResourceScope
    role: ResourceRole
    valid_from: datetime
    expires_at: datetime | None = None
    revoked_at: datetime | None = None

    def __post_init__(self) -> None:
        """Valida a forma, sem criar uma pertença ou a guardar numa base."""
        _text(self.membership_id)
        _text(self.subject_id)
        if not isinstance(self.scope, ResourceScope) or not isinstance(
            self.role, ResourceRole
        ):
            raise ValueError("Âmbito/papel tipados são obrigatórios.")
        _aware(self.valid_from)
        for value in (self.expires_at, self.revoked_at):
            if value is not None:
                _aware(value)
        if self.expires_at is not None and self.expires_at <= self.valid_from:
            raise ValueError("A expiração deve ser posterior ao início da pertença.")


@dataclass(frozen=True)
class PermissionDecision:
    """Resultado da avaliação offline, não reutilizável como token de acesso."""

    allowed: bool
    reason: str
    membership_ids: tuple[str, ...] = ()


def evaluate_permission(
    principal: Principal | None,
    permission: Permission,
    scope: ResourceScope,
    memberships: Sequence[Membership],
    *,
    at: datetime,
) -> PermissionDecision:
    """Nega por omissão; exige identidade ativa e pertença válida no mesmo âmbito.

    A futura integração tem de carregar identidade, scope e pertenças de fontes
    confiáveis e recentes. Receber estes objetos de um cliente não os autentica.
    """
    _aware(at)
    if (
        not isinstance(principal, Principal)
        or not principal.authenticated
        or not principal.active
    ):
        return PermissionDecision(
            False, "Identidade ausente, inativa ou não autenticada."
        )
    if not isinstance(permission, Permission) or not isinstance(scope, ResourceScope):
        return PermissionDecision(False, "Permissão ou âmbito desconhecido.")
    if any(not isinstance(item, Membership) for item in memberships):
        return PermissionDecision(False, "Snapshot de pertenças inválido.")
    if len({item.membership_id for item in memberships}) != len(memberships):
        return PermissionDecision(False, "Snapshot com pertenças duplicadas/ambíguas.")
    applicable = tuple(
        sorted(
            {
                item.membership_id
                for item in memberships
                if item.subject_id == principal.subject_id
                and item.scope == scope
                and item.valid_from <= at
                and (item.expires_at is None or at < item.expires_at)
                and (item.revoked_at is None or at < item.revoked_at)
                and permission in _ROLE_PERMISSIONS[item.role]
            }
        )
    )
    if not applicable:
        return PermissionDecision(
            False, "Sem pertença/permissão válida para este recurso."
        )
    return PermissionDecision(True, "Permitido pela política proposta.", applicable)


class Category(StrEnum):
    """Resultado é separado de completude de golos e restantes acontecimentos."""

    RESULT = "result"
    GOALS = "score_events"
    SHOTS = "shots"
    CARDS = "cards"
    SUBSTITUTIONS = "substitutions"
    SQUAD = "squad"
    OTHER_EVENTS = "other_events"
    PLAYER_ATTRIBUTION = "player_attribution"


class Status(StrEnum):
    """Vocabulário interno compatível com os estados do contrato v1."""

    UNKNOWN = "unknown"
    PARTIAL = "partial"
    COMPLETE = "complete"
    UNAVAILABLE = "unavailable"
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    CONFLICT = "conflict"


class EvidenceKind(StrEnum):
    """Tipo de revisão declarada; a função não verifica documentos externos."""

    COLLECTION_REVIEW = "collection_review"
    EVENT_RECONCILIATION = "event_reconciliation"
    OFFICIAL_CAPTURE = "official_capture"
    MANUAL_REVIEW = "manual_review"
    CORRECTION = "correction"


@dataclass(frozen=True)
class Evidence:
    """Referência e explicação auditáveis, sem recolher ficheiros ou dados reais."""

    kind: EvidenceKind
    reference: str
    rationale: str

    def __post_init__(self) -> None:
        """Exige evidência explícita em vez de inferir qualidade de FINISHED."""
        if not isinstance(self.kind, EvidenceKind):
            raise ValueError("Tipo de evidência desconhecido.")
        _text(self.reference)
        _text(self.rationale)


@dataclass(frozen=True)
class AuditEntry:
    """Evento imutável de uma transição; o histórico permanece no objeto devolvido."""

    record_id: str
    actor_id: str
    at: datetime
    action: str
    previous_status: Status
    target_status: Status
    previous_version: str
    content_version: str
    evidence: Evidence
    membership_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        """Valida os metadados mínimos de auditoria sintética."""
        for value in (
            self.record_id,
            self.actor_id,
            self.previous_version,
            self.content_version,
        ):
            _text(value)
        _aware(self.at)
        if self.action not in {"assess", "invalidate"}:
            raise ValueError("Ação de auditoria desconhecida.")
        if not isinstance(self.previous_status, Status) or not isinstance(
            self.target_status, Status
        ):
            raise ValueError("Estados de auditoria devem ser tipados.")
        if type(self.membership_ids) is not tuple:
            raise ValueError("Pertenças de auditoria devem ser imutáveis.")
        for membership_id in self.membership_ids:
            _text(membership_id)
        if not isinstance(self.evidence, Evidence):
            raise ValueError("A auditoria exige evidência tipada.")


def _initial(category: Category) -> Status:
    return Status.UNVERIFIED if category == Category.RESULT else Status.UNKNOWN


@dataclass(frozen=True)
class CertificationState:
    """Avaliação de uma categoria num jogo/versão, com histórico append-only em memória."""

    scope: ResourceScope
    match_id: str
    category: Category
    status: Status
    content_version: str
    history: tuple[AuditEntry, ...] = ()

    def __post_init__(self) -> None:
        """Impede estados incompatíveis e certificados elevados sem histórico."""
        _text(self.match_id)
        _text(self.content_version)
        if not isinstance(self.scope, ResourceScope) or not isinstance(
            self.category, Category
        ):
            raise ValueError("Categoria/âmbito inválidos.")
        valid = (
            {Status.UNVERIFIED, Status.VERIFIED, Status.CONFLICT, Status.UNAVAILABLE}
            if self.category == Category.RESULT
            else {Status.UNKNOWN, Status.PARTIAL, Status.COMPLETE, Status.UNAVAILABLE}
        )
        if not isinstance(self.status, Status) or self.status not in valid:
            raise ValueError("Estado incompatível com a categoria.")
        if type(self.history) is not tuple or any(
            not isinstance(row, AuditEntry) for row in self.history
        ):
            raise ValueError("Histórico deve ser um tuple imutável de eventos.")
        if not self.history:
            if self.status != _initial(self.category):
                raise ValueError("Estado certificado/revisto exige histórico.")
        else:
            if self.history[0].previous_status != _initial(self.category):
                raise ValueError("O histórico deve começar no estado inicial.")
            transitions = (
                _RESULT_TRANSITIONS
                if self.category == Category.RESULT
                else _QUALITY_TRANSITIONS
            )
            for row in self.history:
                if row.previous_status not in valid or row.target_status not in valid:
                    raise ValueError(
                        "Auditoria de estado incompatível com a categoria."
                    )
                if row.action == "assess" and (
                    row.target_status not in transitions[row.previous_status]
                    or row.previous_version != row.content_version
                    or not row.membership_ids
                ):
                    raise ValueError("Transição de auditoria inválida.")
                if row.action == "invalidate" and (
                    row.target_status != _initial(self.category)
                    or row.previous_version == row.content_version
                    or row.evidence.kind != EvidenceKind.CORRECTION
                    or row.membership_ids
                ):
                    raise ValueError("Invalidação de auditoria inválida.")
            last = self.history[-1]
            if (
                last.target_status != self.status
                or last.content_version != self.content_version
            ):
                raise ValueError("Estado diverge do último evento de auditoria.")
            if len({row.record_id for row in self.history}) != len(self.history):
                raise ValueError("IDs de auditoria duplicados.")
            for before, after in zip(self.history, self.history[1:], strict=False):
                if (
                    before.at > after.at
                    or before.target_status != after.previous_status
                    or before.content_version != after.previous_version
                ):
                    raise ValueError("Histórico descontínuo ou fora de ordem.")


def initial_certification(
    scope: ResourceScope, match_id: str, category: Category, content_version: str
) -> CertificationState:
    """Começa em unknown/unverified, sem atribuir uma certificação implícita."""
    return CertificationState(
        scope, match_id, category, _initial(category), content_version
    )


_QUALITY_TRANSITIONS = {
    Status.UNKNOWN: {Status.PARTIAL, Status.COMPLETE, Status.UNAVAILABLE},
    Status.PARTIAL: {Status.COMPLETE, Status.UNAVAILABLE},
    Status.COMPLETE: {Status.PARTIAL, Status.UNAVAILABLE},
    Status.UNAVAILABLE: {Status.PARTIAL, Status.COMPLETE},
}
_RESULT_TRANSITIONS = {
    Status.UNVERIFIED: {Status.VERIFIED, Status.CONFLICT, Status.UNAVAILABLE},
    Status.VERIFIED: {Status.CONFLICT, Status.UNAVAILABLE},
    Status.CONFLICT: {Status.VERIFIED, Status.UNAVAILABLE},
    Status.UNAVAILABLE: {Status.UNVERIFIED},
}


def assess_certification(
    state: CertificationState,
    target: Status,
    *,
    principal: Principal,
    memberships: Sequence[Membership],
    at: datetime,
    evidence: Evidence,
    expected_version: str,
    finished: bool,
    record_id: str,
    goals_certification: CertificationState | None = None,
) -> CertificationState:
    """Avalia uma transição sintética com autorização, evidência e controlo de versão.

    Verificar um resultado por eventos exige golos completos do mesmo jogo e
    versão. A reconciliação numérica e a autenticidade da evidência pertencem
    à futura integração; esta função não lê nem certifica um jogo operacional.
    """
    _aware(at)
    permission = (
        Permission.CERTIFY_RESULT
        if state.category == Category.RESULT
        else Permission.CERTIFY_STATISTICS
    )
    decision = evaluate_permission(
        principal, permission, state.scope, memberships, at=at
    )
    if not decision.allowed:
        raise PermissionError(decision.reason)
    if not isinstance(target, Status) or not isinstance(evidence, Evidence):
        raise ValueError("Transição exige estado/evidência tipados.")
    if type(finished) is not bool:
        raise ValueError("finished deve ser booleano.")
    if expected_version != state.content_version:
        raise ValueError("Versão desatualizada; é necessária uma nova avaliação.")
    transitions = (
        _RESULT_TRANSITIONS
        if state.category == Category.RESULT
        else _QUALITY_TRANSITIONS
    )
    if target not in transitions[state.status]:
        raise ValueError("Transição inválida para a categoria/estado atual.")
    if state.history and at < state.history[-1].at:
        raise ValueError("Avaliação anterior ao último evento.")
    if target in {Status.COMPLETE, Status.VERIFIED} and not finished:
        raise ValueError(
            "Certificação final exige jogo terminado, mas FINISHED não basta."
        )
    if (
        state.category != Category.RESULT
        and evidence.kind != EvidenceKind.COLLECTION_REVIEW
    ):
        raise ValueError("Completude exige revisão explícita de recolha.")
    if state.category == Category.RESULT:
        if evidence.kind not in {
            EvidenceKind.EVENT_RECONCILIATION,
            EvidenceKind.OFFICIAL_CAPTURE,
            EvidenceKind.MANUAL_REVIEW,
        }:
            raise ValueError(
                "Resultado exige evidência de reconciliação/captura/revisão."
            )
        if (
            target == Status.VERIFIED
            and evidence.kind == EvidenceKind.EVENT_RECONCILIATION
        ):
            goals = goals_certification
            if goals is None or (
                goals.scope,
                goals.match_id,
                goals.category,
                goals.status,
                goals.content_version,
            ) != (
                state.scope,
                state.match_id,
                Category.GOALS,
                Status.COMPLETE,
                state.content_version,
            ):
                raise ValueError(
                    "Resultado por eventos exige golos completos do mesmo jogo/versão."
                )
            if goals.history[-1].at > at:
                raise ValueError(
                    "Certificação de golos posterior à avaliação do resultado."
                )
    entry = AuditEntry(
        record_id,
        principal.subject_id,
        at,
        "assess",
        state.status,
        target,
        state.content_version,
        state.content_version,
        evidence,
        decision.membership_ids,
    )
    return CertificationState(
        state.scope,
        state.match_id,
        state.category,
        target,
        state.content_version,
        (*state.history, entry),
    )


def invalidate_for_correction(
    state: CertificationState,
    *,
    new_content_version: str,
    at: datetime,
    changed_by: str,
    change_reference: str,
    record_id: str,
) -> CertificationState:
    """Invalida a avaliação após correção previamente autorizada noutro serviço.

    Não autoriza nem executa a correção. Pode ser usada como reação de sistema,
    mesmo que o certificador original já não tenha permissão. A política proposta
    invalida conservadoramente todas as categorias afetadas pela versão do jogo.
    """
    _aware(at)
    _text(new_content_version)
    if new_content_version == state.content_version:
        raise ValueError("Uma correção relevante exige versão diferente.")
    if state.history and at < state.history[-1].at:
        raise ValueError("Correção anterior à última avaliação.")
    evidence = Evidence(
        EvidenceKind.CORRECTION,
        change_reference,
        "Conteúdo alterado; avaliação anterior não certifica a nova versão.",
    )
    entry = AuditEntry(
        record_id,
        changed_by,
        at,
        "invalidate",
        state.status,
        _initial(state.category),
        state.content_version,
        new_content_version,
        evidence,
        (),
    )
    return CertificationState(
        state.scope,
        state.match_id,
        state.category,
        _initial(state.category),
        new_content_version,
        (*state.history, entry),
    )


def effective_status(
    state: CertificationState, *, current_version: str, finished: bool
) -> Status:
    """Evita usar certificado antigo após alteração, mesmo antes de persistir invalidação."""
    _text(current_version)
    if type(finished) is not bool:
        raise ValueError("finished deve ser booleano.")
    if current_version != state.content_version or (
        not finished and state.status in {Status.COMPLETE, Status.VERIFIED}
    ):
        return _initial(state.category)
    return state.status
