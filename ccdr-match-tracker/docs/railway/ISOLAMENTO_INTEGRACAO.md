# Proposta de isolamento dos oito testes PostgreSQL

## Segunda ronda C1–C9 — revisão documental R2

Norma atual em [VALIDADORES_CORRECOES_P1_P10.md](VALIDADORES_CORRECOES_P1_P10.md).
Uma ArtifactBinding só associa bytes imutáveis; observação fica no boot original.
HistoricalQualification e QualificationApplicability exprimem uso histórico
revisto/autorizado sem afirmar estado atual. LocalResult assinado é preservado;
Invalidation e FinalResult são novos registos, e só o final participa no gate.
H16 é proposto H01–H08 mais confiança do pacote/imagem/exportador; aprovação
humana ainda necessária. Sem alteração de arquitetura aplicada ou ensaio real.

## Correções P1–P10 — contrato 2.0.0, sem implementação

Ver [contrato transversal](VALIDADORES_CORRECOES_P1_P10.md) e
[fixtures atualizadas](VALIDADORES_FIXTURES.md). O desenho separa coleta C0,
admissibilidade C1, avaliações locais independentes C2, consistência cruzada C3
e consolidação C4. HOST/ARTEFACTOS podem consumir factos guest admitidos sem
depender de aprovação VAL-GUEST. Referências tipadas, ArtifactBindings e
validades por classe evitam misturar boots ou autorizações com revisões.
As secções históricas não substituem essas regras. NÃO APTO; nada foi executado.

## Contratos documentais para o gate

Acrescentados [schemas fechados](VALIDADORES_SCHEMAS.md) para os sete validadores,
proveniência e decisão consolidada, e [fixtures sintéticas](VALIDADORES_FIXTURES.md)
positivas de estrutura e negativas. Não houve implementação ou execução.
O DAG por camadas separa factos de resultados locais e avaliação cruzada final;
nenhuma evidência em falta pode desencadear ações para a obter. Report documental
é sempre NÃO APTO. Revisão independente dos contratos e do mapping do build
é a próxima etapa segura, sem criar VM nem solicitar ensaio.

## Revisão de mecanismos e validação fail-closed

Acrescentada [matriz requisito/mecanismo/evidência/recusa](HYPERV_VALIDADORES.md),
com 16 requisitos e sete validadores propostos. Distingue análise estática,
verificação host, verificação guest e demonstração por ensaio de infraestrutura
separadamente autorizado. Nenhum controlo foi implementado ou consultado.

Bloqueios: HV sockets/relays e sessão/clipboard sem prova; quota global e
watchdog externos; boot imutável e exportador por definir; atestação guest sem
canal de retorno ainda sem continuidade comprovada. Desativar todos os drivers
Hyper-V não é compatível com hardware virtual mínimo. Corrigida a terminologia
do contrato para integração opcional, mantendo allowlist essencial pendente.
Estado NÃO APTO. Próxima etapa apenas schemas e fixtures documentais.

## Especificação e manifesto preparados para revisão

Ver [contrato declarativo da VM](VM_ESPECIFICACAO.md) e
[manifesto mínimo](PACOTE_TESTES_MANIFESTO.md). Proposta: Hyper-V geração 2 com
Ubuntu Server 24.04 LTS amd64, boot imutável e offline, sem NIC/canais opcionais,
2 vCPU/4 GiB fixos, volume work de 2 GiB e orçamento host rígido de 32 GiB.
Limites, recursos Hyper-V, boot Linux, quotas e watchdog ainda não têm implementação
nem validação real. O contrato é documental e não é importável/provisionável.

O manifesto fixa os hashes locais de três fontes estritamente necessários;
imagem, lock Linux, preflight, controlos e ISO continuam pendentes. Campos null
e qualquer divergência fazem recusar. Nenhum teste foi executado nesta etapa,
o harness não foi alterado e nenhum resíduo foi investigado. Mantém-se NÃO APTO.
Próxima etapa: revisão estática do mapping Hyper-V e do esquema de validação,
sem criar ambientes ou solicitar ensaio.

Estado: **arquitetura proposta; não implementada nem validada operacionalmente**.
Mantém-se NÃO APTO no Windows atual. Nenhuma VM/contentor/processo PostgreSQL
foi criado, iniciado, parado ou consultado nesta etapa. Não executar comandos
do ensaio com base neste documento. Railway está fora do âmbito.

## Decisão e modelo de ameaça

Recomenda-se **uma VM Linux nova por execução, offline, sem adaptador de rede,
sem integração de ficheiros com o host e com discos/recursos limitados**.
Python, runner e PostgreSQL vivem na mesma VM; a ligação SQL ocorre apenas no
loopback do guest. Não é necessário Docker dentro da VM.

O objetivo é retirar do caminho operacional tanto produção como a base Windows:
o guest não tem interface para as alcançar, credenciais para as autenticar nem
volumes/processos do host que possa modificar. A segurança deixa de depender
apenas de reconhecer caminhos/PIDs e de conseguir redigir todos os segredos.

Pressupostos: host, hipervisor e imagem base são confiáveis; o operador não altera
a configuração aprovada durante a execução. Não é uma garantia contra escape
de hipervisor, administrador malicioso ou host comprometido. Não se promete
isolamento absoluto. A escolha/versão do hipervisor depende da disponibilidade
local e terá revisão própria; não foi inspecionada nem instalada nesta fase.

## Comparação das três opções

| Critério | VM Linux descartável offline | Docker isolado | Windows local atual |
| --- | --- | --- | --- |
| Processos | Kernel guest separado; todos os descendentes permanecem na VM | Namespaces e cgroups; partilha kernel com o host Linux/VM Docker | Mesmo SO e utilizador; guardas por ficheiros não são contenção |
| Ficheiros | Só discos guest dedicados; sem pastas partilhadas | Boa contenção se root read-only, sem bind mounts/volumes/socket Docker | TEMP/ACL/reparse points e corridas no host real |
| Rede | Adaptador ausente no hipervisor; apenas loopback guest | Network namespace sem rede externa, sem host networking/port publishing | Loopback do host inclui bases reais; rede de produção continua disponível |
| Produção Railway | Sem NIC, canais do host ou credenciais; sem caminho operacional previsto | Bloqueável com rede none e ausência de segredos; daemon/configuração privilegiada são riscos | Exclusão depende do programa/configuração, não de uma fronteira externa |
| Memória/CPU | Limites hipervisor e cgroup guest; watchdog externo | Limites cgroups; exigem confirmação do runtime e das opções | Não existem limites globais do ensaio demonstrados |
| Disco | Volume guest de tamanho fixo e reserva física; nenhum destino host gravável | Root layer/log driver exigem quotas próprias; limites CPU/RAM não limitam disco | Logs/capturas/PGDATA podem ocupar o disco partilhado |
| Descendentes | Cgroup guest + encerramento da VM por identidade do hipervisor | Cgroup/init apropriado + lifecycle do contentor, sem PID namespace host | Timeout do helper não garante terminar PostgreSQL |
| Portas | Só guest, sem NAT/forward; colisão não atinge serviços do host | Só namespace do contentor, sem publish; execução de tudo no mesmo contentor | Reutilização pode atingir outro listener local |
| Logs/credenciais | Apenas sintéticos; retenção em disco guest privado | Apenas sintéticos; cuidado com logging externo/daemon | Logs residem no TEMP real; ACLs ainda não comprovadas |
| Reprodução | Imagem e pacote fixados por hash; estado novo por ensaio | Muito boa com digest/dependências fixos | Dependências e processos concorrentes do host variam |
| Complexidade | Maior preparação; fronteira de isolamento mais clara | Média; disco, daemon e diferenças Docker Desktop precisam de revisão | Menor arranque inicial; segurança exigiria continuar a expandir o harness |

Docker é alternativa futura aceitável apenas após desenho equivalente de quotas,
rede, volumes e lifecycle; não se considera um contentor privilegiado, montagens
do host ou o socket Docker uma solução de isolamento. A VM offline é preferida
para este caso porque o host já possui bases reais e resíduos não atribuídos.

## Requisitos derivados do harness atual

O harness usa initdb/pg_ctl, binários PostgreSQL 18, Python 3.12, psycopg 3 e
SQLAlchemy 2; unittest é suficiente. O módulo de integração importa helpers de
test_read_only_probe.py, que por sua vez importa read_only_probe.py por caminho.
Preservar essa pequena árvore de ficheiros no pacote. Não precisa de iniciar a
aplicação, importar settings, carregar dotenv ou executar Alembic.

As dependências atuais da aplicação são intervalos de versões, não um lock de
ensaio. Preparar um manifesto próprio com versões exatas, hashes das wheels e
origem da imagem/binários. Não copiar a venv Windows para Linux. Os 52 testes
simulados são evidência histórica, não certificação da futura imagem Linux.

Continuam úteis as verificações de root/PID/data_directory, failfast e relatórios
sanitizados, mas passam a ser defesa adicional. A fronteira que impede alcançar
o host/produção é o hipervisor sem NIC nem canais partilhados.

## Perfil de configuração obrigatório proposto

| Área | Configuração alvo | Evidência exigida |
| --- | --- | --- |
| Rede | Zero adaptadores virtuais; sem NAT, bridge, host-only, encaminhamento, DNS ou acesso de gestão guest pela rede | Configuração efetiva exportada pelo hipervisor + inventário guest |
| Integrações | Sem clipboard, drag/drop, pastas partilhadas, USB/passthrough, discos host, port/serial forwarding, sockets de gestão ou agente com execução no host | Lista de dispositivos/canais efetivos; só consola gráfica local aprovada |
| Entrada | ISO de código mínimo, read-only, verificada por hash; nenhuma pasta de projeto montada | Manifesto de ficheiros permitido e hash do ISO/pacote |
| Imagem | Linux/Python/PostgreSQL pré-instalados e fixados; sem contas/tokens pessoais, SSH keys, cloud-init credentials ou ferramentas Railway | Proveniência, hashes, inventário de pacotes e revisão de conteúdo |
| Recursos VM | Proposta inicial: 2 vCPU, RAM fixa 4 GiB, sem ballooning/dynamic memory | Configuração efetiva e limites reconhecidos pelo hipervisor |
| Disco | Sistema base read-only adequado ao boot; /work num disco guest dedicado de 2 GiB, tamanho fixo e espaço host reservado; armazenamento runtime/volátil também limitado | Inventário de discos/mounts e orçamento total host; validar que a ferramenta não criou disco expansível sem limite físico |
| Escritas | PGDATA, WAL, capturas, server.log e relatórios em /work; /tmp aponta para o mesmo volume; sem exportação/log collector externo | Mounts guest e caminhos resolvidos; logging guest volátil com teto, por exemplo 16 MiB |
| Utilizador | Runner dedicado não-root, umask 077, sem sudo e sem dados reais | Identidade/grupos/permissões efetivos; initdb não deve correr como root |
| Contenção guest | Serviço/cgroup exclusivo para runner e todos os descendentes; KillMode=control-group; proposta MemoryMax=2 GiB, TasksMax=128, CPUQuota=200%, swap desativada | Configuração e membership kernel, sem confiar no ficheiro PID |
| Tempo | Timeout de comando preservado; orçamento global proposto de 180 s, supervisionado fora do guest | Especificação do watchdog e vínculo ao UUID da VM, não a PID numérico reutilizável |
| Saída | Nenhum ficheiro gravável do host exposto ao guest; exportação só após execução/encerramento autorizados | Procedimento de extração offline, allowlist e armazenamento privado |

Estes números são limites propostos, não resultados de capacidade. Se forem
insuficientes, o resultado é falha documentada; qualquer aumento exige revisão.
Um disco cheio deve afetar apenas o volume descartável. É necessário contabilizar
também snapshots, overlays, journaling e logs do hipervisor no orçamento host;
um limite de /work isolado não limita esses outros destinos.

O runner futuro deve recusar a execução sem um manifesto de ensaio aprovado e
sem preflight de isolamento. Um manifesto dentro do guest não é prova suficiente:
deve ser cruzado com configuração independente do hipervisor. Não acrescentar
agora uma opção que apenas desative proteções do Windows.

## Evidência independente de ausência de acesso à produção

Não testar conectividade contra Railway, DNS de produção ou IPs reais. A prova
pretendida é a ausência do canal, não uma tentativa de ligação que falhe.

1. Um operador/revisor obtém configuração efetiva da VM do plano de controlo do
   hipervisor: UUID, zero NICs, zero canais partilhados, discos identificados e
   read-only input. Comparar configuração declarada com a efetivamente aplicada.
2. Outro plano de evidência, dentro do guest e antes de PostgreSQL, inventaria
   interfaces, rotas e sockets: só loopback, nenhuma rota não local e nenhum
   PostgreSQL previamente ativo. O preflight não inicia serviços nem usa SQL.
3. Cruzar o pacote por hashes com uma allowlist: só diagnóstico, helpers/testes
   aprovados e manifesto; excluir .env, .git, ai-learning, dumps, certificados,
   credenciais e configuração da aplicação. A verificação não imprime segredos.
4. Confirmar ausência de canais indiretos: agente guest/host, filesystem partilhado,
   proxy de credenciais, dispositivos e forwarding. Zero NICs isoladamente não
   exclui todos os canais possíveis.
5. Após autorização própria, um teste de rede separado pode usar um destino
   sintético de laboratório, nunca Railway, para validar o preflight/recusa.
   Não é necessário para esta fase documental e não substitui os inventários.
6. Guardar relatório assinado/identificado pelo revisor, hashes, horário e UUID.
   Ausência de evidência, discrepância ou interface inesperada implica paragem
   antes do arranque PostgreSQL. Não aceitar apenas declaração do harness.

Nenhuma destas verificações reais foi feita nesta fase. A fronteira depende de
hipervisor/host confiáveis e de não alterar a configuração depois de a verificar.

## Migração em etapas pequenas

| Etapa | Trabalho proposto | Validação/saída | Autoriza executar PostgreSQL? |
| --- | --- | --- | --- |
| 0 — atual | Arquitetura, comparação e critérios | Este documento; nenhuma alteração do harness | Não |
| 1 | Especificação declarativa vendor-specific, esquema do manifesto e exportação | Revisão estática + testes de rejeição de NIC/share/disk ilimitado; sem criar VM | Não |
| 2 | Definição do pacote mínimo e lock de dependências; desenho da imagem | Manifesto/hashes propostos, análise de imports, auditoria sem segredos | Não |
| 3 | Adaptar runner a Linux não-root, preflight obrigatório e relatórios independentes | Mocks de mounts/interfaces/cgroup/manifesto, opt-in/failfast, 8 casos preservados | Não |
| 4 | Rever lifecycle externo por UUID e extração offline segura | Simulações de timeout, identidade divergente e falta de evidência; nada executado | Não |
| 5 | Provisionar a imagem/VM e recolher evidência de isolamento, sem PostgreSQL | Só mediante autorização separada para criação/boot e inspeção; relatório host+guest | Não |
| 6 | Rever evidência e pedir autorização dirigida aos oito testes nessa VM | Destino/UUID/imagem/limites conhecidos; protocolo de falha aceite | Só após nova autorização explícita |
| 7 | Futuro ensaio e revisão de resultados | 8 resultados individuais, erros de setup distinguíveis, prova de contenção/encerramento | Apenas no âmbito autorizado |
| 8 | Quarentena, exportação e descarte | Evidências retidas e destino revisto; eliminar VM/discos apenas com autorização própria | Não implica outras operações |

Não misturar ensaio de migrações/restauro com estes oito testes. As fixtures
continuam sintéticas e não reproduzem o esquema completo. Falha de setup significa
zero testes executados, não oito testes aprovados/ignorados. Os critérios de
autorização e os critérios de sucesso dos testes são decisões distintas.

## Critérios objetivos de aceitação

Antes de considerar aptidão para pedir ensaio:

- AC1: configuração host+guest confirma zero NICs/canais partilhados e apenas
  discos descartáveis identificados, sem volumes do host de desenvolvimento.
- AC2: pacote contém exclusivamente a allowlist e dependências fixadas; hashes
  coincidem com a revisão aprovada e não há credenciais/dados da aplicação.
- AC3: todos os destinos de escrita e logs têm limites rígidos contabilizados;
  memória/CPU/tempo/árvore de processos estão sujeitos a controlo externo.
- AC4: preflight recusa qualquer discrepância antes de executar PostgreSQL;
  casos de rejeição têm regressões simuladas e revisão independente.
- AC5: UUID da VM, mounts, UID, cgroup e estado inicial sem bases existentes
  estão documentados; ações de lifecycle só podem referir essa VM.
- AC6: procedimento de inspeção/extração mantém o guest sem acesso gravável ao
  host; relatório sanitizado limitado, brutos privados e nunca partilhados automaticamente.
- AC7: plano de falha de setup/timeout não depende de matar PIDs desconhecidos;
  eventual encerramento do guest mantém todos os descendentes na fronteira VM.
- AC8: resíduos anteriores são tratados num procedimento separado, sem ligação
  nem montagem no guest e sem os apagar. Ambiguidade impede ações sobre o host.

Após um futuro ensaio autorizado: oito testes efetivamente aprovados, zero
falhas/ignorados; setup e cleanup explicitamente reportados; confirmação externa
do estado da VM/árvore sem confiar apenas em PID-file; evidências exportadas de
forma controlada. Qualquer critério incumprido mantém NÃO APTO.

## Investigação separada dos resíduos Windows — plano não executado

Alvo histórico: diretório `futanalysis_probe_disposable_mk01i3nk` anteriormente
reportado. Não foi relido, modificado, copiado ou apagado nesta fase.

1. Obter autorização exclusiva para inspeção local de leitura, com escopo de
   caminho/processos e sem SQL. Se a permissão disponível não bastar, reportar
   desconhecido e parar; não escalar automaticamente nem reiniciar serviços.
2. Um operador autorizado inventaria metadados/ACLs/reparse points desse caminho,
   presença de PID/opções/logs e horários. Não partilhar conteúdos brutos, linhas
   de comando integrais ou variáveis; podem conter segredos. Não seguir links
   para outros diretórios. Qualquer hash/cópia de evidência requer escopo próprio.
3. Correlacionar por fontes do SO PID + creation time + executável + proprietário
   + árvore pai/filhos + listener, comparando diretório e horários do ensaio.
   Não inferir identidade por nome postgres.exe, PID-file ou porta isolados.
4. Classificar: pertença confirmada, não pertencente ou desconhecida. A ausência
   de um ficheiro PID não confirma que todos os processos desapareceram.
5. Produzir relatório sanitizado e preservar o estado. Não executar pg_ctl,
   taskkill, SQL, remoção, alteração de ACL ou tentativa de reparação. Qualquer
   encerramento/limpeza posterior exige proposta e autorização separadas.

Os resíduos não são reutilizados na VM e não são motivo para alterar a base
real. Uma VM nova pode ser desenhada independentemente da resolução da causa
do primeiro erro; a investigação do host não se converte em cleanup automático.

## Riscos residuais e próxima etapa

Subsistem vulnerabilidades de hipervisor/imagem, configuração incorreta do
operador, adulteração por administrador, falha do watchdog, pressão de recursos
no host e fugas na exportação de artefactos. São reduzidos com imagem mínima,
origem verificável, revisão em dois planos, reservas/quotas e ausência de segredos.
Linux também tem symlinks/TOCTOU; a VM contém o impacto, não elimina os bugs.

**Próxima etapa sem ensaio real:** redigir a especificação declarativa do
hipervisor escolhido e o esquema do manifesto/preflight, com fixtures de
configuração válida e inválida, revistos estaticamente. Não criar VM, contentor,
imagem em execução ou processos. A arquitetura fica proposta; a execução
continua NÃO APTO até haver implementação e evidência dos critérios acima.
