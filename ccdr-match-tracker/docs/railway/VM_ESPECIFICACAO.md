# Contrato declarativo da VM descartável — revisão estática

## Segunda revisão documental R2 — NÃO APTO

O [contrato transversal R2](VALIDADORES_CORRECOES_P1_P10.md) substitui o rascunho
anterior 2.0.0. C1–C9 distinguem qualificação histórica/aplicabilidade de
ArtifactBinding, definem Checkpoint e resultados locais/finais imutáveis.
Nenhuma configuração da VM foi aplicada. O âmbito proposto H16 é H01–H08 mais
pacote/imagem/exportador, por depender também da confiança no boot; é decisão
normativa pendente de aprovação humana, não garantia de ausência de acesso.
Valores 2/4GiB/2GiB/32GiB/180s mantêm-se candidatos não demonstrados.

## Correções documentais P1–P10 — schemas 2.0.0

O [contrato transversal](VALIDADORES_CORRECOES_P1_P10.md) separa Run, Boot,
Capture, Review e Authorization; observação de outro boot não prova estado atual.
Prazo de captura volátil não é TTL de imagem imutável nem de encerramento
histórico. O contract_version:1 da proposta VM é distinto de schema_version:2.0.0
dos avaliadores. Não houve alteração/validação de configuração real.
IDs de devices são únicos globalmente; slots são únicos por controller_id/slot.
Política criptográfica, mapping build, hardware essencial e mecanismos externos
continuam pendentes. Estado obrigatório NÃO APTO.

## Schemas de avaliação: apenas documentação

Disponíveis [sete contratos fechados e relatório](VALIDADORES_SCHEMAS.md) e
[fixtures documentais](VALIDADORES_FIXTURES.md). Não são configuração de VM,
validadores implementados ou atestação real. Todos os campos/provas pendentes
continuam a bloquear. Nem fixture que declare configuração segura ou natureza
real pode aprovar-se sem bytes/proveniência/raízes externas independentes.

## Correspondência e validadores: bloqueios ainda abertos

Ver [matriz H01–H16 e sete validadores](HYPERV_VALIDADORES.md).
Os mecanismos aí indicados são alvos de verificação, sem consulta oficial externa
ou validação no host nesta fase. O contrato abaixo continua NÃO APTO.
Não existe uma única opção Hyper-V que implemente quota global, deadline,
contenção cgroup, sanitização ou ausência de todos os relays/HV sockets.
São dependências externas. Atestação guest sem canal de retorno e exportação
offline segura exigem desenho adicional e autorizações separadas.

Estado: **NÃO APTO — especificação proposta, sem provisionamento**.
Este documento não é um template importável nem um script. Nenhum comando de
criação/arranque está autorizado. Propriedades sem implementação/evidência
equivalem a recusa, nunca a valores predefinidos permissivos.

## Plataforma proposta

Hipervisor: **Microsoft Hyper-V, VM geração 2**, no host Windows. Justificação:
evitar outro daemon/runtime e usar uma fronteira de VM com configuração externa
de dispositivos, memória, discos e identidade. Disponibilidade, edição Windows,
versão, estado do componente e compatibilidade dos controlos **não verificados**.
Não instalar/ativar Hyper-V nem substituir silenciosamente por outro hipervisor.
Qualquer alternativa exige nova revisão do contrato.

Guest proposto: **Ubuntu Server 24.04 LTS amd64, Python 3.12**; PostgreSQL **18.6**,
psycopg **3.3.6** e SQLAlchemy **2.0.54** são versões candidatas, não um lock Linux
aprovado. A origem e compatibilidade dos artefactos Linux não foram consultadas
externamente nem validadas. O sistema deve ser uma imagem mínima imutável,
pré-preparada, sem serviços PostgreSQL arrancados ou clusters inicializados.
Não copiar a venv Windows. Atualizações de segurança exigem nova imagem/hash e
revisão; não instalar ou atualizar pacotes no ensaio offline.

## Declaração normativa

Os identificadores null são obrigatoriamente preenchidos numa revisão futura.
Este rascunho, tal como está, deve ser recusado por qualquer futuro validador.

```yaml
contract_version: 1
state: NAO_APTO
authorization_to_provision: false
authorization_to_run_tests: false
hypervisor:
  provider: Microsoft-Hyper-V
  generation: 2
  approved_host_build: null
  inventory_verified: false
identity:
  run_id: null
  vm_uuid: null
  immutable_image_sha256: null
  payload_iso_sha256: null
  approved_manifest_sha256: null
  unique_vm_per_run: true
guest:
  os_candidate: Ubuntu-Server-24.04-LTS-amd64
  exact_image_release: null
  architecture: amd64
  root_filesystem: immutable-read-only
  boot_image: dedicated-read-only-ISO
  boot_chain_verification: required
  secure_boot_profile_and_signatures: null
  existing_postgresql_clusters: forbidden
  postgres_autostart: forbidden
network:
  adapters: []
  virtual_switches: []
  nat_bridge_host_only: forbidden
  forwarding: forbidden
  dns_configuration: forbidden
  guest_interfaces_allowlist: [lo]
  guest_routes: loopback-only
  guest_ip_families: [IPv4-loopback, IPv6-loopback]
channels:
  enhanced_session: false
  clipboard: false
  drag_and_drop: false
  shared_folders: []
  host_volumes: []
  usb_pci_gpu_passthrough: []
  serial_named_pipes: []
  guest_services_file_copy: false
  optional_guest_integration_services: disabled
  essential_virtual_hardware_and_drivers_allowlist: null
  powershell_direct_and_host_guest_execution: forbidden
  hv_socket_vsock_and_management_relays: forbidden
  remote_display_redirection: forbidden
  operator_console: basic-local-display-only
resources:
  vcpu: 2
  processor_limit_percent: 100
  fixed_ram_bytes: 4294967296
  dynamic_memory: false
  guest_swap: false
  global_deadline_seconds_from_vm_start: 180
storage:
  writable_guest_disks:
    - purpose: work
      type: dedicated-fixed-VHDX
      maximum_bytes: 2147483648
      filesystem: ext4
      mount: /work
      mount_options: [nodev, nosuid]
  payload_device: dedicated-read-only-ISO
  host_partition_passthrough: forbidden
  differencing_disks: forbidden
  checkpoints_and_automatic_checkpoints: forbidden
  snapshots: forbidden
  save_state_on_timeout: forbidden
  host_per_run_storage_budget_bytes: 34359738368
  host_budget_enforcement_backend: null
  budget_includes: [images, ISO, VHDX, VM-config, runtime-state, hypervisor-logs, evidence]
runtime:
  uid: dedicated-non-root
  sudo: false
  capabilities: none-for-runner
  umask: '077'
  working_tree: read-only-payload
  TMPDIR: /work/tmp
  pgdata_wal_logs_captures: beneath-/work/tmp
  python_bytecode_writes: disabled
  runtime_tmpfs_combined_limit_bytes: 134217728
  volatile_journal_limit_bytes: 16777216
  credential_input: synthetic-generated-in-guest-only
  inherited_PG_variables: forbidden
  inherited_Railway_or_application_variables: forbidden
containment:
  mechanism: systemd-cgroup-v2
  runner_unit: dedicated-per-run
  KillMode: control-group
  MemoryMax_bytes: 2147483648
  TasksMax: 128
  CPUQuota_percent: 200
  runtime_scope: runner-and-all-descendants
  external_watchdog: mandatory-by-hypervisor-VM-UUID
  watchdog_implementation: null
lifecycle:
  allowed_states: [draft, reviewed, provision-authorized, isolated-attested, run-authorized, stopped, quarantined, dispose-authorized, disposed]
  boot_requires_separate_authorization: true
  test_execution_requires_separate_authorization: true
  no_automatic_restart_or_retry: true
  timeout_action: stop-only-attested-VM-by-UUID-under-approved-run-scope
  ambiguous_identity_action: refuse-and-report
  automatic_delete: false
  preserve_disks_on_failure: true
  disposal_requires_separate_explicit_authorization: true
evidence:
  host_effective_configuration: required
  guest_independent_inventory: required
  reviewer_approval_and_hash_binding: required
  runtime_drift_action: refuse
  export_only_after_stop: true
  automatic_export_raw_logs: false
  host_writable_share_for_export: forbidden
```

O guest precisa de dispositivos virtuais mínimos de boot/display/storage e
hypercalls do hipervisor; não se afirma que toda a comunicação hardware guest/host
desaparece. Proíbe-se comunicação adicional de rede, transferência de ficheiros,
credenciais e execução cruzada. Se um canal de integração não puder ser removido
ou demonstravelmente restringido, a implementação é NÃO APTO. O mapping para
as propriedades reais do Hyper-V ainda falta; não inventar que todas estas
propriedades existem como opções nativas diretas.

Um disco de sistema normal não deve ser considerado read-only só por estar
numa VM. A imagem bootável imutável e os mounts limitados exigem implementação
própria. O limite host de 32 GiB exige quota/volume dedicado comprovados; não
é uma opção Hyper-V aqui verificada. A configuração cgroup não autoriza o runner
a gerir o host. O watchdog deve atuar fora do guest e verificar UUID e relação
com o ensaio; PID do ficheiro PostgreSQL nunca é autoridade para ações no host.

## Preparação prévia da imagem, sem rede no ensaio

Proposta futura, não executada: aquisição/revisão dos artefactos num pipeline
de preparação separado e sem segredos de produção, depois criação de imagem
offline com repositório de pacotes e wheels aprovados. Essa preparação poderá
exigir rede num ambiente distinto, com autorização própria; nada será descarregado
nesta fase. A imagem final não mantém NIC, proxy, mirrors, tokens ou ferramentas
Railway. Não se permite habilitar rede temporariamente no guest do ensaio.

Fixar release exata, hashes e proveniência do ISO/kernel/initramfs, binários
PostgreSQL/libpq/OpenSSL, Python, bibliotecas do SO, systemd e wheels transitivas.
Confirmar compatibilidade de arquitetura/ABI/libc; nomes e versões não bastam.
Desativar autostart de PostgreSQL e não incluir PGDATA pré-existente. Uma imagem
que instale pacotes com criação automática de cluster tem de ser revista antes
de se tornar candidata; não reparar isso durante o ensaio.

A raiz imutável contém dependências, supervisor/preflight e definição systemd
aprovados. Esses componentes futuros também precisam de inventário e hashes:
não ficam implicitamente aprovados por constarem de uma imagem. O payload de
testes é separado e mínimo, conforme [manifesto](PACOTE_TESTES_MANIFESTO.md).

## Fail-closed e critérios de aceitação

O futuro preflight deve exigir os critérios abaixo antes de qualquer binário
PostgreSQL. Não existe ainda implementação de preflight ou provisionamento.

| ID | Requisito | Evidência independente obrigatória | Estado atual |
| --- | --- | --- | --- |
| V1 | Plataforma/boot aprovados e identificados | Build host efetivo, origem/hash imagem e boot chain, revisão do revisor | Pendente |
| V2 | Zero NICs e apenas loopback guest | Inventário Hyper-V efetivo e interfaces/rotas guest, sem tentar contactar Railway | Pendente |
| V3 | Zero shares/passthrough/canais opcionais | Dispositivos e políticas efetivos host + inspeção guest; canais não observáveis bloqueiam aprovação | Pendente |
| V4 | 2 vCPU/4 GiB fixos e cgroup limitado | Configuração hipervisor, cgroup kernel e membership de todos os descendentes | Pendente |
| V5 | Disco fixo 2 GiB e orçamento host rígido 32 GiB | Tipo/tamanho/alocação/quotas, mounts read-only, tmpfs e logs contabilizados | Pendente |
| V6 | Deadline externo de 180 s por UUID | Design revisto do watchdog e posterior evidência de contenção sem afetar host | Pendente |
| V7 | Runner sem privilégios e sem cluster inicial | UID/grupos, mounts, capabilities e inventário inicial guest sem SQL | Pendente |
| V8 | Pacote/imagen/dependências exatos e aprovados | Comparação de bytes/hashes com manifesto aprovado fora do guest | Só hashes de 3 fontes disponíveis |
| V9 | Lifecycle sem ações sobre terceiros | UUID/discos únicos, autorização por transição e protocolo de ambiguidade | Especificado, não implementado |
| V10 | Logs privados e exportação controlada | ACLs host/guest e extração offline read-only com allowlist, sem partilha gravável | Pendente |

Falha de leitura, campo ausente/null, propriedade não suportada, chave inesperada,
rede/canal partilhado, dependência extra ou limite ausente implica recusa. Não
considerar rede desligada equivalente a adaptador ausente. UUID deve ser gerado
apenas em futuro provisionamento autorizado, nunca aceitar um UUID reutilizado.
Alteração após atestação invalida o estado isolated-attested e a autorização.

A evidência host é obtida pelo plano do hipervisor, a guest por inspeção do SO
antes do ensaio. Nenhuma substitui a outra; ambas ficam vinculadas a run_id,
UUID, horário, hashes e revisor. Ausência de rota ou falha de ping não prova
isolamento. Nenhum destes controlos reais foi consultado nesta fase.

## Descarte e limitações

Após futuro ensaio autorizado, confirmar VM parada externamente; preservar
discos em quarentena se houver erro. Exportar somente ficheiros regulares
aprovados por inspeção offline num ambiente de análise, sem automount do guest
no host da aplicação, sem executar conteúdo e sem canais graváveis. Discos/logs
antigos não são inputs. Eliminação de VM/discos só após autorização específica,
verificando UUID, caminhos e inventário do ensaio; não usar padrões globais.

Não comprovável estaticamente: ausência efetiva de rede/canais, ACLs, integridade
do hipervisor, quotas aplicadas, árvore de processos, watchdog, descarte seguro
e ausência de resíduos. Riscos de escape, administrador malicioso e fuga na
exportação permanecem. A especificação não constitui prova de isolamento real.
