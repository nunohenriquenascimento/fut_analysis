# Railway: frontend, API e WebSocket no mesmo domínio

Esta é a estratégia de produção recomendada para a aplicação interna. Substitui a arquitetura Vercel/Railway de [PRODUCAO_DEPLOY.md](PRODUCAO_DEPLOY.md). Nenhum deployment automático foi efetuado.

## Serviços e rotas

**Dois serviços Railway:** aplicação combinada e PostgreSQL existente. A aplicação tem um container, uma réplica, uma região, um processo Next.js, um worker Uvicorn e Caddy. Só Caddy tem porta pública. Não é necessário comprar domínio, usar Vercel ou Redis.

| Pedido público | Destino interno | Caminho no upstream |
|---|---|---|
| `/`, `/login`, `/players`, `/matches`, `/_next/*`, imagens | Next.js em `127.0.0.1:3000` | Preservado |
| `/api/auth/login`, `/api/auth/me`, `/api/*` | FastAPI em `127.0.0.1:8000` | `/api` removido |
| `/ws/matches/{id}/live` | FastAPI em `127.0.0.1:8000` | `/ws/...` preservado |
| `/health` | FastAPI | `/health` |
| `/api/health` | FastAPI | `/health` |

O browser usa exclusivamente `https://DOMINIO.up.railway.app` e `wss://DOMINIO.up.railway.app/ws/...`. `/auth/login` público não é API: o cliente usa `/api/auth/login`. Nenhum endpoint funcional do backend foi renomeado; o prefixo pertence ao proxy.

Escolhi Caddy porque `handle_path` remove o prefixo e `reverse_proxy` gere WebSocket Upgrade e tráfego bidirecional sem configuração manual de Connection/Upgrade. Mantém Cookie, Origin, Host e Set-Cookie; não reescreve atributos do cookie. O proxy não tem access logging de cookies. [Caddy reverse_proxy](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy).

## Ficheiros e build

- `Dockerfile` na raiz `ccdr-match-tracker`: build frontend em Node 22, cópia da saída Next standalone, runtime Python 3.12 + Node + Caddy 2.10.2, aplicação como utilizador sem privilégios.
- `.dockerignore`: exclui `.env`, Git, ferramentas locais, testes, caches, node_modules e builds locais. Nenhum secret entra na imagem.
- `deploy/Caddyfile`: rotas da tabela, listener HTTP interno no `PORT` público. TLS é terminado pelo edge Railway; auto HTTPS e admin Caddy desligados.
- `deploy/start.py`: supervisor dos três processos, startup com espera por API/frontend, sinais e encerramento conjunto. Se um processo sair, container termina e Railway pode reiniciá-lo. Não executa migrações.
- `deploy/.env.production.example`: referência das variáveis do serviço combinado.
- `backend/Dockerfile` continua disponível para o deployment antigo; **não é usado** nesta arquitetura.

Next é construído com `BUILD_STANDALONE=true` e **`NEXT_PUBLIC_API_URL=/api` fixo no Dockerfile**. O build copia `public` e `.next/static` para o runtime; inclui emblemas/fotos/fontes do frontend. Não há upload em runtime. Variável NEXT_PUBLIC é incorporada no build e não corrigida por alterações runtime. [Next standalone](https://nextjs.org/docs/app/api-reference/config/next-config-js/output).

Railway Root Directory = raiz `ccdr-match-tracker`, contendo ambos `frontend/` e `backend/` e o **Dockerfile da raiz**. Se o repositório já começa nessa pasta, usar `/`; se começa em `SUB-19`, usar `/ccdr-match-tracker`. Remover a root antiga `/backend`. Não alterar `RAILWAY_DOCKERFILE_PATH` para `backend/Dockerfile`; usar Dockerfile da root. Neste checkout, os ficheiros frontend já aparecem versionados no repositório do projeto. Confirmar que o repositório remoto selecionado na Railway também os contém, incluindo assets. Não basta existirem na máquina local. Esta fase não reestrutura nem publica os repositórios.

Build command adicional: vazio; Dockerfile faz `npm ci`, `npm run build` e instalação Python. Start command: vazio para usar CMD, ou **`python /app/deploy/start.py`**. Não usar `next start` como único start nem `python -m app.start` do deployment antigo. [Dockerfiles Railway](https://docs.railway.com/builds/dockerfiles).

## Portas e processos

| Processo | Bind / porta | Público |
|---|---|---|
| Caddy | `0.0.0.0:$PORT`, default 8080 | Sim, via HTTPS Railway |
| Next.js | `127.0.0.1:3000` | Não |
| FastAPI | `127.0.0.1:8000`, um worker | Não |

`PORT` não pode ser 3000 ou 8000. Railway injeta a porta; escolher target port do domínio igual a esse `PORT` (normalmente 8080). Não gerar domínios adicionais para as portas internas. Healthcheck `/health`, timeout 90 segundos; arranque só abre Caddy depois de API e Next responderem. O healthcheck verifica disponibilidade dos processos na abertura, mas o endpoint backend continua liveness, sem comprovar esquema/base.

Comando Uvicorn interno: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 --proxy-headers --forwarded-allow-ips 127.0.0.1 --root-path /api`. Apenas Caddy em loopback é confiável; define X-Forwarded-Proto=https para a terminação TLS Railway e remove X-Forwarded-For recebido. Não confiar em todos os proxies. O throttle existente por IP agrupa pedidos através do proxy local; limite por email permanece. Não foi alterado o algoritmo de throttling.

## Variáveis do serviço combinado

| Variável Railway | Valor |
|---|---|
| `APP_ENV` | `production` |
| `DATABASE_URL` | Referência `${{Postgres.DATABASE_URL}}`, com o nome real do serviço existente |
| `CORS_ORIGINS` | `["https://DOMINIO.up.railway.app"]`, URL exato sem slash/path |
| `AUTH_COOKIE_SECURE` | `true` |
| `AUTH_COOKIE_SAMESITE` | **`lax`** |
| `AUTH_SESSION_HOURS` | `8` ou valor permitido de 1–24 |
| `AUTH_DEBUG_LOGGING` | `false` normalmente |
| `PORT` | Railway fornece; default de referência 8080 |

Não é necessário `NEXT_PUBLIC_API_URL` runtime, pois `/api` está incorporado na imagem. Remover o valor antigo absoluto da Vercel/Railway para evitar confusão; não o utilizar como build override. NEXT_PUBLIC_AUTH_DEBUG fica false/ausente no build; para diagnóstico temporário, alterar explicitamente o build e reconstruir, sem colocar secrets em argumentos Docker. O ambiente do processo Next é filtrado e não recebe DATABASE_URL nem configuração de sessões.

Configurar uma réplica/região, sem autoscaling/múltiplos workers e sem App Sleeping inicialmente. Reservar recursos para Node, Python, Caddy e hashing seguro de passwords. Não existe requisito de Redis nesta fase.

## Autenticação e segurança

Cookie continua `__Host-ccdr_session`, **HttpOnly=true, Secure=true, SameSite=Lax, Path=/**, sem Domain. O cookie pertence ao único hostname público e é enviado para `/api` e `/ws`. Não é necessário SameSite=None; não depende de cookies third-party. Ao mudar de hostname público, fazer login de novo.

A imagem combinada define por defeito APP_ENV=production, Secure=true e SameSite=lax; o supervisor recusa SameSite diferente de lax em produção. As verificações existentes do backend continuam a recusar Secure=false em produção. Não copiar a configuração None do deployment antigo.

O cliente HTTP com `/api` mantém `credentials: include`; CSRF da sessão permanece apenas em memória. Escritas/logout mantêm CSRF, sessão ativa e autorização no backend. Login mantém Origin e X-Requested-With. WebSocket é construído pelo host da página quando a API é relativa, sem `/api` no caminho, com cookie automático, Origin permitido e revalidação de sessão. Nenhum token em localStorage/query.

Manter CORS explícito com o próprio Origin público e credentials; não permitir `*` nem manter a Vercel na lista se deixar de ser utilizada. Mesmo same-origin, a validação de Origin das escritas e do WebSocket continua necessária. Não transformar `CORS_ORIGINS` numa comparação livre de Host fornecido pelo browser.

Uvicorn comunica root_path=/api para URLs e redirects corretos. Os filtros de erros de validação e o diagnóstico temporário foram adaptados para reconhecer `/api/auth/*`; passwords continuam excluídas dos erros públicos. Reconexão, snapshots e regras Live/Estatísticas mantidas. TLS/WSS público é fornecido pelo Railway, sem certificados locais Caddy em produção.

## Migração manual do deployment atual

1. Rever e publicar manualmente o código nos repositórios corretos, garantindo que o checkout usado pela Railway contém frontend, backend, assets, lockfile npm, Dockerfile root e deploy/. Não incluir `.env` ou `.local-tools`.
2. Fazer backup PostgreSQL e confirmar a revisão atual `0006`. **Manter o mesmo serviço/base PostgreSQL**: não criar uma base vazia, não executar seed de demonstração nem importar por cima dos dados existentes.
3. Preferência: adaptar o serviço Railway atual para preservar `futanalysis-production.up.railway.app`. Parar utilização Live durante a troca. Alterar Root Directory de backend para raiz do projeto e selecionar Dockerfile root/start supervisor. Isto substitui o processo atual; não manter dois backends ativos a escrever enquanto o hub está dividido.
4. Configurar Secure=true, SameSite=lax, CORS com `https://futanalysis-production.up.railway.app`, DATABASE_URL referenciado e debug=false. Retirar overrides antigos de Dockerfile/start/pre-deploy. Confirmar uma réplica/região.
5. Fazer deployment **manualmente**. Verificar build Docker, arranque dos três processos, `/health` e `/api/health`. Não configurar upgrade Alembic no build/start. Sem mudanças de esquema nesta entrega, não é necessário upgrade se já está em `0006`.
6. Se mantiver o domínio existente, atualizar o target port para o `PORT` do Caddy (normalmente 8080). Se criar outro serviço, usar Settings → Networking → Generate Domain **apenas no serviço combinado**, uma vez, com a porta Caddy; atualizar CORS para o hostname gerado e aplicar a variável antes de login. Não colocar domínio público no PostgreSQL. Se experimentar outro serviço, retirar o backend antigo de utilização antes de escritas na mesma base.
7. Abrir `https://DOMINIO.up.railway.app/login`. Fazer login novamente; verificar `/api/auth/login` 200, `/api/auth/me` 200, cookie Secure/HttpOnly/Lax/Path=/ e logout. Confirmar desktop e Safari mobile. Sessões existentes na base podem manter-se, mas não assumir que cookies de outro hostname migram.
8. Testar ADMIN/COACH/VIEWER, Plantel, convocatória, Estatísticas e gestão de jogos. Abrir mesmo Live em dois dispositivos e confirmar WSS, eventos, partes, cancelamento e reconexão. Validar que o browser não faz chamadas à Vercel ou a outro host API.
9. Depois de confirmar funcionamento, retirar a Vercel de utilização e desativar os seus deployments/links conforme necessário. Não é preciso apagar imediatamente para o teste; não a manter como ponto de entrada normal. Remover origens e configuração antiga cross-site do serviço ativo.
10. Confirmar backup/restauro, monitorização, recursos e uma réplica. Reiniciar container fecha sockets e a reconexão recupera o estado; não há fila de escritas offline. Fazer upgrades futuros revistos e manuais, nunca downgrade destrutivo automático.

Se houver domínio novo ou rollback de arquitetura, ajustar cookie/SameSite/CORS para o destino e pedir novo login. Não resolver rollback com tokens frontend ou desativação de CSRF. Rolling deployments podem temporariamente coexistir: durante a troca, usar janela de manutenção e reconectar/atualizar depois; hub em memória não garante notificações entre containers.

## Operação e desenvolvimento

SSH no serviço combinado e `cd /app/backend`. Comandos existentes:

```sh
python -m alembic current
python -m alembic check
# Apenas se houver migração revista a aplicar:
python -m alembic upgrade head
# Apenas numa base sem ADMIN, interativamente:
python -m app.create_admin
```

Não criar novo ADMIN por defeito; o atual está na mesma base. `python -m app.seed` apenas para contexto numa base nova, não como passo obrigatório desta migração.

Desenvolvimento local permanece com `.env.example`, API `http://localhost:8000`, Next em localhost:3000, cookies Lax/Secure=false e CORS localhost. Sem BUILD_STANDALONE, `npm run dev/build/start` mantém o funcionamento habitual. Também se pode testar a imagem com Docker e variáveis locais Secure=false; o Caddy continua a representar o edge HTTPS na configuração de produção, pelo que o teste definitivo do cookie Secure exige HTTPS.

## Validação e limites

Novos testes cobrem autenticação same-origin por HTTPS, cookie em `/auth/me`, CSRF/logout, WSS autenticado e origem inválida, contrato de rotas/prefixos, um worker e portas. Integração adicional executa **Caddy real + Uvicorn + PostgreSQL isolado** e comprova routing HTTP, Set-Cookie preservado, WebSocket Upgrade e notificação após evento. O teste local simula o edge TLS Railway usando transporte HTTP interno; não comprova o certificado público cloud.

Para executar a integração real, instalar Caddy 2.10.2 e definir `CADDY_BIN` com caminho do executável, além de TEST_DATABASE_URL. Sem CADDY_BIN esse teste específico é skip; os restantes testes backend continuam. Ferramenta descarregada para validação local ficou numa pasta `.local-tools` ignorada, excluída da imagem.

Docker não está instalado neste ambiente: imagem Linux completa e ciclo de vida do supervisor exigem validação no primeiro build/container manual. A configuração Caddy foi validada pelo executável real; Next standalone e build API relativa foram verificados localmente. Nenhum schema/migração/regra de negócio alterado.

Resultados: **235 testes Python/PostgreSQL passaram**, incluindo a integração Caddy real; **44 testes frontend/Playwright passaram**. Lint, TypeScript, build normal, build standalone com `NEXT_PUBLIC_API_URL=/api`, validação Caddy e Alembic check passaram. Head permanece `0006`; nenhuma migração criada. Aviso de depreciação TestClient/httpx existente, sem falhas.

Criados nesta fase: `Dockerfile`, `.dockerignore`, `deploy/Caddyfile`, `deploy/start.py`, `deploy/.env.production.example`, `backend/tests/test_auth_same_origin.py`, `backend/tests/test_auth_proxy_real.py`, `frontend/tests/same-origin.spec.ts` e este documento.

Modificados: `.gitignore`, exemplos de produção backend/frontend, `backend/app/auth.py`, `backend/app/auth_debug.py`, `backend/app/main.py`, `frontend/next.config.ts`, `frontend/lib/live-socket.ts`, `frontend/lib/auth-debug.ts`, `README.md`, `PRODUCAO_DEPLOY.md` e `AUTH_MOBILE_DIAGNOSTICO.md`.
