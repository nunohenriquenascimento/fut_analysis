"""Backend-only evidence projection and deterministic presentation.

No LLM string, name, note or generated JSON contributes to displayed facts/text.
Verification means faithful extraction from authorized recorded evidence, not
proof of real-world completeness. No scoring formula is reimplemented here.
"""
from app.ai.schemas import (
    AgentMetadata, AgentNoData, AgentSuccess, MatchStatisticsEvidence,
    ToolExecutionError, VerifiedEvidenceScope, VerifiedMatchFacts, VerifiedSource,
    VerifiedStatistic,
)

_LABELS = {
    'goals': ('Golos marcados', 'Golos sofridos'),
    'shots_on_target': ('Remates à baliza da equipa', 'Remates à baliza do adversário'),
    'shots_off_target': ('Remates fora da equipa', 'Remates fora do adversário'),
    'shots_blocked': ('Remates bloqueados da equipa', 'Remates bloqueados do adversário'),
    'shots_total': ('Remates totais da equipa', 'Remates totais do adversário'),
    'corners': ('Cantos da equipa', 'Cantos do adversário'),
    'free_kicks': ('Livres da equipa', 'Livres do adversário'),
    'fouls': ('Faltas da equipa', 'Faltas do adversário'),
    'offsides': ('Foras de jogo da equipa', 'Foras de jogo do adversário'),
    'penalties': ('Penáltis da equipa', 'Penáltis do adversário'),
    'yellow_cards': ('Amarelos da equipa', 'Amarelos do adversário'),
    'red_cards': ('Vermelhos da equipa', 'Vermelhos do adversário'),
    'saves': ('Defesas da equipa', 'Defesas do adversário'),
    'own_goals': ('Autogolos da equipa', 'Autogolos do adversário'),
    'substitutions': ('Substituições da equipa', 'Substituições do adversário'),
}
_STATUS = {
    'SCHEDULED': 'agendado', 'FIRST_HALF': 'primeira parte', 'HALF_TIME': 'intervalo',
    'SECOND_HALF': 'segunda parte', 'FINISHED': 'terminado', 'CANCELLED': 'cancelado',
}


def extract_facts(evidence: MatchStatisticsEvidence) -> VerifiedMatchFacts:
    stats = evidence.statistics
    values = [VerifiedStatistic(metric='total_events', side='match', value=stats.total_events,
                               source_path='statistics.total_events')]
    for side, event_team in [('us', 'US'), ('opponent', 'OPPONENT')]:
        totals = getattr(stats.comparison, side)
        for metric, value in totals.model_dump().items():
            values.append(VerifiedStatistic(metric=metric, side=side, value=value,
                                            source_path=f'statistics.comparison.{side}.{metric}'))
        # These aggregates are absent from EventTotals: project the service timeline.
        # In particular, never add own goals to the service's score a second time.
        for metric, kind in [('own_goals', 'OWN_GOAL'), ('substitutions', 'SUBSTITUTION')]:
            ids = tuple(event.id for event in stats.timeline
                        if event.event_type == kind and event.team == event_team)
            values.append(VerifiedStatistic(metric=metric, side=side, value=len(ids),
                                            source_path='statistics.timeline', event_ids=ids))
    return VerifiedMatchFacts(
        scope=VerifiedEvidenceScope(**evidence.scope.model_dump()),
        queried_at=evidence.queried_at, service=evidence.service,
        sources=tuple(VerifiedSource(entity=s.entity, record_ids=tuple(s.record_ids)) for s in evidence.sources),
        match_status=stats.match.status, is_final=stats.is_final,
        result_basis="RECORDED_EVENTS" if stats.total_events else "NO_RECORDED_EVENTS",
        statistics=tuple(values),
        limitations=tuple(item.description for item in evidence.limitations),
    )


def render_facts(facts: tuple[VerifiedMatchFacts, ...]) -> str:
    sections = []
    for sample in facts:
        lines = [f'Jogo {sample.scope.match_id} — estado: {_STATUS[sample.match_status]}.',
                 'Factos — valores derivados dos eventos registados.']
        total = next(value.value for value in sample.statistics if value.metric == 'total_events')
        for value in sample.statistics:
            if value.metric == 'total_events':
                lines.append(f'Eventos registados: {value.value}')
            elif total:
                label = _LABELS[value.metric][0 if value.side == 'us' else 1]
                lines.append(f'{label}: {value.value}')
        if not total:
            lines.append('Sem eventos registados; não é possível confirmar o resultado nem a ausência de ações.')
        lines.append('Limitações')
        lines.extend(sample.limitations)
        sections.append('\n'.join(lines))
    return '\n\n'.join(sections)


def build_response(evidence: list[MatchStatisticsEvidence], errors: list[ToolExecutionError],
                   metadata: AgentMetadata, *, unsupported_metrics: bool = False) -> AgentSuccess | AgentNoData | None:
    facts = tuple(extract_facts(sample) for sample in evidence)
    limitations = list(dict.fromkeys(item for sample in facts for item in sample.limitations))
    limitations.append('Os factos são uma projeção dos registos do backend; não foi produzida interpretação tática.')
    if errors:
        limitations.append('Algumas consultas falharam e não constituem evidência.')
    if not evidence:
        reason = 'NOT_FOUND' if any(e.code == 'NOT_FOUND' for e in errors) else 'NO_EVIDENCE'
        if errors and reason != 'NOT_FOUND':
            # Invalid/unknown proposals are execution failures, never clarifications.
            return None
        return AgentNoData(reason=reason, answer='Não foi possível obter dados para o jogo indicado.',
                           tool_errors=errors, metadata=metadata, limitations=limitations)
    answer = render_facts(facts)
    if unsupported_metrics or all(sample.statistics.total_events == 0 for sample in evidence):
        reason = 'UNSUPPORTED_METRICS' if unsupported_metrics else 'NO_EVENTS'
        if unsupported_metrics:
            answer = 'xG, posse de bola e precisão de passe não estão disponíveis.\n\n' + answer
        return AgentNoData(reason=reason, answer=answer, facts=facts, evidence=evidence,
                           tool_errors=errors, limitations=limitations, metadata=metadata)
    return AgentSuccess(answer=answer, facts=facts, evidence=evidence, tool_errors=errors,
                        limitations=limitations, metadata=metadata)
