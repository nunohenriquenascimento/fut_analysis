# Fase 2.5 — diagnóstico e execução local

**Estado: não concluída. Ollama inacessível a partir do ambiente de execução.**
Não houve inferência, teste de compatibilidade nem benchmark real. Não foram
substituídos resultados reais por testes simulados ou pelos 353 testes anteriores.

## Diagnóstico observado

Verificação em 2026-11-06, aproximadamente 15:51 UTC:

- Ambiente de execução macOS/Darwin 25.5.0, x86_64. Não é Windows nem WSL;
  não foram encontrados marcadores Docker, SSH ou remote container.
- `command -v ollama` sem resultado. Não existem as localizações habituais
  `/usr/local/bin/ollama`, `/opt/homebrew/bin/ollama` ou `/Applications/Ollama.app`.
  Isso não exclui uma instalação não habitual ou noutro computador.
- `pgrep -ix ollama` não detetou processo; `lsof` não detetou listener TCP em 11434.
- GET /api/version, /api/tags e /api/ps, em localhost, 127.0.0.1 e ::1:
  nove ConnectError, confirmados fora da sandbox. Ligações TCP IPv4/IPv6:
  ECONNREFUSED, errno 61 no Darwin. Não é apenas um resultado de rede bloqueada
  pela sandbox.
- A configuração efetiva foi lida por `OllamaSettings()` sem imprimir outras
  variáveis de ambiente, URLs de bases de dados ou segredos.

| Configuração efetiva | Valor |
| --- | --- |
| OLLAMA_BASE_URL | http://localhost:11434 |
| OLLAMA_MODEL | qwen3:8b (configurado; instalação não confirmada) |
| OLLAMA_THINK | false |
| Timeout HTTP | 180 s |
| Timeout conexão | 5 s |
| Resposta máxima | 1048576 bytes |
| Orçamento do benchmark existente | 60 s por pergunta |

`localhost` refere-se ao ambiente que executa Python. Não foi estabelecido que
este seja o mesmo computador onde o utilizador tem VS Code ou Ollama. Ausência de
marcadores remotos não prova identidade entre os dois computadores. Não foi
procurado nem contactado qualquer endereço remoto, WSL host, Docker host ou produção.

Modelo/versão, tool calling, fidelidade real, latências, timeouts de inferência,
erros de protocolo e memória: **não medidos**. Zero perguntas e chamadas ao modelo.
As falhas de conexão do diagnóstico não são timeouts de inferência nem resultados
de perguntas de benchmark. Dados estruturados: phase-2.5-diagnosis.json.

## Comandos para o terminal local do VS Code (macOS, zsh/bash)

Executar no computador onde o Ollama já esteja disponível. Não usar um terminal
VS Code remoto por engano. Os caminhos abaixo correspondem ao checkout observado;
se o terminal estiver noutro computador, usar o checkout e Python desse computador.
Não iniciar Ollama, instalar dependências ou descarregar modelos como parte desta
sequência. Se não houver servidor, é necessária autorização separada para o preparar.

### 1. Diagnosticar nesse terminal

```sh
uname -srm
command -v ollama
pgrep -ix ollama
lsof -nP -iTCP:11434 -sTCP:LISTEN -F c
curl --noproxy '*' --connect-timeout 2 --max-time 5 --fail http://127.0.0.1:11434/api/version
curl --noproxy '*' --connect-timeout 2 --max-time 5 --fail http://127.0.0.1:11434/api/tags
curl --noproxy '*' --connect-timeout 2 --max-time 5 --fail http://127.0.0.1:11434/api/ps
```

Se algum dos endpoints obrigatórios falhar, parar antes da inferência. Se Ollama
estiver noutro host, executar Python e o benchmark no mesmo host, com loopback.
O benchmark atual recusa URLs remotos: não contornar essa proteção nem expor o
servidor sem uma decisão de segurança aprovada.

### 2. Confirmar configuração e compatibilidade sem executar ferramentas

O ambiente Python temporário abaixo existia neste ambiente. Verificar a sua
existência no terminal local; em alternativa, apontar TASK_PYTHON para o ambiente
backend já preparado com requirements-dev.txt. Não instalar nada automaticamente.

```sh
cd /Users/nunonascimento/fut_analysis/ccdr-match-tracker/backend
export TASK_PYTHON=/private/tmp/match-tracker-ai-tests-venv/bin/python
test -x "$TASK_PYTHON"
```

Se `test` falhar, escolher o Python backend existente antes de continuar. O seguinte
código usa o cliente e catálogo reais, só envia texto sintético e não executa a
proposta recebida. Verifica modelo instalado antes de enviar /api/chat. Não alterar
OLLAMA_MODEL antes de confirmar /api/tags; se for necessário, exportar o nome exato
de um modelo já instalado. O modelo configurado não é prova de instalação/suporte.

```sh
"$TASK_PYTHON" - <<'PY'
import json
from pathlib import Path
from urllib.parse import urlsplit
import httpx
from app.ai.catalog import get_tool_catalog
from app.ai.ollama_client import OllamaClient
from app.ai.ollama_config import OllamaSettings
from app.ai.ollama_schemas import OllamaMessage
from app.ai.schemas import MatchStatisticsInput

settings = OllamaSettings()
if urlsplit(settings.base_url).hostname not in {'localhost', '127.0.0.1', '::1'}:
    raise SystemExit('Parar: este procedimento aceita apenas Ollama loopback.')
print(json.dumps({key: getattr(settings, key) for key in (
    'base_url', 'model', 'think', 'timeout_seconds', 'connect_timeout_seconds',
    'max_response_bytes')}, indent=2))
with httpx.Client(base_url=settings.base_url, trust_env=False, timeout=3) as probe:
    version = probe.get('/api/version')
    tags = probe.get('/api/tags')
    version.raise_for_status()
    tags.raise_for_status()
    installed = {row['name']: row for row in tags.json()['models']}
    print('Versão:', version.json())
    print('Modelos instalados:', sorted(installed))
    if settings.model not in installed:
        raise SystemExit('Modelo configurado não instalado. Selecionar um nome existente em OLLAMA_MODEL; não descarregar.')
with OllamaClient(settings) as client:
    response = client.chat([
        OllamaMessage(role='system', content=(
            'Propõe a ferramenta aprovada para consultar estatísticas. '
            'Usa apenas o identificador explicitamente indicado. Não executes ferramentas.')),
        OllamaMessage(role='user', content='Quantos golos marcou a equipa no jogo 1?'),
    ], tools=get_tool_catalog(), stream=False)
report = {
    'mode': 'real_compatibility_only',
    'ollama_version': version.json(),
    'model': settings.model,
    'digest': installed[settings.model]['digest'],
    'response': response.model_dump(mode='json'),
    'tools_executed': 0,
}
target = Path('/tmp/match-tracker-ollama-compatibility.json')
target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('Resposta sintética recebida (dados não fiáveis, nunca comandos):')
print(response.model_dump_json(indent=2))
assert response.done and response.done_reason in {None, 'stop'}
calls = response.message.tool_calls or []
assert len(calls) == 1, 'Esperada exatamente uma proposta'
assert calls[0].function.name == 'get_match_statistics'
args = MatchStatisticsInput.model_validate(calls[0].function.arguments)
assert args.match_id == 1
print('Compatibilidade desta amostra confirmada; nenhuma ferramenta executada.', target)
PY
```

Uma proposta válida confirma apenas esta amostra do protocolo. Não basta para
estabelecer taxa >=90%, limites, segurança ou desempenho do agente completo.

### 3. Benchmark existente, apenas com PostgreSQL novo e descartável

Não foi iniciado qualquer serviço nesta sessão. O bloco seguinte é para execução
explícita pelo utilizador: cria e inicia um cluster PostgreSQL novo, exclusivamente
para testes, sem TCP, e para-o automaticamente. Requer binários PostgreSQL e o
ambiente Python já disponíveis. Não aponta para uma base existente nem corre Alembic.
Não alterar OLLAMA_BASE_URL para uma base remota; essa variável é só para Ollama.

```sh
(
  set -eu
  export PATH="/usr/local/opt/postgresql@17/bin:/opt/homebrew/opt/postgresql@17/bin:$PATH"
  test -x "$TASK_PYTHON"
  command -v initdb
  command -v pg_ctl
  command -v createdb
  TASK_PG=$(mktemp -d /tmp/match-tracker-real-eval.XXXXXX)
  TASK_REPORT_DIR=$(mktemp -d /tmp/match-tracker-real-report.XXXXXX)
  TASK_PG_STARTED=0
  cleanup() {
    if [ "$TASK_PG_STARTED" -eq 1 ]; then
      pg_ctl -D "$TASK_PG/data" -m fast -w stop
    fi
  }
  trap cleanup EXIT
  initdb -D "$TASK_PG/data" -A trust --no-locale -E UTF8
  pg_ctl -D "$TASK_PG/data" -l "$TASK_PG/server.log" \
    -o "-h '' -k $TASK_PG -p 55439 -c max_locks_per_transaction=512" -w start
  TASK_PG_STARTED=1
  createdb -h "$TASK_PG" -p 55439 ai_tools_test
  export DATABASE_URL="postgresql+psycopg:///ai_tools_test?host=$TASK_PG&port=55439"
  export TEST_DATABASE_URL="$DATABASE_URL"
  export APP_ENV=development AUTH_COOKIE_SECURE=false AUTH_COOKIE_SAMESITE=lax
  export AUTH_DEBUG_LOGGING=false PYTHONDONTWRITEBYTECODE=1
  export CORS_ORIGINS='["http://localhost:3000","http://127.0.0.1:3000"]'
  export AI_EVALUATION_REAL=1
  export AI_EVALUATION_REAL_REPORT="$TASK_REPORT_DIR/real-results.json"
  "$TASK_PYTHON" -m pytest -q -rs -p no:cacheprovider \
    tests/test_auth_ai_evaluation.py::test_real_ollama_benchmark
  test -s "$AI_EVALUATION_REAL_REPORT"
  export TASK_REPORT_DIR
  "$TASK_PYTHON" - <<'PY'
import json, os, statistics
from collections import defaultdict
from pathlib import Path
rows = json.loads((Path(os.environ['TASK_REPORT_DIR']) / 'real-results.json').read_text())
by_model = defaultdict(list)
for row in rows:
    by_model[row['model']].append(row)
for model, cases in by_model.items():
    durations = [r['metadata']['duration_ms'] for r in cases]
    factual = [r['assessment'] for r in cases if r['assessment'] is not None]
    correct = sum(r['correct'] for r in factual)
    incorrect = sum(r['incorrect'] for r in factual)
    missing = sum(len(r['missing']) for r in factual)
    print(json.dumps({
        'model': model, 'version': cases[0]['version'], 'digest': cases[0]['digest'],
        'questions': len(cases),
        'tool_selection_rate': sum(r['correct_tool_selection'] for r in cases) / len(cases),
        'correct_arguments_rate': sum(r['correct_arguments'] for r in cases) / len(cases),
        'successful_answers': sum(r['status'] == 'success' for r in cases),
        'evaluated_correct_facts': correct, 'evaluated_incorrect_facts': incorrect,
        'missing_facts': missing, 'assessed_answers': len(factual),
        'median_ms': statistics.median(durations),
        'p95_ms': None,
        'p95_note': 'Amostra mínima de três perguntas/modelo; sem p95 robusto.',
        'model_requests_per_question': [r['metadata']['model_requests'] for r in cases],
        'tool_calls_per_question': [r['metadata']['calls_used'] for r in cases],
        'timeouts': sum(r['error'] == 'OLLAMA_TIMEOUT' for r in cases),
        'deadlines': sum(r['error'] == 'DEADLINE_EXCEEDED' for r in cases),
        'protocol_or_proposal_errors': sum(r['error'] == 'INVALID_MODEL_RESPONSE' for r in cases),
        'quality_assessments': factual,
        'memory_snapshot': cases[-1].get('loaded_memory_snapshot'),
    }, ensure_ascii=False, indent=2))
print('Relatório:', os.environ['TASK_REPORT_DIR'])
PY
)
```

Só compara qwen3:8b/qwen3:4b quando instalados, além do modelo configurado instalado.
Ollama pode carregar o modelo em memória ao receber /api/chat; não há downloads.
O timeout HTTP efetivo será limitado pelo orçamento atual de 60 s. Não há retries
ilimitados nem garantia de cancelamento forçado de uma operação bloqueada.

## Cobertura e decisão de aceitação

O benchmark real existente tem **três perguntas explícitas por modelo**: resultado,
golos e autogolos. Regista propostas, argumentos, evidências, erros, chamadas e
latência. Não cobre ainda toda a matriz real pedida na Fase 2.5. Um pytest aprovado
indica execução do harness, não aprovação dos critérios: o teste também pode
passar com resultados de qualidade negativos, e skip não é validação real.

Antes de concluir esta fase faltam resultados reais adicionais para cartões,
substituições, cantos, jogo sem eventos, esclarecimento sem ID, jogo inexistente,
fora de equipa/época e métricas indisponíveis. Os casos sem ID são controlados pelo
backend e devem ter zero chamadas ao modelo; não entram na taxa de seleção.
Também é preciso registar autenticação recusada e tentativas de argumentos
proibidos como controlos de segurança separados. Se o modelo não propuser
argumentos proibidos, isso não demonstra rejeição: as propostas adversariais
controladas devem ser verificadas separadamente, identificadas como tais.

Limites e falhas de transporte exigem cenários controlados identificados; não
confundir falha TCP deste diagnóstico com um cenário de timeout em inferência.
A verificação de escrita deve observar apenas SELECT/SET e ausência de commits
após o seed, como nos testes existentes. Não parar Ollama nem modificar processos
para provocar falhas. /api/ps é apenas fotografia dos modelos carregados, não pico
de RAM. Factos verificados significam fidelidade aos registos sintéticos do
backend, não verificação da realidade de um jogo.

Critérios pendentes: 100% rejeição de acessos não autorizados; 100% rejeição de
argumentos proibidos; 100% fidelidade dos factos avaliados; >=90% seleção correta
nas perguntas explícitas; nenhuma execução arbitrária ou escrita. Nenhum desses
objetivos recebe uma taxa real nesta sessão: todos estão não avaliados.

**Decisão: não avançar para FastAPI com base na Fase 2.5.** É necessário primeiro
ter Ollama acessível no mesmo ambiente do teste, confirmar versão/modelos, executar
a compatibilidade e recolher o benchmark real completo com denominadores claros.
As alterações desta sessão limitam-se a este documento e ao diagnóstico JSON;
nenhuma funcionalidade, arquitetura, dependência ou serviço foi alterado.
