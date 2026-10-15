# Interface do campeonato — 15/10/2026

Etapa posterior: [ATIVACAO_CAMPEONATO_VALIDACAO.md](ATIVACAO_CAMPEONATO_VALIDACAO.md)
regista o ensaio de ativação e a nova gestão posterior de participantes por ADMIN,
resolvendo essa pendência abaixo. Os resultados deste relatório são históricos.

## Estado e âmbito

Implementação convencional da interface, sobre os endpoints já documentados
em `COMPETICOES_VALIDACAO.md`. Não foram acrescentados endpoints nem alterações
ao esquema nesta etapa. A migração `0007` continua por aplicar à base real;
`alembic current` voltou a confirmar **0006** após os testes.

Git em `main`, sem merge pendente. Já existiam alterações não commitadas do
backend da etapa anterior e a pasta `ai-learning/` não versionada. Foram
preservadas. Não houve commit, merge, push, deploy, seed ou importação real.
A pasta `ai-learning/` não foi editada. Não foram implementadas funcionalidades IA.

## Funcionalidades concluídas

Entrada «Campeonato» no cabeçalho e na página inicial. Todas as páginas usam
a sessão, permissões, CSRF, transporte HTTP e componentes visuais existentes.

| Página | Função |
| --- | --- |
| `/competitions` | Listar competições; criar uma competição da época/equipa do contexto atual |
| `/competitions/{id}` | Classificação, com pontos, jogos, vitórias, empates, derrotas e golos |
| `/competitions/{id}/results` | Resultados agrupados por jornada, com filtro |
| `/competitions/{id}/calendar` | Calendário completo, incluindo jogos sem data/resultado |
| `/competitions/{id}/teams` | Participantes e identificação da nossa equipa |
| `/competitions/{id}/manage` | Configuração provisória e importação JSON, ADMIN/COACH |
| `/competitions/{id}/fixtures/{fixtureId}` | Detalhes, origem e correção de resultado externo |

Criação: permite selecionar equipas existentes e criar uma equipa adversária
em falta, associando-a à seleção. A nossa equipa vem do contexto da aplicação
e permanece selecionada. A associação dos participantes é feita na criação,
conforme o contrato existente de POST `/competitions`.

Configuração: pontuação de vitória/empate/derrota e lista ordenada de critérios
suportados pelo backend, com adição, remoção e mudança de ordem. Não existe
critério de desempate selecionado por defeito. A classificação continua
sempre identificada como **Classificação provisória**. A interface não afirma
que os critérios são oficiais e identifica os empates não resolvidos.

Importação: colar JSON ou escolher ficheiro até 1 MB; rever lote e confirmar.
A revisão não escreve dados. A validação de negócio e a transação pertencem
ao backend. Alterar o JSON invalida a revisão. Erros 409/422 preservam o
conteúdo e são apresentados ao utilizador. Há proteção contra submissões
repetidas enquanto uma operação está em curso.

Detalhe: mostra equipas, resultado/estado, jornada, data em Lisboa, local,
chave e origem do registo. ADMIN/COACH podem corrigir golos e origem de jogos
externos. A correção reimporta apenas os campos de transporte do mesmo jogo
e volta a ler o calendário no servidor. Jogos internos mostram uma ligação
para `/matches/{id}`, sem formulário de correção externa. Não há chamadas
de escrita aos endpoints dos nossos jogos nestes fluxos.

Leituras e cálculos: a interface apresenta a ordem, posições, estatísticas e
empates recebidos do backend. Não calcula classificações ou resultados.
Listagens paginadas são percorridas integralmente. Existem estados de carga,
erro, repetição, lista vazia e registos inexistentes. As rotas e o transporte
evitam reaproveitar dados de uma vista anterior ao mudar de página.

## Layout e acessibilidade

Identidade CCDR existente, componentes Card/Button/TeamCrest e cores atuais.
Páginas mobile-first, navegação que quebra linha, formulários sem overflow,
alvos de toque de pelo menos 44 px nos testes e tabela de classificação
com scroll horizontal próprio, focável por teclado e com cabeçalhos semânticos.
As abreviaturas das estatísticas têm legenda. Nomes e origens longos quebram
linha. As horas são apresentadas no fuso Europe/Lisbon.

Capturas em `frontend/artifacts/competitions/teams-{360,390,1280}.png`.
Foi inspecionada a captura de 360 px. Os artefactos estão ignorados pelo Git.

## Investigação e correção do WebSocket

Antes da correção, 12 repetições do cenário parametrizado de reopen/resume
(36 casos) produziram uma execução com `CancelledError` no encerramento.
Um teste novo, sem PostgreSQL nem TestClient, isolou um problema concreto:
o cancelamento AnyIO durante `await gather(...)` interrompia a limpeza antes
de remover a subscrição do hub. O teste falhou com a implementação anterior.

Correção limitada ao `finally` de `match_live_socket`: remover a subscrição
antes dos awaits e proteger apenas a espera pelas tarefas canceladas com
`CancelScope(shield=True)`. Não foi acrescentado um catch de CancelledError,
skip, retry automático ou relaxamento das asserções. Relógio, eventos,
resultados, notificações e autenticação Live mantêm a implementação existente.

O teste isolado passou depois da correção. As 12 repetições seguintes do
cenário parametrizado passaram (36 casos). A suite completa backend também
passou. Isto valida a correção observada; não constitui uma garantia sobre
todas as possíveis condições de cancelamento de bibliotecas externas.

## Backup e ativação

Procedimento completo: [docs/MIGRACAO_0007.md](docs/MIGRACAO_0007.md).
Inclui pausa de escritas, `pg_dump` custom, listagem e checksum do arquivo,
ensaio de restauro numa base separada, auditoria READ ONLY dos dados de `0006`,
ponto de confirmação explícita, upgrade dirigido a `0007`, `alembic check`
e comparação dos dados antes de retomar logins/escritas.

O utilitário `python -m app.migration_audit` não aplica migrações. Compara
contagens e SHA-256 de todas as linhas/colunas das nove tabelas preexistentes.
O teste em schema descartável confirmou preservação em `0007` e deteção de
alteração de conteúdo mesmo sem alteração da contagem de linhas.

**Nenhum backup, restauro ou upgrade da base real foi executado.** A ativação
real exige confirmação e execução do procedimento. Os ecrãs necessitam do
backend com `0007` aplicada para consultar ou gravar competições.

## Testes

- ESLint e TypeScript: passaram.
- Build de produção: passou, incluindo as sete rotas novas; requer acesso
  às fontes Google já usadas pela aplicação.
- Playwright completo: **65 passed**, incluindo **12 testes novos**.
- Suite backend completa com Caddy, antes de acrescentar o teste de auditoria:
  **294 passed, 4 skipped**. Os skips são os quatro percursos de navegador opt-in.
- Teste de auditoria em PostgreSQL: **1 passed**.
- Teste de limpeza WebSocket: passou, depois de falhar com o código anterior.
- Repetições de reopen/resume após correção: **36 casos aprovados**.
- Verificação real dirigida: **7 passed** — quatro percursos Live/união em
  navegador a 360/390 px, proxy Caddy, auditoria de migração e limpeza WebSocket.
- Repetição final de ESLint/TypeScript: passou. `git diff --check`: passou.
- Releitura final da base real: `0006`.

Os testes usam dados sintéticos, APIs simuladas no Playwright ou schemas
PostgreSQL descartáveis `roster_test_<uuid>`. A suite Playwright precisou de
terminar o servidor Next que ela própria lançou após os cenários passarem,
para concluir a limpeza dos processos no Windows, tal como na etapa anterior.

Na primeira execução dos testes novos foram corrigidos a associação explícita
do label «Jornada» ao select e os seletores de alertas dos testes, que também
encontravam o route announcer do Next. O build e a suite foram repetidos com
as correções; o resultado de 65 passed corresponde à versão corrigida.

## Ficheiros desta etapa

- `frontend/lib/competitions.ts`: tipos e cliente dos endpoints existentes.
- `frontend/app/competitions/page.tsx`: lista de competições.
- `frontend/app/competitions/competition-screen.tsx`: vistas de leitura e gestão.
- `frontend/app/competitions/competition-ui.tsx`: navegação, aviso e cartões.
- `frontend/app/competitions/create-form.tsx`: criação e seleção de participantes.
- `frontend/app/competitions/rules-form.tsx`: configuração provisória.
- `frontend/app/competitions/import-form.tsx`: JSON, revisão e confirmação.
- `frontend/app/competitions/fixture-detail.tsx`: origem e correção externa.
- `frontend/app/competitions/[competition_id]/page.tsx` e subrotas `results`,
  `calendar`, `teams`, `manage`, `fixtures/[fixture_id]`: wrappers de rota.
- `frontend/app/globals.css`, `frontend/components/app-header.tsx`,
  `frontend/app/page.tsx`: estilos e navegação.
- `frontend/tests/competitions.spec.ts`, `frontend/tests/layout.spec.ts`:
  novos fluxos e atualização da navegação inicial.
- `backend/app/live_socket.py`, `backend/tests/test_live_socket_cleanup.py`:
  correção de limpeza e regressão de cancelamento.
- `backend/app/migration_audit.py`, `backend/tests/test_migration_audit.py`:
  auditoria de migração em leitura.
- `docs/MIGRACAO_0007.md`, este relatório e referência em
  `COMPETICOES_VALIDACAO.md`.

Os restantes ficheiros backend assinalados no Git são os da etapa anterior,
preservados sem novas alterações nesta etapa.

## Pendências e limites

- Autorizar, executar e validar a ativação de `0007` na base real, com backup.
- Configurar as oito equipas, competição e calendário reais apenas quando
  forem fornecidos/confirmados; não foram criados dados fictícios na base real.
- Validar os regulamentos e artigos oficiais aplicáveis a 2026/2027. A
  classificação permanece provisória.
- A gestão posterior de participantes já está implementada para ADMIN, com
  preview, confirmação, deteção de edição concorrente e bloqueio por jogos
  dependentes. Não elimina equipas nem jogos. Renomear a competição ou mudar
  de época não faz parte do contrato atual.
- A retirada de um resultado externo (ambos os golos NULL) continua disponível
  pela importação JSON; o formulário de correção serve para registar dois golos.
- Sem sanções administrativas, crawler ou importação CSV, como na etapa anterior.

## Verificação funcional atual — 15/10/2026

Esta secção distingue a execução atual dos resultados históricos acima.
Não foram alteradas as bases reais, a documentação Hyper-V/Railway ou ai-learning.

- Implementação revista: criação/configuração, participantes, calendário e
  jornadas, importação idempotente/correção externa, origem e associação interna.
- A classificação é calculada nas leituras: pontos, J/V/E/D, GM/GS/DG;
  mantém indicação provisória e empates não resolvidos, sem critérios oficiais
  presumidos. Jogos cancelados ou não terminados não somam à classificação.
- ADMIN gere participantes; ADMIN/COACH mantêm as permissões editoriais
  existentes para criação, regras e resultados. VIEWER apenas consulta.
- Os jogos internos continuam a obter o resultado dos eventos. Jogos ligados
  não podem ser eliminados normalmente nem absorvidos como continuação;
  a FK impede a eliminação forçada e a transação deve fazer rollback.
  Esta garantia transacional não foi revalidada em PostgreSQL nesta execução.
- Backend: **30 passed, 284 skipped**, um aviso de depreciação Starlette/httpx.
  TEST_DATABASE_URL não está configurado; não há Docker disponível. Não foi
  identificada base de testes comprovadamente isolada e nenhuma foi contactada.
  O subprocesso pytest recebeu configuração sem destino real e sem opt-in de
  navegador backend. Os 284 testes ignorados não contam como aprovados.
- Novas regressões sem base: test_competition_read_models.py (quatro casos):
  agregados completos/exclusão de cancelados e inacabados, recálculo após
  correção/política de pontos, leitura interna casa/fora sem persistir golos.
- Playwright: **67 passed (48.8s), exit 0**; API/WebSockets simulados. Inclui
  jogos, convocatórias, estatísticas, cancelar/eliminar, união e Campeonato.
- Encerramento: reprodução curta ficou em "Terminating the WebServer" dentro
  da sandbox e foi interrompida, sem contar como aprovada. Fora da sandbox,
  o mesmo caso passou e terminou (exit 0), assim como a suite completa. A versão
  instalada encerra a árvore Windows via taskkill; não se alterou o runner nem
  se mascarou a falha. Estes testes precisam de permissão de encerrar os seus
  próprios processos no Windows.
- ESLint, tsc --noEmit e build Next.js: concluídos com sucesso. O build inclui
  as rotas de classificação, calendário, resultados, equipas, detalhe e gestão.
- 0007: revisão estática aditiva coerente com os modelos novos; ensaio atual e
  alembic check pendentes de PostgreSQL isolado. Não foi executada migração.

### Separação preparada para integração, sem staging nem commits

O checkout permanece em main, HEAD 59c3bce (união de jogos já existente), sem
novos commits. Preservar todos os ficheiros; não usar staging global.

1. Campeonato: app/competition_{api,participants,schemas,service}.py,
   app/{main,models,match_service,merge_service}.py, migração 0007,
   tests/test_{auth_competitions,competitions,participants,competition_read_models}.py;
   frontend/app/competitions/**, frontend/lib/competitions.ts,
   frontend/tests/{competitions,layout}.spec.ts, frontend/app/{globals.css,page.tsx},
   frontend/components/app-header.tsx e relatórios funcionais COMPETICOES*.
   Os caminhos app/tests/migração neste ponto são relativos a backend/.
2. Live separado: backend/app/live_socket.py,
   backend/tests/test_live_socket_cleanup.py e test_auth_proxy_real.py.
3. Fora dos commits funcionais: ai-learning/**, docs/railway/**,
   RAILWAY_PRODUCAO_AUDITORIA.md, activation_rehearsal.py, migration_audit.py,
   test_migration_audit.py e artefactos/procedimentos de ensaio/ativação.

**NÃO APTO para integração validada:** falta a regressão backend completa numa
base isolada. Não há falhas nos testes concluídos. O estado documental Hyper-V
não é o motivo desta pendência. Não foi feito staging porque a condição de
validação completa ainda não está satisfeita.

### Ativação futura, não executada

Confirmar revisão e destino de produção; autorizar separadamente backup e
restauro isolado; ensaiar 0006→0007 e preservar os dados existentes; coordenar
manutenção e writers; só com autorização aplicar o alvo explícito 0007 e
publicar código compatível. Não publicar o código novo contra 0006: consultas
de elegibilidade/união já dependem de competition_fixtures. O auto-deploy
informado para main exige coordenação antes de qualquer futuro push.
