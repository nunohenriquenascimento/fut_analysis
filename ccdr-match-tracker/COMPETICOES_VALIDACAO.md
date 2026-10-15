# Competições — 15/10/2026

Atualização: a interface foi implementada na etapa seguinte, documentada em
[COMPETICOES_INTERFACE_VALIDACAO.md](COMPETICOES_INTERFACE_VALIDACAO.md).
O procedimento de ativação está em [docs/MIGRACAO_0007.md](docs/MIGRACAO_0007.md).
Os resultados abaixo registam a etapa backend original.

## Âmbito

Backend convencional, sem IA. Liga Dappin, Campeonato Distrital Juniores A
Sub-19 masculino de futebol de 11 da AF Guarda, época 2026/2027, oito equipas
(identificação e formato fornecidos pelo utilizador). Não foram inventados
participantes, calendário ou resultados reais.

## Etapa 1 — estado inicial

- Git limpo em `main`, commit `59c3bce`, sem `MERGE_HEAD`. A funcionalidade
  de união de jogos está integrada nesse commit; não havia merge Git pendente.
- `main` alinhado com a referência local `origin/main`; não foi feito fetch.
- Base configurada em `0006`; `alembic check` sem diferenças antes das alterações.
- Primeira execução sem configuração PostgreSQL de teste: 25 passed, 254 skipped.
- ESLint e TypeScript passaram.

## Etapas 2–4 — modelo e importação

Migração aditiva `0007`: `competitions`, `competition_teams`,
`competition_fixtures`. Não altera tabelas internas nem faz backfill.
Não foi aplicada à base da aplicação. Os testes usam exclusivamente schemas
temporários `roster_test_<uuid>`; o downgrade recusa apagar competições existentes.

`Team` continua partilhada. A criação de uma competição associa participantes
existentes explicitamente por ID. Não faz correspondência automática por nome.
Uma jornada agrupa os jogos pelo inteiro `matchday`, sem impor datas comuns:
jogos adiados podem ter datas diferentes e datas desconhecidas podem ser NULL.

Importação JSON, até 200 jogos por lote, numa transação. `external_key` estável
identifica cada jogo na competição. Repetir o lote atualiza os mesmos registos.
Uma chave existente não pode mudar equipas, jornada ou ligação interna.
Conflitos de identidade/duplicados devolvem 409; erro num lote reverte tudo.
Resultados têm dois inteiros não negativos ou ambos NULL; NULL retira o
resultado externo e devolve o jogo a agendado. `source` é obrigatório.

Jogos do CCDR exigem `internal_match_id` compatível com época, equipa, adversário,
casa/fora e jornada. Não aceitam golos importados. Datas, local, estado e
resultado são lidos do jogo interno, com golos derivados dos eventos existentes.
Só jogos FINISHED entram na classificação. Jogos reabertos, cancelados ou
agendados ficam excluídos. A ligação impede eliminar o jogo interno por FK;
as operações existentes devolvem 409 e fazem rollback. Não executar uniões
reais sem confirmação do utilizador.

## Etapa 5 — classificação provisória

Não foi possível confirmar os regulamentos indicados: consulta web e descarga
direta devolveram HTTP 403. Não foram guardados PDFs incompletos nem usados
regulamentos de outra época como se fossem os de 2026/2027.

- Específico: https://afguarda.fpf.pt/DesktopModules/AssociationsDocuments/DownloadFiles.ashx?IdDoc=170661
- Geral: https://afguarda.fpf.pt/DesktopModules/AssociationsDocuments/DownloadFiles.ashx?IdDoc=180668

Aplicabilidade à época e artigos de pontuação/desempate: **por confirmar**.

Todas as respostas de classificação incluem `provisional: true` e aviso.
A política inicial é explicitamente provisória: vitória 3, empate 1, derrota 0,
sem desempate automático por diferença de golos. Pode ser substituída por PUT.
Suporta critérios ordenados de pontos no confronto direto, diferença de golos
no confronto direto, diferença global, golos marcados e vitórias. Cada critério
é aplicado ao grupo ainda empatado, avançando para o seguinte; confronto direto
considera os jogos terminados entre membros desse grupo. Não exige segunda volta
completa. Não implementa jogo de desempate, sorteio ou reinício recursivo dos
critérios: validar estes detalhes quando o regulamento estiver disponível.
Empates restantes partilham posição e têm `unresolved_tie: true`; ID apenas
estabiliza a apresentação. Sanções/perdas de pontos não estão implementadas.

## Etapa 6 — contrato HTTP

Leituras autenticadas por sessão existente; escritas exigem ADMIN/COACH,
origem autorizada e CSRF. Não há endpoints públicos anónimos.

| Método | Endpoint | Função |
| --- | --- | --- |
| POST | `/teams` | Criar equipa |
| POST/GET | `/competitions` | Criar/listar competições |
| GET | `/competitions/{id}/teams` | Participantes |
| PUT | `/competitions/{id}/rules` | Substituir política provisória |
| POST | `/competitions/{id}/fixtures/import` | Importar/corrigir lote JSON |
| GET | `/competitions/{id}/calendar?matchday=1` | Jogos e resultados |
| GET | `/competitions/{id}/matchdays` | Calendário agrupado por jornada |
| GET | `/competitions/{id}/standings` | Classificação calculada na leitura |
| GET | `/matches`, `/matches/{id}` | Jogos internos, endpoints existentes |
| GET | `/matches/{id}/stats`, `/statistics/season`, `/statistics/players` | Estatísticas internas existentes |

Exemplo de criação (substituir IDs pelos IDs reais):

```json
{"name":"Liga Dappin 2026/2027","season_id":1,"internal_team_id":1,
 "team_ids":[1,2,3,4,5,6,7,8],
 "rules":{"win":3,"draw":1,"loss":0,"tiebreakers":[]}}
```

Exemplo de importação de resultado entre adversários:

```json
{"fixtures":[{"external_key":"j1-2-3","matchday":1,
 "home_team_id":2,"away_team_id":3,"home_goals":2,"away_goals":1,
 "source":"Boletim oficial / referência da fonte"}]}
```

Para um jogo interno, usar `internal_match_id` e omitir os golos.
O esquema completo está no OpenAPI `/docs`. Não há crawler, importação CSV
nem ecrãs novos de gestão nesta etapa; os serviços estão disponíveis via API.

## Ficheiros

- `backend/app/models.py`, `backend/app/main.py`.
- `backend/app/match_service.py`, `backend/app/merge_service.py`: detetar
  ligações ao calendário na elegibilidade de eliminação e no preview de união.
- `backend/app/competition_schemas.py`, `competition_service.py`, `competition_api.py`.
- `backend/alembic/versions/0007_competitions.py`.
- `backend/tests/test_competitions.py`, `test_auth_competitions.py`.
- `backend/tests/test_auth_proxy_real.py`: aceitar heartbeats válidos antes
  da notificação de golo, mantendo prazo total e validação de tipo/autor.
- Este relatório.
- `docs/regulamentos/README.md`: fontes e estado da consulta.

## Validação final

- Suite dirigida final de competições/autorização: **18 passed**.
  Inclui reimportação, correção/remoção de resultado, calendário/jornadas,
  ligação interna fora de casa, autogolo, reabertura, isolamento dos dados
  internos, lotes atómicos, duplicados, desempates configuráveis, sessão,
  papéis, CSRF/origem, proteção de eliminação/união e migração aditiva.
- Migração `0007` e `alembic check` passaram num schema temporário;
  downgrade com dados foi recusado sem perda de informação.
- Frontend: **53 passed** em Playwright; ESLint, TypeScript e build passaram.
  O build exigiu acesso à rede para as fontes Google já usadas pelo projeto.
  Foi necessário parar o servidor Next lançado pela suite após os cenários
  terminarem, para concluir a limpeza do processo Playwright no Windows.
- Primeira suite PostgreSQL completa após adicionar a funcionalidade:
  **287 passed, 5 skipped, 2 failed**, com `CancelledError` no encerramento
  de WebSockets do TestClient. Repetição das duas suites afetadas:
  **23 passed**. Não foi alterada a implementação Live para mascarar
  esta intermitência de encerramento.
- Execução alargada com navegador real e Caddy: **295 passed, 2 failed**.
  Os quatro percursos reais Live/união, a 360/390 px, passaram.
  Uma falha era uma expectativa de `can_delete` anterior à proteção nova,
  já corrigida e validada nos 18 testes dirigidos. A outra era o teste Caddy
  assumir que nunca receberia um heartbeat antes do evento. O teste foi
  corrigido para responder `pong` e esperar a notificação dentro do prazo
  total de cinco segundos, preservando a validação do autor e tipo do evento.
- Última suite completa sobre os ficheiros finais, com Caddy ativado:
  **292 passed, 4 skipped, 1 failed** em 123,36 s. Os quatro skips são os
  percursos de navegador opt-in, aprovados na execução alargada anterior.
  O teste Caddy corrigido e todos os testes de competições passaram.
  Falha restante: `test_reopen_resume_permissions_and_two_socket_notifications[COACH]`,
  `concurrent.futures.CancelledError` ao sair do contexto WebSocket do
  TestClient. **A suite global não está totalmente verde**; a intermitência
  continua por resolver, apesar de a repetição dirigida das suites afetadas
  ter passado (23 testes). Não se confirmou falha funcional no navegador real.
- `git diff --check`: passou.

Não houve merge Git, push, deployment, união de jogos reais ou migração da
base da aplicação. A base real permanece em `0006`; aplicar `0007` é um passo
operacional separado antes de usar os novos endpoints.
