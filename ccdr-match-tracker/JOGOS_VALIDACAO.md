# Jogos, jornadas e convocatórias

A fase posterior de eliminação/cancelamento seguro com ADMIN está documentada em [JOGOS_ELIMINACAO_VALIDACAO.md](JOGOS_ELIMINACAO_VALIDACAO.md). O restante documento regista a validação original desta fase.

Implementação de 1 de outubro de 2026. Plantel preservado; não foram implementados Jogo ao Vivo, autenticação, cronómetro, transições de estado, eventos, resultados, estatísticas, WebSockets ou offline.

## Funcionalidade

- `/matches`: lista os jogos da equipa e época devolvidas por `/players/context` (`CCDR Vila Cortez do Mondego`, `2026/27`). Obtém todas as páginas da API, sem IDs fixos. Cartões com jornada, adversário, data/hora, casa/fora e estado.
- Criação: jornada positiva, adversário por nome, data, hora, casa/fora e local opcional. Após criar, abre o detalhe. Todos os novos jogos começam em `SCHEDULED`.
- `/matches/{match_id}`: dados do jogo, edição e convocatória com titulares, suplentes e não convocados. Contadores imediatos e botão explícito de gravação.
- As datas do formulário e da apresentação usam o fuso horário do dispositivo. A API exige um instante com fuso; o frontend envia UTC. Configurar os dispositivos para a hora local correta.
- Adversários: reutiliza o nome ignorando maiúsculas/minúsculas e espaços redundantes. Se não existir, cria uma `Team` na mesma transação do jogo. Não cria jogadores adversários. Uma equipa não pode jogar contra si própria.
- Convocatória: mostra ativos da mesma equipa/época e inativos que já constam da convocatória. Um inativo preservado pode manter-se ou mudar entre titular/suplente. Se for retirado e a alteração guardada, deixa de poder ser adicionado enquanto estiver inativo.
- Loading, retry do carregamento, sucesso e erros; campos bloqueados durante gravação e bloqueio síncrono de submissões repetidas. As seleções permanecem no ecrã se uma gravação falhar.

## Modelo e migração

Nova migração: `backend/alembic/versions/0003_matchday.py`, dependente de `0002`.

Acrescenta `matches.matchday`, inteiro anulável, com constraint `matchday > 0`. Os novos pedidos exigem jornada; os jogos existentes ficam com NULL, apresentados como “Jornada por definir”. Não inventa jornadas nem apaga jogos/convocatórias. A relação ORM `Match.opponent` permite incluir `opponent_name` nas respostas, sem nova coluna para o nome.

`MatchSquad` mantém o modelo e a unicidade `(match_id, player_id)`. `is_starter=true` representa TITULAR, `false` representa SUPLENTE; ausência de linha representa NÃO CONVOCADO. A desativação do jogador não remove linhas da convocatória. Os registos mantidos conservam ID e data de criação.

Upgrade e downgrade foram testados com um jogo e convocatória existentes. **O downgrade de `0003` elimina os valores de jornada**, pois remove essa coluna; preserva os restantes dados de jogos e convocatórias. Fazer backup antes de um rollback que precise de conservar jornadas. A migração pode aguardar por bloqueios na tabela de jogos; aplicar com o backend parado.

`0001` e `0002` não foram alteradas. SHA-256 antes/depois:

```text
0001: 42F6B0C4B3A1F0FE8ECA2B4F1A5AB057F4CE0B2935152D397DE188D8471E6A4E
0002: F228A227165D3A17A9B4DA3AE1292E435CC1DD8D06DA27DC43FA4E7C67DBBEC0
```

A base local foi atualizada para `0003`; `alembic check` não detetou diferenças.

## API

| Método | Endpoint | Comportamento |
| --- | --- | --- |
| GET | `/matches` | Lista com filtros `season_id`, `team_id`, `limit` e `offset` |
| POST | `/matches` | Cria jogo e resolve/cria adversário; 201 |
| GET | `/matches/{match_id}` | Dados do jogo, incluindo nome do adversário |
| PATCH | `/matches/{match_id}` | Edita jornada, adversário por nome, data/hora, casa/fora e local |
| GET | `/matches/{match_id}/squad` | Jogadores disponíveis/preservados com `player` e `role` |
| PUT | `/matches/{match_id}/squad` | Substitui a convocatória completa; devolve a lista atualizada |

O POST recebe `season_id`, `team_id`, `matchday`, `opponent_name`, `kickoff_at`, `is_home` e `venue`. Mantém-se a alternativa `opponent_id`, mas nunca ambos os campos de adversário. A jornada passou a ser obrigatória nos novos pedidos, incluindo clientes que usam `opponent_id`.

O PATCH aceita apenas dados editáveis; não aceita `season_id`, `team_id`, estado ou cronómetro. `venue: null` limpa o local; outros campos enviados como NULL são rejeitados. Os seis estados antigos mantêm-se inalterados.

PUT completo, exemplo:

```json
{
  "players": [
    {"player_id": 12, "is_starter": true},
    {"player_id": 15, "is_starter": false}
  ]
}
```

Os IDs são ilustrativos; usar os devolvidos pela API. Jogadores omitidos ficam não convocados. `{"players": []}` esvazia a convocatória. `GET /squad` devolve `role` igual a `TITULAR`, `SUPLENTE` ou `NAO_CONVOCADO`.

- 404: jogo, jogador ou referência inexistente.
- 409: jogador duplicado, equipa/época incompatível, novo convocado inativo, adversário igual à própria equipa ou conflito de integridade.
- 422: tipos/valores inválidos, jornada não positiva, instante sem fuso, campos não permitidos ou PATCH vazio.
- 503: falha de ligação à base de dados.

O PUT bloqueia o jogo para serializar substituições concorrentes e bloqueia os jogadores selecionados durante a validação de atividade. Valida toda a lista antes de alterar linhas. A gravação é única e qualquer erro faz rollback. A criação de adversários por nome usa um bloqueio transacional PostgreSQL, evitando duplicações entre pedidos desta API para o mesmo nome.

A função `validate_squad` concentra as regras para futura introdução de limites. Nesta fase não há limite de titulares ou suplentes.

## Testes e resultados

- **58 testes Python aprovados, zero ignorados**, em PostgreSQL real com esquemas temporários isolados.
- Incluem criação/listagem/detalhe/edição, criação e reutilização de adversários, guardar/substituir/esvaziar convocatória, equipa/época incompatíveis, inativos, duplicados, 404/422, CORS PUT, atomicidade em falha de validação e em falha de escrita, histórico de inativos e 12 titulares sem limite.
- Repetir o mesmo PUT mantém uma linha por jogador e os IDs das linhas existentes.
- Regressão do Plantel e da migração de posições aprovada; teste novo de `0003` preserva jogo/convocatória no upgrade/downgrade.
- `python -m alembic check`: **No new upgrade operations detected**.
- Lint, TypeScript e build de produção: **aprovados**.
- **6 testes de browser aprovados** no Microsoft Edge, a 360 e 1280 px: 4 de Jogos/Convocatórias e 2 de regressão do Plantel. Incluem criação, listagem, navegação, edição, gravação/alteração, contadores, loading, erros, histórico inativo e double-submit.

Os testes de browser usam respostas HTTP controladas para validar a interface. Os testes backend exercitam FastAPI/SQLAlchemy/PostgreSQL real. Não foi validado um percurso integrado browser–API real nem um telemóvel físico.

Avisos não bloqueantes: aviso de descontinuação do transporte `httpx` no Starlette e aviso de cores no terminal Playwright. O build usa fontes Google e pode necessitar de acesso à rede.

## Comandos manuais

A partir de `ccdr-match-tracker`, com o `.env` existente configurado. Parar/reiniciar o backend para carregar o código novo; não sobrescrever os ficheiros de ambiente.

```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic check
.\.venv\Scripts\python.exe -m app.seed
.\.venv\Scripts\python.exe -c "import os; from app.config import get_settings; os.environ['TEST_DATABASE_URL']=get_settings().database_url.get_secret_value(); import pytest; raise SystemExit(pytest.main(['-q','-p','no:cacheprovider']))"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

O comando dos testes usa a ligação do `.env` sem imprimir credenciais. O utilizador PostgreSQL precisa de CREATE na base para os esquemas temporários, eliminados no final. Não são alteradas as tabelas da aplicação pelos testes. Como alternativa, definir `TEST_DATABASE_URL` para uma base dedicada e executar `python -m pytest -q` com o ambiente virtual ativo.

Noutro terminal, a partir de `ccdr-match-tracker`:

```powershell
cd frontend
npm.cmd ci
npm.cmd run lint
npx.cmd tsc --noEmit
npm.cmd run build
npm.cmd run test:e2e
npm.cmd run dev
```

Os testes exigem Microsoft Edge instalado e porta **3100** livre; iniciam e terminam o servidor de produção de testes sem reutilizar o servidor manual na porta 3000. O relatório anterior do Plantel referia a porta 3000; a configuração atual usa 3100 para todos os testes de browser.

Abrir `http://localhost:3000/matches`. Criar um jogo, selecionar titulares/suplentes, guardar, recarregar e alterar a convocatória. Desativar um dos convocados no Plantel e confirmar que continua visível nesse jogo, mas não aparece num jogo novo.

Para o telemóvel, seguir a configuração LAN de [PLANTEL_VALIDACAO.md](PLANTEL_VALIDACAO.md): API pública com IP do PC, origem frontend nos CORS e servidores em `0.0.0.0`. Abrir `http://IP_DO_PC:3000/matches`. Reiniciar o frontend após mudar `NEXT_PUBLIC_API_URL` (e repetir o build se usar produção).

## Limitações

- Substituições concorrentes são atómicas, mas a última gravação vence. Não há controlo de versões nem aviso de edição simultânea nesta fase.
- Não há auditoria das alterações de convocatória. A preservação pedida aplica-se à desativação de jogadores; remover explicitamente um convocado e guardar elimina a associação a esse jogo.
- Nomes antigos de equipas que já sejam duplicados apenas por maiúsculas/espaços não são fundidos automaticamente; é reutilizado o registo com menor ID. Escritas externas à API não usam o bloqueio de resolução de nomes.
- A API continua sem autenticação e destina-se a desenvolvimento local.
- A migração `0003` é compatível com os dados existentes, mas o seu downgrade perde as jornadas.

## Ficheiros desta fase

Criados:

- `backend/alembic/versions/0003_matchday.py`
- `backend/app/match_service.py`
- `backend/tests/test_matches.py`
- `backend/tests/test_match_migration.py`
- `frontend/lib/matches.ts`
- `frontend/app/matches/page.tsx`
- `frontend/app/matches/match-form.tsx`
- `frontend/app/matches/[match_id]/page.tsx`
- `frontend/app/matches/[match_id]/match-detail.tsx`
- `frontend/tests/matches.spec.ts`
- `JOGOS_VALIDACAO.md`

Modificados:

- `backend/app/models.py`, `schemas.py`, `api.py`, `main.py`
- `backend/tests/test_api.py`, `test_player_migration.py`
- `frontend/lib/api.ts`
- `frontend/app/page.tsx`
- `frontend/playwright.config.ts`
- `frontend/README.md`
- `README.md`

O backend não tem histórico Git neste workspace; esta lista compara com o início desta fase. Não foram alteradas migrações anteriores nem acrescentadas dependências.

**Jogos e Convocatórias prontos para teste manual no browser e no telemóvel**, sujeito à configuração LAN. Jogo ao Vivo não foi implementado.
