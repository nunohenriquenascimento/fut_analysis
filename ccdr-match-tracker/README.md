# CCDR Vila Cortez do Mondego — Sub-19

Base de uma aplicação mobile-first de registo de jogos. Frontend Next.js/TypeScript/Tailwind e backend FastAPI/SQLAlchemy, exclusivamente com PostgreSQL e migrações Alembic.

## Estado desta fase

- A página inicial mantém o design original. Plantel abre `/players`; Jogos abre `/matches`. O detalhe `/matches/{match_id}` permite editar o jogo e guardar a convocatória.
- API do Plantel preservada. Jogos: `GET/POST /matches`, `GET/PATCH /matches/{match_id}` e `GET/PUT /matches/{match_id}/squad`.
- Jogo ao Vivo em `/matches/{match_id}/live`: relógio persistido, transições controladas, eventos, resultado derivado e timeline com edição/eliminação. Abrir pelo detalhe de um jogo; o botão inicial Jogo ao Vivo permite escolher o jogo.
- Estatísticas em `/statistics` e `/matches/{match_id}/stats`: comparação por jogo, resumo competitivo da época, atividade, rankings e valores individuais. Calculadas a partir dos dados existentes, sem tabelas agregadas.
- Modelos `User`, `Season`, `Team`, `Player`, `Match`, `MatchSquad` e `MatchEvent`.
- Clientes tipados em `frontend/lib/api.ts`, `frontend/lib/live.ts` e `frontend/lib/statistics.ts`. O contexto resolve os IDs de equipa e época no backend.
- Manifesto web e idioma português preparados. Ainda faltam ícones próprios, service worker, instalação validada e estratégia de sincronização offline para uma PWA completa.
- Não existem autenticação, aplicação de permissões, WebSockets, sincronização multiutilizador ou estatísticas avançadas nesta fase. A API destina-se a desenvolvimento local; autenticação e autorização são necessárias antes da publicação para a equipa técnica.

## Estrutura

O repositório Git existente está dentro de `frontend/`. O backend e este README estão fora desse repositório. Antes de publicar, decidir se o histórico será promovido para um único repositório na raiz ou se serão usados repositórios separados. Esta fase não move nem apaga o `.git` existente.

```text
frontend/
  app/                 página existente, layout e manifesto
  lib/api.ts           tipos e chamadas HTTP
  .env.example
backend/
  app/
    main.py            aplicação e CORS
    api.py             endpoints
    config.py          configuração por ambiente
    database.py        engine, sessões e Base SQLAlchemy
    enums.py           valores do domínio
    models.py          tabelas
    schemas.py         validação e respostas
    seed.py            época e clube iniciais
  alembic/             migração inicial e futuras revisões
  tests/               validação HTTP e integração PostgreSQL
  alembic.ini
  requirements.txt
  requirements-dev.txt
  .env.example
```

## Pré-requisitos no Windows

Python 3.12 ou superior, Node.js 20.9 ou superior com npm, e PostgreSQL instalado e em execução. Os comandos seguintes usam PowerShell. Executar a partir da pasta `ccdr-match-tracker` (não da pasta `SUB-19`).

### 1. Criar a base de dados PostgreSQL

No pgAdmin, criar um utilizador com LOGIN para desenvolvimento e uma base de dados `ccdr_match_tracker` pertencente a esse utilizador. Definir a password apenas localmente. O utilizador deve poder criar tabelas, índices e tipos na base de dados.

Alternativa com as ferramentas PostgreSQL disponíveis no PATH:

```powershell
createuser -U postgres --pwprompt ccdr_app
createdb -U postgres --owner=ccdr_app ccdr_match_tracker
```

Estes comandos pedem as passwords interativamente. Se não forem reconhecidos, usar o pgAdmin ou adicionar a pasta `bin` da instalação PostgreSQL ao PATH. Não reutilizar uma base de dados com tabelas de outros projetos.

### 2. Criar e ativar o ambiente Python

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Se a ativação for bloqueada pela política do PowerShell, permitir scripts apenas nesta sessão e voltar a ativar:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

No `.env`, substituir `YOUR_USER` e `YOUR_PASSWORD` pelos dados locais:

```dotenv
DATABASE_URL=postgresql+psycopg://YOUR_USER:YOUR_PASSWORD@localhost:5432/ccdr_match_tracker
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

Caracteres especiais no utilizador/password têm de ser codificados para URL (por exemplo, `@` → `%40`, `#` → `%23`). Nunca publicar `.env`. A configuração também aceita `postgresql://` e seleciona o driver psycopg 3. Outros motores são rejeitados. O backend lê sempre `backend/.env`, independentemente da diretoria atual.

### 3. Aplicar migrações e iniciar o backend

Ainda na pasta `backend`, com o ambiente ativo:

```powershell
python -m alembic upgrade head
python -m app.seed
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

O seed é explícito e pode ser repetido: cria apenas o clube e a época 2026/27 (1 de julho de 2026 a 30 de junho de 2027). Mostra os IDs efetivos para os pedidos. Não cria utilizadores, passwords, jogadores fictícios ou adversários. Ajustar estas datas em `app/seed.py` antes da primeira execução se necessário.

Swagger: http://localhost:8000/docs. As tabelas são criadas exclusivamente pelo Alembic; iniciar o servidor não altera o esquema.

### 4. Iniciar o frontend

Noutro terminal PowerShell, a partir de `ccdr-match-tracker`:

```powershell
cd frontend
npm ci
Copy-Item .env.example .env.local
npm run dev
```

Abrir http://localhost:3000. O ficheiro `.env.local` contém apenas:

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Variáveis `NEXT_PUBLIC_` são públicas e incorporadas no build; nunca colocar credenciais nelas. Reiniciar o frontend após alterar a configuração. Se `node`/`npm` não forem reconhecidos depois da instalação, reabrir o terminal e o editor para atualizar o PATH. Se apenas `npm.ps1` for bloqueado, usar `npm.cmd` nos comandos.

### 5. Testar a API

Noutro terminal:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/players
Invoke-RestMethod http://localhost:8000/matches
```

`/health` responde `{"status":"ok"}` e verifica apenas que o processo está ativo; não verifica a ligação ao PostgreSQL. As listagens devem devolver arrays vazios numa instalação nova.

Criar um jogador com os IDs resolvidos pelo contexto:

```powershell
$context = Invoke-RestMethod http://localhost:8000/players/context
$player = @{
    name = "Nome do jogador"
    season_id = $context.season_id
    team_id = $context.team_id
    position = "MC"
    shirt_number = 8
} | ConvertTo-Json
Invoke-RestMethod http://localhost:8000/players -Method Post -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($player))
```

Para criar um jogo, usar `/matches` no browser ou enviar o nome do adversário à API. Uma equipa existente é reutilizada, ignorando maiúsculas e espaços redundantes; caso contrário, é criada sem plantel adversário:

```powershell
$context = Invoke-RestMethod http://localhost:8000/players/context
$match = @{
    season_id = $context.season_id
    team_id = $context.team_id
    matchday = 1
    opponent_name = "Nome do adversário"
    kickoff_at = "2026-10-04T15:00:00+01:00"
    is_home = $true
    venue = "Campo de jogos"
} | ConvertTo-Json
Invoke-RestMethod http://localhost:8000/matches -Method Post -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($match))
```

IDs inexistentes devolvem 404; camisola repetida na mesma equipa/época devolve 409; dados inválidos devolvem 422; falha de ligação à base de dados devolve 503. As datas dos jogos exigem fuso horário. As listagens aceitam `season_id`, `team_id`, `limit` (1–200, padrão 100) e `offset` (padrão 0), por exemplo `/players?season_id=1&team_id=1&limit=25&offset=0`.

## Decisões do modelo e evolução

- `Player` representa a inscrição num plantel de uma época. Não se deve mudar a sua época depois de existirem jogos. Uma futura entidade de identidade de atleta permitirá agregar a mesma pessoa entre épocas, sem recorrer ao nome.
- `Team` é partilhada entre épocas e também identifica adversários; `team_id` no jogo é sempre a nossa equipa. `is_home` indica onde jogamos.
- Uma linha `MatchSquad` representa um convocado; `is_starter` distingue titular de suplente. Não convocado corresponde à ausência de linha. O PUT substitui a convocatória numa transação e valida equipa, época, duplicados e estado ativo; jogadores anteriormente convocados permanecem visíveis se forem desativados.
- `Match.matchday` guarda a jornada, obrigatória nos novos jogos. A migração `0003` mantém NULL nos jogos antigos sem jornada conhecida. O PATCH não altera equipa, época ou estado; todos os novos jogos começam em `SCHEDULED`.
- Papéis: `ADMIN`, `COACH`, `VIEWER`; ainda sem controlo de acesso. Posições: `GR`, `DC`, `ALA`, `MDC`, `MC`, `PL`, `UNIVERSAL`.
- Estados preservados: `SCHEDULED`, `FIRST_HALF`, `HALF_TIME`, `SECOND_HALF`, `FINISHED`, `CANCELLED`. O serviço ao vivo permite apenas a sequência agendado → 1.ª parte → intervalo → 2.ª parte → terminado. Não há ação de cancelamento/reabertura nesta fase.
- O relógio acumula tempo efetivamente jogado, incluindo compensação e excluindo intervalo. `clock_started_at` e `elapsed_seconds` persistidos permitem reconstruí-lo após refresh. O servidor calcula período e tempo dos eventos; o cliente não os envia. A timeline ordena por período, segundos e ID.
- `player_id` identifica o marcador; `related_player_id` identifica a assistência opcional. Em substituições representam quem sai e quem entra, obrigatoriamente diferentes. Todos os jogadores associados têm de pertencer à equipa/época e convocatória. Ainda não há controlo de quem está em campo.
- `GOAL` atribui golo à equipa indicada; `OWN_GOAL` atribui à contrária. `PENALTY` não altera o resultado. Só existem remates específicos; a migração `0004` remove `SHOT` e recusa a aplicação enquanto houver eventos antigos sem classificação. Um golo não cria outro remate.
- O resultado é derivado dos eventos e recalculado ao editar/apagar. A convocatória não pode retirar jogadores referenciados em eventos sem os corrigir primeiro. Novos eventos só durante as partes; correções também são permitidas após o fim. Não existe sincronização entre dispositivos; usar Atualizar estado ou refresh.
- Para testar num telemóvel futuramente, configurar o IP LAN no URL público da API e nos CORS e expor os servidores na rede local. `localhost` no telemóvel aponta para o próprio telemóvel. Publicação e PWA exigirão HTTPS e autenticação.

## Verificações e futuras migrações

Na pasta `backend` com ambiente ativo:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m alembic check
```

Os testes HTTP não precisam de PostgreSQL. Os testes PostgreSQL são ignorados sem `TEST_DATABASE_URL`. Criam e removem exclusivamente esquemas temporários `roster_test_<uuid>`; o utilizador precisa de permissão CREATE na base. As tabelas da aplicação não são usadas pelos testes. Incluem upgrade de dados antigos, downgrade permitido e rollback dos downgrades recusados. `alembic check` requer a base de dados configurada e verifica diferenças entre esquema e modelos; os valores do enum são verificados explicitamente nos testes.

Para preparar a base dedicada num terminal de testes, definir `$env:DATABASE_URL` com o URL dessa base, executar `python -m alembic upgrade head`, definir `$env:TEST_DATABASE_URL = $env:DATABASE_URL` e executar `python -m pytest -q`. Não colocar credenciais reais em scripts versionados.

Para alterar o esquema no futuro:

```powershell
python -m alembic revision --autogenerate -m "descrever alteracao"
# Rever a migração gerada antes de a aplicar; alterações de enums exigem atenção manual.
python -m alembic upgrade head
```

Na pasta `frontend`:

```powershell
npm run lint
npx tsc --noEmit
npm run build
```

O layout existente usa fontes Google através de `next/font`; o build pode necessitar de acesso à Internet para as obter.

## Validação do Plantel

Consultar [PLANTEL_VALIDACAO.md](PLANTEL_VALIDACAO.md) para resultados, limitações da migração e comandos de teste no browser/telemóvel.

## Jogos, jornadas e convocatórias

Consultar [JOGOS_VALIDACAO.md](JOGOS_VALIDACAO.md) para o relatório da fase de Jogos, incluindo a migração `0003` e os respetivos testes.

## Jogo ao Vivo

O relatório de Jogos acima documenta essa fase. O Jogo ao Vivo está descrito em [LIVE_VALIDACAO.md](LIVE_VALIDACAO.md), com endpoints, migração `0004`, regras do relógio e resultado, testes e comandos manuais.

## Estatísticas

Consultar [ESTATISTICAS_VALIDACAO.md](ESTATISTICAS_VALIDACAO.md) para endpoints, regras, rankings, testes e comandos manuais. Resumo competitivo apenas de jogos terminados; atividade/eventos de todos os jogos da época, incluindo cancelados com eventos. Convocado/titular conta todas as convocatórias, incluindo jogos agendados. Remates totais não incluem GOAL; não são calculados minutos jogados. Não foi necessária migração nem alteração à lógica do Jogo ao Vivo.
