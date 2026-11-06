"""Conservative, deterministic factual checks, not a natural-language verifier.

Only labelled integer claims in the evaluation vocabulary are scored. Any other
numeric sentence requires human review. Passing these checks never proves that
all prose is supported or that Portuguese style is adequate.
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Assessment:
    correct: int
    incorrect: int
    missing: tuple[str, ...]
    review_sentences: tuple[str, ...]
    limitations_present: bool
    portuguese_structure: bool

    @property
    def passes(self):
        return (self.correct > 0 and not self.incorrect and not self.missing
                and not self.review_sentences and self.limitations_present)


def assess(answer: str, expected: dict[str, int]) -> Assessment:
    """Match complete labelled claims, refusing partial/substring validation."""
    correct = incorrect = 0
    seen, review = set(), []
    for sentence in re.split(r'[\n;.!?]+', answer.casefold()):
        sentence = sentence.strip()
        if not sentence:
            continue
        match = re.fullmatch(r'([^:=]+)\s*[:=]\s*(\d+)', sentence)
        if match and match[1].strip() in expected:
            key, value = match[1].strip(), int(match[2])
            seen.add(key)
            if value == expected[key]:
                correct += 1
            else:
                incorrect += 1
        elif re.search(r'\d|\b(um|uma|dois|duas|três|quatro|cinco|seis|sete|oito|nove|dez|zero)\b', sentence):
            review.append(sentence)
        # Unsupported nonnumeric factual claims also require manual review:
        # this checker deliberately makes no all-prose validation assertion.
    return Assessment(correct, incorrect, tuple(sorted(set(expected) - seen)), tuple(review),
                      'limitações' in answer.casefold(),
                      all(label in answer.casefold() for label in
                          ('factos', 'interpretação', 'hipóteses', 'limitações')))


def reference(statistics) -> dict[str, int]:
    """Project service output; never recalculate score or statistical totals."""
    return {
        'golos marcados': statistics.comparison.us.goals,
        'golos sofridos': statistics.comparison.opponent.goals,
        'cantos da equipa': statistics.comparison.us.corners,
        'amarelos da equipa': statistics.comparison.us.yellow_cards,
        'vermelhos da equipa': statistics.comparison.us.red_cards,
        'autogolos da equipa': sum(e.event_type == 'OWN_GOAL' and e.team == 'US' for e in statistics.timeline),
        'substituições da equipa': sum(e.event_type == 'SUBSTITUTION' and e.team == 'US' for e in statistics.timeline),
        'eventos registados': statistics.total_events,
    }


def assess_backend_result(result, expected: dict[str, int]) -> Assessment:
    """Evaluate typed backend facts AND exact backend rendering, never LLM prose.

    This establishes provenance for the controlled renderer only; it is not an
    attempt to validate arbitrary language using numeric substring matching.
    """
    from app.ai.facts import render_facts
    mapping = {
        'golos marcados': ('goals', 'us'), 'golos sofridos': ('goals', 'opponent'),
        'cantos da equipa': ('corners', 'us'), 'amarelos da equipa': ('yellow_cards', 'us'),
        'vermelhos da equipa': ('red_cards', 'us'), 'autogolos da equipa': ('own_goals', 'us'),
        'substituições da equipa': ('substitutions', 'us'), 'eventos registados': ('total_events', 'match'),
    }
    if result.status not in {'success', 'no_data'} or len(result.facts) != 1:
        return Assessment(0, 0, tuple(expected), ('No unique backend facts',), False, False)
    actual = {(item.metric, item.side): item.value for item in result.facts[0].statistics}
    missing = tuple(key for key in expected if mapping.get(key) not in actual)
    correct = sum(actual.get(mapping.get(key)) == value for key, value in expected.items())
    incorrect = len(expected) - correct - len(missing)
    rendered = render_facts(result.facts)
    if result.status == 'no_data' and result.reason == 'UNSUPPORTED_METRICS':
        rendered = 'xG, posse de bola e precisão de passe não estão disponíveis.\n\n' + rendered
    review = () if result.answer == rendered else ('Output differs from controlled renderer',)
    return Assessment(correct, incorrect, missing, review, bool(result.limitations),
                      'Factos' in result.answer and 'Limitações' in result.answer)
