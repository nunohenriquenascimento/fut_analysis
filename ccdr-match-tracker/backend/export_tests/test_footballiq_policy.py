"""Regras propostas com objetos fictícios, sem auth, ORM, rede ou dados reais."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta

import pytest

from app.footballiq_policy import (
    Category,
    CertificationState,
    Evidence,
    EvidenceKind,
    Membership,
    Permission,
    Principal,
    ResourceRole,
    ResourceScope,
    Status,
    assess_certification,
    effective_status,
    evaluate_permission,
    initial_certification,
    invalidate_for_correction,
)

NOW = datetime(2026, 11, 9, 10, tzinfo=UTC)
SCOPE = ResourceScope("fictional-instance", "fictional-club", "42", "7")
ACTOR = Principal("fictional-reviewer", authenticated=True, active=True)
EVIDENCE = Evidence(
    EvidenceKind.COLLECTION_REVIEW,
    "synthetic-review:1",
    "Revisão exclusivamente fictícia",
)


def membership(role=ResourceRole.REVIEWER, **changes):
    """Pertença só em memória; não corresponde a uma concessão no sistema real."""
    return Membership(
        **(
            dict(
                membership_id="synthetic-membership",
                subject_id=ACTOR.subject_id,
                scope=SCOPE,
                role=role,
                valid_from=NOW - timedelta(days=1),
            )
            | changes
        )
    )


def state(category=Category.SHOTS, **changes):
    """Começa com qualidade desconhecida e versão sintética explícita."""
    return initial_certification(
        **(
            dict(
                scope=SCOPE,
                match_id="10",
                category=category,
                content_version="synthetic-v1",
            )
            | changes
        )
    )


def assess(current=None, target=Status.COMPLETE, **changes):
    """Simula uma avaliação autorizada apenas pela política proposta."""
    return assess_certification(
        current or state(),
        target,
        **(
            dict(
                principal=ACTOR,
                memberships=(membership(),),
                at=NOW,
                evidence=EVIDENCE,
                expected_version="synthetic-v1",
                finished=True,
                record_id="synthetic-record:1",
            )
            | changes
        ),
    )


@pytest.mark.parametrize(
    "role,allowed",
    [
        (ResourceRole.READER, {Permission.VIEW_MATCHES}),
        (ResourceRole.RECORDER, {Permission.VIEW_MATCHES, Permission.RECORD_EVENTS}),
        (
            ResourceRole.REVIEWER,
            {
                Permission.VIEW_MATCHES,
                Permission.CORRECT_EVENTS,
                Permission.CERTIFY_RESULT,
                Permission.CERTIFY_STATISTICS,
            },
        ),
        (ResourceRole.EXPORTER, {Permission.VIEW_MATCHES, Permission.EXPORT_MATCHES}),
    ],
)
@pytest.mark.parametrize("permission", list(Permission))
def test_explicit_resource_role_permission_matrix(role, allowed, permission):
    result = evaluate_permission(ACTOR, permission, SCOPE, (membership(role),), at=NOW)
    assert result.allowed == (permission in allowed)
    assert bool(result.membership_ids) == result.allowed


@pytest.mark.parametrize(
    "actor",
    [None, replace(ACTOR, active=False), replace(ACTOR, authenticated=False), "ADMIN"],
)
def test_authentication_or_global_role_cannot_replace_resource_authorization(actor):
    assert not evaluate_permission(
        actor, Permission.EXPORT_MATCHES, SCOPE, (membership(),), at=NOW
    ).allowed


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_instance_id", "other-instance"),
        ("club_id", "other-club"),
        ("team_id", "99"),
        ("season_id", "8"),
    ],
)
def test_manipulated_ids_cannot_cross_any_scope_boundary(field, value):
    target = replace(SCOPE, **{field: value})
    assert not evaluate_permission(
        ACTOR, Permission.VIEW_MATCHES, target, (membership(),), at=NOW
    ).allowed


def test_missing_or_unknown_permissions_deny_by_default():
    assert not evaluate_permission(
        ACTOR, Permission.VIEW_MATCHES, SCOPE, (), at=NOW
    ).allowed
    assert not evaluate_permission(
        ACTOR, "matches:delete", SCOPE, (membership(),), at=NOW
    ).allowed
    assert not evaluate_permission(
        ACTOR, Permission.VIEW_MATCHES, SCOPE, (object(),), at=NOW
    ).allowed
    assert not evaluate_permission(
        ACTOR,
        Permission.VIEW_MATCHES,
        SCOPE,
        (membership(subject_id="other-subject"),),
        at=NOW,
    ).allowed


@pytest.mark.parametrize(
    "changes",
    [
        {"revoked_at": NOW},
        {"revoked_at": NOW - timedelta(seconds=1)},
        {"expires_at": NOW},
        {"valid_from": NOW + timedelta(seconds=1)},
    ],
)
def test_revoked_expired_or_future_membership_is_not_effective(changes):
    assert not evaluate_permission(
        ACTOR, Permission.VIEW_MATCHES, SCOPE, (membership(**changes),), at=NOW
    ).allowed


def test_revocation_rechecked_at_boundary_and_history_is_not_erased():
    grant = membership(revoked_at=NOW + timedelta(seconds=1))
    assert evaluate_permission(
        ACTOR, Permission.CERTIFY_STATISTICS, SCOPE, (grant,), at=NOW
    ).allowed
    assert not evaluate_permission(
        ACTOR,
        Permission.CERTIFY_STATISTICS,
        SCOPE,
        (grant,),
        at=NOW + timedelta(seconds=1),
    ).allowed
    certified = assess(memberships=(grant,))
    with pytest.raises(PermissionError):
        assess(
            certified,
            Status.PARTIAL,
            memberships=(grant,),
            at=NOW + timedelta(seconds=1),
            record_id="new",
        )
    assert certified.history[0].actor_id == ACTOR.subject_id
    assert certified.status == Status.COMPLETE


def test_independent_active_membership_is_an_explicit_separate_grant():
    revoked = membership(revoked_at=NOW)
    active = membership(membership_id="synthetic-second-membership")
    result = evaluate_permission(
        ACTOR, Permission.VIEW_MATCHES, SCOPE, (revoked, active), at=NOW
    )
    assert result.allowed and result.membership_ids == (active.membership_id,)


@pytest.mark.parametrize("category", list(Category))
def test_default_quality_is_unknown_or_unverified(category):
    value = state(category)
    assert value.status == (
        Status.UNVERIFIED if category == Category.RESULT else Status.UNKNOWN
    )
    assert value.history == ()


def test_complete_requires_explicit_evidence_authority_and_audit():
    current = state()
    certified = assess(current)
    assert current.status == Status.UNKNOWN and current.history == ()
    assert certified.status == Status.COMPLETE
    entry = certified.history[0]
    assert (entry.actor_id, entry.at, entry.content_version) == (
        ACTOR.subject_id,
        NOW,
        "synthetic-v1",
    )
    assert entry.evidence == EVIDENCE and entry.membership_ids == (
        "synthetic-membership",
    )
    with pytest.raises(FrozenInstanceError):
        certified.status = Status.UNKNOWN


@pytest.mark.parametrize(
    "category",
    [
        Category.GOALS,
        Category.SHOTS,
        Category.CARDS,
        Category.SUBSTITUTIONS,
        Category.SQUAD,
        Category.OTHER_EVENTS,
        Category.PLAYER_ATTRIBUTION,
    ],
)
def test_categories_can_be_assessed_independently(category):
    assert assess(state(category)).status == Status.COMPLETE
    assert state(Category.RESULT).status == Status.UNVERIFIED
    other = Category.CARDS if category != Category.CARDS else Category.SHOTS
    assert state(other).status == Status.UNKNOWN


@pytest.mark.parametrize(
    "changes",
    [
        {"finished": False},
        {"finished": 1},
        {"expected_version": "old-version"},
        {"evidence": None},
        {"evidence": Evidence(EvidenceKind.MANUAL_REVIEW, "fixture:1", "Fictício")},
    ],
)
def test_finished_alone_stale_version_or_wrong_evidence_cannot_certify(changes):
    with pytest.raises(ValueError):
        assess(**changes)


@pytest.mark.parametrize(
    "role", [ResourceRole.READER, ResourceRole.RECORDER, ResourceRole.EXPORTER]
)
def test_roles_without_certification_permission_cannot_assess(role):
    with pytest.raises(PermissionError):
        assess(memberships=(membership(role),))


def test_cross_team_reviewer_cannot_certify():
    with pytest.raises(PermissionError):
        assess(memberships=(membership(scope=replace(SCOPE, team_id="99")),))


@pytest.mark.parametrize("target", [Status.UNKNOWN, Status.VERIFIED, Status.CONFLICT])
def test_invalid_quality_transitions_are_rejected(target):
    with pytest.raises(ValueError):
        assess(target=target)


def test_partial_complete_and_unavailable_have_explicit_transitions():
    partial = assess(target=Status.PARTIAL)
    complete = assess(partial, record_id="record:2")
    unavailable = assess(complete, Status.UNAVAILABLE, record_id="record:3")
    assert [entry.target_status for entry in unavailable.history] == [
        Status.PARTIAL,
        Status.COMPLETE,
        Status.UNAVAILABLE,
    ]
    with pytest.raises(ValueError):
        assess(
            complete, record_id="record:4"
        )  # Não recertificar a mesma versão sem transição.
    with pytest.raises(ValueError):
        assess(partial, record_id="synthetic-record:1")


def test_result_by_events_requires_complete_goals_same_scope_match_and_version():
    current = state(Category.RESULT)
    evidence = Evidence(
        EvidenceKind.EVENT_RECONCILIATION,
        "synthetic-result:1",
        "Reconciliação fictícia",
    )
    with pytest.raises(ValueError, match="golos completos"):
        assess(current, Status.VERIFIED, evidence=evidence)
    goals = assess(state(Category.GOALS))
    verified = assess(
        current,
        Status.VERIFIED,
        evidence=evidence,
        goals_certification=goals,
        record_id="result:1",
    )
    assert verified.status == Status.VERIFIED
    for wrong in (
        state(Category.GOALS),
        assess(state(Category.GOALS, match_id="11")),
        assess(state(Category.GOALS, content_version="v2"), expected_version="v2"),
    ):
        with pytest.raises(ValueError, match="golos completos"):
            assess(
                current, Status.VERIFIED, evidence=evidence, goals_certification=wrong
            )


@pytest.mark.parametrize(
    "method", [EvidenceKind.OFFICIAL_CAPTURE, EvidenceKind.MANUAL_REVIEW]
)
def test_result_can_be_verified_without_certifying_event_categories(method):
    verified = assess(
        state(Category.RESULT),
        Status.VERIFIED,
        evidence=Evidence(method, "synthetic-evidence:1", "Apenas resultado fictício"),
    )
    assert verified.status == Status.VERIFIED
    assert (
        state(Category.GOALS).status == state(Category.SHOTS).status == Status.UNKNOWN
    )


def test_result_conflict_requires_new_explicit_review():
    proof = Evidence(
        EvidenceKind.MANUAL_REVIEW, "synthetic-score:1", "Conflito fictício"
    )
    conflict = assess(state(Category.RESULT), Status.CONFLICT, evidence=proof)
    assert conflict.status == Status.CONFLICT
    verified = assess(conflict, Status.VERIFIED, evidence=proof, record_id="result:2")
    assert verified.status == Status.VERIFIED and len(verified.history) == 2


@pytest.mark.parametrize("category", list(Category))
def test_correction_invalidates_version_and_preserves_immutable_history(category):
    current = state(category)
    if category == Category.RESULT:
        certified = assess(
            current,
            Status.VERIFIED,
            evidence=Evidence(
                EvidenceKind.MANUAL_REVIEW, "synthetic-proof:1", "Fictício"
            ),
        )
    else:
        certified = assess(current)
    corrected = invalidate_for_correction(
        certified,
        new_content_version="synthetic-v2",
        at=NOW + timedelta(seconds=1),
        changed_by="synthetic-editor",
        change_reference="synthetic-change:1",
        record_id="invalidate:1",
    )
    expected = Status.UNVERIFIED if category == Category.RESULT else Status.UNKNOWN
    assert corrected.status == expected
    assert corrected.history[0] == certified.history[0]
    assert corrected.history[-1].previous_version == "synthetic-v1"
    assert corrected.history[-1].content_version == "synthetic-v2"
    assert corrected.history[-1].action == "invalidate"
    assert certified.status != corrected.status
    assert (
        effective_status(certified, current_version="synthetic-v2", finished=True)
        == expected
    )


def test_recognition_of_old_version_or_reopening_never_reuses_complete_status():
    certified = assess()
    assert (
        effective_status(certified, current_version="synthetic-v1", finished=True)
        == Status.COMPLETE
    )
    assert (
        effective_status(certified, current_version="synthetic-v1", finished=False)
        == Status.UNKNOWN
    )
    with pytest.raises(ValueError):
        invalidate_for_correction(
            certified,
            new_content_version="synthetic-v1",
            at=NOW,
            changed_by="synthetic-editor",
            change_reference="change:1",
            record_id="x",
        )
    with pytest.raises(ValueError):
        assess(
            certified, Status.PARTIAL, at=NOW - timedelta(seconds=1), record_id="older"
        )


def test_certification_requires_evidence_and_history_even_for_direct_construction():
    with pytest.raises(ValueError):
        Evidence(EvidenceKind.COLLECTION_REVIEW, " ", "Fictício")
    with pytest.raises(ValueError):
        CertificationState(SCOPE, "10", Category.SHOTS, Status.COMPLETE, "v1")
    with pytest.raises(ValueError):
        Membership("m", ACTOR.subject_id, SCOPE, "ADMIN", NOW)
    with pytest.raises(ValueError):
        Principal("actor", authenticated=1, active=True)
    with pytest.raises(ValueError):
        evaluate_permission(
            ACTOR, Permission.VIEW_MATCHES, SCOPE, (), at=NOW.replace(tzinfo=None)
        )


def test_repetition_is_deterministic_and_does_not_mutate_arguments():
    initial = state()
    assert assess(initial) == assess(initial)
    assert initial.history == ()
    assert evaluate_permission(
        ACTOR, Permission.VIEW_MATCHES, SCOPE, (membership(),), at=NOW
    ) == evaluate_permission(
        ACTOR, Permission.VIEW_MATCHES, SCOPE, (membership(),), at=NOW
    )


def test_policy_import_is_standalone_without_auth_orm_or_network():
    script = """
import importlib.abc, socket, sys
from unittest.mock import patch
class NoInfrastructure(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in {'app.auth', 'app.database', 'app.models', 'app.footballiq_export'} or fullname.split('.')[0] in {'sqlalchemy', 'psycopg', 'fastapi'}:
            raise AssertionError('Policy must remain independent of infrastructure')
def forbidden(*args, **kwargs):
    raise AssertionError('No network in pure policy')
sys.meta_path.insert(0, NoInfrastructure())
with patch.object(socket.socket, 'connect', forbidden), patch.object(socket, 'create_connection', forbidden):
    import app.footballiq_policy
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", script],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_ambiguous_duplicate_membership_does_not_resurrect_revoked_permission():
    old = membership(revoked_at=NOW)
    inconsistent = membership()
    result = evaluate_permission(
        ACTOR, Permission.VIEW_MATCHES, SCOPE, (old, inconsistent), at=NOW
    )
    assert result.allowed is False


def test_tampered_audit_chain_is_rejected_without_mutating_history():
    certified = assess()
    previous = certified.history[0]
    with pytest.raises(ValueError):
        replace(
            certified, history=(replace(previous, previous_status=Status.COMPLETE),)
        )
    with pytest.raises(ValueError):
        replace(certified, history=(replace(previous, membership_ids=()),))
    assert certified.history == (previous,)
