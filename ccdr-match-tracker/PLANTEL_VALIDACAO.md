# Plantel — validação de 1 de outubro de 2026

Implementação revista apenas no âmbito do Plantel. Não foram acrescentadas funcionalidades de Jogos, Convocatórias ou Eventos.

## Ficheiros

Já existentes ao retomar e revistos: `backend/alembic/versions/0002_player_positions.py`, `backend/app/enums.py`, `models.py`, `schemas.py`, `api.py`, `roster.py`, `seed.py`, `main.py`, testes backend, `frontend/lib/api.ts`, `frontend/app/players/page.tsx` e ligação em `frontend/app/page.tsx`. Não foi necessário alterar o código funcional destes ficheiros nesta revisão.

Criados nesta revisão:

- `backend/tests/conftest.py`
- `backend/tests/test_player_migration.py`
- `frontend/playwright.config.ts`
- `frontend/tests/players.spec.ts`
- `PLANTEL_VALIDACAO.md`

Modificados nesta revisão:

- `backend/tests/test_api.py`
- `backend/tests/test_players.py`
- `frontend/package.json` e `frontend/package-lock.json`
- `frontend/.gitignore`
- `frontend/README.md`
- `README.md`

O backend não tem histórico Git neste workspace. A classificação acima compara com o início desta revisão; não permite reconstruir todas as alterações de sessões anteriores.

## Migração PostgreSQL

`0001` não foi alterada. SHA-256 antes e depois desta revisão: `42F6B0C4B3A1F0FE8ECA2B4F1A5AB057F4CE0B2935152D397DE188D8471E6A4E`. Sem uma cópia histórica não se pode comprovar a identidade com versões de sessões anteriores.

`0002` cria um enum temporário e converte a coluna `players.position`:

| Antiga | Final |
| --- | --- |
| GOALKEEPER | GR |
| DEFENDER | DC |
| MIDFIELDER | MC |
| FORWARD | PL |

O enum final contém exatamente `GR`, `DC`, `ALA`, `MDC`, `MC`, `PL`, `UNIVERSAL`. O tipo antigo é removido e o novo assume o nome `player_position`. Não há DELETE, DROP TABLE nem recriação de jogadores. IDs, equipa, época, nomes, números (incluindo NULL legado), estado e datas são preservados. Tudo decorre na transação Alembic do PostgreSQL.

O downgrade bloqueia a tabela antes da verificação e recusa a operação se encontrar `ALA`, `MDC` ou `UNIVERSAL`. A falha mantém dados, enum e revisão `0002`. Só é reversível automaticamente para `GR`, `DC`, `MC`, `PL`. Reatribuir as outras posições exige uma decisão explícita sobre o significado dos dados; não há conversão automática sem perda semântica.

A migração exige bloqueio exclusivo da tabela e pode bloquear pedidos concorrentes. Executar com o backend parado. Dependências personalizadas no enum, defaults ou views acrescentadas fora das migrações não foram testadas; podem impedir a alteração, com rollback transacional. Fazer backup antes de aplicar numa base com dados importantes.

A base local estava em `0001`, com zero jogadores. Foi atualizada para `0002`, seguida de `alembic check` e seed. O teste com dados antigos foi realizado em esquemas isolados, sem inserir jogadores fictícios no plantel local.

## Endpoints finais do Plantel

| Método | Caminho | Resultado |
| --- | --- | --- |
| GET | `/players/context` | Resolve por nome a época `2026/27` e o clube `CCDR Vila Cortez do Mondego`; 404 se faltar configuração |
| GET | `/players` | Lista ativos e inativos, com filtros de época/equipa e paginação |
| POST | `/players` | Cria jogador ativo; 201 |
| PATCH | `/players/{player_id}` | Edita nome, número, posição ou estado; 200 |

Duplicação de número na mesma equipa/época: 409, incluindo números de inativos. Jogador inexistente: 404. Dados inválidos: 422. Falha de ligação à base: 503. Desativação altera apenas `is_active`, sem eliminar o registo. O frontend obtém IDs do contexto; os testes de browser usam IDs 17 e 23 para verificar este contrato.

## Resultados

- Python/PostgreSQL: **40 testes passaram, zero ignorados**. Cobrem as sete posições, criação/listagem, edições individuais e combinadas, desativação/reativação, preservação do registo, duplicados na criação/edição, 404/422, contexto, CORS PATCH e migrações.
- `python -m alembic check`: **No new upgrade operations detected**, na base local e nos testes de migração.
- Frontend: lint, TypeScript e build concluídos com sucesso.
- Playwright/Microsoft Edge: **2 cenários passaram**, a 360 e 1280 px. Cobrem carregamento, criação, edição, ativação/desativação, erros 404/409/422/503/rede, retry, campos desativados durante gravação, bloqueio de submissões repetidas e ausência de overflow horizontal.
- Os testes de browser usam HTTP simulado; os testes backend usam PostgreSQL real. Não foi realizado teste num telemóvel físico nem teste integrado browser–API real.

Avisos não bloqueantes: Starlette anuncia a futura substituição do transporte de testes `httpx`; Playwright emite aviso sobre variáveis de cor do terminal. O primeiro build falhou por acesso às fontes Google; a repetição com rede passou. Não foram alteradas as fontes nem o design.

## Comandos manuais — Windows/PowerShell

Partindo de `ccdr-match-tracker`, com `.env` já configurado. Não substituir o `.env` existente.

Terminal backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic check
.\.venv\Scripts\python.exe -m app.seed
.\.venv\Scripts\python.exe -c "import os; from app.config import get_settings; os.environ['TEST_DATABASE_URL']=get_settings().database_url.get_secret_value(); import pytest; raise SystemExit(pytest.main(['-q','-p','no:cacheprovider']))"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

O comando Python de testes usa a ligação do `.env` sem imprimir credenciais. Os testes criam e removem esquemas próprios; não migram nem alteram as tabelas da aplicação. Pode também definir `TEST_DATABASE_URL` para uma base dedicada e executar `python -m pytest -q` no ambiente virtual.

Terminal frontend, novamente a partir da raiz do projeto:

```powershell
cd frontend
npm.cmd ci
npm.cmd run lint
npx.cmd tsc --noEmit
npm.cmd run build
npm.cmd run test:e2e
npm.cmd run dev
```

Os testes de browser exigem Microsoft Edge instalado e porta 3000 livre; iniciam e terminam o servidor de produção automaticamente, após o build. Abrir `http://localhost:3000/players` para testar manualmente.

### Telemóvel na mesma rede Wi-Fi

1. Executar `ipconfig` e obter o IPv4 LAN do PC, por exemplo `192.168.1.50`.
2. Em `frontend/.env.local`, definir `NEXT_PUBLIC_API_URL=http://192.168.1.50:8000`, substituindo pelo IP real.
3. Em `backend/.env`, incluir a origem exata: `CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000","http://192.168.1.50:3000"]`.
4. Parar os servidores anteriores e iniciá-los nos respetivos diretórios:

```powershell
# backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```powershell
# frontend
npm.cmd run dev -- --hostname 0.0.0.0
```

5. Permitir Python/Node na firewall apenas na rede privada, se solicitado. Abrir `http://192.168.1.50:3000/players` no telemóvel. Não usar `localhost` no telemóvel. Se usar produção, repetir o build depois de alterar `NEXT_PUBLIC_API_URL`.

Confirmar criação, edição, número repetido, desativação/reativação e persistência após recarregar. A aplicação continua sem autenticação e destina-se a desenvolvimento local.

**Fase pronta para testes manuais no browser e telemóvel**, com a configuração LAN acima. A validação em dispositivo físico fica a cargo deste teste manual.
