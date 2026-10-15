# Contratos fechados dos sete validadores — versão documental 2.0.0

Revisão documental R2: contrato 2.0.0 ainda não aprovado/implementado. Os hashes
dos documentos exatos têm de ser vinculados à futura política; o número 2.0.0
sozinho não admite mistura de rascunhos. R2 substitui as regras anteriores,
mantendo rejeição de 1.0.0. Aplicam-se [C1–C9](VALIDADORES_CORRECOES_P1_P10.md).

**NÃO APTO.** Especificação normativa em tabelas, sem implementação de schemas,
scripts, parsers, coletores ou validadores. Nada foi executado. As
[fixtures](VALIDADORES_FIXTURES.md) são sintéticas e nunca são evidência real.
Nenhum campo ou declaração deste documento constitui autorização operacional.

Contrato transversal obrigatório: [correções P1–P10](VALIDADORES_CORRECOES_P1_P10.md).
Define identidades separadas, temporalidade, referências tipadas, fontes,
assinatura proposta, DAG e decisão 2.0.0. Não há compatibilidade automática
com bundles/fixtures 1.0.0. Os tipos KernelRelease/PackageVersion substituem
os usos inadequados de ID/VersionText para versões reais.

## 1. Sintaxe, tipos e política comum

Representação futura: JSON UTF-8, sem BOM, comentários, NaN/Infinity ou chaves
duplicadas. Objetos **fechados recursivamente**: só os campos enumerados abaixo,
todos obrigatórios salvo indicação explícita. Nenhum destes contratos tem campos
opcionais, null ou extensões livres. Unknown/ausente não se converte em false,
zero, array vazio ou enum predefinido. Não converter strings para boolean/int.
Datas não são comparadas lexicograficamente sem parsing UTC estrito.

Tipos normativos reutilizados:

| Tipo | Definição fechada / restrição |
| --- | --- |
| ID | String ASCII `[A-Za-z][A-Za-z0-9_.-]{0,127}`; não é URL/path |
| KernelRelease / PackageVersion | Tipos próprios do contrato transversal §6; preservação de bytes, scheme de pacote e comparação com imagem/lock aprovados |
| UUID | String canónica minúscula `8-4-4-4-12` hexadecimal, não nula; comparar bytes UUID |
| SHA | String de exatamente 64 hexadecimais minúsculos; apenas SHA-256; validade sintática não prova correspondência |
| UTC | String RFC3339 `YYYY-MM-DDTHH:MM:SSZ`, calendário válido, precisão em segundos |
| N | Integer JSON entre 0 e 9007199254740991 inclusive, sem boolean, float ou overflow |
| Flag | Boolean JSON verdadeiro/falso, sem coerção |
| IDs | Array de ID, único, máximo 256; vazio só onde explicitamente permitido |
| TypedRefs | Array único de TypedRef 1..256 do contrato transversal; tipo e alvo resolvidos, sem referências indiferenciadas |
| RelPath | String ASCII 1–240, separador `/`, segmentos `[A-Za-z0-9_.-]+`; sem vazio, `.`, `..`, raiz, drive, UNC, `:`, barra invertida, case collision ou normalização ambígua |
| Endpoint | Enum `absent`, `blocked`, `present`, `unknown`; blocked exige evidência da aplicação, não apenas intenção |
| Result | Enum `PASS`, `FAIL`, `UNKNOWN`, `NOT_EVALUATED`; os três últimos bloqueiam aprovação global |

Limites de parsing: bundle máximo 8 MiB, profundidade 16, string máxima 4096,
arrays teto absoluto1024, default256 e limites específicos da tabela C §4.
Limites específicos podem exceder o default, nunca o teto. Strings livres não são
mensagens/logs nem conteúdo executável. Proibir campos `password`, `token`,
`connection_string`, `database_url`, `environment_values`, `raw_log`, `command`,
`script`, `url`, `private_key` em qualquer nível por não pertencerem aos schemas.
Não seguir referências pela rede, executar imports, resolver comandos ou abrir
paths durante validação documental. Os coletores futuros têm escopo próprio.

## 2. Envelope, contexto, evidências e política externa

Cada entrada de validador é exatamente:
`{schema_id:ID,schema_version:"2.0.0",context_ref:ID,evidence_refs:TypedRefs,
claims:Claim[1..256],body:Body}`.
Claim=`{field:Field,source_record_refs:ID[1..256]}`. Cada campo/elemento do body
tem cobertura por source records admissíveis do sujeito/checkpoint correto;
listas são representadas inteiras por Field, não por chaves [] livres. Uma
lista vazia exige SourceRecord value=[] e CollectionEnumeration com suporte;
não aceitar claim que aponte apenas para a declaração do próprio consumidor.
O body é exclusivamente o do schema identificado, nunca união permissiva.
As referências resolvem-se num bundle fechado:
`{bundle_version:"2.0.0",contexts:AssessmentContext[1..16],runs:Run[1..16],
boots:Boot[1..64],captures:Capture[1..256],reviews:Review[0..256],
artifact_bindings:ArtifactBinding[0..256],authorizations:Authorization[0..256],
historical_qualifications:HistoricalQualification[0..256],
qualification_applicabilities:QualificationApplicability[0..256],checkpoints:Checkpoint[1..256],
technical_catalog:ReferenceRecord[0..256],observation_catalog:ReferenceRecord[0..256],
inventories:SourceInventory[0..256],observations:OBS-TEMPO[0..256],entries:Entry[1..32]}`.
ReferenceRecord é o registo fechado technical/observation do contrato transversal.
Arrays vazios representam ausência, nunca aprovação. Refs em falta bloqueiam.
IDs únicos globalmente por categoria; entry schema/context não se repete. Um
schema desconhecido é recusado, sem fallback. O bundle é dados, não trust store.

Context é agora AssessmentContext. Run, Boot, Capture, Review, ArtifactBinding e
Authorization são registos distintos; estrutura e relações estão no contrato
transversal §§1–2. Referências não usam um ID indiferenciado: evidence_refs
é TypedRefs apenas technical/observation; autorizações e revisões têm tipos
próprios e não são evidência técnica intercambiável. Subjects de build são
artifact; não lhes atribuir um boot que ainda não existia.

Política externa aprovada e íntegra é pré-requisito, não é configurável por estas
entradas: hashes de contrato/mapping/imagem/manifesto/lock, allowlists completas
de dispositivos/serviços/paths/dependências, identidades de coletores e revisores,
trust anchors/algoritmo de assinatura/serialização, limites e qualificações reais
exigidas por H01–H16/V1–V10. Esses artefactos ainda não existem aprovados.
Ausência deles resulta UNKNOWN, nunca geração automática de aprovação.

Aplicam-se as seis classes temporais do contrato transversal §3. Não existe
TTL global uniforme para build, boot, encerramento e exportação. Hora de revisão
não altera a captura original. Nenhuma política temporal está aprovada.

## 3. SC-HOST / VAL-HOST

schema_id=`SC-HOST`, schema_version=`2.0.0`.

Body fechado:
`provider:enum(Microsoft-Hyper-V), host_build:ID, mapping_sha256:SHA,
generation:N, secure_boot:Flag, secure_boot_template:ID,
nic_ids:IDs, switch_binding_ids:IDs, integrations:Integration[0..64],
session_mode:enum(basic,enhanced,unknown), clipboard:Flag, file_copy:Flag,
relay_state:Endpoint, devices:Device[1..64]`.

Integration=`{service_id:ID, enabled:Flag}`. Device=
`{device_id:ID, kind:enum(boot_iso,payload_iso,work_vhdx,essential_virtual,other),
controller_id:ID, slot:N, backing_sha256:SHA, writable:Flag}`.
Para dispositivo essencial sem backing em disco, backing_sha256 identifica
entrada do perfil de hardware aprovado, não um hash fictício de ficheiro.

Relações/política: generation=2, secure_boot=true, template/build/mapping aprovados;
nic/switch arrays vazios; integrações enumeradas exatamente como no mapping e
todas opcionais disabled; basic, clipboard/file_copy=false; relay absent/blocked
com demonstração. Dispositivos iguais à allowlist, device_id globalmente único
e unicidade composta de (controller_id,slot),
boot/payload imutáveis, apenas work gravável. Nenhum inventário vazio de serviços
prova ausência se o mapping enumera serviços esperados.

Evidência: host/host_inventory + guest/guest_inventory + qualificação controlada
dos canais; proveniência do coletor host separada do runner. Serviço/device extra,
unknown, template ou mecanismo sem demonstração bloqueiam. Schema permite
representar configuração insegura: estruturalmente válido não significa política PASS.

## 4. SC-MANIFESTO / VAL-MANIFESTO

Body=`{manifest_sha256:SHA, package_sha256:SHA, full_enumeration:Flag,
files:PackageFile[1..1024], control_files:PackageFile[1..128]}`.
PackageFile=`{path:RelPath, sha256:SHA, size_bytes:N,
kind:enum(regular,symlink,hardlink,reparse,other), stream_ids:IDs}`.
schema_id=`SC-MANIFESTO`, versão `2.0.0`.

Exigir full_enumeration=true, paths únicos entre ambas as listas; files é a
allowlist de três fontes, control_files é allowlist externa separada aprovada.
Só regular, streams vazios, hash/tamanho exatos. Nenhuma regra autoriza incluir
controlos ainda inexistentes. Excluir segredos/dados/ficheiros Railway conforme
PACOTE_TESTES_MANIFESTO.md; marcador sintético só é permitido em fixtures.
Entrada não redefine a allowlist nem aprova o próprio manifesto.

Evidência build/package_inventory e revisão independente/exportada do inventário
de bytes, não só lista declarada pelo pacote. Extra/missing/hash errado = FAIL;
inventário/proveniência/bytes indisponíveis = UNKNOWN. Nunca importar os módulos
para calcular/verificar hashes.

## 5. SC-ARTEFACTOS / VAL-ARTEFACTOS

Body=`{image_sha256:SHA, lock_sha256:SHA, sbom_sha256:SHA,
architecture:enum(amd64), os_release:ID, boot_chain_refs:TypedRefs,
dependencies:Dependency[1..1024], postgres_autostart:Flag, initial_clusters:N}`.
Dependency=`{name:ID, version:PackageVersion, version_scheme:enum(debian,pep440,opaque), sha256:SHA,
kind:enum(os_package,wheel,binary,control), abi:ID, source_review_ref:TypedRef}`.
schema_id=`SC-ARTEFACTOS`, versão `2.0.0`.

Exigir image/context iguais e lock/SBOM/boot chain correspondentes à revisão
externa; conjunto transitivo completo e exato, versões fixas e ABI Linux aprovada,
postgres_autostart=false/initial_clusters=0. Dependências com mesmo nome/kind
duplicados recusados; não resolver ranges/baixar pacotes como parte da validação.
Evidência build/image_inventory + independent_review e inspeção guest real para
estado inicial. Declaração de assinatura ou SBOM correto não demonstra o boot
efetivo; divergência com SC-HOST/GUEST = FAIL. Origem não verificável = UNKNOWN.

## 6. SC-GUEST / VAL-GUEST

Body=`{kernel_release:KernelRelease, os_release:ID, image_sha256:SHA,
interfaces:IDs, non_loopback_route_count:N, mounts:Mount[1..64],
uid:N, group_ids:IDs, capability_ids:IDs, sudo_allowed:Flag,
inherited_environment_names:IDs, active_service_ids:IDs,
cgroup_id:ID, outside_cgroup_process_count:N, initial_clusters:N}`.
Mount=`{mountpoint:enum(root,payload,work,tmp,run,journal),
source_id:ID, mode:enum(ro,rw), limit_bytes:N, device_id:ID}`.
schema_id=`SC-GUEST`, versão `2.0.0`.

Exigir só lo, zero rotas não locais, root/payload ro, fontes de mounts e serviços
exatamente aprovados, uid não-root aprovado, capabilities vazias/sudo false,
nenhum PG*/Railway/segredo no ambiente por nomes (sem recolher valores), zero
clusters iniciais e processos fora do cgroup. Limites/mounts referem dispositivos
de SC-HOST e valores de SC-RECURSOS; limite zero não representa "ilimitado aprovado".
Mountpoints únicos. Group IDs são identificadores de grupos do perfil, não logs.

Evidência guest/guest_inventory + host correlacionado e qualificação real da
contenção. Inventário do próprio runner sem proveniência independente não prova
estado real; boot/image/env/mount desconhecido = UNKNOWN ou FAIL se contradição.
Proibição de canais para enviar este inventário continua um bloqueio arquitetural.

## 7. SC-RECURSOS / VAL-RECURSOS

Body=`{vcpu:N, cpu_limit_percent:N, ram_bytes:N, dynamic_memory:Flag,
work_disk_bytes:N, work_disk_kind:enum(fixed,dynamic,differencing),
host_budget_bytes:N, quota_backend_id:ID, quota_effective:Flag,
accounted_target_ids:IDs, tmpfs_bytes:N, journal_bytes:N,
cgroup_memory_bytes:N, cgroup_tasks:N, cgroup_cpu_percent:N,
swap_enabled:Flag, deadline_seconds:N, watchdog_id:ID,
watchdog_vm_id:UUID, qualification_applicability_refs:ID[1..256]}`.
schema_id=`SC-RECURSOS`, versão `2.0.0`.

Política alvo: 2/100/4294967296/dynamic=false; fixed work=2147483648,
host_budget=34359738368, quota_effective=true com backend aprovado, tmpfs
total<=134217728/journal<=16777216, cgroup memory=2147483648/tasks=128/CPU=200,
swap=false/deadline=180. Nenhum limite relevante zero; conjuntos contabilizados
cobrem discos, configs, runtime, memória guardada/logs/evidência. Watchdog VM
igual ao contexto. Os valores só são aceites quando aprovados externamente.

Evidência host+guest e observações de comportamento de quota/limites/watchdog,
identificadas pelos SourceContracts. Qualificação histórica só é aplicável por
HistoricalQualification + QualificationApplicability, nunca ArtifactBinding de
observação. Espaço livre ou quota declarada sem aplicação não PASS.
Controlos só em ficheiro systemd, parent chain desconhecido ou qualificação
ausente impedem aprovação. Correlacionar com HOST/GUEST, sem confiar em flags.

## 8. SC-LIFECYCLE / VAL-LIFECYCLE

Body=`{registry_record_id:ID, authorization_refs:TypedRefs,
transitions:Transition[1..64], final_vm_state:enum(Off,Running,Paused,Saved,Unknown),
external_stop_refs:TypedRefs, descendant_containment_refs:TypedRefs,
identity_drift:Flag, timeout_observed:Flag, cleanup_confirmed:Flag}`.
Transition=`{from:Stage, to:Stage, at:UTC, authorization_ref:TypedRef}`.
Stage=enum(draft,reviewed,provision-authorized,isolated-attested,run-authorized,
stopped,quarantined,dispose-authorized,disposed).
schema_id=`SC-LIFECYCLE`, versão `2.0.0`.

Sequência temporal monotónica, cada from igual ao to anterior; só transições
adjacentes da política VM aprovada ou ramo de falha para quarantined, documentado
externamente. Proibido saltar autorização. Para decisão operacional final:
estado Off confirmado externamente, zero drift, cleanup_confirmed real; timeout
não é sucesso e exige evidência externa que confirme contenção e encerramento.
Sem eliminar discos para satisfazer cleanup: stopped não implica disposed.

Evidências host/lifecycle_observation + controlled_trial da árvore + revisão do
registo externo que associa UUID único ao run. Autorização é uma referência a
ato externo, não concedida pelo JSON. PID-file não satisfaz external_stop_refs.
Off declarado pelo guest ou snapshot de outro UUID = FAIL/UNKNOWN e bloqueio.

## 9. SC-EXPORTACAO / VAL-EXPORTACAO

Body=`{authorization_ref:TypedRef, source_disk_id:ID, source_sha256:SHA,
source_vm_state:enum(Off,Running,Paused,Saved,Unknown),
appliance_policy_sha256:SHA, parser_sha256:SHA, destination_id:ID,
files:ExportFile[1..32], read_only_source:Flag,
private_destination:Flag, secrets_review_ref:TypedRef}`.
ExportFile=`{path:RelPath, sha256:SHA, size_bytes:N,
kind:enum(regular,symlink,hardlink,reparse,other),
classification:enum(sanitized_report,raw,credential,unknown)}`.
schema_id=`SC-EXPORTACAO`, versão `2.0.0`.

Exigir autorização específica externa, VM Off igual à SC-LIFECYCLE, disco
inventariado para o run, hash do original/cópia correspondente à cadeia de
custódia, appliance/parser revistos; só regular/sanitized_report em allowlist
externa. Teto proposto 1 MiB por ficheiro, 4 MiB total; sem exportar esta quota
como autorização genérica. read_only_source/private_destination=true com prova.
Paths/IDs não são instruções para abrir, copiar, montar ou transferir.

Evidência independent_review/export_review e host/lifecycle_observation, mais
qualificação real do exportador. Documento não executa exportação. Classificação
autodeclarada sanitized não prova ausência de segredos. Tentativa proibida = FAIL,
conteúdo/proveniência/revisão indisponíveis = UNKNOWN, sem imprimir o conteúdo.

## 10. Pipeline e dependências sem aprovação circular

O DAG normativo é o do contrato transversal §7: C0 coleta autorizada separada;
C1 estrutura/identidade/bytes/assinatura/proveniência; C2 sete avaliações locais
sem dependência dos resultados umas das outras; C3 consistência cruzada com
invalidação transitiva; C4 decisão. Factos guest admitidos podem ser consumidos
por HOST/ARTEFACTOS sem depender de PASS de VAL-GUEST. EXPORTACAO local consome
facto Off, e C3 confronta esse facto com lifecycle. Não há aprovação provisória.

Cinco dimensões distintas: (a) estrutura/tipos, (b) bytes/criptografia,
(c) proveniência/independência, (d) configuração aplicada, (e) comportamento real.
Só (a) pode ser demonstrado por fixture. (b) sem bytes é UNKNOWN; (c) sem raiz
externa é UNKNOWN; (d) sem inventário real é UNKNOWN; (e) sem ensaio autorizado
é UNKNOWN. A etapa documental pode especificar todas, mas nunca executá-las.

O gate final trata qualificação completa após operações separadamente autorizadas,
não autorização prévia para causar essas operações. Uma decisão anterior não
autoriza exportação, execução ou descarte. Se for preciso avaliar prontidão
pré-execução/antes de exportar, produzir relatório parcial NÃO APTO, sem exigir
"evidência futura" através de uma execução automática ou autorização circular.

## 11. Schema SC-DECISAO 2.0.0

Formato fechado normativo R2 no contrato transversal §§7–8: LocalResult imutável,
Invalidation e FinalResult novo e assinado separadamente; identidade completa da
implementação/coletores, eixos, referências tipadas, sete pares local/final e
dezasseis RequirementResult H01–H16. A lista
informal de requisitos pendentes foi substituída por cobertura obrigatória total.
Nenhum requisito omitido/desconhecido ou resultado sem prova pode contar PASS.

Sete IDs exatos VAL-HOST/MANIFESTO/ARTEFACTOS/GUEST/RECURSOS/LIFECYCLE/EXPORTACAO;
schemas correspondentes únicos, sem resultado agregado que esconda desconhecidos.
Refs aceites/rejeitadas FINAIS são disjuntas; conflito invalida consumidores
finais. LocalResult histórico assinado não é reescrito e pode conservar o PASS
que tinha quando foi emitido. Somente FinalResult participa na aprovação final;
ref hoje rejeitada nunca sustenta PASS final. Sem assinatura do novo FinalResult,
UNKNOWN; não inserir final_status no LocalResult para contornar a imutabilidade.

Reason codes fechados desta versão: SYNTHETIC_NOT_EVIDENCE, DOCUMENTARY_ONLY,
SCHEMA_INVALID, UNKNOWN_VERSION, EXTRA_FIELD, MISSING_FIELD, VALUE_INCOMPATIBLE,
HASH_MISMATCH, INCOMPLETE_EVIDENCE, IDENTITY_MISMATCH, CONTRADICTORY_EVIDENCE,
UNVERIFIABLE_PROVENANCE, UNAPPROVED_DEPENDENCY, UNDEMONSTRATED_MECHANISM,
QUOTA_NOT_APPLIED, CHANNEL_PRESENT, DEVICE_UNAPPROVED, UNCONFIRMED_STOP,
EXPORT_NOT_AUTHORIZED, STALE_EVIDENCE, POLICY_NOT_APPROVED, DEPENDENCY_BLOCKED.
Conjunto R2 inclui ainda REF_TYPE_MISMATCH,REPLAY,REASSOCIATION,
INVALID_SIGNATURE_SCOPE,SOURCE_INCOMPLETE,SOURCE_TRUNCATED,COLLECTION_FAILED,
RESOURCE_DYNAMIC,INVALID_TRANSITION,RESULT_INCONSISTENT,REQUIREMENT_MISSING,
IMPLEMENTATION_UNVERIFIED,MAPPING_UNAPPROVED,QUALIFICATION_NOT_APPLICABLE,
ASSOCIATION_NOT_REVIEWED,ENUMERATION_UNSUPPORTED,COLLECTION_OVERFLOW,
CANONICAL_ORDER_INVALID,CHECKPOINT_MISMATCH,ORIGINAL_RESULT_CHANGED,
H16_POLICY_UNAPPROVED,FINAL_SIGNATURE_UNAVAILABLE. Este conjunto é a união
explícita e fechada, não nomes inferidos das fixtures. Unknown reason code
exige revisão do contrato, não texto livre.

Regra global: document_review ou documentary ou qualquer evidência synthetic
impõe NAO_APTO. APTO só é possível numa qualificação operacional implementada,
autorizada e real: sete FinalResult PASS, provas completas independentes, nenhum requisito
pendente, zero recusa, identidades/hashes coerentes e política aprovada. Nos
cinco eixos só PASS satisfaz; uma dimensão não necessária deve ser coberta por
revisão externa explícita da política, não por omissão/default local. APTO é
decisão de âmbito/instante, não autorização de ação nem garantia universal.

## 12. Dependências de documentação oficial e bloqueios

Os sete bodies são resumos com claims e referências. O contrato transversal §5
define SourceInventory/SourceRecord/OBS-TEMPO e a projeção campo a campo.
O mapping nativo, a exaustividade e a implementação de cada coletor ainda exigem
aprovação por build. Bytes de formato não aprovado são UNKNOWN mesmo com hash
correto. complete/relay_state/quota_effective não se autocomprovam; o contrato
documental não é uma fonte verificada nem um payload executável.

Antes de concretizar schemas/mapping: documentação oficial offline do build
Hyper-V real para IDs e estados de Integration Services, Enhanced Session e
redirecionamento, endpoints HV sockets/relays, firmware/template Secure Boot,
enumeração de dispositivos/controladores, semântica de CPU/memória, VHDX/parent
chain/checkpoints/runtime files, VMId/import/clones, estados Off/Saved e APIs do
watchdog. Nada disso foi consultado/verificado aqui. Não preencher IDs/enumerações
reais com valores sintéticos destes exemplos.

Continuam bloqueados o lock/imagem Linux, preflight, quota global e aplicação,
observação independente guest sem canal, contenção/timeout e exportador seguro.
Schemas não provam exaustividade dos coletores, segurança dos parsers ou ausência
de comprometimento do host. A análise estática desta fase mantém **NÃO APTO**.
