# FPF: auditoria de pre-deploy Railway — 16/10/2026

## Diagnóstico

Código validado: 56 jogos, 14 jornadas, sete resultados e 49 jogos agendados;
435 testes backend e 76 Playwright aprovados na validação anterior, além de lint,
TypeScript e build. Não foram repetidos nesta auditoria de configuração.

**PUBLICAÇÃO PENDENTE**: falta configurar healthcheck e preparar recuperação por
backup, além da autorização do proprietário. Nenhum commit, merge, push, deploy,
backup, restauro, migração ou escrita em produção foi executado nesta auditoria.

### Git e ficheiros

- Raiz Git: `SUB-19`; aplicação em `ccdr-match-tracker`.
- Branch atual: `main`; index vazio. Commit local e remoto de `main` e
  `feat/campeonato-fpf`: `8df6ac4cd3b1a97e8ace53cf0130d5dd41b80445`.
- No início da auditoria: 16 ficheiros modificados e 22 novos, todos ligados à FPF.
  Este relatório acrescenta um novo ficheiro documental. A entrega ainda não está
  incluída em nenhum commit, apesar de os ficheiros já existirem no disco.
- Os 15 HTML estão organizados em `backend/tests/fixtures/fpf`: competição,
  13 fragmentos e ficha individual. Jornada 3 vem do HTML da competição;
  `fixtureId=677924.html` é a origem explicitamente associada à jornada 4.
  Não se deve renomear este ficheiro sem atualizar `tests/fpf_calendar_data.py`.
- O inventário, URLs e hashes estão em `FPF_CALENDARIO_COMPLETO_VALIDACAO.md`;
  o contrato de origem está em `FPF_FRAGMENTOS.md`; `FPF_CALENDARIO_LOCAL.md`
  documenta a conversão para fixtures locais.
- Pesquisa por padrões de chaves privadas, tokens GitHub, chaves AWS, JWTs e URLs
  com credenciais: nenhum achado nos 38 ficheiros candidatos à publicação.
  Nenhum `.env` real, dump, chave privada ou ficheiro temporário foi encontrado
  entre os ficheiros novos/modificados, nem ficheiro sensível versionado pelos
  padrões verificados. Isto é uma verificação por padrões, não uma garantia absoluta.
- `.env`, ferramentas locais, ambientes virtuais, node_modules, builds e resultados
  Playwright estão ignorados. `.dockerignore` também exclui testes, fixtures,
  documentação, `.env`, chaves e artefactos de testes da imagem de produção.
- A ficha individual **já versionada** contém 34 entradas de jogadores, cinco de
  técnicos/dirigentes e três de arbitragem: dados pessoais públicos da FPF, não
  credenciais. Não se deve afirmar que todos os HTML estão isentos de dados pessoais.
  A visibilidade do repositório GitHub não foi confirmada pela consulta pública.
  Os 13 novos fragmentos contêm tabelas de equipas/jogos, sem fichas individuais.

### Railway confirmado por consultas de leitura

| Elemento | Valor |
|---|---|
| Projeto | `practical-consideration` |
| Project ID | `212601f0-504d-43cf-8e4a-23653bbf2956` |
| Ambiente | `production` |
| Environment ID | `78f844d2-5beb-4172-93ea-5f6aaa7203f1` |
| Serviço aplicação | `fut_analysis` |
| Service ID | `d804aae2-0722-4fb6-81cf-815862e2d0d9` |
| Serviço PostgreSQL | `Postgres` |
| PostgreSQL Service ID | `fe6d0109-6989-4cb1-93ee-9f275048f24e` |
| Repositório | `nunohenriquenascimento/fut_analysis` |
| Trigger GitHub | `main`, ambiente production; `checkSuites=false` |
| Domínio | `https://futanalysis-production.up.railway.app` |
| Deployment ativo | `fadb9af0-def1-4840-bc41-08218abd2eab`, SUCCESS |
| Commit ativo | `8df6ac4cd3b1a97e8ace53cf0130d5dd41b80445` |
| Root Directory | `/ccdr-match-tracker` |
| Builder efetivo no deployment | `DOCKERFILE` |
| Dockerfile efetivo | `/ccdr-match-tracker/Dockerfile` |
| Start override | vazio; usa `python /app/deploy/start.py` do CMD |
| Pre-deploy / cron | vazios |
| Réplicas / região | uma, `sfo` |
| Sleeping | desativado |
| Healthcheck | **não configurado** |

A configuração genérica do serviço indica RAILPACK, mas o manifesto efetivamente
publicado confirma deteção e uso do Dockerfile. Não substituir o build pela imagem
backend isolada. Next recebe `/api` no build; Caddy serve frontend, API e WebSocket.

Há um trigger GitHub de `main` e o serviço não espera pelos checks de CI. Tratar
qualquer push para `main` como capaz de publicar imediatamente. Não executar também
`railway up` ou `railway redeploy` para o mesmo lançamento. Para uma publicação
manual separada do push, desativar primeiro Autodeploy no painel; depois usar
**Deploy Latest Commit**, não Redeploy do deployment antigo.

### Base de produção e arranque

Consulta via SSH ao serviço `fut_analysis`, usando a sua ligação de runtime,
em transação explícita READ ONLY com timeouts:

```json
{"alembic_revisions":["0008"],"fpf_data_types":["json"],"transaction_read_only":"on"}
```

Confirmado: revisão única `0008` e `competitions.fpf_data` JSON. Não há alterações
locais a modelos ou migrações. Não executar upgrade, stamp, downgrade ou seed nesta
entrega. Os documentos antigos de arquitetura que referem `0006` são históricos.
O antigo `docs/railway/read_only_probe.py` reconhece apenas revisões até `0007`;
não é o procedimento usado nesta auditoria nem deve ser usado para certificar `0008`.

Dockerfile/supervisor/main não importam HTML, não executam seed/migrações e não
criam nem atualizam jogos no arranque. Os HTML nem sequer entram na imagem.
O importador só grava através de endpoints ADMIN com confirmação explícita; preview
não grava. O deploy do código e a importação manual dos 56 jogos são atos separados.

### Backups: pendência confirmada

- Volume: `postgres-volume`, montado em `/var/lib/postgresql/data`.
- Volume ID: `e9f9f298-089b-4953-bc87-0b050b186636`.
- Volume instance ID: `8ce00db9-4c71-465a-906a-31ccd093a584`.
- `volumeInstanceBackupList`: vazio.
- `volumeInstanceBackupScheduleList`: vazio.
- PITR: `enabled=false`.

Não existe backup nativo demonstrado; dumps ou backups externos não foram
verificados. Antes da importação manual, exigir backup recente e recuperabilidade
testada. O plano abaixo não cria qualquer backup por si próprio.

## Ordem recomendada — comandos NÃO executados

Os passos de escrita/publicação abaixo só podem começar após autorização.
Executar os comandos individualmente e parar se algum devolver erro.

### 1. Preparar a proteção operacional após autorização

No painel do projeto/serviço acima, configurar `/health`, timeout 90 segundos,
mantendo Root Directory, Dockerfile, um worker/réplica, origem e pre-deploy vazio.
Rever mudanças pendentes antes de aplicar: aplicar configurações pode criar um
deployment. Não alterar DATABASE_URL nem substituir o serviço Postgres.

Verificar se a visibilidade do repositório é adequada à ficha individual já
versionada. Se a política exigir retirar/anomizar esses dados, parar e tratar isso
como mudança separada, com nova validação dos testes que dependem da ficha.

Criar e verificar um backup antes da publicação; repetir imediatamente antes da
importação se entretanto houver escritas. Ver comandos na secção 6.

### 2. Guardar a entrega numa branch de publicação

PowerShell, na pasta da aplicação:

```powershell
Set-Location 'C:\Users\javai\OneDrive\Ambiente de Trabalho\SUB-19\ccdr-match-tracker'
git fetch origin
git status --short --branch
git rev-parse origin/main
git switch -c release/fpf-calendario-validado
git add -u -- backend/app backend/tests frontend/app/competitions frontend/lib frontend/tests/fpf.spec.ts
git add -- backend/tests/fixtures/fpf backend/tests/fpf_calendar_data.py backend/tests/test_auth_fpf_calendar.py backend/tests/test_auth_fpf_conflicts.py backend/tests/test_auth_fpf_fragments.py backend/tests/test_auth_fpf_local.py backend/tests/test_auth_fpf_rounds.py
git add -- docs/competicoes/FPF_CALENDARIO_COMPLETO_VALIDACAO.md docs/competicoes/FPF_CALENDARIO_LOCAL.md docs/competicoes/FPF_FRAGMENTOS.md docs/competicoes/FPF_PRE_DEPLOY_RAILWAY.md
git diff --cached --check
git diff --cached --stat
git diff --cached
git status --short
git commit -m 'fix: validar importacao FPF do calendario completo'
git push -u origin release/fpf-calendario-validado
```

Rever o staged antes do commit: esperado 16 ficheiros anteriormente modificados,
13 fragmentos, seis novos ficheiros de testes/apoio e quatro documentos.
Não incluir `.env`, `.local-tools`, dumps, logs ou resultados de testes.
Se `origin/main` já não for o commit auditado, parar e rever a nova base antes de
integrar. Publicar a branch release não deve afetar production, cujo trigger é main.

### 3. Integrar e publicar — ponto que pode disparar deploy

Após revisão da branch e resolução das pendências operacionais:

```powershell
git switch main
git pull --ff-only origin main
git merge --ff-only release/fpf-calendario-validado
git push origin main
railway.cmd deployment list --project 212601f0-504d-43cf-8e4a-23653bbf2956 --environment production --service fut_analysis --limit 3 --json
```

O push para `main` é o gatilho de publicação se Autodeploy estiver ativo. Confirmar
no deployment novo o SHA criado e o builder DOCKERFILE. Se Autodeploy tiver sido
desativado para separar as operações, usar **Deploy Latest Commit** no painel.
Não usar um comando Redeploy do commit antigo como substituto deste passo.

### 4. Verificações pós-deploy, antes de importar

```powershell
curl.exe --fail --silent --show-error https://futanalysis-production.up.railway.app/health
curl.exe --fail --silent --show-error https://futanalysis-production.up.railway.app/api/health
railway.cmd deployment list --project 212601f0-504d-43cf-8e4a-23653bbf2956 --environment production --service fut_analysis --limit 3 --json
railway.cmd ssh --project 212601f0-504d-43cf-8e4a-23653bbf2956 --environment production --service fut_analysis
```

Na sessão SSH, shell Linux:

```sh
cd /app/backend
PGOPTIONS='-c default_transaction_read_only=on -c statement_timeout=10000' python -m alembic current
PGOPTIONS='-c default_transaction_read_only=on -c statement_timeout=10000' python -m alembic check
exit
```

Exigir `0008` e ausência de operações de esquema pendentes. `/health` é liveness
e não substitui a verificação da base. Confirmar no browser HTTPS: login, cookie
Secure/HttpOnly/Lax, API same-origin `/api`, permissões ADMIN/COACH/VIEWER, leitura
do plantel, calendário, resultados, classificação e Live/WSS em dois dispositivos.
Não criar eventos/jogos fictícios em produção como smoke test. Comparar os dados
existentes com o estado anterior e confirmar que os 56 jogos não foram importados
automaticamente. Só depois abrir a etapa separada de importação manual.

### 5. Rollback do código

Suspender novas importações e atividades Live. No painel, escolher **Rollback**
no deployment `fadb9af0-def1-4840-bc41-08218abd2eab`, último ativo antes desta
publicação, confirmando que a imagem ainda está retida. A opção restaura a imagem
e variáveis desse deployment; rever se reintroduz configurações antigas, incluindo
a ausência de healthcheck. Repetir health, login, WSS e leitura do esquema.

Se a imagem expirou, o fallback é Redeploy desse deployment no painel, reconstruindo
o commit antigo. Não usar `railway redeploy` do deployment mais recente para tentar
voltar arbitrariamente a um commit anterior. Não executar downgrade de `0008`.

Rollback de código não desfaz uma importação FPF já aplicada. Se o problema for
dados importados, parar as escritas e restaurar primeiro o backup numa base isolada,
comparar e preparar recuperação/cutover separadamente autorizados. Um restauro
integral pode apagar alterações legítimas posteriores ao backup; não o automatizar.

### 6. Backup imediatamente antes da importação manual

No Postgres/Backups do Railway, confirmar o serviço e volume acima. Criar backup
manual com rótulo `pre-fpf-import-<data UTC>` e esperar conclusão bem-sucedida.
Alternativa exata pela API, **apenas após autorização para criar o backup**:

```powershell
@'
mutation { volumeInstanceBackupCreate(volumeInstanceId:"8ce00db9-4c71-465a-906a-31ccd093a584", name:"pre-fpf-import") { workflowId } }
'@ | railway.cmd api --compact
```

Guardar o workflowId devolvido. Consultar o estado com o seu ID real:

```powershell
$backupWorkflowId = Read-Host 'workflowId devolvido ao criar o backup'
$backupWorkflowQuery = 'query { workflowStatus(workflowId:"' + $backupWorkflowId + '") { status } }'
$backupWorkflowQuery | railway.cmd api --compact
@'
query { volumeInstanceBackupList(volumeInstanceId:"8ce00db9-4c71-465a-906a-31ccd093a584") { id name createdAt expiresAt } }
'@ | railway.cmd api --compact
```

Exigir conclusão sem erro e registo de backup novo, com ID, criação e retenção
compatíveis com a janela de recuperação. Não basta existir um agendamento ou um
workflow ainda em curso. Guardar esses metadados num registo operacional privado.

Para um backup lógico adicional e verificação de recuperabilidade, usar pg_dump
com a ligação PostgreSQL pública/túnel fornecida pelo operador. Não imprimir URLs
com password nem guardar credenciais/dumps no repositório ou no OneDrive:

```powershell
$backupDir = Join-Path $env:LOCALAPPDATA 'CCDR-private-backups'
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
$backupFile = Join-Path $backupDir ('pre-fpf-' + (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss') + '.dump')
$dbHost = Read-Host 'Host PostgreSQL confirmado no Railway ou tunel'
$dbPort = Read-Host 'Porta PostgreSQL confirmada'
$dbName = Read-Host 'Nome da base de producao confirmada'
$dbUser = Read-Host 'Utilizador PostgreSQL confirmado'
pg_dump.exe --host $dbHost --port $dbPort --username $dbUser --dbname $dbName --password --format=custom --no-owner --no-acl --file $backupFile
if ($LASTEXITCODE -ne 0) { throw 'Backup falhou; nao importar.' }
Get-Item -LiteralPath $backupFile | Select-Object Name,Length,LastWriteTimeUtc
Get-FileHash -LiteralPath $backupFile -Algorithm SHA256
pg_restore.exe --list $backupFile
if ($LASTEXITCODE -ne 0) { throw 'Arquivo invalido; nao importar.' }
```

Usar a configuração TLS exigida pela ligação confirmada, sem desativar a validação
para contornar erros. Proteger a pasta por ACL/encriptação e retenção adequadas:
um dump contém dados pessoais e hashes de autenticação. Usar cliente pg_dump da
mesma versão major ou superior à do servidor. pg_restore --list verifica o índice
do arquivo, **não demonstra restauro**.

Numa instância local descartável e privada previamente criada em
`127.0.0.1:55440`, sem ligação a produção, comprovar o restauro numa base nova:

```powershell
$restoreDb = 'fpf_restore_' + (Get-Date).ToUniversalTime().ToString('yyyyMMddHHmmss')
createdb.exe --host 127.0.0.1 --port 55440 --username postgres --password $restoreDb
if ($LASTEXITCODE -ne 0) { throw 'Base descartavel nao criada; parar.' }
pg_restore.exe --host 127.0.0.1 --port 55440 --username postgres --password --dbname $restoreDb --no-owner --no-acl --single-transaction --exit-on-error $backupFile
if ($LASTEXITCODE -ne 0) { throw 'Restauro nao comprovado; nao importar.' }
psql.exe --host 127.0.0.1 --port 55440 --username postgres --password --dbname $restoreDb --set ON_ERROR_STOP=1 --command 'SELECT version_num FROM alembic_version; SELECT count(*) AS matches FROM matches; SELECT count(*) AS events FROM match_events; SELECT count(*) AS squads FROM match_squads; SELECT count(*) AS players FROM players; SELECT count(*) AS fixtures FROM competition_fixtures;'
```

Comparar revisão `0008`, contagens e dados essenciais com o snapshot de origem.
Não restaurar nem testar recovery diretamente sobre a base de produção. Se houve
escritas após o backup, criar outro imediatamente antes da importação. Suspender
escritas na janela de verificação/importação para manter uma referência coerente.

Depois, importar manualmente o HTML da competição e oito fragmentos no primeiro
lote (36 jogos), e os cinco fragmentos restantes no segundo (20 jogos), com os IDs
reais das equipas revistos. Os IDs dos testes não servem para produção. Confirmar
56 jogos, 14 jornadas, sete resultados oficiais/49 agendados antes de considerar
resultados internos derivados dos seus eventos. Reimportar só após rever o preview.

## Referências

- [Autodeploys e branch de trigger](https://docs.railway.com/deployments/github-autodeploys).
- [Rollback e retenção de imagens](https://docs.railway.com/guides/roll-back-bad-deploy).
- [Backups e testes de restauro](https://docs.railway.com/guides/postgres-backups-restores).

Este plano é uma proposta para revisão. A autorização para publicar continua pendente.
