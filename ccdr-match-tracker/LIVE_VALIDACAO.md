# Jogo ao Vivo — validação de 1 de outubro de 2026

Registo da fase inicial, implementada após a validação manual do Plantel e Jogos/Convocatórias. As fases posteriores acrescentaram Estatísticas, autenticação, permissões e sincronização multiutilizador; consultar os respetivos documentos e [LIVE_WEBSOCKETS_VALIDACAO.md](LIVE_WEBSOCKETS_VALIDACAO.md). PWA offline continua fora do âmbito.

## Interface

Abrir um jogo em `/matches`, entrar no detalhe e escolher **Abrir Jogo ao Vivo**. A página `/matches/{match_id}/live` só apresenta os controlos depois de obter um jogo existente.

- Cabeçalho fixo com CCDR Vila Cortez do Mondego, adversário, resultado, cronómetro e estado.
- Duas zonas: NOSSA EQUIPA e ADVERSÁRIO, com botões de toque grandes. Golo e remates surgem primeiro.
- Golos nossos pedem marcador e assistência opcional; substituições pedem saída/entrada. A seleção contém apenas convocados, incluindo inativos já convocados.
- Outros eventos nossos com associação a jogador usam seleção opcional; canto, livre e penálti têm registo direto. Eventos adversários não pedem jogadores.
- Timeline por período, segundos e ID, com nomes e assistência/entrada. Edição curta de tipo, equipa e jogadores; eliminação sempre com confirmação.
- Resultado e timeline são substituídos pela resposta persistida do servidor após cada alteração. Loading, erros, sucesso e bloqueio de double-submit.
- O botão **Atualizar estado** volta a consultar o servidor. Não existe polling ou sincronização com outro dispositivo.

## Migração `0004_live_events.py`

Remove `SHOT` do enum PostgreSQL `event_type` por substituição transacional do tipo. Mantém os restantes 14 valores e todos os registos existentes. Não altera o esquema do relógio: os campos necessários já existiam.

Antes de alterar o enum, bloqueia `match_events` e verifica eventos `SHOT`. Se existirem, **recusa a migração**, mantendo dados, enum e revisão `0003`. É necessário classificar cada remate antigo, com informação real, como `SHOT_ON_TARGET`, `SHOT_OFF_TARGET` ou `SHOT_BLOCKED`. Não há classificação automática nem eliminação de dados. A base local não tinha esse impedimento e foi atualizada para `0004`.

O downgrade repõe o valor `SHOT` através da substituição inversa do enum, preservando eventos. Ambos os caminhos e o rollback da recusa foram testados em PostgreSQL. Tipos/views/defaults personalizados fora das migrações podem impedir a conversão; executar com o backend parado e backup dos dados importantes.

Migrações anteriores intactas, hashes iguais antes/depois:

```text
0001: 42F6B0C4B3A1F0FE8ECA2B4F1A5AB057F4CE0B2935152D397DE188D8471E6A4E
0002: F228A227165D3A17A9B4DA3AE1292E435CC1DD8D06DA27DC43FA4E7C67DBBEC0
0003: 7B562E85F29C5390C3987BD9386F1AC961E62BFE9683AA01876D3290AB263BD5
```

## Endpoints

| Método | Caminho | Resposta |
| --- | --- | --- |
| GET | `/matches/{match_id}/live` | Snapshot de jogo, relógio, resultado, eventos e convocados |
| POST | `/matches/{match_id}/transition` | Transição e snapshot atualizado |
| GET | `/matches/{match_id}/events` | Eventos ordenados |
| POST | `/matches/{match_id}/events` | Criação, 201, snapshot atualizado |
| PATCH | `/matches/{match_id}/events/{event_id}` | Correção e snapshot atualizado |
| DELETE | `/matches/{match_id}/events/{event_id}` | Eliminação, 200, snapshot atualizado |

`GET /matches/{match_id}` passa a incluir `score: {us, opponent}` calculado. Os endpoints anteriores continuam disponíveis; CORS passa a permitir DELETE.

Transição: `{"status":"FIRST_HALF"}`, depois `HALF_TIME`, `SECOND_HALF`, `FINISHED`. Apenas a transição seguinte é aceite. Repetições/saltos devolvem 409. CANCELLED mantém-se um estado válido, sem ação de cancelamento nesta fase.

Exemplo de golo (IDs ilustrativos; escolher convocados reais):

```json
{"event_type":"GOAL","team":"US","player_id":12,"related_player_id":15}
```

Exemplo de remate adversário:

```json
{"event_type":"SHOT_ON_TARGET","team":"OPPONENT"}
```

POST/PATCH não aceitam `period`, `elapsed_seconds`, `match_id` ou `recorded_by_id` no corpo. O PATCH aceita tipo, equipa, jogadores e notas; campos de jogadores/notas podem ser limpos com NULL. Ao mudar um evento para OPPONENT, limpar também os jogadores. O instante original de um evento nunca é alterado pelo PATCH.

404 para jogo/evento/jogador inexistente; 409 para transição ou associação inválida; 422 para tipos, campos e valores inválidos; 503 para falha de ligação à base. Um evento de outro jogo não pode ser alterado através do ID do jogo atual.

## Relógio

O backend guarda segundos acumulados em `Match.elapsed_seconds` e o início UTC da parte em `clock_started_at`. Em jogo, calcula acumulado + segundos desde o início. Ao terminar a parte, persiste o acumulado e limpa o timestamp. Ao iniciar a segunda, conserva o acumulado e guarda novo início.

O relógio conta **tempo efetivamente jogado acumulado**, incluindo compensação, sem intervalo; não força 45:00/90:00 nem termina automaticamente as partes. Por exemplo: uma primeira parte de 47 minutos faz a segunda começar em 47:00. Não existem pausa manual, reabertura, correção retroativa de tempos ou duração configurável nesta fase.

O frontend usa timestamps e `server_now` enviados pelo backend para reconstruir o relógio e interpola os segundos com `performance.now()`. O estado React apenas apresenta essa projeção. Refresh volta a obter o estado persistido; o relógio do telemóvel não define o tempo dos eventos. A latência de rede pode introduzir uma pequena diferença visual; o instante gravado é sempre o do servidor.

Novos eventos são permitidos apenas em FIRST_HALF ou SECOND_HALF. O servidor atribui período 1/2 e segundos acumulados no instante em que recebe o registo. Editar/eliminar é permitido no intervalo e após o fim, conservando os tempos dos eventos mantidos.

## Eventos e validações

`GOAL`, `OWN_GOAL`, `SHOT_ON_TARGET`, `SHOT_OFF_TARGET`, `SHOT_BLOCKED`, `CORNER`, `FREE_KICK`, `FOUL`, `YELLOW_CARD`, `RED_CARD`, `OFFSIDE`, `SAVE`, `PENALTY`, `SUBSTITUTION`.

- Não existe `SHOT` genérico e um golo não gera remate adicional.
- GOAL US exige marcador; assistência opcional. SUBSTITUTION US exige saída e entrada. Os dois jogadores devem ser diferentes.
- Qualquer jogador associado deve pertencer à equipa/época do jogo e à convocatória. Não é exigida atividade atual, para preservar os convocados entretanto desativados.
- Segundo jogador apenas em GOAL ou SUBSTITUTION. Eventos OPPONENT proíbem ambos os IDs de jogadores.
- Não há validação de quem está em campo, de expulsões ou de reentrada. As regras estão concentradas no serviço para evolução posterior.
- A edição da convocatória recusa a remoção de jogadores referenciados em eventos. É necessário corrigir esses eventos primeiro; desativar um jogador continua a preservar o histórico.

## Resultado e transações

GOAL soma à equipa indicada; OWN_GOAL soma à equipa contrária. PENALTY, remates e restantes eventos não alteram o resultado. Não existem colunas de contadores manuais. O detalhe e os snapshots derivam o resultado dos eventos atuais, corrigindo-o após editar/apagar.

Transições e alterações de eventos bloqueiam a linha do jogo, validam e gravam numa transação. O snapshot de resposta é preparado na mesma transação; falhas de escrita fazem rollback. O GET ao vivo usa o mesmo bloqueio para obter um snapshot coerente. Estes bloqueios protegem a persistência; não constituem sincronização multiutilizador.

## Testes

- **99 testes Python/PostgreSQL aprovados, zero ignorados**. Incluem regressões das fases anteriores, transições, relógio/refresh/intervalo, CRUD, períodos, 14 tipos para ambas as equipas, golos/autogolos, correção do resultado, convocatória, assistência/substituição inválidas, campos temporais rejeitados, eventos de outro jogo, CORS DELETE e rollback em falha de escrita.
- Migração: recusa de SHOT legado sem alteração parcial, preservação dos eventos classificados, downgrade seguro e verificação explícita dos valores do enum.
- `python -m alembic check`: **No new upgrade operations detected**, base local em `0004`.
- Lint, TypeScript e build: **aprovados**.
- **10 testes de browser aprovados** no Microsoft Edge: 4 do Jogo ao Vivo e 6 de regressão. Percursos completos a 360 e 1280 px, relógio após refresh, golo com assistência, evento adversário, editar/eliminar com confirmação, resultado/timeline, segunda parte/fim, jogo inexistente e seleção preservada após erro.

Os testes de browser usam respostas HTTP controladas. O backend é testado com FastAPI/SQLAlchemy/PostgreSQL real em esquemas isolados, removidos no final. Não foi testado um telemóvel físico nem o percurso integrado browser–API real; essa validação fica para o teste manual.

Avisos não bloqueantes: descontinuação futura do transporte `httpx` nos testes Starlette e configuração de cores do terminal Playwright. O build necessita de acesso às fontes Google usadas pelo projeto.

## Comandos manuais

Partindo de `ccdr-match-tracker`, preservar os `.env` existentes. Parar o backend antes de migrar e reiniciá-lo para carregar os novos endpoints.

```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic check
.\.venv\Scripts\python.exe -m app.seed
.\.venv\Scripts\python.exe -c "import os; from app.config import get_settings; os.environ['TEST_DATABASE_URL']=get_settings().database_url.get_secret_value(); import pytest; raise SystemExit(pytest.main(['-q','-p','no:cacheprovider']))"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Os testes requerem permissão CREATE para esquemas temporários; não alteram as tabelas da aplicação. Como alternativa, definir TEST_DATABASE_URL para uma base dedicada e executar `python -m pytest -q` no ambiente virtual.

Noutro terminal, partindo da raiz do projeto:

```powershell
cd frontend
npm.cmd ci
npm.cmd run lint
npx.cmd tsc --noEmit
npm.cmd run build
npm.cmd run test:e2e
npm.cmd run dev
```

Os testes de browser usam Edge e a porta 3100, sem interromper o servidor manual da porta 3000. Abrir `http://localhost:3000/matches`, escolher um jogo com convocatória e abrir Jogo ao Vivo. Iniciar a primeira parte, aguardar alguns segundos, atualizar a página e confirmar a continuidade. Testar golo, assistência, autogolo, edição, eliminação, intervalo, segunda parte e fim.

Para telemóvel na mesma rede: `NEXT_PUBLIC_API_URL=http://IP_DO_PC:8000` no frontend, incluir `http://IP_DO_PC:3000` nos CORS do backend, iniciar uvicorn com `--host 0.0.0.0` e Next com `npm.cmd run dev -- --hostname 0.0.0.0`. Abrir `http://IP_DO_PC:3000/matches`. Reiniciar/reconstruir frontend após mudar o URL da API. Ver também os passos LAN em [PLANTEL_VALIDACAO.md](PLANTEL_VALIDACAO.md).

## Riscos e limites

- O relógio depende da hora do servidor e das ações manuais para terminar cada parte. Não há ajuste de tempos ou transições inversas nesta fase.
- Registar depois de escolher jogadores guarda o instante de submissão, não o instante em que o botão foi inicialmente tocado.
- Na fase inicial não existia sincronização entre dispositivos. Esta limitação foi resolvida na fase documentada em [LIVE_WEBSOCKETS_VALIDACAO.md](LIVE_WEBSOCKETS_VALIDACAO.md), com um worker/instância backend.
- Double-submit é bloqueado no ecrã, mas não há chave de idempotência para repetir pedidos após perda de rede. Se uma resposta se perder, atualizar o estado e verificar a timeline antes de repetir.
- Editar/eliminar eventos não tem auditoria de versões. Não há autenticação; uso local de desenvolvimento.
- `0004` exige classificação manual de eventuais SHOT legados. Não altera dados silenciosamente.

## Ficheiros desta fase

Criados:

- `backend/alembic/versions/0004_live_events.py`
- `backend/app/live_schemas.py`, `live_service.py`, `live_api.py`
- `backend/tests/test_live.py`, `test_live_migration.py`
- `frontend/lib/live.ts`
- `frontend/app/matches/[match_id]/live/page.tsx`, `live-match.tsx`, `event-dialog.tsx`
- `frontend/tests/live.spec.ts`
- `LIVE_VALIDACAO.md`

Modificados:

- `backend/app/enums.py`, `models.py`, `api.py`, `main.py`
- `backend/tests/test_matches.py`
- `frontend/lib/api.ts`
- `frontend/app/matches/[match_id]/match-detail.tsx`
- `frontend/app/page.tsx`
- `frontend/README.md` e `README.md`

Sem novas dependências. O backend continua fora do repositório Git; o inventário compara com o início desta fase.

**Jogo ao Vivo pronto para teste manual no browser e no telemóvel**, sujeito à configuração LAN. Não se avançou para Estatísticas.
# Sincronização entre utilizadores

A fase de WebSockets está descrita em [LIVE_WEBSOCKETS_VALIDACAO.md](LIVE_WEBSOCKETS_VALIDACAO.md), incluindo autenticação, protocolo, reconexão, testes e limite de um worker/instância. As regras Live descritas acima permanecem.
