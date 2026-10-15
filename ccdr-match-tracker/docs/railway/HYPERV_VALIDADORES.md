# Hyper-V: correspondência de mecanismos e contrato dos validadores

## Contratos de dados e fixtures documentais

Ver [schemas normativos 2.0.0](VALIDADORES_SCHEMAS.md) e
[fixtures sintéticas](VALIDADORES_FIXTURES.md). Especificam envelope/evidência
fechados, sete bodies, relatório consolidado e recusas; nenhum parser/validador
foi implementado ou executado. Validade estrutural nunca equivale a prova de
isolamento. A fase documentary e qualquer fixture sintética impõem NÃO APTO.
As regras mais específicas de contexto/freshness/ordem desses contratos
complementam este desenho e não autorizam operações reais.
As [correções P1–P10](VALIDADORES_CORRECOES_P1_P10.md) são normativas para
identidades, prazos, fontes, referências, DAG e resultados. Não aceitar envelopes
1.0.0 como 2.0.0. O mapping nativo do build continua não aprovado.
R2 (segunda revisão documental) substitui o primeiro rascunho 2.0.0 pelo conteúdo
normativo exato, a fixar por hashes externos antes de qualquer aprovação.
ArtifactBinding não se aplica a observações/qualificações; usar HistoricalQualification
e QualificationApplicability com revisão do destino e checkpoints próprios.

**NÃO APTO.** Apenas revisão estática dos cinco documentos de arquitetura.
Nenhuma consulta Hyper-V, administração, rede, VM, processo, SQL ou teste foi
executada. Não houve pesquisa externa. Os nomes de interfaces/propriedades
abaixo são alvos de mapeamento para futura verificação na versão suportada,
não funcionalidades confirmadas neste host nem comandos para executar.
Campos não disponíveis/observáveis devem produzir UNKNOWN e bloquear, não PASS.

## Matriz requisito → mecanismo → verificação → evidência → recusa

Classificação: S = estática; H = host; G = guest; E = ensaio controlado futuro.

| ID / requisito | Mecanismo concreto ou dependência | Método futuro de verificação | Evidência exigida | Condição de recusa / classe |
| --- | --- | --- | --- | --- |
| H01 Zero NICs | Inventário de adaptadores sintéticos/legados e dispositivos atribuídos da VM no Hyper-V | Enumerar dispositivos efetivos por VMId, não só a configuração desejada | Inventário completo zero NICs, UUID e horário + interfaces guest | NIC desligada também recusa; inventário incompleto recusa / H,G |
| H02 Zero switches associados | Vínculos dos adaptadores a switches virtuais | Correlacionar todos os vínculos com H01 | Zero vínculos para a VM | SwitchId/vínculo inesperado ou oculto / H |
| H03 Integração opcional desativada | Inventário Hyper-V Integration Services, incluindo file-copy, shutdown, heartbeat, KVP, time sync e backup/VSS quando disponíveis | Mapear IDs estáveis e estado efetivo; cruzar daemons/drivers guest | Lista exaustiva aprovada, canais opcionais disabled, sem serviço desconhecido | Nome traduzido não é identificação suficiente; missing/unknown/enabled recusa / H,G |
| H04 Enhanced Session | Política de Enhanced Session do host e modo efetivo VMConnect | Verificar política aplicável e sessão básica, sem mudar política global | Configuração e modo real; revisão do caminho de redirecionamento | Sessão melhorada/redirecionamento possível não controlado ou estado desconhecido / H,E |
| H05 Clipboard/transferência | Ausência de Enhanced Session/RDP redirection/file-copy; controlos específicos do cliente de consola | Inventariar cliente, canais, drives/clipboard/devices redirecionados | Zero redirecionamentos, consola apenas básica autorizada | Desativar um Integration Service não prova isto; qualquer canal extra recusa / H,G,E |
| H06 HV sockets/relays/execução cruzada | VMBus/HV sockets/vsock, agentes e serviços host; não há aqui um botão global por VM comprovado | Inventariar endpoints, serviços registados, permissões e agentes na versão alvo | Mapa de transporte/endpoint com prova de ausência ou bloqueio efetivo | Não observável/bloqueável mantém bloqueio; ausência de NIC não basta / H,G,E |
| H07 Dispositivos e discos exatos | Inventário de controladores, DVD/ISO, VHDX, COM pipes, passthrough/DDA/GPU e dispositivos adicionais | Comparação exata com allowlist por identidade/controlador/slot/hash | Só boot ISO, payload ISO, work VHDX e hardware mínimo aprovado | Disco/ISO adicional, pass-through, pipe, parent disk ou dispositivo desconhecido / H,G |
| H08 Geração 2 / Secure Boot | Propriedades de geração/firmware Hyper-V e trust template aplicável a Linux | Cruzar geração, SecureBoot efetivo, template e cadeia da imagem | Firmware config + imagem/kernel/shim assinados e hashes aprovados | Gen diferente, Secure Boot off/template desconhecido, cadeia incompleta / S,H,G,E |
| H09 Memória fixa | Configuração de memória: DynamicMemoryEnabled e Startup RAM, mais estado efetivo | Exigir dynamic=false e 4294967296 bytes; confirmar sem ballooning | Configuração efetiva e memória guest | Valor divergente ou apenas valor desejado / H,G |
| H10 CPU | Virtual processor Count=2 e limite relativo à capacidade atribuída; cgroup CPUQuota guest | Interpretar unidades/semântica do build e cruzar CPU guest | Perfil 2 vCPU, limite definido, cgroup 200% e sem delegação ao runner | Maximum=100 não é quota de disco nem tempo; propriedade/unidade ausente recusa / H,G,E |
| H11 Work limitado | VHDX fixed de 2147483648 bytes, sem parent/checkpoint; ext4 guest | Validar tipo, tamanho, parent chain, inventário e mounts | Volume próprio e limites/mounts efetivos | Discos dinâmicos/differencing/parent desconhecido e mounts extra / H,G |
| H12 Orçamento host 32 GiB | **Externo ao limite do VHDX:** quota rígida/volume exclusivo para todos os artefactos | Provar backend, contabilização e comportamento ao limite | Quota aplicada a imagens, RAM state, configs, logs, evidências e snapshots proibidos | Apenas espaço livre/NTFS quota por utilizador não demonstra quota por ensaio; backend null recusa / H,E |
| H13 Deadline/encerramento externo | **Supervisor externo**, relógio monotónico, vínculo ao VMId e política Hyper-V de estado | Validar autorização, deadline e estado Off, não Saved/Paused | Histórico por UUID; confirmação externa de fim; não depender do shutdown guest | Timeout, falha do supervisor ou ausência de Off confirmado = UNKNOWN/recusa / S,H,E |
| H14 Identidade/lifecycle | VMId GUID Hyper-V + identidade da instância host + run_id e hashes externos | Correlacionar inventário e transições; nome/PID nunca são autoridade | Registro imutável/revisor, UUID não reutilizado, sem reassociação | UUID/host/disk/hash divergente, clone importado/replay/drift / S,H,E |
| H15 Descendentes | Fronteira VM para host; **cgroup v2/systemd guest** para árvore runner | Verificar cgroup e kernel membership; encerramento externo da VM é última contenção | Árvores/cgroup e estado VM observados independentemente | Processos fora do cgroup, capacidade de escape/delegação ou limpeza não confirmada / G,H,E |
| H16 Sem acesso Railway | **Proposta normativa: H01–H08**, mais pacote/imagem/exportador, sem segredos/passthrough/relay; nenhum controlo único | Revisão cruzada host/guest/manifesto e integridade da imagem/boot, sem sondar produção | Dois planos de evidência e aprovação humana explícita deste âmbito conservador | H16 UNKNOWN enquanto âmbito não aprovado; DNS/ping falhado não prova isolamento; canal/credencial/ambiguidade recusa / S,H,G,E |

Existirem switches no host para outras VMs não é motivo para os modificar ou
apagar. H02 exige zero associações à VM do teste. Inventários não devem divulgar
configuração de terceiros além do estritamente necessário para demonstrar ausência
de associação. Nenhuma operação global de host é autorizada por este contrato.

## Incompatibilidades e pressupostos por resolver

1. **Zero comunicação guest/host literal é incompatível com virtualização.**
   Display, storage, firmware, hypercalls e drivers sintéticos são necessários.
   Proíbem-se canais opcionais e redirecionamentos; VMBus não pode ser simplesmente
   equiparado a file-copy. Exigir zero VMBus tornaria esta arquitetura inviável.
2. Desativar Integration Services não descarrega todos os drivers/transportes
   guest nem garante bloquear HV sockets. PowerShell Direct não deve ser presumido
   disponível em Ubuntu nem considerado a única forma de execução cruzada.
   A ausência dos endpoints relevantes permanece sem mecanismo comprovado.
3. Enhanced Session tem dimensão host/cliente. Não se pode impor mudança global
   neste host como efeito lateral de criar uma VM. Se o perfil só puder ser
   garantido mudando globalmente políticas de terceiros, requer host dedicado
   e nova revisão. Não usar a simples ausência de RDP no guest como prova.
4. Com integração shutdown/heartbeat desativada, esses serviços não podem ser
   usados para cleanup/atestação. O watchdog tem de obter estado pelo hipervisor
   e poder encerrar somente a VM autorizada; não requer agente dentro dela.
5. Secure Boot não prova integridade de rootfs, dependências ou ausência de segredos.
   Um ISO Ubuntu normal de instalação não é a imagem read-only mínima proposta.
   A cadeia completa e o boot imutável ainda têm de ser desenhados/aprovados.
6. Não há mecanismo Hyper-V único para orçamento total de armazenamento, prazo
   global, cgroups, sanitização de logs ou manifesto. São componentes externos,
   ainda não implementados; valores declarados não contam como limites aplicados.
7. Fixar RAM não impede RAM-state/config/logs no host. Quota deve contemplar
   artefactos do hipervisor fora da pasta work e pressupostos de caminho reais.
8. **Atestação guest externa antes dos testes sem canal de retorno** não está
   resolvida. Propõe-se uma fase de boot só de preflight, parada e extração offline
   autorizadas, seguida de revisão e nova fase autorizada com preflight local.
   Um boot novo pode divergir do anterior: exige vínculo à imagem/configuração
   e nova verificação host. Esse fluxo não prova atestação contínua do guest.
   Se for exigida evidência independente síncrona antes de cada operação, falta
   um canal aprovado ou reformulação do requisito; manter bloqueio, não o omitir.
9. Não há prova absoluta contra administrador/hipervisor comprometido ou exportador
   malicioso. Os validadores são planos distintos de observação, não raízes de
   confiança independentes se todos correrem no mesmo host comprometido.

## Contrato comum dos validadores — sem implementação

Sete validadores, nenhum com permissão para reparar, provisionar, executar teste,
desligar VM ou alterar quota/configuração. Coletores futuros recolhem evidência
de leitura sob autorização própria; validadores avaliam essa evidência e a política.

Entrada: contrato versionado e aprovado externamente, inventários tipados, hashes,
run_id, host_instance_id, VMId, image_hash, configuration_hash, horário e origem
do coletor/revisor. Registo guest inclui boot_id; boot_id sozinho é autodeclaração.
Schemas fechados, tipos/unidades explícitos; propriedades/IDs desconhecidos,
valores null, chaves duplicadas, erro de parsing/coleta, falta de permissões,
truncagem do inventário e evidência de outro boot/host impedem aprovação.
Validadores devem tratar entradas como dados não confiáveis, sem eval, execução
de imports do payload, resolução de URLs ou comandos embutidos.

Saída proposta R2: LocalResult imutável com implementação/hash/schema/coletor,
Invalidation separada e FinalResult novo, ambos com âmbito/contexto assinados.
PASS local histórico não é PASS final após uma ref ser rejeitada.
FAIL/UNKNOWN/NOT_EVALUATED bloqueiam consumidores finais. Não incluir valores
secretos, outputs brutos ou texto de exceção. PASS só para o âmbito do validador;
FAIL ou UNKNOWN bloqueiam o gate. Todos PASS não autorizam executar: exige revisão
externa e autorização dirigida à execução/VM. Aprovação não é autorreferente.

Para freshness aplicam-se as seis classes temporais do contrato 2.0.0.
Artefactos imutáveis e factos históricos não têm o TTL de estado volátil. Cada
boot/controlo exige identidade e captura apropriadas; qualificação histórica
admitida não se converte em estado atual. Revisão não renova a data da captura.
Qualquer drift invalida atestação; política temporal ainda requer aprovação.

| Validador | Entradas/decisões específicas | Casos de recusa obrigatórios |
| --- | --- | --- |
| VAL-HOST | Configuração efetiva H01–H10/H14, dispositivos e canais completos do build aprovado | NIC extra/desligada, vínculo de switch, integração enabled/unknown, sessão/canal não aprovado, disco/device extra, Secure Boot incorreto, build sem mapping |
| VAL-MANIFESTO | Árvore integral e hashes contra allowlist externa; separar payload/control; ficheiros regulares exatos, sem extrair paths inseguros | Hash divergente/ausente, ficheiro extra/em falta, duplicate/case/Unicode ambíguo, symlink/hardlink/reparse/ADS, path traversal, hash do próprio manifesto não aprovado |
| VAL-ARTEFACTOS | Imagem, cadeia boot, SBOM/lock Linux transitivo, ABI, bibliotecas/wheels, supervisor/preflight | Dependência/binário não aprovado, origem/hash sem aprovação, sdist/build inesperado, intervalo de versão em vez de lock, serviço/cluster pré-instalado ativo |
| VAL-GUEST | Evidência de interfaces/rotas, mounts, UID/capabilities, serviços, env names, cgroup e baseline; fase sem SQL | Interface não loopback, rota não local, mount/serviço extra, PG*/Railway herdados, root/sudo/capabilities excessivas, preflight não aprovado ou evidência não independente |
| VAL-RECURSOS | Configuração host+cgroup+volume/quota+watchdog; limites H09–H13 e todos os destinos contabilizados | Quota ausente/não aplicada, VHD dinâmico, disco extra, CPU/RAM/TasksMax ausentes ou divergentes, limite só documental, deadline/watchdog sem prova |
| VAL-LIFECYCLE | Identidades aprovadas e transições, autorização por fase, vínculo VM/discos, confirmação externa de encerramento | UUID divergente/reutilizado, hash/host/boot divergente, transição sem autorização, Saved/Paused em vez de Off, timeout sem confirmação externa, resíduos atribuídos só por PID-file |
| VAL-EXPORTACAO | Autorização e allowlist de saída separadas, VM parada, snapshot de evidência offline, parsers/armazenamento aprovados | Exportação não autorizada, VM ativa, raw/log/dump extra, segredo suspeito, path/link/stream inesperado, tamanho excessivo, destino não privado, tentativa de montar no host da aplicação |

## Casos de aceitação/rejeição a especificar em fixtures futuras

Sem código nem execução nesta fase. Para cada validador: uma fixture positiva
completa e casos negativos independentes, sem credenciais reais. A fixture
positiva só comprova a regra do parser, nunca segurança real do ambiente.

- R01 NIC inesperada ou detached: FAIL VAL-HOST; R02 canal KVP/file-copy/vsock
  não aprovado ou não enumerado: FAIL/UNKNOWN; R03 disco/ISO/pipe adicional: FAIL.
- R04 hash de um dos três fontes divergente: FAIL VAL-MANIFESTO; R05 ficheiro
  adicional num subdiretório ou stream: FAIL; R06 transitiva extra: FAIL VAL-ARTEFACTOS.
- R07 quota backend ausente/não aplicada ou prova de capacidade confundida com
  quota: FAIL/UNKNOWN VAL-RECURSOS; R08 UUID errado: FAIL VAL-LIFECYCLE.
- R09 timeout com estado final não confirmado: UNKNOWN e bloqueio, não cleanup
  genérico; R10 inventário parcial/erro de acesso: UNKNOWN; schema/versão
  desconhecidos: FAIL estrutural, sem fallback. Ambos bloqueiam consumidores.
- R11 tentativa de exportar raw, credenciais ou path não autorizado: FAIL e
  quarentena, sem imprimir conteúdo; R12 drift após PASS: invalidar aprovação.
- R13 false/zero ausentes convertidos em defaults permissivos, tipos string em
  vez de boolean, overflow/unidades erradas e duplicate keys: FAIL de schema.
- R14 pacote tenta declarar a própria aprovação ou UUID de outra execução:
  FAIL de origem/identidade; R15 evidência guest do boot anterior: UNKNOWN.

## Importação e exportação sem rede: proposta e autorizações

**Importação futura:** preparar pacote/controlo em ambiente de build separado,
gerar ISO read-only e verificar hashes fora do guest. Com autorização explícita
de provisionamento/associação, anexar apenas ISO aprovado à VM desligada por
UUID. Nenhum shared folder/file-copy/agente é permitido. O ISO de boot é separado.
Verificar ISO e árvore dentro do guest em preflight; não instalar dependências.
O plano não cria nem associa ISO nesta fase. Imagem e ISO são canais de entrada
intencionais, finitos e read-only, não uma alegação de zero fluxo de informação.

**Exportação futura:** só após autorização específica e estado Off confirmado,
preservar work VHDX original em quarentena, calcular hashes sob escopo autorizado
e produzir cópia offline de análise. A leitura do original pode exigir locking
host e armazenamento privado; nada disso está implicitamente autorizado.
Inspecionar a cópia numa segunda VM/appliance offline de análise, com imagem e
parser aprovados, sem montar filesystems guest no host da aplicação e sem
executar ficheiros convidados. Storage read-only e noexec/nodev/nosuid são defesa
adicional, não prova de segurança do parser. A appliance também necessita de
arquitetura/recursos/canais revistos: ainda não existe.

Extração só de JSON regular e limitado previamente autorizado, com schema e
hashes, para media/disco de saída novo, dedicado e finito. Esse dispositivo é
um **canal de saída explicitamente autorizado da appliance**, nunca um volume
partilhado permanente da VM de teste. Antes de o conteúdo chegar ao host,
validar allowlist, paths, tamanho e segredos; brutos permanecem em quarentena.
Se não existir caminho de extração com parser/ACL/contenção aprovados, recusar
exportação. Não substituir por clipboard, screenshot indiscriminado, rede ou
file-copy. Retenção, cópia, associação de discos e descarte são ações separadas
que exigem escopo e autorização; não apagar evidências para obter conformidade.

Riscos: filesystem hostil explora parser, cópia afeta integridade da evidência,
logs sanitizados ainda contêm segredos, extração cria um novo canal de exfiltração,
disco residual ou quota ultrapassada. Hash prova bytes iguais, não benignidade;
revisão humana não elimina riscos. O desenho do exportador é bloqueio pendente.

## Classes de prova e critérios de decisão

| Classe | Pode demonstrar | Não pode demonstrar |
| --- | --- | --- |
| S — estática | Coerência do contrato, allowlists, hashes locais, regra de recusa e dependências descritas | Configuração aplicada, ausência de canais, quota ou estado real |
| H — host, autorização própria | Dispositivos/estado/VMId/memória/discos/quota/watchdog observados no hipervisor/SO | Integridade completa do guest nem ausência de drift posterior |
| G — guest, autorização própria | Interfaces/mounts/UID/cgroups/pacotes vistos no kernel guest | Autenticidade do host ou independência da própria observação |
| E — ensaio controlado, autorização própria | Aplicação real de limites, falha/timeout, descendants, boot, exportação e lifecycle nos casos testados | Garantia universal contra todas as corridas, bugs e administradores |

Aceitação exige S coerente + H/G completos da mesma execução + controlos E
previamente demonstrados sob autorização separada e critérios V1–V10 satisfeitos.
Nenhuma evidência ausente pode ser substituída por um mock PASS ou por documentação.
O procedimento para demonstrar E sem executar os oito testes deverá ser desenhado
como validação de infraestrutura separada; não está autorizado nesta fase.

Próxima etapa segura: especificar schemas fechados e fixtures documentais para
os sete validadores; obter posteriormente documentação offline oficial do build
alvo e revisão independente do mapping, sem consultas administrativas. Não
implementar/provisionar/executar nem solicitar ensaio real agora.
