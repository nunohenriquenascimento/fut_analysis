# Ativação da migração 0007

Procedimento preparado em 15/10/2026. **Não executado na base real.**
A leitura `alembic current` confirmou `0006` nesta etapa.

## Resultado da preparação e ensaio

Em 15/10/2026 foi executado um ensaio completo com dados exclusivamente
sintéticos num cluster PostgreSQL 18 temporário em loopback, separado da
instância da aplicação. Incluiu `0006`, backup custom, listagem/checksum,
restauro noutra base vazia, comparação de esquema/dados/sequências,
upgrade para `0007`, `alembic check` e cinco endpoints de leitura com HTTP 200.
Os dados das nove tabelas anteriores ficaram intactos. O servidor temporário
foi parado. Evidência: [ensaio-0007.json](competicoes/2026-27/ensaio-0007.json).

A inspeção READ ONLY da base configurada confirmou PostgreSQL 18.6, revisão
0006, esquema/constraints/índices/enums equivalentes ao baseline 0006 e as
permissões necessárias de CREATE no schema, REFERENCES nas tabelas de destino,
UPDATE em alembic_version e SELECT nas nove tabelas auditadas. Isto confirma
o destino atualmente configurado; não verifica outro destino de produção.

O ensaio pode ser repetido, com as ferramentas PostgreSQL no PATH e uma pasta
nova a cada execução, a partir de `backend`:

```powershell
.\.venv\Scripts\python.exe -m app.activation_rehearsal --directory '../.local-tools/activation-0007-NOVO_ENSAIO'
```

Este comando cria uma instância sintética própria, não faz backup dos dados
reais e apenas inspeciona o esquema da aplicação em leitura. Os ficheiros do
cluster e arquivo sintéticos são conservados para revisão. No Windows o arranque
do PostgreSQL temporário pode exigir execução fora do sandbox; não é necessário
nem permitido alterar a instância da aplicação para contornar isso.

O SQL de `0006:0007` foi também gerado em modo offline, sem execução, em
[migration-0007.sql](competicoes/2026-27/migration-0007.sql). O upgrade cria
três tabelas, constraints e sequências novas; só altera a revisão Alembic.
Não altera registos de jogos/jogadores/convocatórias/eventos. O downgrade é
uma operação distinta e não está autorizado.

**Continua a faltar o backup real verificado e a confirmação de aplicação.**
O ensaio sintético não substitui o ensaio do futuro arquivo real nem verifica
o tempo necessário para o volume real e as condições de produção.

## Preparação

1. Rever `backend/alembic/versions/0007_competitions.py`: cria apenas três
   tabelas e respetivas restrições. Não contém backfill nem UPDATE/DELETE.
2. Usar os clientes PostgreSQL compatíveis com a versão do servidor. Neste
   ambiente existem `pg_dump` e `pg_restore` do PostgreSQL 18 no PATH.
3. Reservar uma janela de manutenção e parar escritas da aplicação, incluindo
   login/logout, alterações de utilizadores e registos Live. Manter a janela
   até terminar a comparação dos dados; sessões e throttles também são auditados.
4. Escolher uma pasta privada de backup fora do repositório e do diretório
   publicado. Confirmar host, porta, nome da base e utilizador do destino
   com a configuração existente, sem copiar a password para o histórico.

## Backup e ensaio

Exemplo PowerShell: substituir os valores de exemplo pelo destino confirmado.
Executar a partir de `backend`. A password é pedida pelo cliente PostgreSQL.
As variáveis abaixo não alteram a configuração da aplicação.

```powershell
$backupFolder = 'C:\Backups\CCDR\antes-0007-20261015'
New-Item -ItemType Directory -Path $backupFolder -ErrorAction Stop | Out-Null
$backupFile = Join-Path $backupFolder 'ccdr-0006.dump'
$snapshotFile = Join-Path $backupFolder 'dados-0006.json'

# NÃO usar literalmente os valores de exemplo: confirmar o destino primeiro.
pg_dump --host=HOST_CONFIRMADO --port=5432 --username=UTILIZADOR_CONFIRMADO --password --format=custom --file=$backupFile BASE_CONFIRMADA
if ($LASTEXITCODE -ne 0) { throw 'Backup falhou; não avançar.' }
pg_restore --list $backupFile
if ($LASTEXITCODE -ne 0) { throw 'Arquivo inválido; não avançar.' }
Get-FileHash -Algorithm SHA256 -LiteralPath $backupFile

.\.venv\Scripts\python.exe -m alembic current
if ($LASTEXITCODE -ne 0) { throw 'Não foi possível verificar a revisão.' }
.\.venv\Scripts\python.exe -m app.migration_audit capture --output $snapshotFile
if ($LASTEXITCODE -ne 0) { throw 'Auditoria de 0006 falhou; não avançar.' }
```

`pg_restore --list` confirma a leitura do índice do arquivo, mas não substitui um ensaio
de restauro. Restaurar numa **base de ensaio nova e vazia**, criada manualmente
para esse fim, usando `pg_restore --exit-on-error --no-owner --no-privileges`.
Nunca apontar o ensaio à base real. Verificar a revisão 0006 e os registos
restaurados. Nessa base isolada, ensaiar `alembic upgrade 0007`, `alembic check`
e a comparação das fingerprints. Não alterar `backend/.env` para o ensaio:
usar um terminal separado com `DATABASE_URL` da base de ensaio e fechá-lo no fim.

Exemplo de restauro autorizado para uma base de ensaio **já confirmada vazia**:

```powershell
pg_restore --host=HOST_ENSAIO_CONFIRMADO --port=PORTA_ENSAIO_CONFIRMADA --username=UTILIZADOR_ENSAIO --password --dbname=BASE_ENSAIO_VAZIA --exit-on-error --no-owner --no-privileges $backupFile
if ($LASTEXITCODE -ne 0) { throw 'Restauro de ensaio falhou; não migrar a base real.' }
```

Não usar `--clean`, não reutilizar uma base com dados e não restaurar sobre
a base real. Estas flags não reproduzem proprietários/grants: validar as
permissões do utilizador que executará a migração no destino real.

O backup deve incluir a base completa. As fingerprints são apenas um controlo
de integridade, não substituem o backup e não permitem recuperar os dados.

## Ponto de confirmação

**Parar aqui.** Antes da aplicação real, obter confirmação explícita do
utilizador para o destino, o backup verificado e a aplicação de `0007`.
Nenhum script desta etapa faz upgrade automaticamente.

## Aplicar — apenas depois da confirmação

No terminal da base real, ainda em manutenção e na pasta `backend`:

```powershell
.\.venv\Scripts\python.exe -m alembic current
# Confirmar visualmente: 0006. Se for diferente, parar.
.\.venv\Scripts\python.exe -m alembic upgrade 0007
if ($LASTEXITCODE -ne 0) { throw 'Migração falhou; manter manutenção e investigar.' }
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic check
if ($LASTEXITCODE -ne 0) { throw 'Esquema não validado; manter manutenção.' }
.\.venv\Scripts\python.exe -m app.migration_audit verify --before $snapshotFile
if ($LASTEXITCODE -ne 0) { throw 'Dados divergentes; manter manutenção.' }
```

A auditoria usa uma transação PostgreSQL READ ONLY / REPEATABLE READ, compara
contagem e SHA-256 de todas as linhas/colunas das nove tabelas de `0006` e
não imprime dados nem credenciais. Deve ser feita antes dos novos logins,
porque o uso normal de sessões altera tabelas auditadas.

## Validar a aplicação

1. Reiniciar o backend com o código revisto e servir o build frontend aprovado.
2. Confirmar `/health` e, depois de autenticar, `/competitions` devolver lista
   vazia ou dados existentes, sem 500. `/health` sozinho não valida o esquema.
3. Confirmar Plantel, Jogos, Live e Estatísticas em leitura.
4. Abrir «Campeonato» como VIEWER: sem controlos de gestão. ADMIN/COACH devem
   ter regras/importação disponíveis; só ADMIN deve gerir participantes após
   a criação. A classificação deve indicar «Classificação provisória».
5. Criar participantes, competição ou importar dados reais apenas mediante
   instrução específica do utilizador. Os testes desta entrega usam dados sintéticos.

Se falhar alguma validação, manter a aplicação em manutenção e investigar.
Não executar downgrade, restauro sobre a base real ou eliminação automática.
O downgrade de `0007` recusa apagar competições com dados; mesmo sem dados,
qualquer rollback operacional exige confirmação separada.

## Ordem de ativação e carregamento

1. Confirmar destino e manutenção; parar todos os processos que possam escrever.
2. Fazer backup real, checksum, snapshot 0006 e restauro de ensaio do arquivo.
3. Rever o resultado e obter autorização explícita para `0007` nesse destino.
4. Aplicar `alembic upgrade 0007`, verificar revisão/check e fingerprints.
5. Iniciar o código revisto e validar leituras/permissões antes de reabrir escritas.
6. Obter autorização separada para criar a competição e carregar os lotes reais,
   com participantes, mapeamentos, jornadas, fontes e resultados revistos.

Não servir o código novo como se `0007` já estivesse ativa: algumas consultas
existentes de gestão de jogos também leem as novas dependências de calendário.
Executar a migração antes de reabrir a aplicação. A nova gestão posterior de
participantes usa as tabelas de `0007` e não exige uma migração adicional.
