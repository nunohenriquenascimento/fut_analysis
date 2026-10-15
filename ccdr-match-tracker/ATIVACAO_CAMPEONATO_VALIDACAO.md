# Preparação da ativação real — 15/10/2026

## Resultado

Preparação técnica validada para o destino atualmente configurado. **Não foi
ativada a área na base real.** A revisão continua em `0006`; não houve backup,
restauro, migração, criação de participantes/competições ou importação nessa
base. Apenas foram lidos revisão, versão, metadados de esquema e permissões.

As alterações não commitadas das etapas anteriores foram preservadas. Sem
commit, merge, push ou alterações a `ai-learning/` nesta etapa.

## Auditoria da migração

- Cadeia linear revista: `0001 -> 0002 -> 0003 -> 0004 -> 0005 -> 0006 -> 0007`.
- Partindo de `0006`, o upgrade executa apenas `0007`.
- `0007` cria `competitions`, `competition_teams` e `competition_fixtures`,
  com chaves, constraints e novas sequências. Referencia `seasons`, `teams`
  e `matches`; não altera tabelas/linhas preexistentes de negócio.
- O único UPDATE no SQL do upgrade é a revisão em `alembic_version`.
- Não há backfill, cascatas de eliminação, migração de enums ou UPDATE/DELETE
  de jogos, jogadores, convocatórias e eventos.
- `downgrade()` contém remoção de tabelas, mas é outro percurso: não foi
  executado no destino real e não está autorizado pelo procedimento.
- PostgreSQL configurado: 18.6; ferramentas do ensaio: PostgreSQL 18.
- Comparação READ ONLY com uma instalação sintética de `0006`: tabelas,
  colunas, defaults, PK/FK, uniques, checks, índices e enums equivalentes.
- Permissões confirmadas em leitura: CREATE no schema, REFERENCES nas três
  tabelas referenciadas, UPDATE em alembic_version e SELECT nas nove tabelas
  auditadas. Não são necessárias alterações de grants na base configurada.

SQL offline para revisão: `docs/competicoes/2026-27/migration-0007.sql`.
Este ficheiro é evidência; a ativação deve usar Alembic, não executar SQL
manualmente em paralelo com o controlo de revisão.

## Ensaio completo

Foi criado um cluster PostgreSQL temporário independente, ligado apenas a
127.0.0.1 numa porta aleatória. A role da aplicação não tem CREATEDB; não foi
alterada essa permissão nem criada uma base na instância real.

1. Criar duas bases vazias na instância temporária.
2. Aplicar a cadeia até `0006` à primeira base.
3. Criar dados expressamente sintéticos nas nove tabelas antigas: utilizador,
   época, equipas, jogador, jogo terminado, convocatória, golo, sessão e throttle.
4. Ajustar as sequências sintéticas para posições válidas e tirar fingerprints.
5. Fazer `pg_dump --format=custom`, ler o índice e calcular SHA-256.
6. Restaurar o arquivo na segunda base com `--exit-on-error`, sem `--clean`.
7. Confirmar esquema, dados e sequências iguais aos da origem sintética.
8. Aplicar `0007` apenas à segunda base; confirmar fingerprints antigas iguais.
9. Executar `alembic check`: sem operações novas.
10. Verificar `/competitions`, `/players`, `/matches/1`, `/matches/1/live`
    e `/matches/1/stats`: todos HTTP 200. Esta verificação de leitura usa
    ator sintético injetado; permissões reais são verificadas separadamente
    pelos testes de autenticação.
11. Parar a instância temporária, conservando os artefactos sintéticos.

Evidência resumida versionável: `docs/competicoes/2026-27/ensaio-0007.json`.
Arquivo e logs locais: `.local-tools/activation-0007-20261015-final/` (ignorados).
As tentativas iniciais encontraram limitações de token/processos do Windows;
o executor foi corrigido para usar logs em ficheiro em vez de pipes herdados.
A instância da tentativa interrompida também foi parada. Não foi usado um
restauro sobre dados existentes para contornar estas limitações.

O ensaio comprova o procedimento com dados sintéticos e não equivale ao
backup da base real. Esse backup e o ensaio do respetivo arquivo continuam
pendentes de autorização e janela de manutenção.

## Gestão posterior de participantes

Implementada sem alteração da migração `0007`:

| Método | Endpoint | Permissão |
| --- | --- | --- |
| POST | `/competitions/{id}/teams/preview` | ADMIN |
| PUT | `/competitions/{id}/teams` | ADMIN |

Ambos recebem `team_ids` e `expected_team_ids`, com IDs únicos e entre 2 e 64
participantes. O PUT exige também `confirmation: "ALTERAR PARTICIPANTES"`.

O preview devolve as adições/remoções e os conflitos, sem gravar. O PUT volta
a calcular o plano dentro da transação, sob o mesmo bloqueio de competição
usado pela importação. Se a lista de participantes mudou desde a leitura,
devolve 409. Um jogo importado depois do preview também impede a remoção.
Assim, o PUT não confia no plano guardado pelo frontend.

A nossa equipa não pode ser retirada. Qualquer jogo de calendário envolvendo
um participante a retirar bloqueia a operação, tenha ou não resultado.
Jogos internos da mesma época/equipa também bloqueiam, mesmo sem ligação ao
calendário. É uma regra conservadora, pois o modelo atual não distingue fases
nos jogos internos. Não são apagadas equipas, jogadores, jogos ou resultados;
só é removida a associação sem dependências em `competition_teams`.

Interface: nova secção na Gestão, apenas para ADMIN, com seleção de equipas,
revisão das diferenças e confirmação escrita. Alterar a seleção invalida a
revisão. Um conflito na gravação invalida a confirmação e exige nova revisão.
Existe ação de atualizar a lista para resolver leituras desatualizadas.

COACH continua a configurar regras e importar resultados, conforme as
permissões anteriores, mas recebe 403 nas novas operações de participantes.
VIEWER mantém apenas leitura. Sessão, origem e CSRF continuam obrigatórios.

## Preparação dos dados oficiais

Pasta `docs/competicoes/2026-27/`: instruções e `draft.json` marcado
`RASCUNHO_NAO_IMPORTAR`, sem participantes adversários, jogos, resultados ou
regras oficiais inventados. Este documento não é um payload aceite pela API.

O fluxo existente continua a permitir rever JSON antes de confirmar. As
importações são idempotentes por `(competition_id, external_key)`, atómicas
por lote e exigem origem. Jogos internos exigem ligação explícita e não
aceitam golos importados. Esses comportamentos foram mantidos e testados.
A revisão JSON da interface não substitui a validação do servidor na gravação.

Classificação continua provisória; não foram configurados novos desempates.
Empates sem critério suficiente permanecem assinalados. Pontuação/desempates
oficiais e eventuais sanções não estão validados nesta preparação.

## Validação

- Suite backend completa, PostgreSQL e Caddy: **306 passed, 4 skipped**.
  Os skips são os quatro percursos de navegador Live/união opt-in; não houve
  alteração Live nesta etapa. Mantêm-se o teste de limpeza e os restantes
  testes Live/WebSocket na suite normal.
- Testes dirigidos de participantes/autorização: **23 passed**.
- Playwright completo: **67 passed**, incluindo os dois cenários novos e
  atualização das verificações de ADMIN/COACH/VIEWER.
- ESLint, TypeScript e build de produção: passaram.
- Ensaio completo de backup/restauro/migração e leituras: passou.
- `git diff --check`: passou.
- Aviso de depreciação Starlette/httpx já existente, sem falhas de testes.

Cobertura nova: preview sem mutação; confirmação ausente/incorreta; adicionar
e remover associação sem apagar Team; duplicados; IDs inexistentes; equipa
interna protegida; lista desatualizada; jogos agendados e terminados; jogo
interno não ligado; dependência criada após preview; permissões e CSRF/origem;
revisão invalidada na interface; confirmação explícita e comportamento mobile.

## Riscos e limites antes da ativação

1. O ensaio não substitui o backup real nem mede o seu tempo de restauro.
2. A compatibilidade foi verificada para a base configurada, não para outro
   servidor/ambiente. Confirmar o destino antes de executar qualquer comando.
3. O código novo depende das tabelas de `0007`, inclusive algumas leituras de
   gestão dos jogos. Manter manutenção até concluir upgrade e validação.
4. As fingerprints incluem sessões/throttles. Login/logout ou outros writers
   durante a janela fazem divergir os dados; parar escritas antes do backup.
5. A remoção posterior é conservadora quanto a jogos internos sem fase explícita;
   um bloqueio não autoriza eliminar jogos para o ultrapassar.
6. Dados/IDs ou chaves mal mapeados podem associar outro adversário ou jogo.
   Rever a lista oficial e os mapeamentos; nunca adivinhar o resultado desconhecido.
7. Sem regulamento aplicável e decisões administrativas confirmadas, não
   apresentar a tabela como classificação oficial.

## Ativação autorizada e informação necessária

Procedimento exato: [docs/MIGRACAO_0007.md](docs/MIGRACAO_0007.md).
Ordem: confirmar destino/manutenção → backup real/checksum/snapshot → ensaio
de restauro do arquivo real numa base vazia → autorização para `0007` →
upgrade/check/comparação → validar leituras/permissões → reabrir aplicação.
O carregamento de dados reais é uma autorização separada, depois da revisão.

Do utilizador são necessários:

- Destino real a ativar (ambiente/host/porta/base), janela de manutenção,
  localização privada do backup e responsável pela execução. Não enviar passwords
  pelo chat; usar a configuração existente/pedido interativo.
- Autorização para executar o backup real e ensaio de restauro do arquivo.
- Após rever o backup/ensaio, confirmação explícita para aplicar `0007` nesse destino.
- Lista oficial das oito equipas, série/fase e calendário, respetivas fontes
  e os mapeamentos revistos para IDs locais e jogos internos.
- Resultados confirmados e origem por jogo; os desconhecidos permanecem NULL.
- Regulamento aplicável a 2026/2027 e artigos de pontuação/desempate. Até lá,
  confirmação de que a classificação continuará provisória.
- Autorização separada para criar a competição e importar cada lote real revisto.

## Ficheiros desta etapa

- `backend/app/competition_schemas.py`, `competition_api.py` e novo
  `competition_participants.py`: seleção, plano e gravação ADMIN.
- `backend/app/activation_rehearsal.py`: executor do ensaio isolado.
- `backend/tests/test_participants.py`, `test_auth_competitions.py`.
- `frontend/lib/competitions.ts`, `frontend/app/competitions/competition-screen.tsx`
  e novo `participants-form.tsx`.
- `frontend/tests/competitions.spec.ts`.
- `docs/MIGRACAO_0007.md`, `docs/competicoes/2026-27/` e este relatório.
- Referência à nova etapa em `COMPETICOES_INTERFACE_VALIDACAO.md`.
