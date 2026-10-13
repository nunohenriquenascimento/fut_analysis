# Recuperação de encerramento acidental — 13/10/2026

## Diagnóstico antes da alteração

A máquina de estados em `backend/app/live_service.py` só permitia
`SCHEDULED -> FIRST_HALF -> HALF_TIME -> SECOND_HALF -> FINISHED`.
Não havia uma operação de recuperação de `FINISHED`. O frontend executava
o encerramento diretamente, sem confirmação.

O relógio já tinha `Match.elapsed_seconds` e `Match.clock_started_at`.
Durante uma parte, o backend somava aos segundos acumulados a diferença
inteira, em segundos, entre a hora atual UTC e a marca de início.
Ao terminar a parte, guardava essa soma e limpava a marca de início.
O intervalo não era contabilizado. O frontend interpolava o snapshot
do servidor com `performance.now()`. Uma parte sem marca de início
era anteriormente rejeitada como relógio inconsistente.

O resultado é calculado a partir dos eventos, incluindo autogolos.
As estatísticas competitivas filtram jogos `FINISHED`; a atividade da época,
rankings, eventos e convocatórias usam os âmbitos existentes, mais amplos.
ADMIN e COACH já tinham permissão para as transições Live; VIEWER só lê.
As escritas Live já bloqueavam a linha do jogo e notificavam os sockets
depois do commit. Não foi necessário alterar estes mecanismos.

## Operações finais

- `POST /matches/{match_id}/reopen`: aceita exclusivamente
  `FINISHED -> SECOND_HALF`, mantém `elapsed_seconds` e define
  `clock_started_at = NULL`. Retorna `LiveState`.
- `POST /matches/{match_id}/resume`: aceita exclusivamente uma segunda
  parte com relógio parado e define a marca de início para a hora atual UTC.
- Ambos exigem ADMIN ou COACH, sessão válida, origem autorizada e CSRF.
  VIEWER recebe 403. Jogo inexistente recebe 404. Estado incompatível recebe 409.
- A validação acontece dentro de `mutate`, após `SELECT ... FOR UPDATE`.
  Dois pedidos de reabertura concorrentes produzem um 200 e um 409.
- O PATCH genérico continua sem aceitar status. A transição normal
  continua sem permitir regressar de FINISHED para SECOND_HALF.
- Reabrir não escreve, apaga nem recria eventos ou convocatórias.
  IDs, timestamps, autores, jogadores, resultado e timeline são preservados.
- Sem retoma, o tempo fica congelado, inclusive após refresh e noutro
  dispositivo. Nenhum segundo entre terminar, reabrir e retomar é acrescentado.
- Novos eventos ficam bloqueados enquanto o relógio está parado.
  Os eventos existentes continuam disponíveis para consulta/correção.
- É possível terminar novamente sem retomar, mantendo o tempo congelado.
- As estatísticas competitivas excluem o jogo enquanto reaberto e voltam
  a incluí-lo ao terminar novamente. Os eventos e restantes estatísticas
  históricas mantêm o âmbito anterior.
- Reabrir e retomar publicam `live.state_changed`, com `actor_id`, após commit.
  O cliente usa a atualização HTTP existente para obter o snapshot atual.
  Mantém-se a arquitetura WebSocket de um processo, sem novo serviço distribuído.
- O logger `app.live_api` regista `match_id` e `actor_id` após reabertura
  bem-sucedida, ao nível INFO. A visibilidade depende da configuração de logging.

## Fluxo do operador

1. “Terminar 2.ª Parte” abre a confirmação “Tens a certeza que o jogo terminou?”.
   A descrição é “Esta ação termina o jogo e fecha o cronómetro.”.
2. “Voltar” recebe o foco inicial. “Terminar jogo” é a confirmação destrutiva,
   visualmente separada.
3. Após terminar, fica disponível “Desfazer” durante 10 segundos; usa exatamente
   o endpoint de reabertura.
4. Em FINISHED, ADMIN e COACH encontram “Reabrir jogo” no detalhe e no Live.
5. A confirmação explica que mantém eventos/resultado e deixa o relógio parado.
   A reabertura pelo detalhe encaminha para o Live.
6. “Retomar 2.ª Parte” inicia o relógio quando o operador decidir. Depois pode
   registar novos eventos e terminar novamente com confirmação.

## Ficheiros

- Backend: `app/live_service.py`, `app/live_api.py`.
- Frontend: `lib/live.ts`, `components/live-state-dialog.tsx`,
  `app/matches/[match_id]/live/live-match.tsx`,
  `app/matches/[match_id]/match-detail.tsx`.
- Testes: `backend/tests/test_live.py`, `backend/tests/test_auth_live_socket.py`,
  `backend/tests/test_auth_live_browser.py`, `backend/tests/live_browser.cjs`,
  `frontend/tests/live.spec.ts`, `frontend/tests/live-socket.spec.ts`.
- Este relatório. Nenhuma migração ou alteração de schema.

## Verificação

Resultados finais:

- Python/PostgreSQL, com integração de navegador e Caddy ativada: **248 passed**,
  sem testes ignorados, em 180,82 s. Inclui os dois percursos reais a 360/390 px.
- Playwright frontend: **48 passed** (45 na suite completa e os 3 testes adicionais
  de permissões/recuperação pelo detalhe numa execução dirigida).
- ESLint, TypeScript (`tsc --noEmit`) e build de produção: passaram.
- Alembic check: **No new upgrade operations detected**.
- `git diff --check`: passou.

O primeiro build precisou de acesso à rede para obter as fontes Google já
usadas pelo projeto. O build final passou sem mudanças às fontes ou dependências.
Na suite Playwright, no Windows, foi necessário encerrar o processo Next de teste
após os testes terminarem para desbloquear a limpeza do servidor; os runners
devolveram exit code 0. O teste integrado gere diretamente os seus processos.

Os testes PostgreSQL verificam relógio, dados preservados, resultado,
convocatórias, autoria, estatísticas, estados inválidos, 404, PATCH proibido,
rollback de falha, ADMIN/COACH/VIEWER e concorrência. Os testes reais de
WebSocket confirmam as notificações em duas ligações autenticadas.

A suite Playwright verifica o percurso de recuperação a 360, 390 e 1280 px,
confirmações e cancelamentos, Desfazer, persistência após refresh, retoma,
eventos posteriores, permissões, erro 409 e sincronização de duas páginas.
A suite de regressão cobre login, roles, eventos, resultado, cancelamento,
eliminação, estatísticas e layout. Estes testes frontend usam a API simulada
da suite existente.

`test_auth_live_browser.py` complementa-os com navegador Edge, build Next,
FastAPI, sessões/CSRF, PostgreSQL isolado e WebSockets reais, sem mocks.
A 360 e 390 px verifica login COACH, jogo completo, vários eventos,
reabertura, preservação do tempo e convocatória, segundo dispositivo,
retoma, mais eventos, novo encerramento e estatísticas finais nas páginas.
O teste usa a porta 8000, exige um build com a API de desenvolvimento padrão
e é ativado explicitamente com `RUN_LIVE_BROWSER_E2E=1`.

Comandos (PowerShell):

```powershell
# frontend
npm.cmd run lint
npx.cmd tsc --noEmit
npm.cmd run build
npm.cmd run test:e2e -- --workers=2

# backend, com TEST_DATABASE_URL numa base PostgreSQL autorizada para testes
$env:RUN_LIVE_BROWSER_E2E = '1'
$env:CADDY_BIN = (Resolve-Path '..\.local-tools\caddy\caddy.exe').Path
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m alembic check
```

Os testes usam schemas descartáveis `roster_test_<uuid>` e não as tabelas
da aplicação. Os servidores e navegadores dos testes integrados são encerrados
no final. O teste Caddy também verifica login/cookies e upgrade WebSocket real.
