# FI-007.6 — Política proposta de autorização e certificação

Estado: regras executáveis apenas em simulações offline, para revisão do ChatGPT.
Não há alteração de autenticação, esquema, permissões, certificados reais,
exportador, rotas HTTP ou workflows. Nenhuma base foi aberta.

## Inspeção e âmbito

Raiz Git: `C:\Users\javai\OneDrive\Ambiente de Trabalho\SUB-19`;
checkout da aplicação em `ccdr-match-tracker`; branch `feat/campeonato-fpf`,
HEAD `8df6ac4cd3b1a97e8ace53cf0130d5dd41b80445`. Staging inicial vazio.
Alterações pendentes do exportador, FootballIQ e ai-learning são preservadas.
Foi encontrado apenas frontend/AGENTS.md no repositório; as instruções para
escrever Next.js não são acionadas por esta tarefa exclusivamente backend.
O contrato FootballIQ FI-007.3 e as instruções FootballIQ foram lidos.

Lacunas reais identificadas em backend/app:

- auth.py autentica sessões e controla ADMIN/COACH/VIEWER globais, sem pertenças
  a clube/equipa. Não se convertem esses papéis em permissões locais implicitamente.
- models.py não tem Club, pertenças por recurso, revisões operacionais ou
  certificações. Team não tem ainda clube. Não existe legitimidade para preencher
  um scope de produção apenas com IDs recebidos de um cliente.
- match_service.py valida referências e convocatórias, mas get_match procura
  por ID sem filtro de clube/equipa do utilizador.
- live_service.py calcula autogolos e gere transições/eventos; FINISHED não
  certifica completude. Corrigir/apagar eventos altera o resultado derivado.
- footballiq_export.py mantém unknown/unverified e recusa a emissão real. Não
  importa nem utiliza o novo módulo de política; este bloqueio permanece.

## Implementado nesta tarefa vs proposto

| Elemento | Estado |
| --- | --- |
| app/footballiq_policy.py | Funções puras e objetos imutáveis de simulação, sem imports de auth, ORM, exportador ou rede. |
| export_tests/test_footballiq_policy.py | Testes com identidades, clubes, equipas, evidências e versões fictícias. |
| Modelo relacional de pertenças/certificações | Apenas proposto; sem tabelas, migrations ou concessões. |
| Resolução segura de recursos e pertenças | Requisito futuro; não implementado nos endpoints atuais. |
| Revogação em sessões, WebSockets ou exportação | Não alterada; o simulador apenas avalia o snapshot fornecido. |
| Ligação da qualidade ao contrato/exportador | Não implementada; não produz certificados operacionais. |

## Autenticação e autorização

Autenticação responde a quem é o utilizador; autorização decide se essa
identidade pode realizar esta ação sobre este recurso. Principal é apenas
um snapshot sintético de identidade autenticada/ativa, não um token ou login.
O módulo não comprova esses campos se forem fornecidos por um cliente.

Modelo futuro a rever: Club; associação de Team a Club; pertença de sujeito a
clube e TeamRoleBinding por equipa/época. O avaliador recebe Membership efetiva
com source_instance_id, club_id, team_id e season_id exatos, papel, validade e
revogação. O futuro adaptador de autorização tem de verificar a pertença ao clube,
a associação real da equipa e a validade da atribuição antes de construir esse
snapshot. Pertença só ao clube não concede acesso automático a todas as equipas.
Não há herança, wildcard, superutilizador implícito ou permissão real nova.

Matriz de papéis proposta, implementada exclusivamente no avaliador puro:

| Permissão | reader | recorder | reviewer | exporter |
| --- | --- | --- | --- | --- |
| matches:read | Sim | Sim | Sim | Sim |
| events:create | Não | Sim | Não | Não |
| events:correct | Não | Não | Sim | Não |
| results:certify | Não | Não | Sim | Não |
| statistics:certify | Não | Não | Sim | Não |
| matches:export | Não | Não | Não | Sim |

Uma identidade pode ter atribuições independentes; nenhuma é criada pela função.
Exportar não implica certificar, e certificar não implica exportar. REVIEWER pode
corrigir e certificar na proposta inicial: exigir duas pessoas ou impedir
revisão do próprio trabalho é uma decisão pendente, não uma garantia existente.

### Negação por omissão e prevenção de manipulação de IDs

A função evaluate_permission exige at com timezone e só permite quando:

1. Principal é tipado, autenticado e ativo.
2. A permissão é conhecida e existe uma pertença efetiva do mesmo sujeito.
3. Instalação, clube, equipa e época coincidem exatamente com ResourceScope.
4. valid_from <= at, at < expires_at se existir e at < revoked_at se existir.
5. O papel inclui explicitamente a ação solicitada.

Permissões desconhecidas, papéis globais, pertenças ausentes/ambíguas ou campos
booleanos inválidos não ampliam o acesso. IDs duplicados de Membership fazem
negar o snapshot, evitando combinar versões contraditórias da mesma pertença.

No futuro backend, resolver clube/equipa/época pelo recurso guardado no servidor,
não por campos do pedido; procurar eventos por event_id E match_id, validar
jogadores/convocatórias e aplicar também o scope do jogo. Um ID válido de outra
equipa deve continuar inacessível. Os testes puros demonstram a comparação de
scopes, não que os endpoints de produção já façam esta resolução.

### Revogação

Uma pertença revogada deixa de valer no próprio instante revoked_at. Expiração
é igualmente exclusiva. Uma segunda atribuição distinta ainda válida pode
continuar a conceder a ação: para revogar todo o acesso, revogar todas as
atribuições aplicáveis ou desativar a identidade/pertença ao clube.

Recarregar o estado de autorização em cada operação futura; PermissionDecision
não é uma capacidade reutilizável. Antes de entregar uma exportação/cache,
revalidar permissões atuais. O snapshot REPEATABLE READ dos dados não pode
servir de prova de que uma autorização não foi entretanto revogada. É necessária
uma verificação de autorização recente, distinta desse snapshot, e uma política
explícita para operações em curso e WebSockets. Nada disso foi ligado nesta tarefa.

Revogar o certificador impede novas avaliações, mas não apaga o histórico de
avaliações feitas quando tinha autoridade. Suspeita de certificação indevida
exige invalidação auditada explícita; não reescrever silenciosamente o passado.

## Categorias de certificação

CertificationState identifica scope, match_id, categoria, estado, versão de
conteúdo e histórico. Não é uma linha SQLAlchemy nem certificado autenticado.

| Categoria | O que a revisão deve comprovar futuramente |
| --- | --- |
| result | Resultado final e proveniência: reconciliação por eventos, captura oficial ou revisão manual verificável. |
| score_events | Todos os golos e autogolos dos dois lados, sem duplicados e com atribuição correta. |
| shots | Recolha completa de remates à baliza, fora e bloqueados dos dois lados; golos não criam remates. |
| cards | Recolha completa de amarelos/vermelhos; não inferir cartões/expulsões ausentes. |
| substitutions | Entradas/saídas, identidade e tempo registados; não inferir minutos jogados da convocatória. |
| squad | Convocatória e titularidade da equipa autorizada; não significa formação válida ao longo de todo o jogo. |
| other_events | Recolha dos restantes acontecimentos contratados nos dois lados. |
| player_attribution | Autoria das ações da equipa autorizada; inscrições e época corretas. |

Para uma certificação complete de eventos, o âmbito inclui o jogo inteiro e os
dois lados; squad e player_attribution referem-se à equipa autorizada, conforme
contrato v1. Ausência de dados mantém unknown; resultado sem verificação mantém
unverified. Um zero só pode ser considerado factual após recolha completa
revista, não pela existência de uma lista vazia.

Evidence contém tipo, referência e justificação não vazios. AuditEntry conserva
ID do registo, autor, data com timezone, ação, estado anterior/seguinte, versões,
evidência e IDs das pertenças usadas. Scope/jogo/categoria acompanham o histórico
no CertificationState; uma futura persistência deve preservar esse contexto
em cada registo de auditoria. Não exportar dados pessoais ou notas sensíveis
como justificação livre sem política de minimização.

A função não descarrega a evidência, não confirma um regulamento nem verifica a
reconciliação numérica. Esses factos têm de ser estabelecidos pelo futuro serviço
responsável antes de autorizar a transição; uma string de evidência não os prova.

## Transições explícitas

Para categorias estatísticas:

- unknown → partial, complete ou unavailable;
- partial → complete ou unavailable;
- complete → partial ou unavailable;
- unavailable → partial ou complete.

Para resultado:

- unverified → verified, conflict ou unavailable;
- verified → conflict ou unavailable;
- conflict → verified ou unavailable;
- unavailable → unverified.

Toda a avaliação manual exige a permissão específica, evidência tipada, versão
esperada coincidente e cronologia válida. Repetir a mesma certificação não cria
outro evento idêntico: é uma transição inválida. Histórico é append-only em
memória, com estados/versões contínuos, datas ordenadas e IDs de auditoria únicos.

A proposta conservadora exige jogo terminado para complete/verified em qualquer
categoria. FINISHED é necessário mas nunca suficiente. Certificar convocatória
antes do jogo, auditoria por categoria mais fina e separação entre revisor e
registador são decisões a rever antes da integração real.

Para result verified por eventos, exigir também CertificationState de golos
complete do mesmo scope, jogo e versão, sem avaliação posterior à do resultado.
Captura oficial ou revisão manual podem verificar apenas o resultado; não
certificam implicitamente golos individuais, remates ou outras categorias.

## Correções, versões e histórico

**content_version desta política não é data_version do exportador.** É uma
revisão proposta dos dados operacionais relevantes, excluindo a própria
certificação/qualidade e auditoria. Vincular o certificado ao hash de exportação
que já inclui qualidade criaria um ciclo: certificar mudaria o hash e invalidaria
o próprio certificado. O formato/cálculo/persistência desta revisão operacional
ainda precisa de desenho e aprovação; aqui só se usam tokens sintéticos.

Uma alteração relevante de jogo/eventos/convocatória deve mudar content_version.
A política inicial invalida conservadoramente todas as categorias dessa versão,
mesmo que uma alteração pareça localizada. Evidência seletiva por categoria
poderá reduzir invalidações no futuro, mas não é assumida nesta implementação.
Alterações só de certificação mudam data_version/snapshot_version de exportação
quando houver integração, sem mudar a revisão operacional a que se referem.

invalidate_for_correction recebe uma correção já autorizada pelo serviço dono
dos dados, nova versão, autor, data e referência da alteração. Não autoriza nem
executa essa correção. Devolve unknown/unverified com novo evento de invalidação
e mantém os eventos anteriores. Não exige que o certificador antigo ainda tenha
permissões para retirar validade a um certificado desatualizado.

effective_status devolve unknown/unverified para versão diferente ou para um
certificado final de jogo reaberto. Assim, falta de persistência imediata de
uma invalidação não deve permitir reutilizar complete/verified. Antes de qualquer
integração, controlo de versão e gravação da avaliação devem ser atómicos com
as alterações relevantes. A função pura não fornece essa atomicidade.

O armazenamento futuro deverá conservar registos de correções, versões anteriores,
invalidations e avaliações novas, em vez de substituir o autor/evidência antigos.
Não existe persistência nem garantia contra adulteração nesta tarefa.

## Testes offline e limites

Os novos testes ficam em backend/export_tests, fora do conftest de backend/tests
que cria schemas/migrações. Testam matriz de permissões, negação por omissão,
revogação/expiração, identidades de outras equipas, categorias independentes,
transições inválidas, evidência, controlo de versão, correções, cadeia de auditoria,
repetibilidade e importação sem infraestrutura.

As funções não são chamadas pelo auth.py ou pelo exportador. Logo, os testes
não demonstram isolamento multi-clube na aplicação atual, nem certificam dados
reais, nem desbloqueiam emit_authorized_package.

## PostgreSQL descartável em GitHub Actions: proposta, sem workflow alterado

Inspeção local: não existe .github/workflows na raiz Git SUB-19 nem na pasta
ccdr-match-tracker; git ls-files não encontrou workflows nesses locais.
Isto não afirma nada sobre estado remoto ou CI configurado fora do checkout.

É viável preparar um job num runner Linux GitHub-hosted com serviço PostgreSQL
descartável, como descrito na [documentação oficial GitHub](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers).
O workflow teria de viver em SUB-19/.github/workflows e configurar working-directory
para ccdr-match-tracker/backend, não na raiz Git FootballIQ.

Plano proposto para uma tarefa própria aprovada:

1. Serviço PostgreSQL de versão explicitamente fixada, healthcheck e base de
   testes exclusiva. Sem credenciais/URLs operacionais, volumes de produção,
   secrets de deploy ou leitura de .env. Não usar footballiq_dev.
2. Preparação apenas no serviço efémero autorizado; schemas exclusivos por teste
   ou worker, search_path explícito, fixtures inteiramente sintéticas e referências
   a clubes/equipas fictícios. Migrações, se necessárias, só no alvo novo autorizado.
3. Separar role de preparação e role de leitura; comprovar READ ONLY e isolamento
   efetivo na ligação do exportador, capturando apenas evidência sanitizada.
4. Dois clientes sincronizados por barreiras, não sleeps: ler seleção, corrigir
   evento com commit concorrente, prosseguir detalhes e confirmar snapshot antigo
   coerente; nova exportação deve refletir a correção e novas versões.
5. Testar revisão da versão entre pedido de certificação e gravação: recusar
   avaliação obsoleta. Testar revogação entre seleção e entrega: impedir acesso
   apesar de os dados continuarem coerentes no snapshot antigo.
6. Testar equipas/clubes alheios, jogos reabertos, golos/autogolos, convocatórias,
   all/single, limite antes de joins e revalidação por DTOs reais FootballIQ.
7. Para testes cruzados, obter o consumidor numa revisão explicitamente fixada;
   não assumir que alterações locais sem commit estão disponíveis no CI. A revisão
   FootballIQ FI-007.4 terá de ser disponibilizada antes desse job ser reproduzível.
8. Contar setup, testes simulados, integração real e testes ignorados separadamente;
   falha de preparação não é validação bem-sucedida. Descarte pelo lifecycle do
   serviço CI; sem comandos contra bases nomeadas fora desse ambiente.

Nenhum destes passos foi executado. A ausência de PostgreSQL descartável
autorizado local continua a impedir a validação real da FI-007.5.1.

## Decisões pendentes para revisão do ChatGPT

- Aprovar matriz de papéis e quem administra pertenças, sem bootstrap global implícito.
- Definir Club e relação com equipas, validade por época e revogação de todo o clube.
- Aprovar separação de funções e eventual regra de duas pessoas na certificação.
- Definir evidências aceites, retenção, correção de certificações indevidas e privacidade.
- Definir revisão operacional, invalidação por categoria e atomicidade na persistência.
- Definir reautorização de entregas concorrentes, sessões/WebSockets e caches.
- Aprovar e disponibilizar testes PostgreSQL no CI em ambiente exclusivamente descartável.

Aguardar revisão antes de ligar a política à produção ou alterar o schema.