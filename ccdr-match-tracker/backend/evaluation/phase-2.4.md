# Fase 2.4 — factos do backend e esclarecimentos

## Arquitetura e fronteira de confiança

Ollama propõe ferramentas; o executor continua a validar argumentos, autenticar e
consultar o âmbito configurado no servidor. Só `ToolExecutionSuccess.evidence`
contribui para factos. O conteúdo livre do modelo, incluindo JSON, thinking,
nomes, valores ou pedidos de esclarecimento, nunca é utilizado na resposta final.

`app/ai/facts.py` projeta `statistics.comparison` diretamente, sem recalcular
resultados nem somar novamente autogolos. Autogolos e substituições são apenas
contagens por lado da timeline do serviço, com IDs dos eventos de origem, pois
não existem esses agregados em EventTotals. Não há alteração ao serviço existente.

`extract_facts()` cria snapshots profundamente imutáveis: tuplos e modelos frozen
para âmbito, fontes, valores e proveniência. O campo `answer` é produzido por
`render_facts()` usando apenas esses snapshots e frases fixas do servidor. Não se
faz comparação de algarismos da prosa para decidir se ela é segura: toda a prosa
do modelo é descartada, mesmo quando correta. Notas e nomes livres do backend
não são interpolados no texto apresentado.

A interpretação tática **não está implementada**. Uma futura camada terá de
possuir contrato/campo separado de `facts` e de `answer`, com proveniência e
validação próprias. Não deverá substituir os factos nem inserir prosa livre no
renderizador atual. Não existem campos vazios, segundo agente ou abstrações
antecipadas para essa camada.

## Entrada e identificação

A assinatura de `run_agent(question, *, request, engine, client, policy=None)`
mantém-se. O pedido, engine, política e autenticação continuam exclusivamente
controlados pelo servidor. Só se aceita exatamente um identificador explícito na
forma `jogo 123` (também `jogo #123`, sem distinção de maiúsculas), inteiro positivo
até 2147483647. Referências múltiplas/ambíguas reconhecidas, formatos não suportados,
nomes, datas e «último jogo» pedem esclarecimento antes de qualquer inferência.

Não se pretende interpretar toda a linguagem natural por expressões regulares.
A gramática deliberadamente limitada evita a escolha de um jogo pelo LLM. Uma
proposta para um ID diferente do identificado termina em INVALID_MODEL_RESPONSE,
antes de executar a ferramenta. Isto restringe a seleção, não concede acesso:
o executor reautentica e verifica o âmbito em todas as chamadas admitidas.

## Contrato de saída (união discriminada por status)

| status | Campos principais | Decisão do servidor |
| --- | --- | --- |
| success | answer, facts, evidence, limitations, tool_errors, metadata | Há eventos registados e evidência autorizada |
| clarification_required | reason, answer fixo, metadata | Falta exatamente um identificador suportado |
| no_data | reason, answer, facts/evidence opcionais, limitations, tool_errors, metadata | Jogo não encontrado, sem eventos, sem evidências ou métricas explicitamente indisponíveis |
| error | error, evidence vazia, tool_errors sanitizados, metadata | Autenticação, autorização, transporte, proposta inválida ou limites |

`no_data.reason`: NOT_FOUND, NO_EVENTS, NO_EVIDENCE, UNSUPPORTED_METRICS.
Sem evidências, propostas desconhecidas/inválidas são erro, nunca esclarecimento.
Falhas recuperáveis podem continuar a ser corrigidas dentro dos limites existentes.
NOT_FOUND não distingue ausência do jogo de outro âmbito: mesmos campos e texto,
sem IDs ou evidências, excetuando metadados de execução.

`AgentSuccess` e `AgentNoData` declaram
`factual_validation="BACKEND_EVIDENCE_PROJECTION"`. Significa fidelidade aos
registos devolvidos pelo backend, **não** verificação da realidade do jogo ou da
completude. `NO_EVIDENCE` deixou de ser um erro do agente e é razão de `no_data`;
`EMPTY_RESPONSE` deixou de existir: conteúdo textual vazio com protocolo válido
não impede a apresentação dos factos. Respostas de protocolo incompletas/truncadas
continuam a ser erros. Alterações circunscritas ao contrato Python de IA; não há
contratos HTTP novos ou modificados.

Cada `VerifiedMatchFacts` tem:

- scope: match_id, team_id, season_id, events e perspective;
- queried_at, service e sources com entidades e IDs;
- match_status e is_final diretamente do serviço;
- coverage=RECORDED_EVENTS_COMPLETENESS_UNKNOWN;
- result_basis=RECORDED_EVENTS ou NO_RECORDED_EVENTS;
- statistics: métrica, lado, valor, source_path e IDs quando derivados da timeline;
- limitations provenientes da ferramenta.

Todos os valores representam registos. Zero contagens não prova ausência de ações.
Sem eventos, `answer` apresenta apenas o total de eventos e o aviso de ausência de
resultado observável, nunca «resultado 0–0». Os factos tipados preservam os zeros
dos agregados com result_basis=NO_RECORDED_EVENTS e coverage explícitos: consumidores
futuros não devem apresentá-los como resultado confirmado. Estados parciais e
cancelados e respetivas limitações são preservados. Não há extrapolação competitiva.

## Exemplos abreviados (fixtures sintéticas)

```json
{
  "status": "success",
  "factual_validation": "BACKEND_EVIDENCE_PROJECTION",
  "facts": [{
    "scope": {"match_id": 1, "team_id": 2, "season_id": 2,
              "events": "ALL_RECORDED_MATCH_EVENTS", "perspective": "MATCH_TEAM"},
    "match_status": "FINISHED",
    "is_final": true,
    "coverage": "RECORDED_EVENTS_COMPLETENESS_UNKNOWN",
    "result_basis": "RECORDED_EVENTS",
    "statistics": [{"metric": "goals", "side": "us", "value": 3,
                    "source_path": "statistics.comparison.us.goals", "event_ids": []}]
  }]
}
```

O exemplo omite outros valores, evidências, fontes, data, limitações e metadados.
A fixture preserva resultado derivado 3–2, incluindo um autogolo por lado. O texto
renderizado inclui `Golos marcados: 3` e `Golos sofridos: 2`, mesmo que o modelo
tenha proposto «99 golos», «noventa e nove» ou JSON com valores falsos.

```json
{
  "status": "clarification_required",
  "reason": "MATCH_IDENTIFICATION_REQUIRED",
  "answer": "Indique o identificador do jogo no formato «jogo 123». É necessário identificar exatamente um jogo."
}
```

Metadados omitidos. O esclarecimento não consulta jogos nem contacta o modelo e
só é devolvido após autenticação e validação do contexto configurado. Uma sessão
revogada ou CSRF inválido permanece error; a prosa do modelo nunca altera o estado.

## Segurança e limitações

Mantêm-se o registo único, leitura exclusiva, orçamento partilhado, CSRF/Origin,
reautenticação antes da inferência, em cada chamada admitida e antes da resposta
final. Todas as sessões próprias fecham antes de HTTP. Falhas fatais descartam
as evidências acumuladas. Nenhum dado de sessão é incluído nas mensagens do modelo.

A ferramenta é ainda uma consulta geral: apresenta todos os agregados disponíveis,
sem seleção semântica de métricas. A deteção de xG, posse e precisão de passe é
conservadora por palavras-chave no pedido; pedidos mistos recebem no_data com
razão UNSUPPORTED_METRICS e também os factos disponíveis. Não é um classificador
completo de perguntas. Outras métricas indisponíveis não são inventadas: o backend
apenas renderiza o seu vocabulário fixo. Múltiplos jogos e identificação por data,
adversário ou contexto de conversa precisam de fases futuras.

As evidências brutas mantêm o contrato anterior e podem conter notas/nomes livres
registados. Não constituem texto validado para apresentação. Consumidores futuros
devem renderizar `facts`/`answer`; não devem transformar notas em factos verificados.

O ciclo ainda pode fazer uma chamada terminal ao modelo depois das ferramentas;
o conteúdo é descartado. Rondas, chamadas, autenticação e prazos mantêm-se. Não há
cancelamento forçado de operações já bloqueadas. A qualidade de seleção real de
ferramentas continua por medir com Ollama disponível; nenhum teste simulado
constitui validação de um modelo real.

## Avaliação e regressões

O benchmark mantém as referências de `match_statistics()` e agora verifica os
factos tipados contra essas referências e a igualdade com o renderizador controlado.
O avaliador antigo de prosa permanece apenas como teste negativo, não como barreira
de segurança da aplicação. O caso «99 golos» passou de demonstrar uma falha para
exigir ausência desse texto e valores corretos no resultado final.

`test_auth_ai_verified_facts.py` cobre prosa/JSON falsos, valores corretos,
autogolos, proveniência, imutabilidade, ausência de eventos, estados parciais e
cancelados, esclarecimentos, proposta de jogo arbitrário, ausência de evidências,
revogação e indistinguibilidade entre jogo inexistente e fora do âmbito.

Usar as instruções de PostgreSQL descartável do README e incluir o novo ficheiro
na seleção de testes. Não executar Alembic. O teste real mantém o opt-in anterior
e fica ignorado por omissão. Resultados da Fase 2.3 em simulated-results.json são
históricos; o artefacto atual é phase-2.4-simulated-results.json.

Execução desta fase: **353 testes aprovados, 1 ignorado**, em 27,89 s. O ignorado
é o benchmark opcional com Ollama real, sem opt-in. Os sete cenários simulados
mantêm dez valores de referência corretos, duas chamadas ao modelo e uma chamada
à ferramenta por caso; duração individual aproximada de 23–29 ms, sem inferência
real. As 25 verificações novas incluem nove variantes de conteúdo terminal do
modelo. Depois da regressão, essas nove variantes foram repetidas com uma asserção
adicional: adulterar apenas a apresentação final com «99 golos», preservando
factos e evidências válidos, tem de ser rejeitado pelo benchmark. As nove passaram.
Existe um aviso de depreciação Starlette/httpx já anterior a esta fase.

Todas as execuções usaram PostgreSQL descartável com dados sintéticos e HTTP
simulado. No fim havia zero schemas temporários roster_test_* e o cluster foi
parado. Não foram executadas migrações, endpoints, alterações de frontend,
commits ou deployments. Ollama real não foi contactado nem validado nesta fase.

Próximo passo: executar o benchmark real de seleção de ferramentas quando Ollama
estiver disponível e rever o contrato de consumo dos factos antes de criar uma API.
A interpretação tática continua adiada e separada por desenho.
