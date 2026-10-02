# Autenticação e permissões — validação

Atualização posterior: a gestão segura de eliminação/cancelamento de jogos foi retomada e concluída; consultar [JOGOS_ELIMINACAO_VALIDACAO.md](JOGOS_ELIMINACAO_VALIDACAO.md). As referências à suspensão abaixo registam o âmbito da fase de autenticação.

DELETE/CANCEL de jogos permanece suspenso. Esta fase implementa autenticação real e autorização sem aceitar identidade ou papel livremente enviado pelo browser.

## Estratégia

- Passwords com scrypt (`N=131072`, `r=8`, `p=1`, salt aleatório de 16 bytes). Passwords novas: 12–128 caracteres; nunca devolvidas pela API ou guardadas em texto simples.
- Cookie de sessão opaco, aleatório de 32 bytes, HttpOnly, SameSite=Lax, Path=/, sem Domain. A base guarda apenas SHA-256 do identificador, utilizador, token CSRF e expiração absoluta (8 horas por defeito; configurável entre 1 e 24). Sem renovação automática da validade.
- `AUTH_COOKIE_SECURE=true` ativa Secure e o nome `__Host-ccdr_session` para HTTPS. Em desenvolvimento HTTP usa `ccdr_session`.
- O utilizador e o papel são consultados na base em cada pedido. Contas inativas, sessões expiradas, revogadas ou falsas recebem 401. Permissões insuficientes recebem 403.
- Login cria um identificador novo e revoga a sessão anterior desse browser. Logout revoga a sessão na base e elimina o cookie; reutilizar o identificador anterior falha.
- Escritas exigem origem configurada e `X-CSRF-Token` emitido pelo servidor. Login exige origem autorizada e `X-Requested-With: CCDR`. CORS aceita credenciais exclusivamente nas origens explícitas configuradas.
- Apenas o token CSRF fica em memória JavaScript. Nenhuma credencial de sessão é guardada em localStorage/sessionStorage.
- Login limitado, em PostgreSQL e partilhado entre processos, a 10 tentativas por email e 30 por IP em 15 minutos, incluindo sucessos. Excesso: 429 com Retry-After. Não se confia em X-Forwarded-For.
- Respostas privadas usam Cache-Control: no-store. Erros de validação de autenticação/utilizadores omitem os valores recebidos.

Referências: [sessões OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html), [CSRF OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html), [scrypt Python](https://docs.python.org/3/library/hashlib.html#hashlib.scrypt).

## Endpoints

| Endpoint | Acesso / resultado |
|---|---|
| POST /auth/login | Público; email/password válidos; cookie e `{user, csrf_token}` |
| GET /auth/me | Sessão ativa; `{user, csrf_token}` |
| POST /auth/logout | Sessão ativa + CSRF; 204 |
| GET /users | ADMIN; lista de contas sem hashes/passwords |
| POST /users | ADMIN + CSRF; cria conta; 201 |
| PATCH /users/{user_id} | ADMIN + CSRF; edita nome/email/password/papel/atividade; 200, 404 ou 409 |

Todos os endpoints existentes de Plantel, equipas, Jogos, convocatórias, Live e Estatísticas exigem sessão. `/health` continua público; a documentação OpenAPI também. Não existe autorregisto público nem DELETE de utilizadores ou jogos.

## Matriz de permissões

| Operação | ADMIN | COACH | VIEWER |
|---|---|---|---|
| Consultar Plantel, Jogos, convocatórias, Live, Estatísticas | Sim | Sim | Sim |
| Criar/editar/ativar/desativar jogadores e editar emblemas | Sim | Sim | Não |
| Criar/editar jogos e guardar convocatórias | Sim | Sim | Não |
| Transições Live e criar/editar/eliminar eventos | Sim | Sim | Não |
| Consultar/criar/editar/desativar contas e definir passwords | Sim | Não | Não |
| DELETE/CANCEL de jogos | Suspenso | Suspenso | Suspenso |

O frontend usa `/auth/me` para apresentar ações; a autorização definitiva é sempre do backend. Alterar papel, email, password ou atividade revoga todas as sessões dessa conta. Alterar apenas o nome mantém as sessões. Desativação substitui eliminação física e preserva referências históricas.

O último ADMIN ativo com credenciais não pode ser desativado ou despromovido: 409. Bootstrap, alterações de contas e escritas autorizadas partilham um bloqueio transacional PostgreSQL, para impedir corridas de permissões e despromoções concorrentes. Contas antigas sem password não são consideradas administradores capazes de iniciar sessão.

## Autoria dos eventos e regressões

O campo existente `MatchEvent.recorded_by_id` passa a receber exclusivamente o ID autenticado no backend ao criar um evento (equivalente ao `created_by` pedido). O cliente não pode fornecê-lo. A API de leitura expõe esse campo; editar um evento mantém o autor original. Eventos antigos continuam com a autoria que já tinham, incluindo NULL.

Não foram alterados cálculos de Estatísticas, regras de convocatória, transições/relógio Live ou regras de Plantel. A alteração funcional transversal é exigir sessão/permissões e registar a autoria dos novos eventos.

## Migração

`backend/alembic/versions/0006_auth_users.py`, dependente de `0005`:

- `users.password_hash`, nullable para preservar contas antigas sem lhes atribuir passwords predefinidas.
- Índice único sobre `lower(users.email)`; evita contas ambíguas por diferença de maiúsculas.
- Tabelas `auth_sessions` e `login_throttles`, com índices de utilizador/expiração.
- Nenhuma migração anterior alterada. Upgrade/downgrade preserva utilizadores, jogos e eventos; downgrade elimina credenciais e sessões desta fase.

A base local foi atualizada de `0005` para `0006`. Não foi criado um ADMIN real automaticamente. Se outra instalação tiver emails duplicados apenas por maiúsculas/minúsculas, a migração recusa o índice; corrigir esses duplicados explicitamente antes de repetir o upgrade.

## Ficheiros desta fase

Criados:

- `backend/app/auth.py`, `auth_api.py`, `auth_schemas.py`, `create_admin.py`.
- `backend/alembic/versions/0006_auth_users.py`.
- `backend/tests/test_auth.py`, `test_auth_migration.py`.
- `frontend/components/auth-provider.tsx`.
- `frontend/app/login/page.tsx`, `frontend/app/users/page.tsx`.
- `frontend/tests/auth-fixture.ts`, `auth.spec.ts`.
- `AUTH_VALIDACAO.md`.

Modificados:

- `backend/app/models.py`, `config.py`, `main.py`, `api.py`, `live_api.py`, `live_schemas.py`, `statistics_api.py`.
- `backend/.env.example`, `backend/tests/conftest.py`, `test_media_assets.py` (a verificação Alembic passa a usar o head atual).
- `frontend/lib/api.ts`, `live.ts`; `frontend/app/layout.tsx`; `frontend/components/app-header.tsx`.
- `frontend/app/players/page.tsx`, `matches/page.tsx`, `matches/[match_id]/match-detail.tsx`, `matches/[match_id]/live/live-match.tsx`.
- `frontend/tests/players.spec.ts`, `matches.spec.ts`, `live.spec.ts`, `statistics.spec.ts`, `layout.spec.ts` (sessão ADMIN nas regressões existentes).
- `README.md`.

Outras alterações que já existiam no workspace pertencem às fases anteriores; não foram revertidas ou atribuídas a esta fase.

## Primeiro ADMIN e arranque manual

Na pasta `backend`, usando a `.venv` existente:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic check
.\.venv\Scripts\python.exe -m app.seed
.\.venv\Scripts\python.exe -m app.create_admin
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

`create_admin` pede nome, email e password com confirmação; password não é mostrada nem passada na linha de comandos. Só funciona enquanto não existir um ADMIN ativo com credenciais. Pode atribuir credenciais a uma conta antiga correspondente ao email, sem alterar a sua identidade histórica. Depois disso, criar contas em `/users`, autenticado como ADMIN. Não há password por defeito.

Noutro terminal, na pasta `frontend`:

```powershell
npm.cmd run dev
```

Abrir `http://localhost:3000/login`, entrar com o ADMIN e criar contas COACH/VIEWER. Usar `localhost` tanto no frontend como em `NEXT_PUBLIC_API_URL=http://localhost:8000`, evitando misturar `localhost` e `127.0.0.1`.

Para HTTPS em produção: `AUTH_COOKIE_SECURE=true`, CORS_ORIGINS com o endereço HTTPS exato do frontend e frontend/API no mesmo site (por exemplo app.clube.pt e api.clube.pt). Esta estratégia não suporta sites independentes com bloqueio de cookies de terceiros. Configurar o proxy para permitir apenas origens previstas; o limite por IP pode agrupar utilizadores atrás de um proxy, pois a aplicação não aceita cabeçalhos de IP não confiáveis.

Para telemóvel na LAN: usar o mesmo IP LAN nos dois URLs, configurar NEXT_PUBLIC_API_URL para `http://IP:8000` e CORS_ORIGINS para `http://IP:3000`, reiniciar frontend/backend e expor os servidores nessa rede com `--host 0.0.0.0` / `--hostname 0.0.0.0`. HTTP é configuração de teste local; a publicação usa HTTPS e Secure.

## Testes

- Python/PostgreSQL: **151 testes passaram**, incluindo todas as regressões anteriores e 37 testes novos de autenticação/migração.
- `python -m alembic check`: **passou**, sem operações novas detetadas; head local `0006`.
- `npm.cmd run lint`: **passou**.
- `npx.cmd tsc --noEmit`: **passou**.
- `npm.cmd run build`: **passou**, incluindo `/login` e `/users`.
- E2E: **27 testes passaram**, incluindo 7 novos de autenticação e os 20 existentes; testes existentes mantidos com uma sessão ADMIN simulada apenas nas fixtures.

Backend cobre hash/salt, login/logout/replay, expiração, cookies Secure, sessões falsas, origens/CSRF, limitação de tentativas, contas antigas, gestão ADMIN, proteção do último ADMIN com duas despromoções simultâneas, revogação e autoria dos eventos. Os E2E verificam login/erro/logout/redirect, permissões dos três papéis, gestão de contas, sessão expirada e 360 px. Os E2E simulam as respostas HTTP; os testes backend usam sessões reais e PostgreSQL em schemas descartáveis.

Repetir validação, na pasta `backend` (o utilizador PostgreSQL precisa de CREATE SCHEMA; o URL nunca é impresso):

```powershell
.\.venv\Scripts\python.exe -c "import os; from app.config import get_settings; os.environ['TEST_DATABASE_URL']=get_settings().database_url.get_secret_value(); import pytest; raise SystemExit(pytest.main(['-q','-p','no:cacheprovider']))"
.\.venv\Scripts\python.exe -m alembic check
```

Na pasta `frontend`:

```powershell
npm.cmd run lint
npx.cmd tsc --noEmit
npm.cmd run build
npm.cmd run test:e2e
```

Avisos observados: depreciação Starlette/httpx nos testes Python e NO_COLOR/FORCE_COLOR em Playwright. No Windows, o servidor temporário Playwright pode demorar a terminar mesmo depois das asserções; não é falha da aplicação.

## Roteiro manual

1. Sem sessão, abrir Plantel, Jogos ou Estatísticas: redirecionamento para `/login`.
2. Password errada: mensagem genérica; credenciais válidas: entrar e regressar à página pedida.
3. ADMIN: criar COACH/VIEWER; editar/desativar contas; tentar desativar/despromover o último ADMIN e confirmar bloqueio.
4. COACH: gerir Plantel/Jogos/convocatória/Live; sem acesso à gestão de contas.
5. VIEWER: consultar todas as áreas; sem ações de escrita. Pedidos diretos de escrita continuam bloqueados no backend.
6. Criar um evento e confirmar `recorded_by_id` nos dados; editar sem mudar o autor.
7. Logout: regressar ao login; o cookie anterior deixa de autenticar. Desativar/mudar credenciais de outra conta invalida as suas sessões.
8. Confirmar login e gestão de contas a 360 px, e repetir no telemóvel com a configuração LAN.

Limites desta fase: sem recuperação por email, MFA ou autoalteração de password por COACH/VIEWER; o ADMIN define novas passwords. Sem funcionamento offline autenticado. Escritas partilham um bloqueio global curto, apropriado à aplicação atual; maior escala exigirá revisão de concorrência e limites no proxy.

Autenticação pronta para teste manual após criar o primeiro ADMIN e iniciar os servidores. DELETE/CANCEL de jogos não foi implementado.
# Configuração de produção posterior

Consultar [PRODUCAO_DEPLOY.md](PRODUCAO_DEPLOY.md): cookie HttpOnly mantém-se; `AUTH_COOKIE_SAMESITE=lax` é o default local/same-site e `none` exige Secure para domínios cross-site. `APP_ENV=production` exige Secure e origens HTTPS explícitas. CSRF, autorização e revogação permanecem. Cookies de terceiros bloqueados exigem domínios próprios same-site para compatibilidade consistente.
