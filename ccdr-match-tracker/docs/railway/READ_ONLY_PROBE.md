# Diagnóstico PostgreSQL READ ONLY — procedimento para revisão

## Segunda ronda documental R2 — nenhuma execução autorizada

Ver [C1–C9](VALIDADORES_CORRECOES_P1_P10.md) e
[fixtures completas e isoladas](VALIDADORES_FIXTURES.md) §§7–10.
Os contratos 2.0.0 continuam rascunhos sem aprovação; R2 fixa propostas explícitas
de H16, qualificação histórica, checkpoint, limites e assinaturas. Hashes de
registos extensos/assinaturas reais não foram fabricados nem calculados.
Nenhuma assinatura ou isolamento foi comprovado; o probe e o harness não
foram executados/modificados. Estado NÃO APTO; aguardar revisão independente.

## Correção documental P1–P10 — NÃO APTO

Schemas e fixtures são agora documentais 2.0.0; o
[contrato transversal](VALIDADORES_CORRECOES_P1_P10.md) substitui ambiguidades
de contexto, temporalidade, referências, fontes, assinatura proposta e DAG.
São contratos, não código/validação/configuração aplicada. Nenhuma autorização
real, raiz de confiança ou evidência foi criada. O procedimento do probe não
foi executado/alterado; nada autoriza aceder à Railway ou ensaiar PostgreSQL.

## Fase atual: schemas e fixtures documentais — NÃO APTO

Consultar [VALIDADORES_SCHEMAS.md](VALIDADORES_SCHEMAS.md) e
[VALIDADORES_FIXTURES.md](VALIDADORES_FIXTURES.md). Os contratos distinguem
estrutura, criptografia, proveniência, configuração aplicada e comportamento.
Fixtures não são evidência e os relatórios documentais nunca podem gerar APTO.
Nenhum teste/script/validador foi executado e nenhuma instrução histórica
autoriza ensaio. Não houve operação host/guest, processo, SQL ou transferência.

## Revisão Hyper-V: mecanismos e validadores apenas especificados

Ver [HYPERV_VALIDADORES.md](HYPERV_VALIDADORES.md). O mapping candidato não
comprova mecanismos disponíveis no host; quotas, deadline, relays e exportação
continuam dependentes de componentes/evidência não aprovados. Nenhuma consulta
de administração, teste, importação/exportação ou operação real foi realizada.
Mantém-se NÃO APTO; nenhum comando histórico deve ser interpretado como permissão.

## Especificação declarativa e pacote — estado NÃO APTO

Preparados o [contrato Hyper-V/Linux](VM_ESPECIFICACAO.md) e o
[manifesto com hashes das três fontes](PACOTE_TESTES_MANIFESTO.md), apenas por
leitura local e documentação. Não existe imagem, VM, lock completo, preflight
ou prova operacional. O contrato recusa rede, canais partilhados, ficheiros/
dependências inesperados, hashes divergentes e limites ausentes; ainda não
existe validador implementado. Não usar instruções históricas para executar.
Nenhum teste, binário PostgreSQL, serviço externo ou processo foi operado nesta
fase; o harness e resíduos permaneceram intactos.

## Direção atual: isolamento externo, sem continuar a expandir o harness

Consultar a [arquitetura proposta de VM offline](ISOLAMENTO_INTEGRACAO.md).
O Windows atual mantém NÃO APTO. Não repetir startup: a próxima etapa consiste
em especificação declarativa e revisão estática, sem provisionar nem executar VM,
contentor ou PostgreSQL. Nenhum comando histórico abaixo constitui autorização.
Os critérios AC1–AC8 e a investigação separada dos resíduos constam da proposta.

## Decisão mais recente: NÃO APTO para solicitar novo ensaio no ambiente atual

Consultar a [matriz de riscos atual](../../RAILWAY_PRODUCAO_AUDITORIA.md).
As recomendações anteriores de prontidão ficam substituídas. Faltam garantias
reais de ACL/reparse points, quota de disco, identidade do listener/processo,
contenção dos descendentes e resolução de resíduos do primeiro ensaio.
Estas evidências exigem operações reais separadamente autorizadas; não foram
obtidas nesta auditoria. A produção Railway continua completamente fora do âmbito.

Melhorias desta revisão: comparação dev/inode do descritor antes de ler excertos;
recusa de hard links no PID e memorização de PID/timestamp/diretório/porta para
detetar alterações entre verificações. Nenhum processo foi consultado ou alterado.
Essa impressão é metadado do ficheiro, não identidade de kernel: não impede
adulteração, reutilização no mesmo segundo ou corridas após validação. As restantes
aberturas por caminho e o próprio pg_ctl continuam sujeitos às limitações do SO.
Nenhum teste simulado constitui prova de que ficheiros/processos externos nunca
serão atingidos. Exigir ambiente descartável isolado, ACLs privadas, quota e
contenção demonstradas antes de pedir autorização para execução real.
Resultado desta revisão: 52 testes simulados passaram (28 harness + 24 probe).
Não houve execução dos oito testes reais, binários PostgreSQL, SQL ou operações
sobre processos. Os resultados anteriores abaixo são históricos.

## Auditoria estática mais recente — sem execução PostgreSQL

Esta secção substitui a descrição de captura por pipes nas revisões históricas
abaixo. Foram revistos o harness, as regressões e os dois documentos, sem
consultar processos, bases ou o diretório do primeiro ensaio.

Problemas classificados antes das correções:

| Criticidade | Constatação | Tratamento |
| --- | --- | --- |
| Alta | PIPE acumulava toda a saída antes do limite de 64 KiB | stdout/stderr redirecionados para ficheiros exclusivos no diretório do ensaio; leitura limitada |
| Alta | Root recalculado a cada acesso; validação/abertura sujeita a corridas | Root ancorado por caminho e identidade dev/inode; recusa symlink/junction; O_EXCL nos captures e O_NOFOLLOW quando suportado; risco concorrente residual |
| Alta | Redação podia deixar passar URLs codificados, rótulos ofuscados ou valores numa nova linha | Inspeção percent-decoded/Unicode normalizada sem controlos; supressão integral de blocos de credenciais ambíguos |
| Média | PID não revalidado entre fast e immediate | Verificação repetida imediatamente antes de cada tentativa |
| Média | 45 testes anteriores não cobriam estas variantes e não provavam o comportamento real | Acrescentadas regressões; integração continua por executar |

Os ficheiros `command-N.stdout.raw` e `command-N.stderr.raw` são evidências
**brutas e potencialmente sensíveis**, tal como server.log. São criados com
O_EXCL, modo 0600 e nomes controlados, dentro do root confirmado. Nunca são
impressos nem anexados automaticamente. Não guardar estes ficheiros no Git.
O JSON referencia os seus nomes, código de saída, evento e indicadores de
truncagem; só apresenta excertos sanitizados. A última linha incompleta de um
excerto truncado é descartada antes de redigir, evitando publicar parte de uma
password. A evidência completa permanece no ficheiro bruto.

Esta mudança limita a memória usada para ler capturas, mas **não limita o tamanho
dos ficheiros no disco**. O timeout de 45 s também não é uma quota de disco.
É necessária capacidade/limitação externa apropriada antes do ensaio. Quando
pg_ctl expira, subprocess.run trata o processo direto; não garante terminar
descendentes PostgreSQL. O cleanup só pode atuar no cluster de identidade
confirmada e pode falhar; ausência de PID não prova ausência de resíduos.

Limites de paths: os novos captures recusam ficheiros pré-existentes e não
seguem symlinks quando o SO suporta O_NOFOLLOW; o JSON é aberto em append com
O_NOFOLLOW quando disponível. A identidade do root é verificada antes dos
acessos de diagnóstico e cleanup. Isto **não elimina TOCTOU**, hard links
introduzidos depois da validação, reparse points Windows ou adulteração por
outro processo do mesmo utilizador. O modo 0600 não configura ACL Windows.
server.log é aberto posteriormente pelo próprio pg_ctl, fora do controlo do
descritor Python. TEMP privado e utilizador/VM isolados continuam necessários.

Isolamento confirmado apenas pelo código: não recebe URL nem destino do operador;
usa loopback e porta reservada, credenciais sintéticas, root novo, PID e
data_directory. Não importa settings da aplicação e os subprocessos não recebem
variáveis Railway/DATABASE_URL. Recusa PG* sem ler valores. Não há caminho
programado para produção. Isso não é prova absoluta contra substituição de
binários, ambiente comprometido, reutilização da porta ou ficheiros adulterados.
Não afirmar que é impossível contactar outra instância numa corrida.

Qualidade dos testes: os mocks de subprocesso escrevem agora nos descritores
temporários fornecidos pelo harness. Há verificações da saída persistida,
truncagem, preservação do bruto, root alterado e mudança de PID entre stops.
Os testes de symlink/permissões simulam o SO; não certificam ACLs ou semântica
Windows real. Redação por padrões pode ocultar mensagens legítimas (falso
positivo) e não deteta todos os segredos desconhecidos, encoding repetido ou
conteúdo arbitrário (falso negativo). Rever privadamente até o JSON antes da
partilha. Não existe garantia geral de ausência de fugas.

`failfast=True` está na entrada direta, depois da validação exata de
`--run-disposable`. A descoberta normal ignora a classe; quem construir outro
runner e desativar manualmente skip pode contornar essa convenção. Não é uma
fronteira de segurança do sistema operativo. Nesta auditoria foram selecionados
exclusivamente testes unitários; nenhum dos oito testes reais foi selecionado.
Resultado: **49 testes simulados passaram** (25 do harness e 24 do probe), com
subprocessos, sockets e ligações reais bloqueados/simulados. Os números de 45
testes nas secções seguintes pertencem à revisão anterior.

Antes de nova autorização: resolver por leitura autorizada os resíduos do ensaio
anterior, confirmar TEMP privado/ACLs e binários confiáveis, capacidade/quota de
disco e execução isolada, rever o patch e usar apenas a entrada protegida com
failfast. Não enfraquecer guardas nem repetir startup como diagnóstico automático.

## Atualização: diagnóstico de falhas de arranque, sem novo ensaio

Esta secção prevalece sobre os estados históricos abaixo. O primeiro ensaio
autorizado terminou em erro em `pg_ctl start`, após initdb, antes de qualquer
teste ou ligação SQL. Não houve server.log, postmaster.pid nem ficheiro de
password no fim. O diretório `futanalysis_probe_disposable_mk01i3nk` foi conservado.
A associação dos processos PostgreSQL aos diretórios não pôde ser concluída
por falta de permissões; não se confirmou integralmente a ausência de resíduos.
A causa exata continua desconhecida. Não executar novamente com base neste guia:
é necessária nova autorização específica.

A revisão atual altera apenas código e documentação e executa testes simulados.
Não inspeciona nem modifica esse diretório antigo e não inicia/para processos.

### Captura preparada no harness

- Antes, stdout/stderr eram descartados com DEVNULL; os códigos não eram
  registados e as exceções perdiam os detalhes. Agora subprocess.run captura
  ambos em memória, com timeout de 45 segundos, sem os enviar para a consola.
- Cada comando acrescenta uma linha JSON a `command-diagnostics.jsonl`, apenas
  dentro do diretório novo do ensaio: etapa, código de saída ou evento timeout/
  erro de sistema, errno, stdout/stderr sanitizados, estado do log/PID e porta
  candidata. Não guarda argumentos, ambiente, passwords ou texto da exceção.
- Timeouts conservam stdout/stderr parciais. Um erro de SO conserva errno;
  uma falha a guardar evidências interrompe o ensaio, sem fallback de destino.
- O arranque mantém `pg_ctl -l <diretório-do-ensaio>/server.log`. Esse ficheiro
  é previamente criado de forma exclusiva e a escrita tem de ser possível
  antes de tentar arrancar. O diretório original é sempre conservado.
- Ambos os caminhos recusam nomes não aprovados, symlinks, hard links e destinos
  fora do diretório. Tentativas de stop acrescentam registos; não substituem a
  evidência de startup. Nenhum diretório é eliminado pelo harness.

### Sanitização e preservação de evidências

O relatório suprime a linha inteira quando contém password/utilizador sintéticos
conhecidos (incluindo representações percent-encoded e JSON), URLs, padrões de
conninfo, passwords, tokens, authorization/Bearer, API keys, cookies ou credenciais.
Blocos com marcador PRIVATE KEY fazem suprimir toda a saída. Caracteres de controlo
são neutralizados; UTF-8 inválido é substituído. Só depois da redação são limitados
os campos stdout/stderr a 64 KiB. O excerto do server.log lê até 64 KiB iniciais,
descartando uma última linha incompleta e assinalando truncagem, sem tocar no original.
Uma expressão de deteção de URLs tem comprimento limitado para evitar trabalho
quadrático com linhas longas sem espaços.

**server.log é evidência original, potencialmente não sanitizada.** O PostgreSQL
escreve diretamente nesse ficheiro através de pg_ctl; não é possível garantir que
todo o seu conteúdo futuro estará isento de segredos. Não o imprimir, anexar ou
partilhar automaticamente. Apenas command-diagnostics.jsonl foi preparado para
partilha, após revisão privada. chmod(0600) é aplicado, mas não substitui ACLs
Windows: o TEMP tem de estar protegido. A sanitização por padrões não reconhece
necessariamente segredos desconhecidos, formatos exóticos ou conteúdo arbitrário.
As pipes capturam a saída completa em memória antes de sanitizar; o limite dos
campos persistidos não constitui um limite global de memória do subprocesso.

### Resíduos e condições para novo ensaio

As verificações de ambiente, PID, porta e data_directory mantêm-se. Antes de stop,
o harness volta a confirmar o PID/diretório/porta e só dirige pg_ctl ao seu cluster.
Se a identidade não for confirmada, não termina nenhum processo. Ausência de
postmaster.pid, isoladamente, não comprova ausência absoluta de processos.
Falhas de limpeza são erros, não sucesso; não usar taskkill ou parar o serviço
PostgreSQL da aplicação para resolver resíduos ambíguos.

Antes de pedir nova autorização: rever estas alterações e resultados simulados,
confirmar um TEMP privado, ferramentas da mesma instalação e ausência de PG*
herdadas; esclarecer os resíduos do primeiro ensaio por um procedimento de leitura
autorizado, sem consultar bases existentes. O futuro ensaio deve usar failfast
para parar na primeira falha e conservar o diretório novo. Não alterar permissões,
desativar guardas, escolher outra base ou repetir o startup automaticamente.

Nesta etapa, nenhum binário PostgreSQL, ligação SQL ou teste de integração foi
executado. Não houve acesso Railway nem alteração do diagnóstico operacional.

Validação atual: **45 testes simulados aprovados** — 21 do harness e 24 do
diagnóstico. Os oito testes reais nem sequer foram selecionados para execução.
Foram usados os comandos locais, na raiz de ccdr-match-tracker:

```powershell
.\backend\.venv\Scripts\python.exe -B -m unittest discover -s docs/railway/tests -p test_disposable_cluster_safety.py -q
.\backend\.venv\Scripts\python.exe -B -m unittest discover -s docs/railway/tests -p test_read_only_probe.py -q
```

Incluem captura/timeout/errno, sanitização de formatos sensíveis, truncagem segura,
UTF-8 inválido, preservação de evidência, escrita append, erros de persistência e
recusa de caminhos inseguros/symlinks. Subprocessos, sockets e ligações reais são
bloqueados/simulados. A entrada futura da suite passa a usar failfast por defeito.

Estado: preparado e testado **apenas localmente com ligações simuladas**.
Não foi executado na Railway. Qualquer acesso remoto exige nova autorização.
Este procedimento substitui as instruções anteriores do diagnóstico no relatório
`RAILWAY_PRODUCAO_AUDITORIA.md`.

## Preparação pelo operador

Confirmar externamente no painel o projeto, ambiente, serviço `fut_analysis`,
deployment ativo e ligação ao PostgreSQL pretendido. Registar separadamente:

- UUID do projeto, UUID do ambiente e UUID do serviço da aplicação.
- Host, porta, nome da base e esquema esperado, confirmados no destino correto.
- SHA/artefacto ativo e diretório de trabalho da imagem.

Não deduzir os valores esperados das próprias variáveis do processo que vai ser
testado. Não assumir que o esquema é `public` ou que a revisão é `0006`.
Host e nome da base podem ser consultados privadamente; não partilhar a URL,
password, utilizador, tokens ou listagens de variáveis. Os argumentos não recebem
credenciais. Não executar `env`, `printenv`, `cat .env` ou comandos que imprimam
valores secretos. Não alterar variáveis para contornar uma recusa do diagnóstico.

O script requer Python 3.12, SQLAlchemy 2 e psycopg 3, já previstos no backend.
Não instalar dependências no container para resolver uma falha sem nova revisão.
Não importa `app`, não lê dotenv e não valida a configuração efetiva dos workers.
Lê exclusivamente o `DATABASE_URL` do processo para construir uma nova ligação.
Exige também `APP_ENV=production` e os três identificadores Railway correspondentes.

## Comandos remotos propostos — NÃO EXECUTADOS

1. Obter autorização explícita para esta sessão e diagnóstico de leitura.
2. Selecionar os identificadores confirmados. Com CLI já disponível e autenticada:

```sh
railway ssh --project PROJECT_ID --environment ENVIRONMENT_ID --service APP_SERVICE_ID
```

3. Confirmar a pasta da imagem identificada. A imagem combinada do repositório
   prevê `/app/backend`. Se isso não corresponder ao artefacto confirmado, parar.

```sh
cd /app/backend
pwd
test -d app && test -f alembic.ini
```

4. O Dockerfile não inclui necessariamente a pasta de documentação. Executar o
   conteúdo integral do script local revisto por stdin, sem upload nem edição do
   container. Substituir TODOS os marcadores abaixo pelos valores confirmados;
   a linha entre `PY` é um marcador, não é o código do diagnóstico:

```sh
python - --expected-project-id 'PROJECT_UUID' \
  --expected-environment-id 'ENVIRONMENT_UUID' \
  --expected-service-id 'APP_SERVICE_UUID' \
  --expected-host 'HOST_CONFIRMADO' \
  --expected-port PORTA_CONFIRMADA \
  --expected-database 'BASE_CONFIRMADA' \
  --expected-schema 'SCHEMA_CONFIRMADO' <<'PY'
# SUBSTITUIR pelo conteúdo integral e exato de docs/railway/read_only_probe.py
PY
echo $?
```

5. Guardar apenas o JSON sanitizado e o código de saída. Não acrescentar saídas
   do ambiente ou exceções. Terminar a sessão; não prosseguir para migração.

Não usar `railway run`: executaria localmente com variáveis Railway. Não executar
o diagnóstico a partir do `.env` local. Os comandos acima pressupõem um shell
remoto POSIX e uma versão da CLI que suporte esses seletores; se não suportar,
parar e rever o acesso, sem instalar, autenticar ou selecionar outro alvo por tentativa.

## Garantias e condições de paragem

Antes da ligação, compara projeto/ambiente/serviço e host/porta/base com os valores
independentes. Recusa loopback, destino incompleto, múltiplos hosts, parâmetros
de URL não aprovados e overrides libpq que possam alterar o destino. Só permite
os parâmetros de URL `sslmode`, `sslrootcert`, `sslcert`, `sslkey` e
`channel_binding`, sem valores repetidos. Não enfraquecer TLS para obter sucesso.

Uma ligação nova usa `connect_timeout=5`. Todas as consultas pertencem a um
único `BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY`.
Antes da primeira consulta, aplica exclusivamente com `SET LOCAL`:

- `statement_timeout=5000ms`;
- `lock_timeout=1500ms`;
- `idle_in_transaction_session_timeout=10000ms`;
- `search_path=pg_catalog`.
- `row_security=off`, para falhar se RLS ocultasse linhas da revisão (não contorna RLS).

Confirma a política na mesma transação. Os catálogos são qualificados com
`pg_catalog`; a tabela de revisão usa identificadores escapados de esquema e
tabela. Pesquisa explicitamente os esquemas não sistémicos das tabelas previstas:
nomes relevantes duplicados ou noutro esquema fazem parar, mesmo que legítimos.
Exige permissão SELECT, uma única revisão conhecida (`0001` a `0007`) e presença
coerente das tabelas previstas para essa revisão. Não inspeciona dados de jogos,
jogadores ou resultados. Só lê dados de `alembic_version` e metadados.

Qualquer recusa interrompe as consultas seguintes. Havendo transação iniciada,
tenta sempre `ROLLBACK` e fecha a ligação, inclusive em erros. Nunca usa COMMIT.
Falhas de rollback/fecho anulam qualquer resultado de sucesso.

| Resultado | Saída | Interpretação e ação |
| --- | --- | --- |
| `CONFIRMED` | 0 | Apenas estas verificações passaram; rever JSON e metadados externos. Não autoriza backup ou migração. |
| `UNCONFIRMED` | 1 | Guarda falhou: destino/ambiente ambíguo, esquema inesperado, revisão ausente/múltipla/desconhecida ou tabelas incoerentes. Parar e investigar. |
| `ERROR` | 2 | Falha de execução, ligação, autenticação, permissão, timeout ou limpeza. Parar; não corrigir a base automaticamente. |

`STATEMENT_TIMEOUT_OR_CANCELLED` não distingue timeout de cancelamento externo;
`LOCK_NOT_AVAILABLE_OR_TIMEOUT` também não identifica sozinho a causa exata.
Erros sem SQLSTATE reconhecido usam um código genérico. Não são impressos texto
da exceção, traceback, URL, host, utilizador ou credenciais.

`alembic_revision` indica a revisão encontrada nesta ligação, sem pressupor `0006`.
`migration_0007_in_image` e `competition_api_in_image` verificam apenas ficheiros:
não validam o conteúdo nem provam que o worker os carregou. Um SHA com formato
válido é apenas metadado do ambiente, não prova criptográfica do artefacto.
Se faltar `0007` na imagem, não tentar migrar nessa imagem.

## Limitações e próximo ponto de decisão

Os identificadores do processo podem estar incorretos ou adulterados; a comparação
não certifica a identidade Railway. Por isso o JSON mantém
`railway_identity_verified_externally=false`. DNS, proxy e identidade física do
cluster não são certificados pelo nome da base nem por `inet_server_addr()`.
TLS depende da configuração existente; o diagnóstico não impõe nem certifica TLS.
`backend_worker_connection_verified=false`: não comprova a ligação dos workers
nem compara os settings efetivos do backend. O operador deve cruzar os resultados
com o painel e o artefacto confirmado.

Os timeouts não constituem um limite global de tempo de rede. READ ONLY impede
escritas SQL desta transação, mas há atividade transitória, locks de leitura e
possíveis logs do servidor. Isto não é uma auditoria completa de colunas, índices,
constraints, grants ou integridade dos dados e não valida permissões de DDL.

Não houve ensaio PostgreSQL real nesta etapa: snapshot, locks e timeouts foram
verificados por simulação da sequência SQL. Produção, revisão Alembic, identidade
do destino e autenticação após rotação continuam desconhecidas.

Antes de pedir autorização separada para backup/restauro: rever este JSON,
confirmar externamente o destino, artefacto e revisão, identificar todos os writers,
executor e versões de pg_dump/pg_restore, armazenamento privado, capacidade,
janela de manutenção e destino isolado do restauro. Não executar essas operações
como continuação automática do diagnóstico.

## Validação local isolada

Na raiz `ccdr-match-tracker`, sem carregar fixtures da aplicação:

```powershell
.\backend\.venv\Scripts\python.exe -B -m unittest discover -s docs/railway/tests -p test_read_only_probe.py -v
```

Os testes injetam conectores simulados, bloqueiam o conector real e não alteram
o ambiente. Cobrem transação/ordem SQL, esquema qualificado, parâmetros de ligação,
identificadores, permissões, revisão ausente/múltipla, falhas de ligação, timeout,
limpeza e JSON/códigos de saída sanitizados.

## Última revisão técnica local — 15/10/2026

Foram lidos os sete ficheiros reais de migração, sem os importar ou executar.
Um teste AST verifica a cadeia `revision/down_revision` e as chamadas de criação
de tabelas nos `upgrade`, comparando o conjunto acumulado com o diagnóstico.

| Revisão | Tabelas aplicacionais acrescentadas | Conjunto esperado pelo diagnóstico |
| --- | --- | --- |
| 0001 | users, seasons, teams, players, matches, match_squads, match_events | CORE + alembic_version |
| 0002 | Nenhuma; substituição do enum de posições | CORE + alembic_version |
| 0003 | Nenhuma; coluna/constraint matchday | CORE + alembic_version |
| 0004 | Nenhuma; substituição do enum de eventos | CORE + alembic_version |
| 0005 | Nenhuma; crest_path e photo_path | CORE + alembic_version |
| 0006 | auth_sessions, login_throttles; também coluna e índice users | CORE + AUTH + alembic_version |
| 0007 | competitions, competition_teams, competition_fixtures | CORE + AUTH + COMPETITION + alembic_version |

`alembic_version` é criada pelo mecanismo Alembic, não por `op.create_table`
destes ficheiros. `REVISION_TABLES_INCONSISTENT` corresponde exatamente a estes
conjuntos **entre os nomes monitorizados**; outras tabelas não são inventariadas.
O teste AST não é um interpretador de SQL dinâmico: alterações futuras exigem
também revisão manual. Não foram alteradas migrações.

Correções demonstráveis desta revisão:

- Bloquear nomes de base com `=` ou prefixo URI PostgreSQL: libpq pode expandir
  `dbname` como conninfo e alterar o destino. Estes nomes são recusados mesmo
  quando confirmados pelo operador, uma restrição conservadora deliberada.
- `SET LOCAL row_security=off` evita interpretar uma vista parcial da tabela de
  revisões como uma revisão única. Se uma política teria de filtrar linhas,
  PostgreSQL falha, em vez de conceder bypass.

Compatibilidade revista estaticamente: psycopg 3 aceita `autocommit=True`,
`cursor.execute` e composição com `sql.Identifier`. O BEGIN explícito inicia
uma transação mesmo em autocommit; todos os SET LOCAL precedem as consultas.
A lista Python adaptada para `ANY(%s)` é compatível com arrays PostgreSQL.
Os catálogos/funções são qualificados; os nomes de tabelas são identificadores,
não parâmetros SQL. Não há context manager da ligação que faça commit implícito.
O cursor fecha antes do ROLLBACK; erros de transação abortada são tratados por
ROLLBACK e fecho. Isto foi verificado em código e por simulação, não num servidor.

Falsos positivos conservadores (paragem apesar de poder existir um alvo legítimo):
nomes monitorizados noutros esquemas, Alembic num esquema separado, tabelas
recriadas como views/foreign tables, esquemas fora da sintaxe permitida, revisões
novas ou branches Alembic legítimos, privilégios SELECT mínimos que não abrangem
todas as tabelas, parâmetros de ligação não aprovados e nomes dbname bloqueados.

Falsos negativos/limites: tabelas com nomes certos mas colunas, enums, índices,
constraints ou conteúdo incorretos; revisão stamped sem migração; tabelas extra
com nomes não monitorizados; tabelas temporárias/sistémicas são excluídas;
partições são aceites, embora as migrações criem tabelas ordinárias. O teste não
certifica integridade, esquema integral nem autenticidade do histórico.
O snapshot REPEATABLE READ estabiliza os dados consultados, mas não elimina
corridas de DDL, locks ou invalidações de objetos. Um erro nessas condições exige
parar e rever, não tentar corrigir a base. Um erro de rede durante BEGIN pode
deixar o resultado do comando incerto; o fecho da ligação é a última salvaguarda.

### Integração PostgreSQL descartável: preparada, NÃO executada

Não foi identificada uma instância descartável segura já em execução. Foram
encontrados `initdb` e `pg_ctl` no PATH, mas não foram invocados. A suite
`tests/test_probe_postgresql_integration.py` fica ignorada na descoberta normal.
Nenhuma ligação PostgreSQL foi aberta nesta etapa.

O futuro comando local, apenas após revisão/autorização do ensaio, é:

```powershell
.\backend\.venv\Scripts\python.exe -B docs/railway/tests/test_probe_postgresql_integration.py --run-disposable
```

Cria um cluster novo em diretório temporário exclusivo, com SCRAM apenas em
loopback, porta efémera e dados sintéticos. Não recebe URL, password, destino
externo ou nome de base existente; não lê dotenv nem invoca Alembic. Confirma
`data_directory` antes de escrever fixtures e não faz fallback para outro servidor.
Cria uma base por teste. No fim tenta parar apenas esse cluster; conserva os
ficheiros para revisão, sem eliminação recursiva. A password sintética é gerada
em memória, passada por ficheiro ao initdb e esse ficheiro é removido logo depois.
Não é impressa nem passada nos argumentos do processo. As roles limitadas recebem
essa password, USAGE e SELECT apenas conforme cada cenário, além de
pg_read_all_settings para permitir a validação de data_directory.

O adaptador de teste força a ligação ao cluster e permite exclusivamente o
endereço de servidor 127.0.0.1, mantendo a recusa de loopback no script operacional.
Logo, a integração não certifica o caminho completo de seleção de destino/TLS;
essas guardas continuam cobertas por testes unitários. As fixtures reproduzem
apenas nomes de tabelas, não a totalidade das migrações. Os testes reais preparados
cobrem isolamento/snapshot, erro de escrita READ ONLY, restauração dos SET LOCAL
após rollback, catálogos/esquema, revisão ausente/múltipla, statement_timeout,
lock_timeout, permissões e RLS. A sua correção operacional ainda depende de execução.

Resultado local desta revisão: descoberta de 32 testes, **24 passaram e 8 de
integração foram ignorados explicitamente**. Comando executado na raiz do projeto:

```powershell
.\backend\.venv\Scripts\python.exe -B -m unittest discover -s docs/railway/tests -p 'test_*.py' -v
```

Foram também compiladas em memória as três fontes Python, sem executar o probe.
Estes resultados são análise estática e verificações simuladas; não constituem
verificação real de PostgreSQL, rede, Railway ou migrações aplicadas.

### Auditoria do isolamento e ciclo de vida da suite — revisão seguinte

Problemas corrigidos no código dos testes, sem alterar o diagnóstico operacional:

- Limpeza registada antes de initdb: falhas em initdb, startup, ligações ou testes
  seguem o mecanismo `addClassCleanup` de unittest. A password é removida em
  finally. Ausência de PID torna o encerramento idempotente.
- Valida postmaster.pid (diretório e porta) antes de cada ligação e antes de
  parar o servidor. Depois de ligar, confirma novamente data_directory antes
  de habilitar escritas. Ligações começam com default_transaction_read_only=on.
- Recusa variáveis herdadas PG* verificando só nomes; não consulta os seus
  valores. Subprocessos recebem apenas uma lista mínima de variáveis do sistema.
  Não alterar configurações da aplicação para contornar esta recusa: rever um
  processo de ensaio isolado. Não há fallback para outro PostgreSQL.
- Substituiu trust por SCRAM e uma role administrativa aleatória. Desativa
  sockets Unix, escuta só em 127.0.0.1 e evita registo de SQL com passwords
  sintéticas nos erros. Não lê passwords da aplicação.
- Stop tenta fast e, se necessário, immediate apenas no cluster de teste.
  Se não confirmar remoção do PID, reporta erro em vez de declarar limpeza.
  Não mata PIDs arbitrários nem elimina diretórios recursivamente.
- Os comandos externos têm timeout e falhas sanitizadas. initdb e pg_ctl têm
  de pertencer à mesma instalação. Não há instalação automática.

Verificação real limitada a metadados locais: postgres.exe, initdb.exe e pg_ctl.exe
identificam-se como 18.6 através dos metadados dos ficheiros, sem os executar.
psycopg 3.3.6 está instalado. SCRAM, pg_read_all_settings, BEGIN explícito e
SET LOCAL row_security=off são compatíveis com o desenho para PostgreSQL 18;
o comportamento real desta combinação ainda não foi ensaiado. RLS off não
concede bypass: a role RLS não é owner nem superuser, pelo que a leitura deve
falhar se uma política teria de ocultar uma revisão.

Riscos residuais: a reserva da porta é libertada antes de pg_ctl arrancar.
Uma colisão deve fazer falhar o arranque; não se tenta outra base. Não existe
garantia absoluta de zero contacto com outro processo perante uma corrida em
que o servidor morra e a porta seja reutilizada entre as verificações. Mesmo
nesse caso, nenhuma escrita de fixture é autorizada sem validar data_directory.
Os controlos pressupõem que ficheiros e processos do mesmo utilizador não estão
a ser adulterados. chmod(0600) não configura uma ACL Windows completa; o
diretório TEMP do operador tem de ser privado. O ficheiro de password é breve
e efémero, mas ferramentas de segurança ou falhas de IO podem impedir a remoção.

Limpeza é uma tentativa verificável, não uma garantia após kill do Python,
queda de energia, bloqueio do SO ou adulteração do PID. Se a limpeza falhar,
parar e inspecionar apenas o diretório temporário criado; não parar o serviço
PostgreSQL de desenvolvimento. Ficheiros sintéticos retidos não são dados reais.

Resultado desta auditoria: **35 testes simulados passaram; os 8 testes PostgreSQL
continuaram ignorados** (43 descobertos). Inclui 11 novas regressões do harness,
com sockets, subprocessos e ligações bloqueados/simulados. Não foram executados
initdb, pg_ctl, migrações ou ligações PostgreSQL. A suite está preparada para
um primeiro ensaio local mediante autorização separada, numa sessão com TEMP
privado, mantendo a possibilidade de reportar falha de arranque/limpeza.
