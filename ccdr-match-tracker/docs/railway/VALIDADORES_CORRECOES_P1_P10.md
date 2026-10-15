# Contrato transversal 2.0.0 — segunda revisão documental (R2)

**NÃO APTO.** Sem implementação, execução, teste ou aprovação. R2 substitui o
rascunho 2.0.0 anterior deste ficheiro; não são duas alternativas normativas.
Mantém-se 2.0.0 porque nenhum contrato foi aprovado/publicado como interface
operacional. Esta é uma decisão de gestão de rascunho proposta à revisão humana.
A futura política deve fixar hashes exatos de TODOS os documentos normativos R2;
mesmo número de versão não admite conteúdo divergente. Ausência desses hashes
aprovados bloqueia. Envelopes 1.0.0 continuam proibidos; nenhum rascunho anterior
é convertido automaticamente. O manifesto de fontes formato 1 é outro artefacto.

Identificar C1–C9 significa correções documentais, não mecanismos verificados.
Os tipos e os sete bodies fechados estão em VALIDADORES_SCHEMAS.md. Regras R2
deste documento prevalecem nas matérias transversais; fixtures não criam exceções.

## 1. Identidades, associações e qualificações — C1/C8

Tipos comuns: ID/UUID/SHA/UTC/N/Flag/RelPath/Result conforme schemas. Todos os
objetos são fechados e todos os campos enumerados obrigatórios. Não há null,
campos opcionais ou defaults. A hierarquia de limites está no §4.

TypedRef={kind:enum(authorization,review,observation,technical),id:ID}.
TypedRefs: 1..256 referências únicas por (kind,id), resolvidas em catálogos.
ReferenceRecord={kind:enum(technical,observation),id:ID,capture_ref:UUID}.
A origem host/guest/build e classe de referência decorrem do SourceContract
aprovado; não se inferem de nomes ou declarações do runner.
IDs únicos globalmente dentro de cada tipo de registo; nenhum ID de catálogo
pode existir em duas categorias de TypedRef. SourceRecord.id é único em todos
os inventários do bundle. UUIDs não nulos, relações externas verificáveis.

Subject é união discriminada:
- {scope:"artifact",artifact_sha256:SHA}.
- {scope:"run",run_id:UUID,vm_id:UUID}.
- {scope:"boot",run_id:UUID,vm_id:UUID,boot_id:UUID,configuration_sha256:SHA}.

Run={id:UUID,host_instance_id:UUID,vm_id:UUID,image_sha256:SHA,
policy_sha256:SHA,registry_review:TypedRef}. Registry review só review externa.
Boot={id:UUID,run_id:UUID,vm_id:UUID,configuration_sha256:SHA,sequence:N,
start_observation:TypedRef}. Só observation; sequence positiva e única por run.
Capture={id:UUID,subject:Subject,original_captured_at:UTC,nature:enum(synthetic,real),
collector_id:ID,collector_sha256:SHA,source_contract_id:ID,
source_contract_version:"2.0.0",artifact_sha256:SHA,
collection_state:enum(complete,partial,truncated,failed),signature:Signature}.

Quatro conceitos não intercambiáveis:
1. Capture de artefacto: subject artifact, bytes imutáveis, sem boot inventado.
2. Capture de observação: subject boot, preserva o boot observado.
3. HistoricalQualification, abaixo, resume comportamento do boot original.
4. QualificationApplicability, abaixo, avalia aplicabilidade a um alvo posterior.
Não reassociar a observação nem mudar timestamps para a reutilizar.

ArtifactBinding (nome normativo; substitui Binding)=
{id:ID,artifact_capture_id:UUID,target_subject:Subject,signature:Signature}.
Origem obrigatoriamente Capture artifact; destino run/boot; a revisão da
associação é um Review cujo alvo é ContentHash(ArtifactBinding), conforme §4,
com o sujeito de destino exato; não é o hash dos bytes da assinatura.
Não colocar esse Review dentro do Binding: evita autorreferência de hashes.
AssessmentContext liga os dois, abaixo. Binding de observação é recusado.

HistoricalQualification={id:ID,original_subject:Subject,observation_refs:TypedRefs,
mechanism_ids:ID[1..256],qualification_policy_sha256:SHA,
result:enum(passed,failed,unknown),recorded_at:UTC,signature:Signature}.
original_subject obrigatoriamente boot; refs só observation do mesmo boot.
Um passed declarado não prova validade; exige bytes, origem e ensaio real
autorizado sob a política original. Nature real/synthetic deriva das capturas.

QualificationApplicability={id:ID,qualification_id:ID,
qualification_record_sha256:SHA,target_subject:Subject,checkpoint_ref:ID,
compatibility_policy_sha256:SHA,comparison_evidence_refs:TypedRefs,
result:enum(applicable,inapplicable,unknown),signature:Signature}.
Destino run/boot autorizado, sem mudar original_subject. Política externa deve
enumerar mecanismos/configurações/versões que se podem transportar historicamente,
diferenças permitidas, validade e autorizações. comparison refs devem demonstrar
a comparação; ausência/alteração não aprovada → UNKNOWN/FAIL, nunca applicable.
Qualificação de quota/timeout não substitui quota/estado atual do novo boot.
Nos bodies, o campo passa a qualification_applicability_refs:ID[1..256]
onde o campo anterior era qualification_refs. descendant_containment_refs
continua observation do boot real, não HistoricalQualification reassociada.

RecordTarget={record_type:RecordType,record_id:ID-or-UUID,
record_content_sha256:SHA,subject:Subject}.
ID-or-UUID é discriminado por record_type, NÃO pelo primeiro carácter: UUIDs
também podem começar por letra hexadecimal. Run/Capture/Decision usam UUID
(Decision refere assessment_id); restantes alvos permitidos usam ID.
Review={id:ID,target:RecordTarget,reviewed_at:UTC,reviewer_id:ID,
verification_policy_sha256:SHA,review_result:enum(accepted,rejected,unknown),
signature:Signature}.
Alvos autorizados: Run, Capture, ArtifactBinding, HistoricalQualification,
QualificationApplicability, LocalResult, FinalResult e Decision.
Target subject deve coincidir com sujeito efetivo do registo; target Run usa
run, Capture usa o próprio subject, associações usam destino. Um Review de
Capture não satisfaz revisão de ArtifactBinding/QualificationApplicability.
Uma revisão não concede autorização: requer ato autorizado independente quando
a associação/aplicabilidade implica utilização num novo run/boot.

AssessmentContext={id:ID,run_ref:UUID,boot_refs:UUID[1..16],
artifact_binding_refs:ID[0..256],qualification_applicability_refs:ID[0..256],
review_refs:TypedRef[1..256],checkpoint_refs:ID[1..256],
purpose:enum(document_review,infrastructure_qualification),
mode:enum(documentary,operational),assessed_at:UTC}.
Run/boots/configurações devem corresponder ao registo externo. Cada associação
citada exige Review accepted do seu conteúdo/destino exatos e ato de utilização
quando aplicável. document_review exige documentary e vice-versa.
Operational exige infrastructure_qualification. Não confere evidência real.
ID/hash reutilizado com bytes diferentes, sujeito divergente, boot antigo usado
como atual ou ref de outro contexto → REPLAY/REASSOCIATION e bloqueio.

## 2. Autorizações e referências tipadas

Authorization={id:ID,operation:enum(provision,boot,inspect,run_tests,stop_vm,
import_payload,export_evidence,dispose),target_subject:Subject,scope_ids:ID[1..256],
issued_at:UTC,not_before:UTC,expires_at:UTC,issuer_id:ID,
issuer_policy_sha256:SHA,nonce:UUID,revocation_record_ref:ID,signature:Signature}.
Alvo run/boot, nunca artefacto isolado; boot/inspect/run_tests/stop_vm exigem
subject boot. Provision usa identidades planeadas revistas externamente.
issued_at<=not_before<expires_at; ação dentro do intervalo; issuer/nonce/revogação
verificados fora do pacote. Estado de revogação desconhecido bloqueia. Scope
exato sem wildcard; nenhuma operação implica outras por omissão.
O registo externo de revogação/nonce ainda precisa de formato e aprovação humana.

authorization_ref(s) e transitions.authorization_ref só authorization.
source_review_ref, secrets_review_ref, registry_review e identity_review_ref só
review. evidence_refs só technical/observation. boot_chain_refs só technical.
external_stop_refs só observation host do boot, nunca autorização ou PID-file.
Referência review/observation em lugar de authorization é REF_TYPE_MISMATCH.
ArtifactBinding e QualificationApplicability não são novos tipos de autoridade:
suas aprovações são reviews tipadas de RecordTarget e autorização externa própria.

## 3. Temporalidade e pontos de controlo — C7

Checkpoint={id:ID,assessment_context_id:ID,subject:Subject,
event:enum(preflight,pre_run,post_stop,pre_export,post_export,assessment),
event_observation_ref:TypedRef,at_utc:UTC,clock_id:ID,monotonic_ns:N,
evaluated_capture_refs:UUID[1..256],signature:Signature}.
Só observation do evento/boot; o checkpoint deve estar no contexto identificado,
com horário e relógio confrontados com fonte externa. Intervalos monotónicos só
se comparam dentro do mesmo clock_id/boot; N limita a representação disponível,
e overflow exige recusa, nunca wrap. Um contador de longa duração fora de N
não é normalizado: a política futura terá de aprovar outro tipo se necessário.
A captura original, o instante da revisão e o checkpoint são campos distintos.
Atualizar Review/Checkpoint não torna a captura mais recente.

| Classe | Validade no checkpoint apropriado | Recusa |
| --- | --- | --- |
| Artefacto imutável | Sem TTL da captura; bytes/hash e aprovação vigentes; ArtifactBinding revisto ao alvo | Artefacto alterado, aprovação revogada ou associação sem revisão específica |
| Inventário aplicado | Mesmo boot/configuração, captura até 60 s antes de preflight/pre_run; nenhuma mudança posterior permitida | Drift, outra identidade, parcial/truncado ou apenas timestamp reescrito |
| Autorização | Intervalo no instante da ação, nonce/issuer/escopo e revogação | Expirada, ato diferente ou prova de revogação ausente |
| Operação | Evento/intervalo original no boot; se pretende estado atual, idade<=60 s no checkpoint | Observação histórica usada como estado atual |
| Encerramento | Observação host após stop, checkpoint post_stop; sem boot posterior para afirmar Off atual | Saved/Paused/Unknown, outro boot ou confirmação apenas guest |
| Exportação | Bytes finais/fonte/cópia/destino específicos no pre/post_export e ato válido à ação | Mudança após revisão ou custódia/ato incompletos |

60 s e tolerância UTC de 5 s são política candidata, não aprovada. A consolidação
histórica conserva validade no checkpoint original, não exige que todo o build/
histórico tenha 60 s. Histórico não demonstra estado atual. Relógio guest sozinho
não é prova. Qualificação histórica usa QualificationApplicability, nunca
ArtifactBinding de observações. Sem evidência/clock confiáveis, UNKNOWN.

## 4. Limites, canonicalização e receitas criptográficas — C4/C5

Hierarquia única: teto absoluto > limite específico do campo > default.
Teto absoluto de qualquer array =1024; default=256. Campo específico PODE
exceder 256 até 1024. Limite específico menor prevalece nesse campo. Aninhados
são limitados independentemente e pelo bundle total de 8 MiB/profundidade16/
strings4096; não multiplicar limites para dispensar o teto global.
N: 0..9007199254740991, somente integer, sem boolean/floats/-0. Overflow,
coleção excessiva ou objeto truncado é recusa antes de canonicalizar.

| Coleção | Limite específico | Chave/ordem |
| --- | --- | --- |
| arrays IDs/TypedRef e subjects/review refs | 256 salvo declaração menor | ID/UUID por ASCII; TypedRef por kind,id |
| context.boot_refs | 1..16 | UUID ASCII, sequence é verificada no registo Boot |
| bundle.runs/contexts | 1..16 | id |
| bundle.boots | 1..64 | id |
| bundle.captures/checkpoints | 1..256 | id |
| bundle.inventories/reviews/catálogos/associações | 0..256 | id; inventories por source_contract_id,capture_ref |
| bundle.entries | 1..32 | schema_id,context_ref |
| Entry.claims | 1..256 | field |
| dependencies, SourceInventory.records | 0..1024, dependencies mínimo1 | kind,name; records id |
| source_record_refs | 1..1024 onde expresso; Claim 1..256 | ID ASCII |
| files/control_files/exports | 1..1024 / 1..128 / 1..32 | path |
| devices/integrations/mounts | 1..64 / 0..64 / 1..64 | device_id / service_id / mountpoint |
| transitions | 1..64 | ordem semântica, at crescente; empate proibido |
| observations/authorizations/qualifications/applicabilities | 0..256 | id |
| schema_versions/local_results/final_results | exatamente7 na decisão completa | schema_id / validator_id / validator_id |
| requirements | exatamente16 | requirement_id lexical H01..H16 |
| invalidations/rejected refs | 0..256 | invalidations id; rejeição por ref.kind,ref.id,reason_code |
| source enumeration collections | 0..256 | field |
| matriz Dimensions (objeto) | exatamente5 campos | ordem de chaves JCS |
| qualquer array novo sem regra explícita | não permitido | falha de contrato, não ordem presumida |

Arrays semanticamente sequenciais nunca são ordenados para obter uma assinatura;
arrays de conjunto têm de vir na ordem acima, com chaves únicas. Fora de ordem,
duplicado ou chave de ordenação não definida → recusa. SourceRecord.value herda
tipo/ordem do campo de origem, incluindo arrays vazios. Objetos aninhados seguem
JCS recursivo, não ordem de apresentação em Markdown. Nenhum campo opcional;
null proibido. Arrays vazios apenas onde mínimo0: bytes são [] (hex 5b5d).
Boolean é true/false, inteiros representação decimal canónica JCS; sem coerção.
Strings preservadas, escapadas por JCS em UTF-8, sem BOM, CR/LF adicional ou
normalização Unicode. Entradas ilegais não são reparadas.
A identificação de RFC 8785 é proposta documental, não consulta externa nesta fase.

Definições EXATAS:
- J(X) = bytes UTF-8 da representação RFC8785 de X, sob estas restrições.
- Content(R) = J(R sem o membro signature de nível superior). Outros membros,
  incluindo hashes de referências, permanecem. Registos sem signature usam J(R).
- ContentHash(R) = SHA256(Content(R)), expresso em hex minúsculo.
- ArtifactHash(B) = SHA256 dos bytes brutos B, sem conversão CRLF/LF.
- SignatureHash(Bsig) = SHA256 dos bytes brutos da assinatura destacada.
- original_record_sha256 (se usado como alias de revisão) e
  RecordTarget.record_content_sha256 = ContentHash do registo alvo exato.
- assessment_context_sha256 = ContentHash(AssessmentContext completo).
- local_result_content_sha256/final_result_content_sha256 = ContentHash
  do LocalResult/FinalResult correspondente. Exclui só a assinatura própria;
  inclui os hashes dos artefactos locais referenciados.
- artifact_sha256 de Capture = ArtifactHash do ficheiro bruto coletado;
  se a fonte for um SourceInventory JSON, o artefacto deve ser precisamente
  J(SourceInventory), sem assinatura embutida e sem LF adicional.

Signature={profile_id:ID,signer_id:ID,key_id:ID,trust_anchor_id:ID,
signed_payload_sha256:SHA,signature_artifact_sha256:SHA}.
Perfil Ed25519 é CANDIDATO, não aprovado. Nenhuma chave/raiz foi criada.
SignBytes(R,T) = ASCII("FUTANALYSIS-EVIDENCE-V2") || byte0a ||
J({record_type:T,record_version:"2.0.0",
payload:(R sem signature, acrescido de signature_profile)}).
signature_profile contém exatamente profile_id,signer_id,key_id,trust_anchor_id,
idênticos aos de Signature. signed_payload_sha256=SHA256(SignBytes).
Signature signs SignBytes, NÃO ContentHash nem o texto hexadecimal do hash.
Proibir campo signature_profile no registo recebido: é construído só nessa
representação assinada. A assinatura e seu hash não entram circularmente no payload.
Não confundir ContentHash, ArtifactHash, signed_payload_sha256 ou TypedRef.

RecordType é enum fechado Run,Boot,Capture,Review,ArtifactBinding,
HistoricalQualification,QualificationApplicability,Authorization,Checkpoint,
LocalResult,Invalidation,FinalResult,RequirementResult,Decision.
Só tipos que têm signature no contrato são assinados diretamente; Run/Boot e
AssessmentContext são autenticados por reviews/capturas/Decision, não por campo
extra proibido. A política futura tem de fixar perfis por tipo e autoridade dos
signatários. Sem política/bytes/assinatura ou origem confiáveis, UNKNOWN.
Hash/sujeito/assinatura divergentes demonstrados → FAIL. Canonicalização ainda
exige revisão humana e vetores futuros; nada foi calculado/executado aqui.

## 5. Inventários e prova de ausência — C6

SourceInventory={source_contract_id:ID,source_contract_version:"2.0.0",
capture_ref:UUID,enumeration:Enumeration,records:SourceRecord[0..1024]}.
Enumeration={scope_ids:ID[1..256],expected_scope_policy_sha256:SHA,
state:enum(complete,partial,truncated,failed),error_codes:ID[0..64],
item_count:N,collections:CollectionEnumeration[0..256]}.
CollectionEnumeration={field:Field,subject:Subject,collector_id:ID,
checkpoint_ref:ID,state:enum(complete,partial,truncated,failed),
observed_count:N,support_refs:TypedRefs}.
SourceRecord={id:ID,subject:Subject,field:Field,value:Value,
unit:enum(none,bytes,percent,seconds,count),observed_at:UTC,
corroboration_refs:TypedRefs}. Só technical/observation independentes do coletor.

Field é enum dos paths qualificados pelos sete prefixos HOST,MANIFESTO,
ARTEFACTOS,GUEST,RECURSOS,LIFECYCLE,EXPORTACAO e pelos campos dos bodies exatos
dos schemas. Para listas usa-se campo inteiro (ex.: HOST.devices), NÃO path de
elemento [] nem wildcard. Value tem exatamente o tipo fechado daquele campo,
incluindo todos os elementos da lista. Zero elementos é value=[] mais registo
CollectionEnumeration complete/observed_count=0 para o mesmo field/subject/
checkpoint, não omissão de SourceRecord. Arrays com mínimo1 continuam a recusar [].
item_count conta SourceRecord, não a soma dos elementos das listas representadas.

CollectionEnumeration refere scope da política, identidade do coletor e
checkpoint; support_refs/corroboration_refs devem demonstrar execução completa
do método independente aprovado, sem erro/truncagem, e cobertura do universo.
observed_count deve igualar o comprimento do Value. Sem suporte verificável,
complete e count0 não passam de alegações → UNKNOWN. Contagem contraditória=FAIL.
Lista [] isolada não aprova ausência. state failed/partial/truncated bloqueia todos
os consumidores; nunca converter coleta falhada em zero.

Extensões fonte fechadas:
HOST.channel_endpoints: EndpointRecord[0..256], EndpointRecord={endpoint_id:ID,
transport:enum(hv_socket,vsock,rdp,file_copy,clipboard,other),
state:enum(present,blocked,unknown),service_id:ID};
HOST.session_policy: {client_profile_id:ID,enhanced_allowed:Flag,redirect_ids:ID[0..256]};
RECURSOS.disk_parents: DiskParent[0..64],
DiskParent={device_id:ID,parent_ids:ID[0..64],checkpoint_ids:ID[0..64]}.
Ordenação: endpoint_id, device_id, ID nas listas parent/checkpoint/redirect.
Consumers endpoints→H05/H06, session→H04/H05, parents→H07/H11.
Qualquer outra extensão, campo nativo desconhecido ou scope incompleto bloqueia.

OBS-TEMPO={id:ID,subject:Subject,event:enum(vm_start,vm_stop,checkpoint,quota_limit,
resource_limit,process_tree,export_read),start_utc:UTC,end_utc:UTC,clock_id:ID,
start_monotonic_ns:N,end_monotonic_ns:N,
observed_state:enum(Off,Running,Paused,Saved,Unknown,limit_applied,limit_unknown),
technical_refs:TypedRefs}.
Mesmo relógio no intervalo e início<=fim; observação host externa é necessária
para Off. OBS-TEMPO pertence aos bytes de uma captura; o catálogo observation
aponta para Capture, nunca só para um texto/flag de estado.

| SourceContract | Âmbito / campos necessários | Projeção e prova independente / recusa |
| --- | --- | --- |
| SRC-HOST | Boot; todos os campos HOST e extensões channel_endpoints/session_policy; cada claim identifica source records | HOST e H01–H08/H14/H16; inventário efetivo host e guest correlacionado; mapping e scope completos; omissão/relay não demonstrado bloqueiam |
| SRC-PACOTE | Artefacto; campos MANIFESTO; inventário de bytes/streams e controlos separados | MANIFESTO/H07/H14/H16; segundo inventário e revisão; extra/hash/link/stream/enumeração incompleta recusam |
| SRC-IMAGEM | Artefacto; ARTEFACTOS e boot chain/lock; estado inicial em captura de boot distinta | ARTEFACTOS/H03/H08/H14/H16; revisão externa mais guest real; build não prova estado inicial do boot |
| SRC-GUEST | Boot; todos GUEST, incluindo cgroup e identidades | GUEST/H01/H03–H11/H15/H16; observador independente do runner e confronto host; autorrelato isolado recusa |
| SRC-RECURSOS | Boot; todos RECURSOS, parents, medições e applicability histórica separada | RECURSOS/H09–H13/H15; limites host+guest e qualificação autorizada; quota true ou espaço livre sem aplicação não aprova |
| SRC-LIFECYCLE | Run/boot por evento; todos LIFECYCLE, atos externos e OBS-TEMPO | LIFECYCLE/H13/H14/H15; hipervisor/relógio/árvore independentes; PID-file e Off guest insuficientes |
| SRC-EXPORT | Run mais boot parado; todos EXPORTACAO, cópia e artefactos finais | EXPORTACAO/H16; custódia, parser/appliance e revisão privada; artefacto mudou/ato ausente bloqueia |

Os campos completos constam de S §§3–9; prefixo é a enumeração exata, sem
campos livres. Claims identificam Field e source IDs globalmente únicos.
Política por SourceContract deve fixar unidade, escopo, método e origens nativas
host/guest/build. Mapping oficial/exaustividade reais continuam pendentes; este
contrato não certifica que um coletor existe ou que enumerou o sistema inteiro.

## 6. Versões e unicidade (P7/P8 preservados)

KernelRelease=[0-9][A-Za-z0-9._+~-]{0,255}, bytes preservados, igualdade com imagem.
PackageVersion=[A-Za-z0-9][A-Za-z0-9.+:~_!-]{0,255}, version_scheme obrigatório
debian/pep440/opaque; sem remoção de epoch, casefold ou normalização destrutiva.
Sintaxe semântica/comparador do scheme precisam aprovação; não comparar versões
lexicograficamente para inferir segurança. Version de implementação é declarada
e só verificada contra bytes/revisão externos.
device_id é único global no inventário HOST; (controller_id,slot) é único.
Slot0 em controladores distintos é permitido; duplicação de par/ID recusa.

## 7. DAG e resultados imutáveis — C2

C0 coleta autorizada e separada → C1 estrutura/refs/bytes/hash/proveniência →
C2 sete avaliações locais independentes → C3 consistência e invalidação →
C4 consolidação. C1 também pode alimentar C3/C4; política externa alimenta
C1–C4. Nenhuma aresta de aprovação regressa a camada anterior. Factos guest
admitidos em C1 não significam PASS de VAL-GUEST. Avaliações não recolhem dados.

LocalResult={id:ID,validator_id:ID,implementation_version:PackageVersion,
implementation_sha256:SHA,schema_version:"2.0.0",subject:Subject,
assessment_context_sha256:SHA,identity_review_ref:TypedRef,
collector_refs:TypedRefs,local_status:Result,dimensions:Dimensions,
used_refs:TypedRefs,rejected_refs:Rejected[0..256],source_record_refs:ID[1..1024],
reason_codes:ID[0..256],signature:Signature}.
É imutável após assinatura. local_status representa a avaliação NO SEU INSTANTE,
não a validade futura. Se as dimensões eram todas PASS e nenhuma ref rejeitada
naquele instante, PASS histórico pode permanecer; não significa PASS final.

Rejected={ref:TypedRef,reason_code:ID}.
Invalidation={id:ID,assessment_context_sha256:SHA,
affected_local_results:ID[1..7],rejected_refs:Rejected[1..256],
discovered_at:UTC,discovery_observation_ref:TypedRef,reason_codes:ID[1..256],
signature:Signature}.
Só observation; originais/hashes preservados. Fecho transitivo deriva de used_refs
e source_record_refs: todos os locais que consomem direta/indiretamente ref
rejeitada ficam mascarados no resultado FINAL. Contradição posterior cria nova
Invalidation/assessment, nunca reescreve um LocalResult anterior.

FinalResult={id:ID,validator_id:ID,implementation_version:PackageVersion,
implementation_sha256:SHA,identity_review_ref:TypedRef,local_result_id:ID,
local_result_content_sha256:SHA,assessment_context_sha256:SHA,
invalidation_refs:ID[0..256],final_status:Result,dimensions:Dimensions,
accepted_refs:TypedRef[0..256],rejected_refs:Rejected[0..256],
reason_codes:ID[0..256],signature:Signature}.
FinalResult é NOVO registo assinado pelo consolidador autorizado, com identidade
de implementação vinculada através de Review externo do seu artefacto e perfil
de assinatura; não é LocalResult modificado. Sem esse perfil/revisão, UNKNOWN.
local_result_content_sha256 deve referir o original exato. Divergência recusa.
Uma ref rejeitada não pode ser aceite noutra dimensão final. FAIL demonstrado
prevalece sobre UNKNOWN, que prevalece sobre NOT_EVALUATED e PASS.
C4 lê FinalResult, nunca usa local_status para contornar invalidação.
Após emissão, alteração de qualquer registo produz NOVO registo/id/assinatura;
histórico não é apagado. FinalResult que declare PASS após invalidação é recusado.

## 8. Rastreabilidade, H16 e decisão — C3

Dimensions={structure:Result,cryptography:Result,provenance:Result,
applied_configuration:Result,real_behavior:Result}.
Todos os eixos necessários têm prova; falta=UNKNOWN; dependência barrada antes
de avaliar=NOT_EVALUATED; violação demonstrada=FAIL. Agregação normativa:
FAIL > UNKNOWN > NOT_EVALUATED > PASS. Um eixo não aplicável precisa de critério
substituto real aprovado externamente, não um PASS por default.

RequirementResult={requirement_id:enum(H01..H16),owner:ID,co_validators:ID[0..6],
dimensions:Dimensions,source_record_refs:ID[1..1024],used_refs:TypedRefs,
final_result_ids:ID[1..7],final_status:Result,reason_codes:ID[0..256]}.
Refs só FinalResult daquele assessment; sete validadores e 16 requisitos exatos,
únicos, sem omissão, owner/co-validadores iguais à matriz. Requirements não
consomem o resultado de outro requisito para obter aprovação provisória.

**Decisão normativa proposta para H16: incluir H01–H08**, mais inventários do
pacote/imagem e canais de exportação. Justificação: a ausência de caminho
operacional previsto a produção depende não só dos canais H01–H07, mas também
da identidade/integridade da imagem e boot que os observa. H08 acrescenta
defesa de confiança, não transforma Secure Boot em prova de isolamento. O
âmbito mais conservador precisa APROVAÇÃO HUMANA; enquanto não aprovado,
H16 é UNKNOWN e global NAO_APTO. Não há interpretação silenciosa alternativa.

| Req | Owner / co-validadores | Claims/fontes / condição de recusa |
| --- | --- | --- |
| H01 | HOST / GUEST | NICs/interfaces; NIC desligada presente, coleta incompleta ou ausência sem prova recusa |
| H02 | HOST / GUEST | Vínculos/switches/rotas; qualquer associação ou omissão recusa |
| H03 | HOST / GUEST,ARTEFACTOS | Integração/serviços/perfil; extra, enabled ou sem mapping recusa |
| H04 | HOST / GUEST | Sessão/política cliente; enhanced/unknown recusa |
| H05 | HOST / GUEST | Clipboard/file-copy/endpoints; canal/enumeração não demonstrados recusa |
| H06 | HOST / GUEST,ARTEFACTOS | Relays/endpoints; flag absent/blocked sem suporte recusa |
| H07 | HOST / GUEST,MANIFESTO | Devices/mounts/pacote; extra, parent/stream ou colisão recusa |
| H08 | ARTEFACTOS / HOST,GUEST | Boot/cadeia/imagem; template/assinaturas/hash sem aprovação recusa |
| H09 | RECURSOS / HOST,GUEST | RAM fixa/medida; dinâmica ou divergência recusa |
| H10 | RECURSOS / HOST,GUEST | CPU/âmbito/cgroup; unidade/limite não demonstrado recusa |
| H11 | RECURSOS / HOST,GUEST | Fixed disk/parents/mounts; parent desconhecido/capacidade extra recusa |
| H12 | RECURSOS / HOST,GUEST | Quota/targets/medição; backend/cobertura/aplicação ausente recusa |
| H13 | LIFECYCLE / RECURSOS,HOST | Deadline/watchdog/stop; timeout ou Off não confirmado bloqueia |
| H14 | LIFECYCLE / HOST,MANIFESTO,ARTEFACTOS | Run/Boot/atos/associações; replay/reassociação/identidade divergente recusa |
| H15 | GUEST / RECURSOS,LIFECYCLE | Árvore/cgroup/contenção; fora do escopo/PID-file isolado recusa |
| H16 | HOST / GUEST,MANIFESTO,ARTEFACTOS,EXPORTACAO | H01–H08 + pacote/imagem/exportador; escopo não aprovado, canal/segredo/prova ausente recusa |

SC-DECISAO={schema_id:"SC-DECISAO",schema_version:"2.0.0",assessment_id:UUID,
context_ref:ID,schema_versions:SchemaVersion[7],local_results:LocalResult[7],
final_results:FinalResult[7],requirements:RequirementResult[16],
accepted_refs:TypedRef[0..256],rejected_refs:Rejected[0..256],
invalidations:Invalidation[0..256],generated_at:UTC,
global_state:enum(NAO_APTO,APTO),refusal_reasons:ID[0..256],signature:Signature}.
RecordType da assinatura desta estrutura é Decision. SchemaVersion={schema_id:ID,
version:"2.0.0"}. IDs/refs únicos; 7 SC/VAL exatos; accepted/rejected disjuntos.
Local e Final correspondem por validator_id + hash original; não pode faltar
um resultado bloqueado para obter sete PASS. Cada requisito refere seus finais,
dimensões e provas, não uma lista vazia de pendências autodeclarada.

Global APTO requer 7 Final PASS, 16 requirements PASS, zero invalidações/recusas,
provas reais completas independentes, política/H16 aprovados. Context documentary
ou qualquer captura synthetic impõe NAO_APTO, mesmo que locais/finais declarem
PASS. Não aprova uma ação. Dados ausentes/versões antigas/mistura de R2 com
rascunho anterior bloqueiam. A identidade dos conteúdos normativos é verificada
pelos hashes externos de política, não apenas por schema_version.

Reason codes do schema são acrescidos de QUALIFICATION_NOT_APPLICABLE,
ASSOCIATION_NOT_REVIEWED,ENUMERATION_UNSUPPORTED,COLLECTION_OVERFLOW,
CANONICAL_ORDER_INVALID,CHECKPOINT_MISMATCH,ORIGINAL_RESULT_CHANGED,
H16_POLICY_UNAPPROVED,FINAL_SIGNATURE_UNAVAILABLE.
RecordType/hash sem bytes ou assinatura indisponível → UNKNOWN; conteúdo
divergente demonstrado → FAIL. Nunca inventar assinatura para satisfazer schema.

## 9. Fixtures e evidência esperada — C9

VALIDADORES_FIXTURES.md inclui bundle estrutural completo sintético com uma
Entry (cardinalidade permitida para input parcial), casos isolados C1–C9 e
receitas de bytes/hashes. Bundle estrutural não é decisão completa de 7/16.
Exemplos de assinatura mostram METADADOS sem bytes de assinatura válida; logo
não alegam resultado efetivamente assinado/verificado. Caso final especifica
novo registo/signed bytes e o hash do original, não finge assinatura Ed25519.

Vetores de SHA conhecidos de entrada simples podem constar como expectativas
não recalculadas nesta fase. Para registos extensos, a expectativa é a receita
exata de bytes/hash; o digest numérico não calculado é PENDENTE, nunca inventado.
Cobertura documental não equivale a execução de fixture nem aprovação final.

## 10. Pendências e alcance

Decisões R2 de H16, limites, criptografia, checkpoints e qualificação histórica
precisam revisão humana independente. Fonte normalizada não prova mapping
oficial de build nem completude real. Revogação, confiança de chaves, imagem/
lock, preflight, quota, relays, watchdog, cgroup, exportador e continuidade
entre boots continuam não implementados/não demonstrados. Nenhuma operação
ou ensaio é autorizado. Estado obrigatório **NÃO APTO**.
