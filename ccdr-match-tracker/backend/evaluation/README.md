# Avaliação factual — Fase 2.3

**Atualização:** a Fase 2.4 corrige a apresentação de prosa livre e os
esclarecimentos. Consultar [contrato e metodologia atuais](phase-2.4.md).
Os resultados e problemas descritos abaixo referem-se à Fase 2.3.

O benchmark está em `tests/test_auth_ai_evaluation.py`; o avaliador em
`tests/ai_evaluation/scoring.py`. Não altera o agente nem serviços de negócio.
Usa sessões reais sintéticas, o executor existente e PostgreSQL com schemas
aleatórios criados por `Base.metadata.create_all`. Não executa Alembic.

## Referências e critérios

As referências são projetadas de `statistics_service.match_statistics()`. Só os
contadores de autogolos e substituições são contados na timeline devolvida pelo
serviço, pois não existem esses agregados no contrato. Há uma verificação fixa
independente dos valores da fixture para detetar alterações de semântica.

| Pergunta sintética | Referência |
| --- | --- |
| Resultado do jogo 1 | 3–2, perspetiva da equipa |
| Golos marcados e sofridos no jogo 1 | 3 e 2 |
| Autogolos da equipa no jogo 1 | 1; existe também 1 autogolo adversário |
| Cartões da equipa no jogo 1 | 2 amarelos, 1 vermelho |
| Substituições da equipa no jogo 1 | 1 registada |
| Cantos da equipa no jogo 1 | 4 |
| Eventos no jogo autorizado vazio | 0 registos; não prova ausência de ações |
| Jogo inexistente ou de outra equipa/época | NOT_FOUND indistinguível, nenhuma evidência |
| xG, posse e precisão de passe | Indisponíveis; nenhum valor fundamentado |
| Resultado sem identificação do jogo | Nenhuma consulta presumida; atualmente NO_EVIDENCE |
| Injeção de team_id, season_id, role, permissions, engine | INVALID_ARGUMENTS |

As fixtures incluem dois golos normais da equipa, um adversário e um autogolo
por lado. Os 13 eventos têm tempos determinísticos. Dados pessoais e notas não
são enviados ao modelo. As credenciais sintéticas ficam exclusivamente no pedido
autenticado, nunca nas mensagens HTTP do Ollama.

A avaliação separa seleção da ferramenta, argumentos, evidências, números,
limitações, estrutura em português, latência e contadores. O avaliador numérico
aceita apenas afirmações completas `métrica: inteiro` no vocabulário de referência.
Números em frases não reconhecidas e números por extenso exigem revisão. Valores
errados, métricas numéricas desconhecidas e omissões impedem aprovação numérica.
Não se utiliza outro LLM como juiz.

**Não é um verificador geral de linguagem natural.** Afirmações sem números,
causalidade, clareza e português europeu precisam de revisão humana. O teste da
estrutura Factos/Interpretação/Hipóteses/Limitações é apenas um indicador mecânico,
não uma nota de qualidade linguística. A aprovação do harness não implica a
aprovação factual de uma resposta livre nem os objetivos de qualidade do modelo.

## Execução segura e reproduzível

Usar um ambiente Python com `requirements-dev.txt` e **um cluster PostgreSQL
novo, descartável, separado de qualquer base existente**. Nunca reutilizar
DATABASE_URL de produção. Exemplo macOS/Linux, ajustando PATH para PostgreSQL:

```sh
TASK_PG=$(mktemp -d /tmp/match-tracker-eval.XXXXXX)
initdb -D "$TASK_PG/data" -A trust --no-locale -E UTF8
pg_ctl -D "$TASK_PG/data" -l "$TASK_PG/server.log" -o "-h '' -k $TASK_PG -p 55439 -c max_locks_per_transaction=512" -w start
createdb -h "$TASK_PG" -p 55439 ai_tools_test
export DATABASE_URL="postgresql+psycopg:///ai_tools_test?host=$TASK_PG&port=55439"
export TEST_DATABASE_URL="$DATABASE_URL"
export APP_ENV=development AUTH_COOKIE_SECURE=false AUTH_COOKIE_SAMESITE=lax AUTH_DEBUG_LOGGING=false
export CORS_ORIGINS='["http://localhost:3000","http://127.0.0.1:3000"]'
cd backend
AI_EVALUATION_REPORT=/tmp/match-tracker-simulated-evaluation.json python -m pytest -q -p no:cacheprovider tests/test_auth_ai_evaluation.py -k 'not real_ollama'
# No fim, inclusive se houver falhas:
pg_ctl -D "$TASK_PG/data" -m fast -w stop
```

O fixture genérico aceita TEST_DATABASE_URL: a responsabilidade de apontar para
este cluster descartável é de quem executa. Não apontar para bases existentes.
Os schemas são eliminados no teardown. Nenhum teste real é iniciado por omissão.

### Ollama real, opcional

Com o mesmo PostgreSQL descartável em execução:

```sh
AI_EVALUATION_REAL=1 AI_EVALUATION_REAL_REPORT=/tmp/match-tracker-real-evaluation.json \
python -m pytest -q -rs -p no:cacheprovider tests/test_auth_ai_evaluation.py::test_real_ollama_benchmark
```

Só aceita servidor loopback. Consulta /api/version e /api/tags antes da inferência;
não instala modelos nem inicia serviços. Avalia três perguntas por modelo instalado
entre o configurado e qwen3:8b/qwen3:4b, sem duplicações. Usa configuração existente,
sem streaming e orçamento de 60 segundos por análise. As chamadas HTTP têm os
limites reais do cliente; o orçamento não cancela uma operação já bloqueada.

O relatório real inclui versão, digest, configuração, seleção/argumentos corretos,
IDs das evidências, erros, duração, rondas e chamadas. /api/ps permite uma fotografia
de size/size_vram depois da inferência; não mede pico de RAM nem memória exclusiva
do processo. O relatório não inclui tokens de sessão nem texto bruto do modelo.
O teste pode passar com resultados de qualidade negativos: consultar o relatório.
Respostas livres não reconhecidas pelo avaliador requerem anotação humana antes
de calcular precisão factual. Não confundir casos sem números avaliáveis com 100%.

## Resultados desta execução

O artefacto `simulated-results.json` contém sete casos simulados, dez afirmações
numéricas corretas, sete seleções/argumentos programados corretos, duas chamadas
ao modelo e uma ferramenta por caso. Duração por análise: aproximadamente
19–31 ms nesta máquina; inclui HTTP simulado, não estima inferência real.

Os restantes testes exercitam respostas adversariais, métricas indisponíveis,
âmbito e injeção. As regressões existentes cobrem adicionalmente ferramentas
inexistentes, autenticação, CSRF, revogação, budgets e transporte.

Execução ampla: 325 aprovados e 1 ignorado. Após acrescentar três casos,
execução final do benchmark: 21 aprovados e 1 ignorado, com opt-in real ativo;
o motivo do skip foi servidor local indisponível. Um aviso de depreciação
Starlette/httpx já existente. Os três casos acrescentados cobrem métricas
indisponíveis num jogo identificado, aceitação pelo agente de texto falso com
evidência válida e rejeição de ferramenta desconhecida. Os dois jogos fora do
âmbito, cinco argumentos proibidos e ferramenta desconhecida foram rejeitados
em todos os casos. São controlos determinísticos, não taxas de resistência
de um modelo real a ataques em linguagem natural.

Todos os testes usaram o cluster descartável via Unix socket, separado da base
da aplicação. No final havia zero schemas roster_test_* e o cluster foi parado.
Nenhum ficheiro da aplicação ou dependência foi alterado nesta fase.

Ollama real **não validado**: GET a 127.0.0.1:11434 em /api/version, /api/tags e
/api/ps falhou com ConnectError, incluindo confirmação fora da sandbox. CLI ollama
não encontrado. Configuração efetiva: localhost:11434, qwen3:8b, think=false,
timeout HTTP 180 s, conexão 5 s, resposta máxima 1 MiB. Não foi possível confirmar
modelos instalados, versão, consumo de memória, desempenho ou taxa de sucesso real.
Nenhum modelo descarregado, processo alterado ou credencial enviada.

## Problemas e próximos passos

O agente aceita texto incorreto quando acompanha evidência válida: a avaliação
deteta alguns casos, mas não impõe validação factual em produção. NO_EVIDENCE
elimina também pedidos legítimos de esclarecimento e respostas sobre ausência de
dados. Recomenda-se um contrato explícito de esclarecimento/indisponibilidade e
factos estruturados verificáveis antes de expor uma API, mediante aprovação dessa
alteração de contrato. Não foram alterados esses comportamentos nesta fase.

Executar o benchmark real quando houver servidor e modelos disponíveis; rever
manualmente texto livre, negações de métricas indisponíveis, causalidade e PT-PT.
Só depois calcular os objetivos >=90% de seleção e 100% de valores avaliados,
sem extrapolar para casos não avaliados. Adiar endpoints e frontend até essa revisão.
