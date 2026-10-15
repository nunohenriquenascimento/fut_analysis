# Fixtures documentais 2.0.0 — correções P1–P10

Segunda revisão documental R2, ainda NÃO APTO: casos adicionais §7–§10 corrigem
C1–C9. Aplicam-se ArtifactBinding, HistoricalQualification/Applicability,
Checkpoint, LocalResult/Invalidation/FinalResult separados. Bundles anteriores
não são convertidos. Nenhum exemplo contém assinatura operacional verificada.

**NÃO APTO.** Exemplos e mutações exclusivamente documentais; nenhum ficheiro
de fixture executável, assinatura, evidência operacional ou teste foi criado.
Os exemplos 1.0.0 foram substituídos, não convertidos em evidências 2.0.0.
Normas: [schemas](VALIDADORES_SCHEMAS.md) e
[contrato transversal](VALIDADORES_CORRECOES_P1_P10.md).

## 1. Pré-condições comuns e isolamento dos motivos

D0 é o cenário documental: Run R, VM V, host H; boots B1/B2 distintos do mesmo
run; artefacto imutável A; capturas CB (build, subject artifact A), CH1/CG1
(boot B1), CH2/CG2 (boot B2), CS1 (stop B1), CX1 (exportação dos bytes finais
do B1); revisão RV1 refere CB/hash original; autorização AU1 do tipo authorization.
Estes nomes são **símbolos**, não UUIDs ou dados coletados. Numa futura
materialização sintética, devem receber IDs/UUIDs válidos e hashes fictícios
distintos, nunca identidades/segredos reais. D0 não é um bundle serializado.

Todas as capturas têm nature=synthetic; contexto purpose=document_review e
mode=documentary. Signature contém somente identificadores sintéticos e hashes
de substituição, sem assinatura real ou trust anchor aprovado. Nenhum valor
PASS criptográfico/proveniência é reivindicado. Estado global sempre NAO_APTO.

Para cada caso isolado abaixo, os restantes campos/relações são estipulados
documentalmente conformes ao contrato; a análise da camada indicada pode usar
um oráculo de pré-condição **apenas no desenho de teste**, nunca na implementação
operacional. Assim uma negativa de quota não é escondida pela recusa anterior
de uma assinatura sintética. Os casos futuros terão fixtures unitárias por
camada, sem caminho para admitir sintéticos como prova real.

Convenções: E=resultado estrutural esperado, S=resultado semântico local esperado.
NOT_EVALUATED significa camada não executada/barrada; nenhum caso é resultado
observado. Todos os casos declaram as sete partes exigidas nas tabelas:
ID/objetivo, pré-condição, alteração, E, S, motivo. NAO_APTO é invariável global.

## 2. Exemplos positivos por camada, não evidências positivas de isolamento

| ID / objetivo | Pré-condição documental | Alteração/conteúdo definido | E | S esperado | Motivo/limite |
| --- | --- | --- | --- | --- | --- |
| POS-HOST: shape completo | D0 + SRC-HOST e claims de todos os campos | generation=2; NIC/vínculos vazios; integrações disabled; basic; devices boot,payload,work e essencial com pares únicos | PASS esperado | UNKNOWN global/proveniência | SYNTHETIC_NOT_EVIDENCE; sem afirmar hardware real |
| POS-MANIFESTO: shape completo | D0 + SRC-PACOTE | Três paths do manifesto e controlos em allowlist sintética separada; tipos regular, streams vazios, tamanhos/hashes fictícios | PASS esperado | UNKNOWN criptográfico | Bytes reais não apresentados; HASH_MISMATCH só se comparação for demonstrada |
| POS-ARTEFACTOS: versões | D0 + SRC-IMAGEM | Dependency version=1:18.6-1, scheme=debian; outra version=3.3.6, scheme=pep440; lock sintético; sem autostart | PASS esperado | UNKNOWN proveniência | Não aprova ABI/lock/build real |
| POS-GUEST: kernel numérico | D0 + SRC-GUEST | kernel_release=6.8.0-xx-generic; apenas lo; UID=1000; root/payload ro; mounts/cgroups nos scopes sintéticos | PASS esperado | UNKNOWN configuração real | Não recolheu kernel/UID/mounts |
| POS-RECURSOS: limites propostos | D0 + SRC-RECURSOS | 2 vCPU/4 GiB, work fixed 2 GiB, host 32 GiB, cgroup/180s conforme política candidata | PASS esperado | UNKNOWN aplicação | Flags de quota não demonstram aplicação |
| POS-LIFECYCLE: refs tipadas | D0 + SRC-LIFECYCLE | Transições conforme política sintética, authorization refs AU1; Off em observação host CS1 tipada observation | PASS esperado | UNKNOWN autorização/Off real | AU1 e CS1 são símbolos sem autoridade real |
| POS-EXPORT: refs próprias | D0 + SRC-EXPORT | authorization AU1 de operação export_evidence; somente relatório regular com teto, fonte Off e revisão própria | PASS esperado | UNKNOWN cadeia real | Não existe transferência nem exportação aprovada |

O envelope completo usa schema_version/bundle_version=2.0.0, contexto por run,
boot_refs explícitos, Capture/Review/Authorization distintos e TypedRef em cada
campo. Todos os campos obrigatórios dos bodies e claims constam da especificação;
não usar as linhas desta tabela como objetos JSON prontos ou afirmar validação
estrutural já executada.

## 3. Identidades, tempo, assinatura e referências

| ID / objetivo | Pré-condição documental | Alteração introduzida | E | S esperado | Motivo específico |
| --- | --- | --- | --- | --- | --- |
| ID01: build sem boot | D0; CB subject artifact A | Associar CB a B2 via ArtifactBinding com Review do hash/destino exatos, preservando captura original | PASS | Relação local admissível; proveniência UNKNOWN | Sem aprovação real; não é replay de observação |
| ID02: replay de boot | D0; CH1 refere B1 | Consumidor trata CH1 como configuração de B2 sem nova captura | PASS | FAIL | REPLAY / REASSOCIATION |
| ID03: VM diferente | D0; CH1 vinculado a V | Trocar sujeito para V2 mantendo assinatura de CH1 | PASS | FAIL na verificação de âmbito estipulada | INVALID_SIGNATURE_SCOPE |
| ID04: run diferente | D0; assinatura de R | Reutilizar Capture.id com outro run | PASS | FAIL | REASSOCIATION; registro de IDs externo |
| ID05: contexto de outro host | D0 | Associar run ao host H2 sem novo registo externo | PASS | FAIL | IDENTITY_MISMATCH |
| TM01: revisão não renova | D0; CH1 envelheceu no ponto avaliado | Atualizar apenas reviewed_at | PASS | FAIL | STALE_EVIDENCE |
| TM02: original adulterado | D0; bytes assinados fixos | Alterar original_captured_at sem nova assinatura | PASS | FAIL | INVALID_SIGNATURE_SCOPE |
| TM03: build antigo imutável | D0; CB antigo, artefacto/revisão vigentes estipulados | Avaliar com ArtifactBinding e revisão específica ao run atual, sem exigir TTL volátil | PASS | Regra temporal local satisfeita; proveniência UNKNOWN | Não redata CB; sintético não produz PASS operacional |
| TM04: autorização expirada | D0; AU1 específico | Instante da ação após expires_at | PASS | FAIL | VALUE_INCOMPATIBLE / autorização sem validade |
| TM05: stop ultrapassado | D0; CS1 confirmou B1 | Reinício B2 e utilização de CS1 como estado atual | PASS | FAIL | REPLAY; CS1 só histórico |
| TM06: export bytes mudaram | D0; revisão CX1 de hash A | Fonte/cópia tem agora hash B | PASS | FAIL | HASH_MISMATCH |
| AU01: revisão não autoriza | D0; campo exige authorization | authorization_ref={kind:review,id:RV1} | FAIL na restrição do campo | NOT_EVALUATED | REF_TYPE_MISMATCH |
| AU02: observação não autoriza | D0; CS1 é observation | Referência authorization aponta para registo CS1 | PASS de sintaxe; falha relacional | FAIL | REF_TYPE_MISMATCH |
| AU03: escopo errado | D0; AU1 só inspect | Reutilizar AU1 para export_evidence | PASS | FAIL | EXPORT_NOT_AUTHORIZED |
| AU04: nonce repetido | D0; registo de consumo externo estipulado | Reusar ato já consumido noutro pedido | PASS | FAIL | REPLAY |
| AU05: revogação desconhecida | D0; AU1 bem tipado | Falta prova local do estado de revogação | PASS | UNKNOWN | UNVERIFIABLE_PROVENANCE |
| CR01: domínio de assinatura | D0; assinatura do tipo Review | Aplicá-la a Capture com mesmos IDs/digests | PASS | FAIL | INVALID_SIGNATURE_SCOPE |
| CR02: raiz não aprovada | D0 | Pacote fornece nova raiz para se validar | PASS | UNKNOWN | UNVERIFIABLE_PROVENANCE |
| CR03: canonicalização | D0 | JSON com duplicate keys ou string inválida | FAIL | NOT_EVALUATED | SCHEMA_INVALID |

Nas variantes de assinatura, a pré-condição é um vetor documental estipulado
para futura verificação unitária, não uma assinatura real existente. Política
JCS/Ed25519 ainda não aprovada; nunca marcar criptografia real como verificada.

## 4. Fontes e recusas por mecanismo

| ID / objetivo | Pré-condição documental | Alteração introduzida | E | S esperado | Motivo específico |
| --- | --- | --- | --- | --- | --- |
| SRC01: incompletude | D0; SRC-HOST | enumeration.state=partial | PASS | UNKNOWN; consumidores bloqueados | SOURCE_INCOMPLETE |
| SRC02: truncagem | D0; SRC-GUEST | state=truncated, omitir parte da enumeração | PASS | UNKNOWN | SOURCE_TRUNCATED |
| SRC03: falha de recolha | D0; SRC-RECURSOS | state=failed e error code fixo | PASS | UNKNOWN | COLLECTION_FAILED |
| SRC04: contagem contraditória | D0 | item_count diferente do número de records | PASS de tipos | FAIL relacional | CONTRADICTORY_EVIDENCE |
| SRC05: claim sem fonte | D0 | quota_effective=true sem SourceRecord/revisão independente | PASS do scalar | UNKNOWN | INCOMPLETE_EVIDENCE |
| SRC06: campo aninhado extra | D0; Signature fechado | Acrescentar verified=true dentro de Signature | FAIL | NOT_EVALUATED | EXTRA_FIELD |
| SRC07: independente só no nome | D0 | Fonte e corroboration_ref vêm do mesmo coletor, política exige separação | PASS | UNKNOWN | UNVERIFIABLE_PROVENANCE |
| HV01: NIC desligada presente | D0; body HOST válido | nic_ids=[nic-disabled], fonte confirma presença mesmo sem vínculo | PASS | FAIL | CHANNEL_PRESENT |
| HV02: switch extra | D0; zero NICs declarado | switch_binding_ids=[switch-extra] | PASS | FAIL | CONTRADICTORY_EVIDENCE / CHANNEL_PRESENT |
| HV03: serviço extra | D0 | Acrescentar service_id fora do mapping ou enabled=true | PASS | FAIL | CHANNEL_PRESENT |
| HV04: endpoint extra | D0; SRC-HOST endpoints | Endpoint vsock não aprovado presente | PASS | FAIL | CHANNEL_PRESENT |
| HV05: Enhanced Session | D0; basic esperado | session_mode=enhanced | PASS | FAIL | CHANNEL_PRESENT |
| HV06: ISO adicional | D0; inventário fechado | Device payload-extra não autorizado | PASS | FAIL | DEVICE_UNAPPROVED |
| HV07: memória dinâmica | D0; fixa aprovada na política candidata | dynamic_memory=true | PASS | FAIL | RESOURCE_DYNAMIC |
| HV08: quota sem prova | D0; quota_effective=true declarado | Falta OBS-TEMPO quota_limit e cobertura de um destino host | PASS | UNKNOWN | UNDEMONSTRATED_MECHANISM |
| HV09: descendente fora | D0; cgroup dedicado | outside_cgroup_process_count=1 | PASS | FAIL | VALUE_INCOMPATIBLE |
| HV10: lifecycle salta ato | D0; transições tipadas | reviewed→run-authorized sem provision/atestação/ato | PASS | FAIL | INVALID_TRANSITION |
| HV11: timeout sem fim | D0; prazo excedido | final_vm_state=Unknown e falta observação host Off | PASS | UNKNOWN e run falhado | UNCONFIRMED_STOP |
| HV12: slot em controllers distintos | D0 | boot slot=0/controller-A; essential slot=0/controller-B | PASS | Sem colisão local; global UNKNOWN | Par composto é distinto |
| HV13: par duplicado | D0 | Dois device_id distintos usam controller-A/0 | PASS | FAIL | DEVICE_UNAPPROVED |
| HV14: device_id duplicado | D0 | Mesmo device_id em slots diferentes | PASS | FAIL | DEVICE_UNAPPROVED |
| HV15: versão de pacote | D0 | version=1.0~rc1-2 e scheme=debian preservado | PASS | Igualdade exata local; proveniência UNKNOWN | Sem normalizar epoch/revision |
| HV16: range indevido | D0 | version=>=3.3 em vez de versão resolvida | FAIL | NOT_EVALUATED | VALUE_INCOMPATIBLE |
| HV17: fonte sem mapping | D0 | mapping do build desconhecido apesar de inventory complete | PASS | UNKNOWN | MAPPING_UNAPPROVED |

## 5. Relatório, dependências e cinco dimensões

| ID / objetivo | Pré-condição documental | Alteração introduzida | E | S esperado | Motivo específico |
| --- | --- | --- | --- | --- | --- |
| RG01: PASS contraditório | D0; FinalResult R2 completo | final_status=PASS com provenance=UNKNOWN | PASS | FAIL | RESULT_INCONSISTENT |
| RG02: FAIL escondido | D0 | RequirementResult PASS com eixo applied_configuration=FAIL | PASS | FAIL | RESULT_INCONSISTENT |
| RG03: requisito omitido | D0; 16 exigidos | Remover H06 | FAIL de cardinalidade | NOT_EVALUATED | REQUIREMENT_MISSING |
| RG04: requisito repetido | D0 | Repetir H01 em vez de H16, mantendo tamanho 16 | PASS de tipos | FAIL de unicidade/cobertura | REQUIREMENT_MISSING |
| RG05: owner errado | D0 | H12 atribuído a MANIFESTO | PASS | FAIL | VALUE_INCOMPATIBLE |
| RG06: implementação declarada | D0 | Hash/version do validador sem revisão dos bytes | PASS | UNKNOWN | IMPLEMENTATION_UNVERIFIED |
| RG07: campo obrigatório | D0; LocalResult R2 | Remover implementation_sha256 | FAIL | NOT_EVALUATED | MISSING_FIELD |
| RG08: downstream bloqueado | D0; facto X usado por H03/H06, resultados locais auditáveis | C3 contradiz X; manter consumidor final PASS | PASS | FAIL | DEPENDENCY_BLOCKED / RESULT_INCONSISTENT |
| RG09: invalidação posterior | D0; relatório antigo com assessment id D1 | Contradição nova exige Invalidation e nova revisão D2; reusar D1 como atual | PASS | FAIL | REPLAY / CONTRADICTORY_EVIDENCE |
| RG10: evidência em ambos lados | D0 | Mesmo ref em accepted_refs e rejected_refs | PASS | FAIL | CONTRADICTORY_EVIDENCE |
| RG11: APTO documental | D0, todos os locais declarados PASS | global_state=APTO | PASS | FAIL | DOCUMENTARY_ONLY / SYNTHETIC_NOT_EVIDENCE |
| RG12: cinco eixos separados | D0 | structure PASS, demais UNKNOWN | PASS | NAO_APTO; sem promoção | INCOMPLETE_EVIDENCE |
| RG13: versão desconhecida | D0 | schema_version=9.0.0 | FAIL | NOT_EVALUATED | UNKNOWN_VERSION |
| RG14: exportação inadequada | D0; ato só permite relatório sanitizado | files[].classification=raw ou destination fora de escopo | PASS | FAIL | EXPORT_NOT_AUTHORIZED |
| RG15: unidade errada | D0; SourceRecord RAM | unit=percent para ram_bytes | PASS de enum | FAIL relacional | VALUE_INCOMPATIBLE |

Também são obrigatórias futuras variantes isoladas de null, missing em cada
tipo aninhado, strings boolean, overflow, UTF-8 inválido, path traversal/ADS,
streams, coleção extra, source desconhecido, assinatura indisponível, autorização
sem escopo, drift/configuração e credenciais suspeitas. Categorias já listadas
não equivalem a casos executados; nenhuma cobertura operacional é reivindicada.

## 6. Cobertura P1–P10 e saída consolidada esperada

P1: ID01–ID05/TM05. P2: TM01–TM06. P3: RG08–RG10. P4: SRC01–SRC07/HV17.
P5: ID03/CR01–CR03. P6: AU01–AU05. P7: POS-GUEST/HV15–HV16.
P8: HV12–HV14. P9: RG06–RG07. P10: RG01–RG05/RG11–RG12.

Relatório documental R2 usa SC-DECISAO 2.0.0, 7 LocalResult/7 FinalResult e 16
RequirementResult H01–H16, context document_review/documentary. Cada LocalResult
contém ID/version/hash de implementação DECLARADOS e revisão ausente/sintética,
collector_refs, dimensões, used/rejected refs tipadas, source_record_refs e
motivos. FinalResult tem os campos próprios de C §7 e referencia o conteúdo do
LocalResult; não herda implicitamente os seus campos. Não preencher versão/hash
verificados ou inventar assinatura para obter
completude. Exemplos abreviados são símbolos de campos futuros, não dados reais.

Resultado global esperado em todos os casos: **NAO_APTO**. Nos casos negativos,
a camada indicada tem FAIL/UNKNOWN e as dependências finais ficam bloqueadas;
nos positivos só há expectativas de estrutura/relação local. A fase documental
não pode produzir APTO mesmo que todas as expectativas locais sejam satisfeitas.

Próxima etapa segura: revisão humana independente da suficiência das fixtures
e dos contratos, especialmente binding/canonicalização/fontes e invalidação.
Não executar validadores, testes nem solicitar ensaio real.

## 7. Bundle estrutural completo R2 — FX-C9-BUNDLE

Objetivo: apresentar TODOS os campos de um bundle parcial permitido, sem
elipses, símbolos D0 ou objetos omitidos. Uma Entry é permitida pelo input
1..32; não é decisão completa dos sete validadores. Pré-condição: avaliação
somente da forma/tipos/refs, não aceitação de hashes, assinaturas ou política.
Hashes 111... são placeholders sintáticos deliberados, NÃO digests calculados.
Review/signatures são sintéticos sem bytes de assinatura válida. Resultado
esperado documental: forma proposta completa; criptografia/proveniência não
demonstradas, global NAO_APTO. Relações de aplicação/Binding/autoridade ainda
ausentes não são encobertas como aprovação. Nada foi validado por execução.

```json
{
  "bundle_version":"2.0.0",
  "contexts":[{
    "id":"CTX1","run_ref":"11111111-1111-4111-8111-111111111111",
    "boot_refs":["33333333-3333-4333-8333-333333333333"],
    "artifact_binding_refs":[],"qualification_applicability_refs":[],
    "review_refs":[{"kind":"review","id":"RV1"}],"checkpoint_refs":["CP1"],
    "purpose":"document_review","mode":"documentary","assessed_at":"2026-10-15T12:00:02Z"
  }],
  "runs":[{
    "id":"11111111-1111-4111-8111-111111111111",
    "host_instance_id":"22222222-2222-4222-8222-222222222222",
    "vm_id":"44444444-4444-4444-8444-444444444444",
    "image_sha256":"1111111111111111111111111111111111111111111111111111111111111111",
    "policy_sha256":"1111111111111111111111111111111111111111111111111111111111111111",
    "registry_review":{"kind":"review","id":"RV1"}
  }],
  "boots":[{
    "id":"33333333-3333-4333-8333-333333333333",
    "run_id":"11111111-1111-4111-8111-111111111111",
    "vm_id":"44444444-4444-4444-8444-444444444444",
    "configuration_sha256":"1111111111111111111111111111111111111111111111111111111111111111",
    "sequence":1,"start_observation":{"kind":"observation","id":"O1"}
  }],
  "captures":[
    {
      "id":"55555555-5555-4555-8555-555555555555",
      "subject":{"scope":"boot","run_id":"11111111-1111-4111-8111-111111111111","vm_id":"44444444-4444-4444-8444-444444444444","boot_id":"33333333-3333-4333-8333-333333333333","configuration_sha256":"1111111111111111111111111111111111111111111111111111111111111111"},
      "original_captured_at":"2026-10-15T12:00:00Z","nature":"synthetic",
      "collector_id":"fixture-host","collector_sha256":"1111111111111111111111111111111111111111111111111111111111111111",
      "source_contract_id":"SRC-LIFECYCLE","source_contract_version":"2.0.0",
      "artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111","collection_state":"complete",
      "signature":{"profile_id":"candidate-fixture","signer_id":"fixture-signer","key_id":"fixture-key","trust_anchor_id":"unapproved-fixture","signed_payload_sha256":"1111111111111111111111111111111111111111111111111111111111111111","signature_artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111"}
    },
    {
      "id":"66666666-6666-4666-8666-666666666666",
      "subject":{"scope":"artifact","artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111"},
      "original_captured_at":"2026-10-15T11:00:00Z","nature":"synthetic",
      "collector_id":"fixture-builder","collector_sha256":"1111111111111111111111111111111111111111111111111111111111111111",
      "source_contract_id":"SRC-PACOTE","source_contract_version":"2.0.0",
      "artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111","collection_state":"complete",
      "signature":{"profile_id":"candidate-fixture","signer_id":"fixture-signer","key_id":"fixture-key","trust_anchor_id":"unapproved-fixture","signed_payload_sha256":"1111111111111111111111111111111111111111111111111111111111111111","signature_artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111"}
    },
    {
      "id":"77777777-7777-4777-8777-777777777777",
      "subject":{"scope":"artifact","artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111"},
      "original_captured_at":"2026-10-15T11:00:00Z","nature":"synthetic",
      "collector_id":"fixture-inspector","collector_sha256":"1111111111111111111111111111111111111111111111111111111111111111",
      "source_contract_id":"SRC-PACOTE","source_contract_version":"2.0.0",
      "artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111","collection_state":"complete",
      "signature":{"profile_id":"candidate-fixture","signer_id":"fixture-signer","key_id":"fixture-key","trust_anchor_id":"unapproved-fixture","signed_payload_sha256":"1111111111111111111111111111111111111111111111111111111111111111","signature_artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111"}
    },
    {
      "id":"88888888-8888-4888-8888-888888888888",
      "subject":{"scope":"boot","run_id":"11111111-1111-4111-8111-111111111111","vm_id":"44444444-4444-4444-8444-444444444444","boot_id":"33333333-3333-4333-8333-333333333333","configuration_sha256":"1111111111111111111111111111111111111111111111111111111111111111"},
      "original_captured_at":"2026-10-15T12:00:01Z","nature":"synthetic",
      "collector_id":"fixture-host","collector_sha256":"1111111111111111111111111111111111111111111111111111111111111111",
      "source_contract_id":"SRC-LIFECYCLE","source_contract_version":"2.0.0",
      "artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111","collection_state":"complete",
      "signature":{"profile_id":"candidate-fixture","signer_id":"fixture-signer","key_id":"fixture-key","trust_anchor_id":"unapproved-fixture","signed_payload_sha256":"1111111111111111111111111111111111111111111111111111111111111111","signature_artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111"}
    }
  ],
  "reviews":[{
    "id":"RV1","target":{"record_type":"Run","record_id":"11111111-1111-4111-8111-111111111111","record_content_sha256":"1111111111111111111111111111111111111111111111111111111111111111","subject":{"scope":"run","run_id":"11111111-1111-4111-8111-111111111111","vm_id":"44444444-4444-4444-8444-444444444444"}},
    "reviewed_at":"2026-10-15T12:00:01Z","reviewer_id":"fixture-reviewer",
    "verification_policy_sha256":"1111111111111111111111111111111111111111111111111111111111111111","review_result":"unknown",
    "signature":{"profile_id":"candidate-fixture","signer_id":"fixture-signer","key_id":"fixture-key","trust_anchor_id":"unapproved-fixture","signed_payload_sha256":"1111111111111111111111111111111111111111111111111111111111111111","signature_artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111"}
  }],
  "artifact_bindings":[],"authorizations":[],"historical_qualifications":[],"qualification_applicabilities":[],
  "checkpoints":[{
    "id":"CP1","assessment_context_id":"CTX1",
    "subject":{"scope":"boot","run_id":"11111111-1111-4111-8111-111111111111","vm_id":"44444444-4444-4444-8444-444444444444","boot_id":"33333333-3333-4333-8333-333333333333","configuration_sha256":"1111111111111111111111111111111111111111111111111111111111111111"},
    "event":"preflight","event_observation_ref":{"kind":"observation","id":"O2"},"at_utc":"2026-10-15T12:00:01Z","clock_id":"fixture-clock","monotonic_ns":2000000000,
    "evaluated_capture_refs":["66666666-6666-4666-8666-666666666666"],
    "signature":{"profile_id":"candidate-fixture","signer_id":"fixture-signer","key_id":"fixture-key","trust_anchor_id":"unapproved-fixture","signed_payload_sha256":"1111111111111111111111111111111111111111111111111111111111111111","signature_artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111"}
  }],
  "technical_catalog":[{"kind":"technical","id":"T1","capture_ref":"66666666-6666-4666-8666-666666666666"},{"kind":"technical","id":"T2","capture_ref":"77777777-7777-4777-8777-777777777777"}],
  "observation_catalog":[{"kind":"observation","id":"O1","capture_ref":"55555555-5555-4555-8555-555555555555"},{"kind":"observation","id":"O2","capture_ref":"88888888-8888-4888-8888-888888888888"}],
  "inventories":[{
    "source_contract_id":"SRC-PACOTE","source_contract_version":"2.0.0","capture_ref":"66666666-6666-4666-8666-666666666666",
    "enumeration":{"scope_ids":["fixture-control","fixture-payload"],"expected_scope_policy_sha256":"1111111111111111111111111111111111111111111111111111111111111111","state":"complete","error_codes":[],"item_count":5,
      "collections":[
        {"field":"MANIFESTO.control_files","subject":{"scope":"artifact","artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111"},"collector_id":"fixture-builder","checkpoint_ref":"CP1","state":"complete","observed_count":1,"support_refs":[{"kind":"technical","id":"T2"}]},
        {"field":"MANIFESTO.files","subject":{"scope":"artifact","artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111"},"collector_id":"fixture-builder","checkpoint_ref":"CP1","state":"complete","observed_count":3,"support_refs":[{"kind":"technical","id":"T2"}]}
      ]},
    "records":[
      {"id":"SM1","subject":{"scope":"artifact","artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111"},"field":"MANIFESTO.manifest_sha256","value":"1111111111111111111111111111111111111111111111111111111111111111","unit":"none","observed_at":"2026-10-15T11:00:00Z","corroboration_refs":[{"kind":"technical","id":"T2"}]},
      {"id":"SM2","subject":{"scope":"artifact","artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111"},"field":"MANIFESTO.package_sha256","value":"1111111111111111111111111111111111111111111111111111111111111111","unit":"none","observed_at":"2026-10-15T11:00:00Z","corroboration_refs":[{"kind":"technical","id":"T2"}]},
      {"id":"SM3","subject":{"scope":"artifact","artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111"},"field":"MANIFESTO.full_enumeration","value":true,"unit":"none","observed_at":"2026-10-15T11:00:00Z","corroboration_refs":[{"kind":"technical","id":"T2"}]},
      {"id":"SM4","subject":{"scope":"artifact","artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111"},"field":"MANIFESTO.files","value":[
        {"path":"docs/railway/read_only_probe.py","sha256":"1111111111111111111111111111111111111111111111111111111111111111","size_bytes":1,"kind":"regular","stream_ids":[]},
        {"path":"docs/railway/tests/test_probe_postgresql_integration.py","sha256":"1111111111111111111111111111111111111111111111111111111111111111","size_bytes":1,"kind":"regular","stream_ids":[]},
        {"path":"docs/railway/tests/test_read_only_probe.py","sha256":"1111111111111111111111111111111111111111111111111111111111111111","size_bytes":1,"kind":"regular","stream_ids":[]}
      ],"unit":"none","observed_at":"2026-10-15T11:00:00Z","corroboration_refs":[{"kind":"technical","id":"T2"}]},
      {"id":"SM5","subject":{"scope":"artifact","artifact_sha256":"1111111111111111111111111111111111111111111111111111111111111111"},"field":"MANIFESTO.control_files","value":[{"path":"control/fixture.json","sha256":"1111111111111111111111111111111111111111111111111111111111111111","size_bytes":1,"kind":"regular","stream_ids":[]}],"unit":"none","observed_at":"2026-10-15T11:00:00Z","corroboration_refs":[{"kind":"technical","id":"T2"}]}
    ]
  }],
  "observations":[
    {"id":"EV1","subject":{"scope":"boot","run_id":"11111111-1111-4111-8111-111111111111","vm_id":"44444444-4444-4444-8444-444444444444","boot_id":"33333333-3333-4333-8333-333333333333","configuration_sha256":"1111111111111111111111111111111111111111111111111111111111111111"},"event":"vm_start","start_utc":"2026-10-15T12:00:00Z","end_utc":"2026-10-15T12:00:00Z","clock_id":"fixture-clock","start_monotonic_ns":1000000000,"end_monotonic_ns":1000000000,"observed_state":"Running","technical_refs":[{"kind":"observation","id":"O1"}]},
    {"id":"EV2","subject":{"scope":"boot","run_id":"11111111-1111-4111-8111-111111111111","vm_id":"44444444-4444-4444-8444-444444444444","boot_id":"33333333-3333-4333-8333-333333333333","configuration_sha256":"1111111111111111111111111111111111111111111111111111111111111111"},"event":"checkpoint","start_utc":"2026-10-15T12:00:01Z","end_utc":"2026-10-15T12:00:01Z","clock_id":"fixture-clock","start_monotonic_ns":2000000000,"end_monotonic_ns":2000000000,"observed_state":"Running","technical_refs":[{"kind":"observation","id":"O2"}]}
  ],
  "entries":[{
    "schema_id":"SC-MANIFESTO","schema_version":"2.0.0","context_ref":"CTX1","evidence_refs":[{"kind":"technical","id":"T1"},{"kind":"technical","id":"T2"}],
    "claims":[{"field":"MANIFESTO.control_files","source_record_refs":["SM5"]},{"field":"MANIFESTO.files","source_record_refs":["SM4"]},{"field":"MANIFESTO.full_enumeration","source_record_refs":["SM3"]},{"field":"MANIFESTO.manifest_sha256","source_record_refs":["SM1"]},{"field":"MANIFESTO.package_sha256","source_record_refs":["SM2"]}],
    "body":{"manifest_sha256":"1111111111111111111111111111111111111111111111111111111111111111","package_sha256":"1111111111111111111111111111111111111111111111111111111111111111","full_enumeration":true,
      "files":[
        {"path":"docs/railway/read_only_probe.py","sha256":"1111111111111111111111111111111111111111111111111111111111111111","size_bytes":1,"kind":"regular","stream_ids":[]},
        {"path":"docs/railway/tests/test_probe_postgresql_integration.py","sha256":"1111111111111111111111111111111111111111111111111111111111111111","size_bytes":1,"kind":"regular","stream_ids":[]},
        {"path":"docs/railway/tests/test_read_only_probe.py","sha256":"1111111111111111111111111111111111111111111111111111111111111111","size_bytes":1,"kind":"regular","stream_ids":[]}
      ],"control_files":[{"path":"control/fixture.json","sha256":"1111111111111111111111111111111111111111111111111111111111111111","size_bytes":1,"kind":"regular","stream_ids":[]}]}
  }]
}
```

Isto não inclui sete Entry nem uma decisão APTO, por desenho. A sintaxe completa
é visível para revisão humana, mas nem forma nem refs foram executadas num
parser. Review unknown, raízes não aprovadas, hashes fictícios e falta de
associações/atos reais tornam impossível aprovação operacional.

## 8. Fixtures adicionais isoladas C1–C9

Cada caso tem objetivo, pré-condições, dados, expectativa e motivo. A base D0
continua synthetic/documentary e todas as saídas globais são NAO_APTO. Nos
casos que pressupõem prova admissível para isolar uma regra, essa pré-condição
é um oráculo documental, nunca evidência real ou caminho de bypass operacional.

| ID / objetivo | Pré-condições documentais | Dados/alteração | Estrutura esperada | Semântica esperada / motivo |
| --- | --- | --- | --- | --- |
| C1-VALID | Qualificação Q1 mantém original_subject=B1; política histórica estipulada | Applicability A1 refere ContentHash(Q1), target=B2, checkpoint CP2, comparação e Review exatos, ato válido | Forma completa se todos os registos presentes | Aplicabilidade local admissível; proveniência real UNKNOWN; sem transferir observação de B1 |
| C1-INVALID | Mesma Q1 | Alterar original_subject para B2 ou usar ArtifactBinding da observação | Tipos podem passar; relação origem viola contrato | FAIL REASSOCIATION/QUALIFICATION_NOT_APPLICABLE |
| C2-HISTORY | Local L1 assinado no instante t1 com local_status PASS | Em t2, I1 rejeita uma ref usada por L1; preservar Content(L1)/assinatura; criar F1 final FAIL referindo hash de L1 e I1 | Local/Invalidation/Final separados válidos em forma | PASS histórico preservado; final FAIL; nenhum APTO |
| C2-MUTATION | L1 original fixo | Inserir final_status em L1 ou alterar seus bytes para acomodar invalidação | Campo extra → FAIL, ou hash diverge | ORIGINAL_RESULT_CHANGED/EXTRA_FIELD |
| C3-SCOPE | Matriz de 16 requisitos | H16 usa H01–H08 e pacote/imagem/exportador; falta aprovação humana do novo âmbito | Forma pode passar | UNKNOWN H16_POLICY_UNAPPROVED |
| C3-OMISSION | Mesma matriz | Declarar H16 PASS com H08 não demonstrado | Forma pode passar | FAIL RESULT_INCONSISTENT/DEPENDENCY_BLOCKED |
| C4-GENERAL | Array sem limite específico, default256 | 257 IDs num campo de default | FAIL de cardinalidade | COLLECTION_OVERFLOW; não truncar |
| C4-SPECIFIC | dependencies tem limite1..1024 | 257 dependencies únicas e ordenadas dentro do bundle<=8MiB | Admissível em cardinalidade | Sem prova de lock/proveniência → UNKNOWN; não recusar só por exceder256 |
| C4-HARD | Teto absoluto1024 | 1025 SourceRecord ou limite agregado8MiB excedido | FAIL | COLLECTION_OVERFLOW/SCHEMA_INVALID |
| C5-ORDER | Rejected com dois refs | Ordem ref.kind/ref.id/reason_code errada ou duplicada | Tipos podem passar | CANONICAL_ORDER_INVALID; sem reordenar pelo consumidor |
| C5-NULL | Objeto fechado | signature=null ou membro obrigatório omitido | FAIL | VALUE_INCOMPATIBLE/MISSING_FIELD |
| C6-ZERO | Fonte HOST completa no scope estipulado, B1/CP1 | SourceRecord field=HOST.nic_ids,value=[]; CollectionEnumeration mesma field/subject/CP1,count0,complete e suporte independente | Forma admissível | Regra local de enumeração satisfeita se suporte real; no caso sintético UNKNOWN; [] sozinho não PASS |
| C6-NOSUPPORT | Mesmo cenário | Remover support_refs ou fornecer suporte de coleta falhada | Missing → FAIL; failed tipado → forma admissível | INCOMPLETE_EVIDENCE/COLLECTION_FAILED; consumidores bloqueados |
| C7-POINT | Checkpoint assinado do B1/pre_run | Reutilizá-lo para B2 ou após drift sem nova captura | Forma pode passar | CHECKPOINT_MISMATCH/REPLAY |
| C8-REVIEW | Review target é Capture original | Usar esse Review para aprovar ArtifactBinding ao novo alvo | Forma pode passar | ASSOCIATION_NOT_REVIEWED |
| C8-EXACT | Review target tipo ArtifactBinding/hash exato/destino B2 | Binding preservado, Review novo do seu conteúdo e ato externo de utilização apropriado | Forma admissível | Associação local admissível; não confere autorização por si só; global UNKNOWN |
| C9-NESTED | Bundle §7 | Remover signature.key_id de uma Capture | FAIL | MISSING_FIELD; não preencher default |
| C9-STREAM | Body/SourceRecord manifesto | stream_ids=[ads-extra] ou kind=hardlink | Tipos podem passar | FAIL DEVICE_UNAPPROVED/VALUE_INCOMPATIBLE |
| C9-NOSIGNATURE | FinalResult com Signature metadata completo | Bytes destacados indisponíveis ou perfil sem revisão | Forma pode passar | UNKNOWN FINAL_SIGNATURE_UNAVAILABLE; não inventar assinatura |

## 9. Resultado final novo e consolidação assinada — FX-C9-FINAL

Objetivo: mostrar a separação imutável e o âmbito da assinatura. Pré-condições:
L1 é um LocalResult histórico completo com source refs X e local PASS; I1 é
Invalidation nova que rejeita X em t2. Todos são SINTÉTICOS. Não se pressupõe
assinatura criptográfica real. Alteração: emitir F1, nunca editar L1.

Forma fechada de F1 por valores documentais:
- id=F1; validator_id=VAL-HOST; implementation_version=2.0.0;
  implementation_sha256=64 caracteres 1; identity_review_ref={kind:review,id:RF};
  local_result_id=L1; local_result_content_sha256=ContentHash(L1 ORIGINAL);
  assessment_context_sha256=ContentHash(contexto CTX1 completo);
- invalidation_refs=[I1]; final_status=FAIL; dimensions={structure:PASS,
  cryptography:UNKNOWN,provenance:UNKNOWN,applied_configuration:FAIL,
  real_behavior:UNKNOWN}; accepted_refs=[];
  rejected_refs=[{ref:{kind:technical,id:X},reason_code:CONTRADICTORY_EVIDENCE}];
  reason_codes=[CONTRADICTORY_EVIDENCE,DEPENDENCY_BLOCKED];
- signature contém os seis campos obrigatórios de Signature. Perfil/signatário/
  key/anchor são sintéticos; signed_payload_sha256 esperado é exatamente
  SHA256(SignBytes(F1,FinalResult)); signature_artifact_sha256 só poderia ser
  SHA256 dos bytes destacados. Digest de F1 e bytes da assinatura estão PENDENTES,
  não foram calculados nem fabricados. Sem eles o resultado NÃO está assinado
  ou verificado operacionalmente. Esta é a especificação do formato assinado.

O exemplo de Decision completa tem exatamente sete pares (L1,F1) a (L7,F7),
um por VAL-HOST/MANIFESTO/ARTEFACTOS/GUEST/RECURSOS/LIFECYCLE/EXPORTACAO, e 16
RequirementResult H01–H16 conforme a matriz C §8. Todos os campos de Decision
são obrigatórios: schema_id/version,assessment_id,context_ref,schema_versions,
local_results,final_results,requirements,accepted_refs,rejected_refs,
invalidations,generated_at,global_state,refusal_reasons,signature.
O caso consolidado declara global_state=NAO_APTO; F1 FAIL invalida H01/H06/H16
dependentes de X; os restantes finais são UNKNOWN pela natureza sintética e
provas não demonstradas. Refusal inclui DOCUMENTARY_ONLY,SYNTHETIC_NOT_EVIDENCE,
DEPENDENCY_BLOCKED; a assinatura de Decision usa domínio record_type=Decision,
não FinalResult. O quadro é uma fixture relacional, não um JSON materializado.
Resultado esperado: nenhuma promoção de PASS histórico ou shape válido a APTO.

## 10. Canonicalização, bytes e hashes esperados — FX-C9-BYTES

Vetores documentais conhecidos, NÃO recalculados nesta fase:

| Objetivo/pré-condição | Entrada e bytes esperados | Hash SHA-256 esperado | Resultado esperado |
| --- | --- | --- | --- |
| ArtifactHash sem normalizar | Ficheiro vazio; zero bytes | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | Vetor básico de bytes, não artefacto aprovado |
| JCS objeto vazio | J({}) é exatamente hex 7b7d, sem BOM/LF | 44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a | Vetor isolado; {} NÃO é registo válido do contrato |

Casos de representação: J([])=hex5b5d; J(null) pode existir no algoritmo geral,
mas null é recusado ANTES pelo contrato; não assinar um registo inválido.
Objeto com chaves b e a deve ter chaves em ordem JCS; strings escapadas e
inteiros usam RFC8785; coleções de sets têm de estar previamente na ordem
específica C §4. Ordem incorrecta e duplicate keys são recusas, não reparação.

Para o F1 completo de §9, a expectativa de bytes é a receita EXATA C §4 com
record_type=FinalResult, R=F1 sem signature e signature_profile definido pelos
quatro campos do seu metadata. Os bytes de Content(L1), Content(contexto),
SignBytes(F1) e SignBytes(Decision) têm receitas distintas e determinísticas.
Os respetivos digests extensos permanecem PENDENTES: obtê-los agora exigiria
cálculo/execução não autorizado. Não usar 111... como digest esperado verdadeiro.
Próxima revisão humana deverá aprovar os vetores; futura fase autorizada poderá
materializá-los, calcular hashes e comparar, sem alegar testes executados agora.
