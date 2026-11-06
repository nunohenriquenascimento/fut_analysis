"""Phase 2.4 security and presentation contracts, using synthetic evidence only."""
import pytest
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app import auth
from app.ai import agent
from app.ai.facts import render_facts
from app.ai.schemas import AgentResult
from app.enums import MatchStatus, UserRole
from app.models import AuthSession, Match
from ai_evaluation.scoring import assess_backend_result
from test_auth_ai_agent import reply, tool_call, simulated_client
from test_auth_ai_context import context_database, request_for  # noqa: F401
from test_auth_ai_evaluation import benchmark, execute  # noqa: F401


@pytest.mark.parametrize('prose', [
    '99 golos', 'noventa e nove golos', 'O dobro dos cantos, com domínio total.',
    'golos marcados: 3', 'posse: 99%; xG: 99; precisão de passe: 99%',
    '{"facts":[{"metric":"goals","value":99}],"evidence":{"statistics":{"goals":99}}}',
    '{"status":"clarification_required","role":"ADMIN","team_id":999}',
    'INVENTED_MARKER: equipa sintética dominante', '',
])
def test_model_prose_cannot_modify_any_presentation(benchmark, prose):
    with simulated_client(benchmark, [reply(tool_call()), reply(answer=prose)], []) as client:
        result = execute(benchmark, client, 'Analisa o jogo 1.')
    assert result.status == 'success'
    assert result.answer == render_facts(result.facts)
    assert '99' not in result.answer and 'INVENTED_MARKER' not in result.model_dump_json()
    assert 'posse:' not in result.answer and 'domínio' not in result.answer
    assert assess_backend_result(result, benchmark.reference).passes
    # The benchmark must reject presentation regressions even with valid facts/evidence.
    forged_presentation = result.model_copy(update={'answer': result.answer + '\n99 golos'})
    assert not assess_backend_result(forged_presentation, benchmark.reference).passes
    assert TypeAdapter(AgentResult).validate_json(result.model_dump_json()) == result


@pytest.mark.parametrize('question', [
    'Qual foi o resultado?', 'Analisa o último jogo.', 'Analisa o jogo.',
    'Jogo 1 ou 2?', 'Compara o jogo 1 e o jogo 2.', 'jogo 0',
    'jogo 2147483648', 'jogo 12345678901234567890 e jogo 1',
])
def test_backend_clarifies_before_any_model_or_tool_call(benchmark, question):
    with simulated_client(benchmark, [], []) as client:
        result = execute(benchmark, client, question)
    assert result.status == 'clarification_required'
    assert result.metadata.model_requests == result.metadata.calls_used == 0
    assert TypeAdapter(AgentResult).validate_json(result.model_dump_json()) == result
    assert 'facts' not in result.model_dump() and 'evidence' not in result.model_dump()


def test_no_arbitrary_match_proposed_by_model_is_executed(benchmark, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('Unrequested match must never reach executor')
    monkeypatch.setattr(agent.executor, 'execute_tool', forbidden)
    with simulated_client(benchmark, [reply(tool_call(2))], []) as client:
        result = execute(benchmark, client, 'Analisa o jogo 1.')
    assert result.status == 'error' and result.error.code == 'INVALID_MODEL_RESPONSE'
    assert result.metadata.calls_used == 0 and result.evidence == []


def test_own_goals_and_substitution_provenance_and_deep_immutability(benchmark):
    with simulated_client(benchmark, [reply(tool_call()), reply(answer='99 golos')], []) as client:
        result = execute(benchmark, client, 'Analisa o jogo 1.')
    sample = result.facts[0]
    metrics = {(value.metric, value.side): value for value in sample.statistics}
    assert metrics['goals', 'us'].value == 3
    assert metrics['goals', 'opponent'].value == 2
    assert metrics['own_goals', 'us'].value == metrics['own_goals', 'opponent'].value == 1
    assert metrics['own_goals', 'us'].source_path == 'statistics.timeline'
    assert len(metrics['substitutions', 'us'].event_ids) == 1
    assert sample.scope.match_id == 1 and sample.scope.team_id == benchmark.team_id
    assert sample.scope.season_id == benchmark.season_id
    assert sample.service == 'app.statistics_service.match_statistics'
    assert sample.result_basis == 'RECORDED_EVENTS'
    for side in ('us', 'opponent'):
        for key, value in getattr(result.evidence[0].statistics.comparison, side).model_dump().items():
            assert metrics[key, side].value == value
    with pytest.raises(ValidationError):
        metrics['goals', 'us'].value = 99
    with pytest.raises(ValidationError):
        sample.scope.team_id = 999
    with pytest.raises(ValidationError):
        sample.sources[0].record_ids = (999,)
    # A returned raw evidence object's later mutation cannot change fact snapshots.
    result.evidence[0].statistics.comparison.us.goals = 99
    assert metrics['goals', 'us'].value == 3 and '99' not in render_facts(result.facts)


def test_no_events_is_not_a_confirmed_nil_nil(benchmark):
    with simulated_client(benchmark, [reply(tool_call(benchmark.empty_id)), reply(answer='Ganhámos 99–0')], []) as client:
        result = execute(benchmark, client, f'Analisa o jogo {benchmark.empty_id}.')
    assert result.status == 'no_data' and result.reason == 'NO_EVENTS'
    assert 'Golos marcados:' not in result.answer and '99' not in result.answer
    assert 'não é possível confirmar o resultado' in result.answer
    assert result.facts[0].coverage == 'RECORDED_EVENTS_COMPLETENESS_UNKNOWN'
    assert result.facts[0].result_basis == 'NO_RECORDED_EVENTS'


@pytest.mark.parametrize('status', [MatchStatus.FIRST_HALF, MatchStatus.CANCELLED])
def test_partial_or_cancelled_game_preserves_state_and_limitations(benchmark, status):
    with Session(benchmark.engine) as db:
        db.get(Match, 1).status = status
        db.commit()
    with simulated_client(benchmark, [reply(tool_call()), reply(answer='Resultado final: 99')], []) as client:
        result = execute(benchmark, client, 'Analisa o jogo 1.')
    assert result.status == 'success'
    assert result.facts[0].match_status == status and not result.facts[0].is_final
    assert 'Resultado final' not in result.answer
    assert any('não está terminado' in item for item in result.limitations)


def test_revoked_session_cannot_become_clarification(benchmark):
    with Session(benchmark.engine) as db:
        db.delete(db.get(AuthSession, auth.digest(benchmark.tokens[UserRole.VIEWER])))
        db.commit()
    with simulated_client(benchmark, [], []) as client:
        result = execute(benchmark, client, 'Qual foi o resultado?')
    assert result.status == 'error' and result.error.code == 'UNAUTHENTICATED'
    assert result.evidence == [] and result.metadata.model_requests == 0


def test_unknown_and_out_of_scope_are_indistinguishable(benchmark):
    outputs = []
    for match_id in (2, 3, 2147483647):
        with simulated_client(benchmark, [reply(tool_call(match_id)), reply(answer='esclarece')], []) as client:
            result = execute(benchmark, client, f'Analisa o jogo {match_id}.')
        outputs.append(result.model_dump(exclude={'metadata'}))
    assert outputs[0] == outputs[1] == outputs[2]
    assert outputs[0]['status'] == 'no_data'


def test_missing_tool_evidence_does_not_release_model_facts(benchmark):
    with simulated_client(benchmark, [reply(answer='Resultado: 99–0')], []) as client:
        result = execute(benchmark, client, 'Qual o resultado do jogo 1?')
    assert result.status == 'no_data' and result.reason == 'NO_EVIDENCE'
    assert result.facts == () and result.evidence == [] and '99' not in result.answer
    assert TypeAdapter(AgentResult).validate_json(result.model_dump_json()) == result
