# Railway — auditoria de preparação do Campeonato, 15/10/2026

## Segunda ronda documental C1–C9 — 2.0.0 R2, NÃO APTO

Corrigidos os nove documentos indicados apenas no plano documental. R2 substitui
o rascunho anterior, mantendo versão 2.0.0 por nunca ter sido aprovado/implementado
como interface operacional. É decisão de gestão de rascunho proposta: a futura
política deverá vincular hashes dos conteúdos exatos; versões iguais com bytes
diferentes não são intercambiáveis. Envelopes 1.0.0 continuam recusados.

| Correção | Definição concreta / referência | Estado e limite |
| --- | --- | --- |
| C1 | Contrato transversal §1: Capture artifact/boot, HistoricalQualification, QualificationApplicability | Sem mudar boot observado; uso posterior exige comparação/revisão/ato próprio |
| C2 | §7: LocalResult imutável, Rejected, Invalidation e FinalResult novo e assinado | PASS histórico não é PASS final; nunca alterar bytes previamente assinados |
| C3 | §8 e matriz HYPERV_VALIDADORES H16: proposta H01–H08 mais pacote/imagem/exportador | Justificação: confiança no boot além dos canais; aprovação humana obrigatória, enquanto ausente UNKNOWN |
| C4 | §4: teto1024 > específico > default256, específicos podem exceder default | Limites aninhados e globais preservados; overflow recusa |
| C5 | §4: ordens por coleção, JCS, Content/Artifact/Signature hashes e domínio de assinatura | Política JCS/Ed25519 candidata; nenhum vetor extenso/digest/assinatura real calculado |
| C6 | §5: CollectionEnumeration + SourceRecord value=[] com scope/collector/subject/checkpoint/support | Lista vazia e complete=true isolados não provam ausência |
| C7 | §3: Checkpoint fechado com evento, instante, sujeito, contexto, relógio e capturas avaliadas | Revisão posterior não renova captura; políticas temporais candidatas |
| C8 | §1: Review de RecordTarget com tipo/id/ContentHash/sujeito; revisão de associação fora do Binding | Rever captura não aprova associação; revisão não concede autorização |
| C9 | Fixtures §§7–10: bundle completo em forma, casos históricos/zero/imutabilidade/limites/H16/missing/overflow/streams/assinatura | Expectativas documentais, não resultados executados nem evidências reais |

As contradições de Binding, resultados locais/finais, H16 e limites foram
substituídas por regras explícitas. Source Fields representam listas inteiras,
sem notação [] ambígua. Reason codes incluem as recusas R2. Comparação de IDs
de registos é por tipo, não pressupõe que UUID não comece por letra.

Limites honestamente pendentes: digests numéricos de registos extensos e vetores
criptográficos completos não foram calculados; exemplos mostram receitas de
bytes e metadados sintéticos, não assinaturas verificadas. O bundle literal é
input parcial com uma Entry, permitido pelo schema; decisão completa exige os
sete pares local/final e os dezasseis requisitos. Exemplo consolidado é relacional,
não JSON materializado. Estes pontos precisam de revisão humana antes de
aprovação documental; não se declara cobertura testada ou implementação pronta.

Dependem ainda de fontes oficiais/revisão: mapping build Hyper-V, política
criptográfica/raízes, registos de revogação/nonce, qualificação/aplicabilidade,
limites e relógios, observação independente e fluxo de exportação. Configuração
real, quotas, boot, watchdog/árvore e ausência de rede/canais não demonstrados.

Não foram executados scripts, testes, fixtures, validadores, comandos
administrativos, SQL ou operações Hyper-V/PostgreSQL/Railway/VM/processos.
Nenhuma dependência instalada, resíduo investigado ou transferência efetuada.
Harness/código/configuração de produção não alterados; não houve aprovação final.
Próximo passo apenas documental: nova revisão independente dos nove ficheiros R2,
com atenção a receitas/hashes, imutabilidade, fixtures e decisões normativas.
Estado final obrigatório **NÃO APTO**. Não solicitar nem executar ensaio.

## Histórico R1: correção exclusivamente documental P1–P10 — NÃO APTO

Normas atuais: [schemas 2.0.0](docs/railway/VALIDADORES_SCHEMAS.md),
[contrato transversal](docs/railway/VALIDADORES_CORRECOES_P1_P10.md) e
[fixtures documentais](docs/railway/VALIDADORES_FIXTURES.md). As regras 1.0.0
de contexto/freshness/ordem/decisão descritas nas secções históricas foram
substituídas, não constituem alternativas nem conversão automática.

| Problema | Correção documental | Limite ainda pendente |
| --- | --- | --- |
| P1 | Run/VM/Boot/Capture/Review separados; Binding de artefactos; replay/reassociação recusados | Registos e observação independentes reais não existem |
| P2 | Seis classes temporais; captura original distinta de revisão, validade por ponto/contexto | Política temporal e relógio externo não aprovados |
| P3 | C0 coleta → C1 admissibilidade → C2 locais → C3 cruzada → C4 decisão; invalidação transitiva | Nenhum DAG/validador implementado |
| P4 | SourceInventory/SourceRecord/OBS-TEMPO, enumeração e projeção por campo; claims ligadas à fonte | Mapping Hyper-V oficial/exaustividade/coletor independente pendentes |
| P5 | Domínio de assinatura + JCS proposto, metadados/contexto vinculados, perfil Ed25519 candidato | Criptografia/raízes/chaves ainda sem aprovação; não geradas |
| P6 | Ato autorizador fechado e refs authorization/review/observation/technical distintas | Emissor/registro/revogação/nonce reais não verificados |
| P7 | KernelRelease e PackageVersion/version_scheme; comparação exata sem normalização destrutiva | Validação semântica de versões e lock ainda por rever |
| P8 | device_id único; par controller_id/slot único | Inventário real não verificado |
| P9 | Resultado inclui versão/hash implementação/schema/coletor e revisão externa | Identidade declarada não é identidade verificada |
| P10 | 16 RequirementResult obrigatórios; owners/fontes/eixos/recusas; 7 resultados finais; agregação determinística | Nenhum requisito operacional demonstrado |

Fixtures substituídas por casos isolados com objetivo, pré-condições, alteração,
resultado estrutural, semântico e motivo. Incluem coleta parcial/truncada/falhada,
extra aninhado, replay, autorização de tipo errado, NIC desligada, switch/serviço/
endpoint/ISO extra, Enhanced Session, memória dinâmica, quota sem prova,
descendente fora da árvore, transição inválida, resultado contraditório, requisito
omitido e dependência invalidada posteriormente. São símbolos documentais,
não assinaturas/evidências reais nem resultados executados.

Revistos os oito documentos pedidos, atualizados apenas para coerência. Nenhum
script/teste/validador foi executado, nenhum controlo implementado, harness/código
de produção alterado, VM/processo operado, rede/SQL/Railway acedidos, dependência
instalada ou resíduo investigado. Hashes existentes não foram recalculados.
Próximo passo apenas documental: revisão humana independente do contrato 2.0.0,
canonicalização/assinaturas propostas, refs tipadas, fontes, DAG/fixtures e mapping
com documentação oficial offline do build. Estado final **NÃO APTO**.

## Histórico: schemas fechados e fixtures 1.0.0 — NÃO APTO

Criados [VALIDADORES_SCHEMAS.md](docs/railway/VALIDADORES_SCHEMAS.md) e
[VALIDADORES_FIXTURES.md](docs/railway/VALIDADORES_FIXTURES.md), exclusivamente
documentais. Especificam SC-HOST, SC-MANIFESTO, SC-ARTEFACTOS, SC-GUEST,
SC-RECURSOS, SC-LIFECYCLE e SC-EXPORTACAO versão 1.0.0; envelope, contexto,
evidências/proveniência e SC-DECISAO consolidado também são fechados.

Definidos campos/tipos/enums/limites/relações, evidências e origem exigidas,
ordem de avaliação, recusas e tratamento de missing/unknown. Sete fixtures de
entrada estruturalmente propostas por inspeção, catálogo sintético e variantes
negativas por schema cobrem extra/missing/tipo/versão, hash/dependência divergente,
contradição, identidade, falta de evidência e proveniência não verificável.
Nenhuma fixture foi materializada/executada por parser; são exemplos documentais.

O relatório exige sete resultados e cinco eixos separados (estrutura,
criptografia, proveniência, configuração aplicada, comportamento real), evidências
aceites/rejeitadas, requisitos pendentes e motivos de recusa. document_review,
documentary ou qualquer evidência synthetic impõem NAO_APTO. Uma declaração
real=true/nature=real não constitui prova: exige fontes/assinaturas/raízes externas.
APTO só é admissível após implementação e validação real, autorizada, independente
e completa, na qualificação operacional definida, sem conceder autorização de ação.

Dependências: sintaxe/identidade inicial → manifesto/artefactos/proveniência →
host → guest/recursos → lifecycle final → exportação → decisão. Falhas bloqueiam
consumidores; evidência futura não autoriza execução/exportação para se obter a si
própria. Relatório parcial permanece NÃO APTO.

Pendências: documentação oficial offline do build Hyper-V para IDs/enumerações,
serviços/relays/Enhanced Session, boot, recursos, discos e lifecycle; formatos
dos inventários fonte, trust store/assinaturas/política aprovada, imagem/lock,
quota/watchdog, atestação guest, contenção e exportador. Assinatura/hash não
prova completude do coletor, ausência de segredos ou host não comprometido.

Só documentação foi criada/alterada. Não houve execução de scripts/validadores,
testes, comandos administrativos, PostgreSQL/SQL/Railway, processos, VMs,
transferências ou investigação de resíduos. Harness e produção não alterados.
Os 52 testes simulados são históricos e não foram repetidos. Próxima etapa:
revisão humana independente dos contratos/fixtures e mapping com documentação
oficial offline, sem solicitar ensaio real. Mantém-se expressamente **NÃO APTO**.

## Fase atual: mapping Hyper-V e especificação de validadores — NÃO APTO

Criado [HYPERV_VALIDADORES.md](docs/railway/HYPERV_VALIDADORES.md), com matriz
H01–H16: requisito, mecanismo candidato, método, evidência e condição de recusa.
Não houve consulta oficial externa nem verificação administrativa: a existência,
semântica e disponibilidade das propriedades no build alvo continuam pendentes.

Especificados sete validadores independentes por âmbito: host, manifesto/hashes,
artefactos/dependências, guest, recursos, identidade/lifecycle e exportação.
PASS/FAIL/UNKNOWN, schemas fechados e vínculo por UUID/host/run/boot/hashes são
propostos. FAIL/UNKNOWN ou evidência incompleta bloqueiam. Nenhum validador
foi implementado; todos PASS ainda exigiriam autorização externa dirigida.

| Bloqueio / requisito | Criticidade | Correspondência / limite identificado | Evidência pendente |
| --- | --- | --- | --- |
| NICs/switches | Alta | Inventário efetivo por VMId; não basta desligar NIC | Host + interfaces guest; nenhum inventário recolhido |
| Integração/Enhanced Session/clipboard | Alta | Integration Services e política host/cliente são controlos distintos | Lista completa de serviços/IDs e sessão efetiva, sem alterações globais |
| HV sockets/relays | Alta | Nenhum bloqueio global por VM comprovado; NIC ausente não resolve | Endpoints/permissões host+guest e mecanismo efetivo no build alvo |
| Dispositivos/boot | Alta | Inventário exato; Secure Boot não verifica todo o rootfs | Geração, firmware, cadeia assinada, mounts e hashes de imagem |
| CPU/RAM | Alta | Perfil Hyper-V mais cgroup; unidades/semântica precisam revisão | Configuração aplicada e limites guest |
| Disco total | Alta | VHDX fixed não limita configs/logs/RAM-state do host | Backend de quota global e demonstração de aplicação |
| Deadline/descendentes | Alta | Watchdog externo por UUID + cgroup + fronteira VM | Protocolo e ensaio futuro de contenção/Off confirmado |
| Atestação guest prévia | Alta | Sem canal de retorno não há prova externa síncrona atual | Fluxo faseado, continuidade entre boots ou revisão explícita do requisito |
| Importação/exportação | Alta | ISO read-only / cópia offline em appliance, não shared folders | Appliance/parser/ACLs/allowlists/aprovação próprias |
| Produção fora do alcance previsto | Alta | Conjunção dos controlos, sem sondar Railway | Dois planos de evidência; não declarar garantia absoluta |

Corrigida apenas a terminologia documental: desativar integração opcional não
significa eliminar VMBus/hypercalls/drivers mínimos. A allowlist desse hardware
essencial permanece null e bloqueia. Importação por ISO e exportação por nova
media finita são canais intencionais sob autorização própria, não zero fluxo
absoluto de informação nem transferências efetuadas.

Casos R01–R15 incluem NIC/canal/device extra, hash/ficheiro/dependência divergente,
quota não aplicada, UUID errado, timeout sem Off, evidência incompleta ou antiga,
tipos ambíguos e exportação não autorizada. A validação documental não demonstra
o comportamento de nenhum destes controlos reais.

Só documentação foi alterada. Não houve testes, comandos Hyper-V/administrativos,
PostgreSQL/SQL/Railway, serviços externos, processos, VMs ou transferências de
ficheiros. Harness, produção e resíduos não foram alterados/investigados.
Próxima etapa segura: schemas fechados e fixtures documentais de aceitação/recusa,
mais revisão do mapping com documentação offline do build alvo quando disponível.
Não se solicita ensaio real. Mantém-se **NÃO APTO**.

## Fase atual: contrato da VM e manifesto — NÃO APTO

Criados [VM_ESPECIFICACAO.md](docs/railway/VM_ESPECIFICACAO.md) e
[PACOTE_TESTES_MANIFESTO.md](docs/railway/PACOTE_TESTES_MANIFESTO.md).
Escolha proposta: Hyper-V geração 2, Ubuntu Server 24.04 LTS amd64, sem NIC,
shares ou canais opcionais; boot read-only, volume dedicado 2 GiB, orçamento
host rígido 32 GiB, 2 vCPU, RAM fixa 4 GiB e deadline externo de 180 s.
Disponibilidade do Hyper-V, mapping das propriedades, imagem, quotas e watchdog
não foram verificados. Não existe implementação de ambiente ou validador.

O inventário mínimo inclui diagnóstico, helper unitário importado e módulo dos
oito testes. SHA-256 calculado apenas para esses três fontes por leitura local;
não foram lidas/hashadas credenciais ou configurações reais. Hashes são snapshot
de bytes do working tree, não prova de aprovação independente. Lock transitivo
Linux, hashes de imagem/binários/preflight/ISO e aprovação continuam pendentes.

Critérios V1–V10 vinculam cada requisito à evidência host/guest ainda necessária.
Política declarada fail-closed: qualquer ficheiro/dependência inesperado, hash
divergente, rede/canal partilhado, limite ausente ou campo pendente impede
execução. As recusas ainda não estão implementadas; não confundir proposta
com controlo efetivo. Lifecycle e descarte exigem autorizações separadas.

Apenas documentação foi criada/alterada. Nenhum teste foi executado, harness
ou código de produção alterado, ambiente criado, processo operado, dependência
instalada, segredo exportado ou serviço externo consultado. Resíduos não foram
investigados/eliminados. Produção Railway permanece inteiramente fora do âmbito.

Próxima etapa segura: revisão estática independente do mapping Hyper-V e dos
esquemas de manifesto/preflight, com especificação de casos de recusa, sem
provisionamento ou pedido de ensaio. Mantém-se **NÃO APTO**.

## Proposta de arquitetura: VM Linux descartável offline

Foi interrompida a expansão incremental do harness. A solução recomendada é
uma VM Linux nova por execução, sem adaptador de rede nem canais partilhados
com o host, pacote mínimo read-only sem segredos e discos/recursos limitados.
Runner e PostgreSQL comunicam apenas pelo loopback guest. Não se recomenda
executar novamente no Windows atual; Docker isolado é alternativa futura com
revisão própria de quotas, namespaces, daemon e volumes.

A [proposta completa](docs/railway/ISOLAMENTO_INTEGRACAO.md) compara as três
opções, define configuração, etapas e critérios AC1–AC8, evidências independentes
host/guest da ausência de canal para produção e um plano separado não destrutivo
para investigar resíduos Windows. Nenhuma tentativa de ligação à Railway faz
parte da comprovação. A ausência de NIC deve ser cruzada com ausência de canais
indiretos, credenciais e mounts do host.

Só houve análise local e documentação nesta etapa: nenhum código de produção
ou harness alterado, nenhum teste executado, VM/contentor/processo iniciado,
parado ou modificado. Nenhum resíduo foi consultado ou apagado. Os 52 testes
simulados anteriores permanecem evidência histórica, sem nova validação real.

**Decisão atual: NÃO APTO para execução; arquitetura proposta, não implementada.**
Próxima etapa documental: escolher hipervisor e preparar especificação declarativa,
manifesto e fixtures de rejeição para revisão estática, sem criar nem executar VM.
Não se solicita autorização de ensaio nesta fase. As propostas não autorizam
provisionamento, execução, encerramento ou descarte. A produção continua fora
do âmbito e não se afirma proteção absoluta contra host/hipervisor comprometidos.

## Decisão atual: NÃO APTO para solicitar autorização de novo ensaio

Decisão limitada ao harness no ambiente atual; produção Railway permanece fora
do âmbito. Uma suite passar com mocks não comprova isolamento real. Não foi
executado qualquer binário PostgreSQL, comando Railway, ligação SQL, consulta
ou alteração de processos nesta revisão. Resíduos antigos não foram consultados
nem eliminados. As conclusões de prontidão das secções históricas ficam substituídas.

### Matriz de riscos e evidência pendente

| Risco | Criticidade | Mitigação existente/implementada | Validação efetuada | Evidência ainda necessária |
| --- | --- | --- | --- | --- |
| TOCTOU em paths/aberturas | Alta | Root ancorado, nomes fechados, O_EXCL/O_NOFOLLOW quando suportado; nova comparação dev/inode do descritor antes de ler | Inspeção e regressão de descritor substituído | Ensaio de filesystem autorizado em ambiente isolado; garantia por handles/ACL no SO, incluindo append JSON e abertura por pg_ctl |
| Reparse points/junctions/symlinks/ACL Windows | Alta | Recusa de links conhecidos, root/junction verificados; modo 0600 | Mocks de root/symlink e links múltiplos | ACL efetiva privada e verificação de todos os reparse points; chmod não é ACL; nenhuma inspeção real nesta etapa |
| Porta reutilizada entre reserva e ligação | Alta | Loopback fixo, porta efémera, PID e data_directory antes de fixtures | Revisão estática; transporte simulado | Instância/VM isolada sem bases existentes, identidade do listener pelo SO; nenhuma garantia absoluta de zero contacto no host partilhado |
| Reutilização de PID | Alta | Nova impressão PID + timestamp do postmaster.pid + diretório + porta, imutável entre verificações | Regressões de mudança de PID/timestamp antes de cleanup | Handle de processo/criação obtido do kernel e associação ao listener; PID-file adulterável e timestamp em segundos não bastam |
| Descendentes sobrevivem a timeout | Alta | Timeout do processo direto; cleanup condicionado à identidade | Timeout parcial e falhas de cleanup simulados | Contenção real da árvore, por exemplo Job Object/VM dedicada, e confirmação de zero resíduos; não implementada nem ensaiada |
| Consumo de disco | Alta | Excertos em memória limitados, ficheiros brutos preservados | Captura grande simulada | Quota rígida/volume descartável limitado, cobrindo capturas, server.log e PGDATA/WAL; espaço livre/timeout não equivalem a quota |
| Segredos nos logs brutos | Alta | Passwords sintéticas, logs restritos ao root, sem partilha automática | Evidência bruta preservada em fixtures | ACL/armazenamento privado e política de retenção; logs reais podem conter segredos |
| Segredos no JSON sanitizado | Média/Alta | Redação por padrões e segredos conhecidos; normalização e excertos por linha | Casos de encoding/controlos/multilinha simulados | Revisão privada do JSON; não existe detector universal, formatos desconhecidos podem passar |
| Escrita/stop fora do ensaio | Alta | Root/PID/data_directory; nenhuma URL externa; novas recusas de PID com hard links | Guardas simuladas, nenhuma operação real | Isolamento SO de ficheiros/processos/rede; ainda há corridas após validação e antes de pg_ctl agir |
| Alteração de binários/ambiente | Alta | Mesmo diretório binário; PG* recusadas; whitelist de ambiente sem DATABASE_URL/Railway | Inspeção estática | Origem/integridade dos binários e sessão isolada; PATH e mesmo diretório não provam autenticidade |
| Resíduos do primeiro ensaio | Alta | Preservação; não matar processos ambíguos | Apenas informação histórica, não revalidada | Diagnóstico de leitura autorizado para atribuir processos/diretórios; pendente |

### Correções e alcance das garantias

Validação atual: **52 testes simulados aprovados** — 28 do harness e 24 do
probe. Foram acrescentadas três regressões de identidade PID/timestamp,
descritor e hard links. Um mock incompleto de stat foi corrigido durante a
validação; a execução final não apresenta erros. Os oito testes reais não foram
selecionados. Subprocessos/sockets/ligações reais foram bloqueados ou simulados.

A leitura de excertos passa a comparar o descritor aberto com os metadados
validados antes de ler e volta a confirmar o root. O ficheiro PID com múltiplos
hard links é recusado. Mudanças de PID ou timestamp entre verificações fazem
parar antes de ligar ou executar cleanup. A primeira impressão vem do ficheiro,
não do kernel: pode ser falsa, adulterada ou reutilizada. Não a tratar como
prova da identidade de processo. A ligação às fixtures continua por validar.

Verificado no código e em simulações: recusa dos casos cobertos, excertos
limitados, ausência de leitura do dotenv/configuração Railway, destino programado
em loopback e entrada direta com opt-in/failfast. Não verificado: isolamento
real, ACLs, reparse points completos, quota, contenção da árvore, correspondência
PID/listener/servidor, encerramento efetivo e ausência de interferência externa.

### Condições obrigatórias antes de pedir novo ensaio

1. Resolver a atribuição dos resíduos anteriores por procedimento de leitura
   separadamente autorizado; não parar processos sem identidade comprovada.
2. Preparar e demonstrar um ambiente SO descartável, preferencialmente VM
   dedicada sem bases existentes, segredos, volumes ou acesso de rede a produção.
3. Confirmar ACLs/reparse points e binários confiáveis; definir quota rígida
   para todo o volume do ensaio e retenção privada dos logs.
4. Definir contenção e atribuição da árvore de processos/porta com identidade
   de kernel, incluindo o procedimento de falha de startup/timeout/cleanup.
5. Rever evidências e patch; só depois solicitar autorização explícita para
   um ensaio no destino isolado identificado. Não alterar o host atual para
   contornar estas condições. Os oito testes continuam não executados.

## Auditoria estática mais recente do harness

Corrigidos: captura ilimitada em memória via PIPE, falta de ancoragem da
identidade inicial do root, variantes de redação percent-encoded/controlos/
multilinha e falta de revalidação do PID antes do stop immediate. Capturas
brutas exclusivas são conservadas só no diretório do ensaio; apenas excertos
limitados e sanitizados entram no JSON. Não há novo processo ou acesso SQL.

Não se certifica isolamento absoluto: subsistem TOCTOU/reparse points/ACLs,
adulteração pelo mesmo utilizador, corrida de porta, descendentes após timeout
e consumo de disco das capturas. PID/caminho não substituem identidade do
processo fornecida pelo SO. Os mocks não provam comportamento PostgreSQL real.
Ver a secção mais recente do [guia](docs/railway/READ_ONLY_PROBE.md).
As descrições anteriores de captura integral em memória são históricas.
Resultado atual: 49 testes simulados passaram (25 harness + 24 probe).
Os oito testes reais não foram selecionados; nenhum binário PostgreSQL foi executado.
Novo ensaio continua dependente de autorização e confirmação de isolamento,
ACLs, capacidade de disco e resolução dos resíduos do primeiro arranque.

## Estado mais recente: ensaio falhado e captura preparada localmente

O primeiro ensaio descartável autorizado falhou em pg_ctl start após initdb.
Os oito testes e as ligações SQL não foram iniciados. O diretório foi conservado,
sem server.log, postmaster.pid ou ficheiro de password ao terminar. Não foi
possível confirmar integralmente processos residuais, pois a consulta de associação
foi recusada. A causa permanece desconhecida; as secções seguintes são históricas.

Nesta nova etapa só foram alterados testes/documentação e executadas simulações.
O harness passa a capturar stdout, stderr, código de saída, timeout parcial e
errno num JSONL sanitizado dentro do diretório temporário. O log pg_ctl -l é
pré-criado e preservado separadamente, sem partilha automática do conteúdo bruto.
As guardas de isolamento e recusa de terminar processos de identidade incerta
mantêm-se. Não houve novo startup, initdb, stop, SQL, acesso Railway ou leitura/
eliminação do diretório do ensaio anterior.

Ver [procedimento atualizado e limitações da sanitização](docs/railway/READ_ONLY_PROBE.md).
Novo ensaio requer autorização específica e revisão prévia dos resíduos, TEMP
privado e guardas; estas alterações não autorizam a repetição do arranque.
Validação desta etapa: 45 testes simulados passaram (21 do harness e 24 do probe).
Os oito testes de integração não foram selecionados. A entrada futura da suite
usa failfast. O diretório antigo e os processos PostgreSQL não foram consultados
nem alterados nesta etapa; a causa do primeiro erro continua desconhecida.

## Conclusão e âmbito

**Não há ainda condições verificadas para autorizar a migração de produção.**
A configuração local foi confirmada em leitura. A aplicação pública respondeu
a três GET de metadados/liveness; não houve acesso autenticado à Railway,
à base de produção ou a dados de utilizadores/jogos publicados.

Não foram executados backup, migração, seed, deploy, reinício, alteração de
variáveis, commit, merge ou push. Não foi modificado `ai-learning/`. Não foram
executados testes que criem schemas ou apliquem migrações nesta etapa.
Os únicos ficheiros criados são este relatório e o diagnóstico de leitura em
`docs/railway/read_only_probe.py`; não foi alterado o arranque da aplicação.

## Estado confirmado versus informação fornecida

| Item | Resultado e origem da informação |
| --- | --- |
| Configuração efetiva local | `localhost:5432/ccdr_match_tracker`, `APP_ENV=development`, confirmado sem imprimir credenciais |
| Base local | Revisão `0006`, PostgreSQL 18.6, consulta em transação READ ONLY |
| Git local | `main`, HEAD `59c3bce`; alterações anteriores do Campeonato não commitadas, incluindo `0007` não versionada |
| Serviço publicado | `https://futanalysis-production.up.railway.app`, indicado pelo utilizador |
| GET público `/health` | HTTP 200, `{"status":"ok"}` |
| GET público `/api/health` | HTTP 200, `{"status":"ok"}` |
| GET público `/api/openapi.json` | HTTP 200, versão declarada `0.1.0`, 27 caminhos, rota de preview de união presente, sem rotas `/competitions` |
| Base de produção distinta da local | Informado pelo utilizador; ligação concreta ainda não inspecionada |
| Rotação da password de produção | Informada pelo utilizador; atualização efetiva na aplicação e nova autenticação não verificadas |
| Revisão Alembic de produção | **Desconhecida**; não é inferida a partir da revisão local ou do OpenAPI |
| SHA/artefacto efetivamente publicado | **Desconhecido**; a versão `0.1.0` não identifica um commit |
| Configuração do painel Railway | **Desconhecida**: não houve sessão autenticada nem CLI disponível no PATH |

A consulta web inicial não conseguiu obter o site. Uma consulta HTTP direta
posterior, apenas GET e sem autenticação, obteve os três resultados acima.
Não se concluiu indisponibilidade a partir da falha da primeira ferramenta.

## Ficheiros e comandos de deployment analisados

### Imagem combinada prevista no repositório

`Dockerfile` na raiz de `ccdr-match-tracker`:

- Build frontend: `npm ci` e `npm run build`, Node 22.
- API pública do frontend fixada no build como `NEXT_PUBLIC_API_URL=/api`;
  `BUILD_STANDALONE=true`. Uma alteração runtime não reconstrói o JavaScript.
- Runtime Python 3.12, Node e Caddy, com `APP_ENV=production`, cookie Secure/Lax.
- `WORKDIR /app/backend`; copia explicitamente `backend/app`, Alembic e deploy.
- `CMD ["python", "/app/deploy/start.py"]`.
- Não copia o `.env` local. `.dockerignore` também exclui `.env`, caches,
  ferramentas locais e ficheiros sensíveis usuais.

`deploy/start.py` inicia um worker Uvicorn em loopback:8000, Next em
loopback:3000 e Caddy na porta pública. Não chama Alembic, seed ou create_admin.
O subprocesso Next recebe uma lista limitada de variáveis, sem DATABASE_URL.
O processo API herda as variáveis do container. O supervisor verifica apenas
liveness no arranque e termina se um subprocesso terminar.

`deploy/Caddyfile` encaminha `/api/*`, `/ws/*` e `/health` para a API. As
respostas públicas observadas são compatíveis com esse contrato, mas não
comprovam que este ficheiro exato esteja implantado.

### Imagem antiga só de backend

`backend/Dockerfile`: `WORKDIR /app`, `CMD ["python", "-m", "app.start"]`.
`backend/app/start.py` inicia Uvicorn, um worker, sem migrações.
Confirmar qual imagem/root/start o serviço ativo usa; não trocar agora.

### Configuração como código e automações

Não foi encontrado `railway.json`, `railway.toml`, Nixpacks, Procfile ou
workflow CI de deployment nos caminhos pesquisados do checkout. Isto não
exclui automação configurada na Railway, noutro repositório ou num pipeline externo.

Nos percursos de build/start, `app.main` e `app.database`, não foi encontrado
`alembic upgrade`, seed ou `Base.metadata.create_all`. Os modelos são registados,
mas o arranque não cria tabelas. `backend/alembic/env.py` só executa Alembic
quando o respetivo comando é chamado.

**Conclusão limitada ao código revisto:** não há migração automática nesses
percursos. É obrigatório consultar Start Command, Pre-deploy Command e eventuais
overrides do deployment efetivo antes de concluir o mesmo para produção.
A Railway permite [start command personalizado](https://docs.railway.com/deployments/start-command)
e [comando pre-deploy](https://docs.railway.com/deployments/pre-deploy-command).

## Variáveis relevantes — nomes, sem valores secretos

| Variável | Utilização local no código e ponto a verificar em produção |
| --- | --- |
| `DATABASE_URL` | Única ligação usada por `get_engine`; obrigatória e validada como PostgreSQL |
| `APP_ENV` | Produção ativa validações de segurança |
| `CORS_ORIGINS` | Lista explícita HTTPS, incluindo a origem publicada |
| `AUTH_COOKIE_SECURE`, `AUTH_COOKIE_SAMESITE` | Imagem combinada espera Secure=true e SameSite=lax |
| `AUTH_SESSION_HOURS`, `AUTH_DEBUG_LOGGING` | Duração de sessão e diagnóstico opt-in; verificar sem mudar |
| `PORT` | Listener público de Caddy; portas 3000/8000 reservadas internamente |
| `NEXT_PUBLIC_API_URL`, `BUILD_STANDALONE` | Fixadas no build combinado; não usar segredos em NEXT_PUBLIC |
| `RAILWAY_DOCKERFILE_PATH` e Root Directory | Eventuais overrides podem selecionar o Dockerfile antigo ou outro contexto |

Pydantic lê o ambiente do processo com precedência sobre o dotenv do backend.
Na imagem revista o dotenv não é copiado. Não existe fallback programado
para localhost quando DATABASE_URL falta: a configuração falha. Uma URL
errada fornecida ao serviço, porém, continua a poder apontar a outra base.

Os exemplos recomendam referência do serviço da aplicação à variável do
PostgreSQL, por exemplo `${{Postgres.DATABASE_URL}}`, usando o nome real do
serviço. Esta é uma recomendação de configuração, **não um valor observado**.
Referências entre serviços estão descritas na
[documentação de variáveis](https://docs.railway.com/variables).
Não alterar, revelar ou copiar o valor resolvido nesta etapa.

PGHOST/PGPASSWORD isolados no serviço não substituem DATABASE_URL para esta
aplicação. A rotação da password, só por si, não comprova que a ligação usada
pela aplicação foi atualizada. O diagnóstico precisa de abrir uma ligação
nova; uma resposta de liveness não testa autenticação PostgreSQL.

## Como confirmar produção exclusivamente em leitura

### Primeiro: revisão do painel, mediante autorização

Selecionar explicitamente projeto, ambiente de produção e serviço associado
ao domínio publicado. Consultar, **sem editar/aplicar alterações**:

1. Deployment ativo: SHA do commit ou identificação da imagem; repositório,
   branch e data do deployment.
2. Root Directory, Dockerfile Path, Start Command, Pre-deploy Command e Build
   Command efetivos. Registar os comandos, retirando qualquer segredo embutido.
3. Autodeploys, mudanças staged/pending e outros serviços/jobs que usem a mesma
   base. Consultar logs já existentes, sem reiniciar nem fazer login na aplicação.
4. Nomes das variáveis relevantes e se DATABASE_URL referencia o serviço
   PostgreSQL esperado. Não partilhar valores resolvidos, URLs ou dumps de env.
5. Serviço PostgreSQL esperado e versão; disponibilidade de uma sessão de
   leitura no container da aplicação e de um futuro executor de backup.

Enviar apenas metadados não secretos e comandos redigidos. Não executar
`env`, `printenv`, listagem de valores Railway ou `cat .env` para partilhar resultados.
Não instalar/autenticar a CLI automaticamente nem mudar configurações para obter acesso.

### Última revisão técnica local do diagnóstico — 15/10/2026

Auditoria posterior do harness descartável: corrigidos registo antecipado de
limpeza, autenticação SCRAM efémera, ambiente dos subprocessos, confirmação do
PID/diretório/porta antes de ligar e de parar, leitura inicial READ ONLY e
encerramento fast/immediate com erro se não confirmado. Foram acrescentadas 11
regressões simuladas; resultado atual: **35 passaram e 8 integrações ignoradas**.
Metadados dos binários locais indicam PostgreSQL 18.6; nenhum binário servidor
foi executado e nenhuma base foi contactada. O teste operacional continua pendente.
O [guia](docs/railway/READ_ONLY_PROBE.md) documenta a corrida residual da porta,
permissões TEMP/Windows e limites da limpeza após terminação forçada.
A suite fica preparada para ensaio local mediante autorização separada, sem
autorizar qualquer acesso Railway. Os números abaixo descrevem a revisão anterior.

Revisão estática de 0001–0007: CORE nasce em 0001, 0002–0005 não acrescentam
tabelas, AUTH nasce em 0006 e COMPETITION em 0007. A comparação de presença
corresponde aos nomes criados; não valida colunas, enums, índices ou constraints.
Foi acrescentado um teste AST da cadeia e inventário, sem executar migrações.

Corrigidos dois riscos: expansão libpq de dbname como conninfo e ocultação de
revisões por RLS. O diagnóstico recusa dbname ambíguo e usa SET LOCAL
row_security=off, que falha perante filtragem necessária, sem contornar políticas.

Preparada suite PostgreSQL descartável com cluster próprio e verificação do
data_directory antes de escrever fixtures. Não foi executada: não havia uma
instância isolada comprovada. As ferramentas initdb/pg_ctl foram apenas localizadas.
Nenhuma base local ou remota foi contactada nesta revisão. Resultados da suite
unitária e condições do ensaio estão no guia diretamente associado.
Resultado: 24 testes locais passaram; 8 testes de integração foram ignorados
explicitamente (32 descobertos). Sintaxe das três fontes validada em memória.
São verificações estáticas/simuladas, não verificações PostgreSQL reais.

Limites: presença de nomes não prova histórico aplicado; tabelas extra não
monitorizadas passam, e esquemas separados/duplicados legítimos provocam paragem
conservadora. REPEATABLE READ não elimina corridas de DDL. Identidade Railway,
revisão real, artefacto e ligação dos workers continuam desconhecidos.

### Diagnostico revisto: apenas preparacao local

O procedimento anterior foi substituido pelo [guia atualizado](docs/railway/READ_ONLY_PROBE.md).
Consultar o [script](docs/railway/read_only_probe.py) e os
[testes isolados](docs/railway/tests/test_read_only_probe.py).
Nao executar os antigos comandos sem argumentos nem SQL dependente do search_path.

O script exige identificadores independentes de projeto, ambiente e servico,
alem do host, porta, base e esquema confirmados pelo operador. Nao importa settings
da aplicacao nem dotenv: compara o DATABASE_URL do processo com o alvo esperado.
Usa uma unica transacao READ ONLY / REPEATABLE READ, timeouts locais e ROLLBACK.
CONFIRMED significa apenas que estas verificacoes passaram; nao certifica a
identidade Railway, os workers nem prontidao para migracao.

Nesta revisao foram executados apenas testes locais com ligacoes simuladas.
Nenhum diagnostico remoto foi executado. As observacoes anteriores deste relatorio
sao historicas, sem nova verificacao das bases local ou de producao.
O operador confirmou fut_analysis, main, root /ccdr-match-tracker, Dockerfile
automatico, sem Start Command personalizado nem Pre-deploy visivel, uma replica
e autodeploy ativo. Indicou tambem que a uniao de jogos nos logs foi intencional.
Revisao Alembic, SHA/artefacto exato e identidade da base de producao continuam
por confirmar. Qualquer acesso remoto exige nova autorizacao.

## Compatibilidade do código publicado e 0007

Confirmado: o contrato OpenAPI público não inclui Campeonato, enquanto o
working tree local inclui os módulos/rotas e a migração não commitada. Não
há prova de que o artefacto publicado tenha o ficheiro `0007`. O SHA é desconhecido.

Avaliação estática: `0007` é aditiva. Com as novas tabelas vazias, não altera
colunas nem registos que a versão anterior usa. Isso sugere compatibilidade
com o código anterior, mas **não certifica o binário atualmente publicado**,
o seu esquema de produção ou automações desconhecidas.

O código novo depende de `0007`: algumas leituras de gestão de jogos também
consultam as dependências de calendário. Não o disponibilizar contra `0006`.
Após começar a ligar jogos a competições, as novas FK podem impedir operações
de eliminação/união do código antigo; por isso um rollback de código após
carregamento exige revisão. Não fazer rollback automático do esquema.

As referências antigas dos documentos do repositório a revisão `0006` não
substituem esta verificação remota. Não usar `upgrade head` de instruções antigas
antes de confirmar revisão/artefacto; o alvo futuro planeado é explicitamente `0007`.

## Riscos identificados

1. Confundir o `.env` local com produção. A base local em 0006 não informa a
   revisão Railway, e migrá-la não ativa o site publicado.
2. Pre-deploy/start personalizado no painel pode executar upgrade, seed ou
   outro script apesar de os Dockerfiles revistos não o fazerem.
3. Build/deploy automático futuro pode publicar alterações antes do backup ou
   iniciar código novo contra o esquema antigo. Não houve push nesta etapa.
4. URL literal/desatualizada após rotação pode impedir novas ligações; health
   200 não prova conectividade nem validade da password.
5. Artefacto publicado sem `0007` não pode executá-la. O working tree não está
   commitado, pelo que não deve ser tratado como revisão remota disponível.
6. O runtime Docker revisto não instala pg_dump/pg_restore. Não assumir que
   o SSH da aplicação serve também como executor de backup. Confirmar clientes
   compatíveis com a versão do PostgreSQL de produção e acesso de rede autorizado.
7. Janela de manutenção deve cobrir todos os writers, incluindo login/logout,
   jobs e outras réplicas. Fingerprints também incluem sessões/throttles.
8. O ensaio sintético anterior validou a mecânica local, não o volume, esquema,
   permissões, restauro ou revisão efetiva da produção Railway.
9. Só uma réplica de API é prevista pelo hub Live em memória; verificar o
   deployment real e tratar a sobreposição de releases durante a manutenção.

## Plano futuro com pontos de confirmação — não executado

### A. Identificação e leitura

Autorizar apenas consulta do painel e diagnóstico READ ONLY. Confirmar projeto,
ambiente, aplicação, PostgreSQL pretendido, revisão, SHA, variáveis referenciadas
e comandos efetivos. Se produção não estiver comprovadamente em 0006, parar
e preparar um plano específico. Se já estiver em 0007, não executar upgrade
ou downgrade por reflexo.

### B. Backup real e ensaio do arquivo

Só após autorização separada para manutenção e backup:

- Identificar todos os writers e acordar a janela. Confirmar acesso do executor
  aprovado à produção sem expor novas portas/credenciais automaticamente.
- Confirmar versão do servidor e clientes. Escolher armazenamento privado,
  retenção e espaço; não guardar dumps reais no Git, pasta pública ou logs.
- Fazer snapshot/fingerprints de 0006 e backup integral custom com pg_dump,
  password pedida interativamente ou pelo mecanismo secreto já autorizado.
  Não inserir URL com credenciais na linha de comandos.
- Verificar código de saída, tamanho, índice do arquivo e SHA-256.
- Restaurar esse arquivo numa instância isolada/vazia autorizada, sem `--clean`
  nem ligação de escrita à produção. Proteger a cópia, pois contém dados reais.
- Comparar esquema, dados e sequências. Ensaiar `0007` nessa cópia com o
  artefacto exato proposto, comparar fingerprints e testar os fluxos necessários.
- Rever que no restauro `--no-owner/--no-privileges` não verifica grants de
  produção; verificar permissões separadamente. Arquivo legível não prova restauro.

O [procedimento anterior](docs/MIGRACAO_0007.md) serve de base técnica, mas os
destinos e permissões locais nele descritos não estão confirmados para Railway.
Não executar agora o ensaio antigo contra uma base Railway por trocar variáveis.

### C. Ativação da migração

Após apresentar backup/ensaio/revisão, pedir confirmação explícita para
aplicar `0007` **à base de produção identificada**. Escolher um executor e
artefacto que contenham a migração; não copiar ficheiros para o container ativo
ou alterar pre-deploy como solução improvisada.

Na janela, com todos os writers suspensos e destino revalidado, o futuro
comando dirigido é `python -m alembic upgrade 0007`. Só nessa fase autorizada.
Depois: confirmar revisão, Alembic check com o código novo e fingerprints dos
dados anteriores. Se houver divergência, manter manutenção e investigar;
restauro sobre produção/downgrade exigem confirmação específica.

### D. Publicação e carregamento

Autorizar separadamente a publicação do código/imagem revistos. A operação
pode exigir primeiro disponibilizar a revisão remota correta; commits/pushes
não estão autorizados agora. Garantir que o deploy não volta a migrar ou semear.

Depois do esquema validado, publicar código compatível, confirmar leituras,
permissões, cookie e Live; só então reabrir utilização. Criar a competição e
carregar participantes/jornadas/resultados oficiais apenas com autorização
separada e lotes revistos. Classificação permanece provisória até validação
do regulamento. Não importar a base local por cima da produção.

## Próximo passo seguro

Precisamos apenas, por agora, dos metadados do deployment ativo e dos campos
Build/Start/Pre-deploy/Root/Dockerfile, sem segredos. Depois, autorização para
o diagnóstico READ ONLY ou execução pelo próprio utilizador e partilha do JSON.

Não é necessário enviar password, token, URL resolvida ou o conteúdo de `.env`.
Se não houver acesso remoto disponível, a revisão de produção e a ligação
continuam assinaladas como desconhecidas; não serão simuladas.
