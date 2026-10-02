# Produção: Vercel + Railway

**Arquitetura anterior.** O plano atual elimina cross-site e Vercel, servindo frontend/API/WebSocket no mesmo domínio Railway: [RAILWAY_SAME_ORIGIN.md](RAILWAY_SAME_ORIGIN.md). Este documento permanece como referência/rollback da fase anterior.

Preparação de 2 de outubro de 2026. Nenhum serviço foi criado, publicado ou alterado na cloud. Sem alterações ao esquema; Alembic continua em `0006`. A configuração abaixo exige intervenção manual nos painéis.

## Arquitetura e domínios

Next.js na Vercel; FastAPI e WebSockets no mesmo serviço Railway; PostgreSQL num serviço Railway separado, ligado pela rede privada. Backend com **um worker, uma réplica e uma região**. Hub Live em memória, sem Redis.

Escolher os domínios antes de configurar autenticação:

| Frontend / API | Relação | Cookie | Condição |
|---|---|---|---|
| `https://app.seudominio.pt` / `https://api.seudominio.pt` | Cross-origin, same-site | `SameSite=Lax; Secure` | Opção recomendada para browser e telemóvel |
| `https://projeto.vercel.app` / `https://api.up.railway.app` | Cross-site | `SameSite=None; Secure` | Depende de cookies de terceiros permitidos |

Domínios diferentes não implicam sempre sites diferentes: dois subdomínios HTTPS do mesmo domínio registável são same-site. `Lax` não envia o cookie nas chamadas fetch/WebSocket cross-site da Vercel para o domínio Railway. `None` permite essa utilização, mas não ultrapassa o bloqueio de cookies de terceiros. Não é possível garantir login em todos os browsers com os domínios independentes das plataformas; para esse requisito, usar os subdomínios próprios recomendados. O backend não define `Domain`: cookie fica exclusivamente no host da API, preservando `__Host-`. [Cookies e SameSite](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies), [bloqueio de cookies de terceiros](https://developer.mozilla.org/en-US/docs/Web/Privacy/Guides/Third-party_cookies).

Não alterar para `Domain=.vercel.app`, não enviar tokens pela URL e não guardar sessão em localStorage. Não existe proxy/BFF nesta fase.

## Variáveis

Os ficheiros `.env.production.example` são referências sem secrets; não são carregados automaticamente pelo backend nem devem ser copiados para o repositório com credenciais reais. Configurar nos painéis. `.env`, `.env.production` e `.env.local` continuam ignorados. A imagem Docker inclui apenas código, migrações e dependências.

| Plataforma | Variável | Valor / regra |
|---|---|---|
| Railway backend | `APP_ENV` | `production` |
| Railway backend | `DATABASE_URL` | Referência `${{Postgres.DATABASE_URL}}`; substituir `Postgres` pelo nome do serviço |
| Railway backend | `CORS_ORIGINS` | JSON: `["https://app.seudominio.pt"]` ou o URL real Vercel |
| Railway backend | `AUTH_COOKIE_SECURE` | `true` |
| Railway backend | `AUTH_COOKIE_SAMESITE` | `lax` para same-site; `none` para cross-site |
| Railway backend | `AUTH_SESSION_HOURS` | `8`; permitido 1–24 |
| Railway backend | `PORT` | Fornecido pela plataforma; não fixar manualmente |
| Vercel frontend | `NEXT_PUBLIC_API_URL` | `https://api.seudominio.pt` ou domínio público Railway, sem path |

`DATABASE_URL` e credenciais PostgreSQL pertencem exclusivamente ao backend/serviço PostgreSQL. Nenhuma password de ADMIN é configurada no frontend ou no repositório. Não é necessária chave JWT: as sessões opacas existentes são persistidas na base e revogáveis.

A URL pública da API é incorporada no build do frontend: alterações exigem novo deployment. Configurar no ambiente **Production** da Vercel. Preview deve usar backend/base separados e origem explicitamente autorizada; nunca permitir `*.vercel.app` ou um wildcard para facilitar previews. O build Vercel rejeita URL ausente, HTTP, localhost, credenciais, query, fragmento ou path. [Variáveis Vercel](https://vercel.com/docs/environment-variables), [NEXT_PUBLIC no build](https://vercel.com/academy/nextjs-foundations/env-and-security).

Em `APP_ENV=production`, o backend recusa cookie não Secure, origens HTTP/localhost e ausência de configuração explícita de CORS/SameSite. `SameSite=None` sem Secure é rejeitado em qualquer ambiente. Desenvolvimento continua com HTTP, Lax e Secure=false, conforme `.env.example`.

## Railway: backend e PostgreSQL

1. Criar projeto e serviço PostgreSQL com volume persistente e política de backup. Referenciar a sua `DATABASE_URL` no serviço backend; não publicar a base para o frontend. A configuração aceita `postgresql://`, `postgres://` e `postgresql+psycopg://`, normalizando para psycopg 3 e preservando opções como `sslmode`. `psycopg[binary]` já existe nas dependências. Na ligação externa, usar o URL público fornecido pela plataforma e a configuração TLS adequada; não desligar validação TLS para resolver erros. [PostgreSQL Railway](https://docs.railway.com/databases/postgresql).
2. Criar serviço backend a partir do código, com **Root Directory = `backend`**, relativamente à raiz `ccdr-match-tracker`. Se o repositório selecionado começa em `SUB-19`, usar `ccdr-match-tracker/backend`. Confirmar que o contexto de build contém `Dockerfile`, `requirements.txt`, `app/`, `alembic/` e `alembic.ini`.
3. Railway deteta `backend/Dockerfile`. Python 3.12 slim; instalação `python -m pip install --no-cache-dir -r requirements.txt`; aplicação executada como utilizador sem privilégios. Build command adicional no painel: deixar vazio, porque o Dockerfile instala as dependências. Não configurar Railpack simultaneamente. [Dockerfiles Railway](https://docs.railway.com/builds/dockerfiles).
4. Start command: `python -m app.start`. Pode ficar vazio para usar o CMD idêntico da imagem. O módulo lê `PORT`, liga a `0.0.0.0` e força `workers=1`, mesmo que exista `WEB_CONCURRENCY`.
5. Healthcheck Path: `/health`, timeout 60 segundos. Resposta pública `200 {"status":"ok"}`, sem autenticação ou secrets. Endpoint existente reutilizado: verifica o processo, não a disponibilidade/migração da base. Confirmar a base com Alembic e pedidos autenticados antes de disponibilizar aos utilizadores. [Healthchecks Railway](https://docs.railway.com/deployments/healthchecks).
6. Replicas = 1, uma região. Desativar Serverless/App Sleeping inicialmente. Não adicionar cron/migração em pre-deploy, nem `alembic upgrade` no start/build. Gerar domínio público e configurar domínio próprio, se escolhido. Verificar certificado HTTPS antes de login.

O start não confia em headers de proxy arbitrários para identificar clientes (`proxy_headers=False`). Não usar `--forwarded-allow-ips="*"`. Consequência: o limite existente de login por IP pode agrupar clientes atrás do proxy Railway; o limite por email também permanece. Se isso produzir 429 legítimos, será necessária uma estratégia explícita de proxy confiável, sem confiar livremente no browser. Não foi alterada a regra de throttling nesta fase.

## Alembic e primeiro ADMIN

Não existem migrações automáticas, geração automática nem downgrade no deployment. O healthcheck pode passar antes da migração; não anunciar a aplicação nessa situação.

Instalar/autenticar Railway CLI na máquina do operador, selecionar projeto/ambiente/serviço e abrir uma sessão interativa no container backend:

```sh
railway login
railway link
railway ssh --service NOME_DO_BACKEND
```

Dentro do container:

```sh
cd /app
python -m alembic current
python -m alembic heads
```

Antes do upgrade, confirmar base e ambiente, rever as migrações e fazer backup se houver dados. Para uma base nova, o upgrade cria o esquema; para uma base existente, rever especialmente a classificação de SHOT legado exigida pela `0004` e o documento Live. Não usar `stamp` para evitar migrações. Executar explicitamente:

```sh
python -m alembic upgrade head
python -m alembic current
python -m alembic check
```

O head esperado desta entrega é `0006`; nenhum ficheiro de migração anterior foi modificado. Um erro exige investigar antes de tentar novamente. Código antigo compatível pode ser redeployado; não executar downgrade destrutivo como rollback automático.

Preparar o contexto inicial de clube/época apenas numa base nova:

```sh
python -m app.seed
python -m app.create_admin
```

`create_admin` pede nome, email, password e confirmação de forma interativa; password sem eco, sem argumentos, sem default. Mantém hash seguro e proteção do ADMIN existente. Depois, outras contas são criadas pelo ADMIN em `/users`. SSH executa no container, com rede privada Railway; `railway run` na máquina local não dá acesso automático a `*.railway.internal`. [SSH Railway](https://docs.railway.com/cli/ssh).

## Vercel

Framework preset **Next.js**; Root Directory **`frontend`**, relativamente à raiz do projeto. O frontend já tem um repositório Git próprio: se esse repositório for importado diretamente, Root Directory é `.`. A Vercel deve receber todos os ficheiros frontend e media; o Railway deve receber backend e migrações. Não assumir que um push do repositório exterior envia as alterações do repositório frontend.

Install command: `npm ci`. Build command: `npm run build`. Output Directory e restantes opções: defaults Next.js, sem static export. Selecionar Node.js 22.x. Configurar `NEXT_PUBLIC_API_URL` no painel antes do primeiro build. Não existe backend FastAPI na Vercel.

Adicionar domínio público Vercel/domínio próprio e confirmar HTTPS. O seu Origin exato — scheme e host, sem barra final ou path — deve constar em `CORS_ORIGINS` Railway. Depois de mudar domínio/URL da API, atualizar ambas as plataformas, reconstruir frontend e voltar a fazer login. Sessões no hostname anterior não são partilhadas automaticamente.

## Cookies, CORS, CSRF e WSS

- Cookie `__Host-ccdr_session`, HttpOnly, Secure, Path=/, sem Domain. `SameSite` escolhido explicitamente; logout remove o cookie com os mesmos atributos e revoga a sessão persistida.
- `fetch` autenticado mantém `credentials: "include"`. Sessão não fica disponível ao JavaScript; CSRF fica apenas em memória.
- CORS com origens explícitas e `allow_credentials=True`; métodos GET/POST/PATCH/PUT/DELETE; headers Content-Type, X-CSRF-Token e X-Requested-With. Preflight da origem correta é permitido; outras origens não recebem acesso credentialed.
- Login mantém Origin validado e `X-Requested-With: CCDR`. Escritas/logout mantêm sessão, autorização, Origin e CSRF associados à sessão. SameSite=None não remove nenhuma destas proteções.
- WebSocket mantém cookie automático, Origin exato, utilizador ativo e sessão válida, revalidada periodicamente. Não recebe role/user_id/token pela query. Endpoint no **mesmo host Railway da API**: `wss://api.seudominio.pt/ws/matches/{match_id}/live`.
- `frontend/lib/live-socket.ts` deriva WSS de HTTPS; não há variável WebSocket separada. Heartbeat/backoff, snapshot/refetch e funcionamento HTTP sem socket continuam existentes. Railway suporta WebSockets na rede pública com TLS. [Rede Railway](https://docs.railway.com/networking/public-networking/specs-and-limits).

## Checklist de deploy manual

1. Rever/guardar os ficheiros desta entrega nos repositórios corretos, incluindo media, sem `.env` reais. Escolher domínios same-site ou aceitar explicitamente as limitações cross-site.
2. Criar PostgreSQL Railway e backups; criar backend com Root Directory correto e Dockerfile.
3. Configurar variáveis Railway, uma réplica/região, start e `/health`; deixar pre-deploy vazio. Confirmar no painel que nenhuma automação de migração antiga está configurada.
4. Gerar domínio backend, completar DNS/TLS e identificar o domínio frontend que será autorizado.
5. Fazer o deployment backend manual; verificar health e logs sem divulgar secrets. Validar instalação da imagem — não foi possível construir Docker neste ambiente local, onde Docker não está instalado.
6. Abrir SSH; rever versão/backup e executar upgrade manual. Confirmar `0006` e Alembic check. Executar seed numa base nova e criar primeiro ADMIN.
7. Importar frontend Vercel com preset/root corretos, Node 22, `npm ci`, `npm run build` e `NEXT_PUBLIC_API_URL` Production HTTPS. Fazer deployment manual.
8. Confirmar Origin frontend final em Railway; redeploy backend se mudou. Confirmar cookie Secure/HttpOnly/SameSite no browser, `/auth/me` autenticado e logout/revogação. Testar telemóvel e browsers com bloqueio de cookies de terceiros; para compatibilidade consistente, concluir os domínios próprios same-site.
9. Testar ADMIN/COACH/VIEWER, Plantel, convocatória, Estatísticas, cancelamento e eliminação. Em dois dispositivos, abrir o mesmo Live, criar/editar/eliminar evento e mudar de parte; verificar WSS, reconexão e HTTP quando o socket cai.
10. Confirmar que a réplica/worker continua em 1, configurar monitorização externa e validar backup/restauro antes de utilização regular. `/health` não verifica todos os serviços e o healthcheck Railway de deployment não substitui monitorização contínua.

## Validação e limitações

Resultados locais: **221 testes Python/PostgreSQL passaram**, **40 testes frontend/Playwright passaram**, lint e TypeScript passaram, build Next.js normal e build com `VERCEL=1`/API HTTPS passaram; `python -m alembic check` sem novas operações. Uma advertência de depreciação TestClient/httpx, sem falhas. E2E de páginas usam mocks HTTP/WebSocket; testes backend exercitam PostgreSQL e sessões reais. Não comprovam DNS, TLS ou política de cookies de terceiros na cloud.

Repetir a partir de `backend`, com `TEST_DATABASE_URL` definido para PostgreSQL de testes:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m alembic check
```

A partir de `frontend`:

```powershell
npm.cmd run lint
npx.cmd tsc --noEmit
npm.cmd run build
npm.cmd run test:e2e
```

Ficheiros criados nesta fase: `backend/Dockerfile`, `backend/.dockerignore`, `backend/app/start.py`, `backend/.env.production.example`, `backend/tests/test_auth_production.py`, `frontend/.env.production.example`, `frontend/tests/production.spec.ts` e `PRODUCAO_DEPLOY.md`.

Ficheiros modificados nesta fase: `.gitignore`, `backend/.env.example`, `backend/app/config.py`, `backend/app/auth_api.py`, `frontend/.gitignore`, `frontend/next.config.ts`, `README.md`, `AUTH_VALIDACAO.md` e `LIVE_WEBSOCKETS_VALIDACAO.md`.

Testes da configuração: URL Railway normalizada para psycopg, Secure/SameSite, origens explícitas, CSRF, logout, handshake WSS, PORT e um worker. Frontend verifica rejeição de configuração Vercel inválida e derivação WSS. Build local com `VERCEL=1` e API HTTPS validado; não representa deployment real na cloud.

Limites: cookies de terceiros nos domínios cross-site; hub numa só instância; possível período de coexistência de deployments durante atualização, com notificações transitórias perdidas até reconectar/atualizar; sem gravações offline; throttle por IP de proxy; `/health` apenas liveness. Dependências backend usam intervalos de versão existentes, não lock exato; rever o build Railway e conservar a imagem/commit validado. Media é estática no frontend, incluída no build; não há armazenamento de uploads em runtime.

Não foram alteradas regras de negócio, roles, eventos, Estatísticas ou migrações. Nenhuma publicação automática, Redis, BFF ou PWA offline.
