# FI-007.5 — Núcleo de exportação Match Tracker → FootballIQ

O serviço interno está em `backend/app/footballiq_export.py`. Não há endpoint,
comando de exportação operacional, migração, escrita, LLM ou alteração do
FootballIQ. A emissão de um pacote completo para consumo real continua bloqueada
por falta de autorização por recurso. Isto é uma limitação explícita, não uma
permissão concedida por um team_id ou pelo papel ADMIN.

## API interna e fronteira de confiança

| Objeto/função | Responsabilidade |
| --- | --- |
| ExportSettings(source_instance_id, timezone) | Configuração explícita e estável da instalação; não lê .env nem cria credenciais. |
| ExportSelection(team_id, season_id, as_of, competition_scope, competition_id) | IDs internos positivos, instante com offset e filtros explícitos. Não autentica o âmbito. |
| recent_matches_query(selection) | Constrói um SELECT PostgreSQL parametrizado, sem o executar. |
| read_export_draft(engine, selection, settings, exported_at=...) | Leitura numa ligação/transação própria, consistente e só de leitura; não chama get_engine/get_settings. |
| build_export_draft(...) | Adaptação pura de objetos ORM previamente lidos; sem mutações ou pedidos adicionais à base. |
| ExportDraft | Conteúdo sem authorized_scope e sem snapshot_version de pacote; inclui selection_version e authorization_blocker. |
| compute_snapshot_version(draft, declared_scope) | Hash com âmbito declarado; verifica integridade do rascunho mas não autentica nem emite um pacote. |
| emit_authorized_package(...) | Recusa sempre com AuthorizationUnavailable, antes de qualquer leitura. |

Só código interno confiável poderá usar o leitor: o rascunho contém dados que
não devem ser servidos a clientes arbitrários. A função não transforma um
team_id recebido de um utilizador em acesso autorizado. Não há fábrica de
scopes de produção nem argumento booleano que contorne o bloqueio de emissão.

Um hash identifica conteúdo, mas não prova quem o produziu ou quem o pode ler.
O scope deve vir futuramente de uma política verificável de autorização, não
do JSON do cliente. Os testes usam exclusivamente `fictional-test-scope` e
`fictional-test-club`; estes valores não são identidades reais nem permissões
registadas na aplicação.

## Seleção e leitura consistente

1. Equipa, época, opção all/single e as_of são obrigatórios. competition_id só
   existe em single; nenhuma época/equipa é inferida de roster.py.
2. Filtrar Match.team_id, season_id, estado FINISHED e kickoff_at <= as_of.
   Não incluir jogos em que a equipa apenas surge como opponent_id: a perspetiva
   dos eventos e convocatórias seria outra.
3. Ordenar kickoff_at DESC, Match.id DESC; LIMIT 5 no SELECT inicial. IDs internos
   são numéricos, logo 10 precede 9 com kickoff igual.
4. Em single, filtrar com EXISTS sobre CompetitionFixture. Sem join multiplicador
   de fixtures, sem selecionar resultados externos como novos jogos internos.
5. Só depois carregar eventos, convocatórias e fixtures dos IDs selecionados;
   carregar as inscrições e competições necessárias ao adaptador. Com zero
   jogos, não executar consultas aos detalhes.
6. O adaptador valida ligações competitivas contra época, equipa interna,
   casa/fora e jornada. Ligações ambíguas/desatualizadas são erros explícitos.
7. Não remover o quinto jogo incompleto nem procurar um sexto para melhorar
   estatísticas. O núcleo puro recusa mais de cinco jogos e jogos fora de ordem.

O leitor recebe uma Engine PostgreSQL explícita, configura REPEATABLE READ antes
de iniciar a transação e emite SET TRANSACTION READ ONLY antes dos SELECTs.
A Session é local, com autoflush=False e join_transaction_mode=rollback_only,
ligada à transação externa do leitor; não confirma a transação nem recebe
objetos pendentes de outra Session. A transformação ocorre antes de fechar o
snapshot. Exceções encerram os contextos e não devolvem um pacote parcial.

Estes controlos são transacionais, não DDL nem alterações de permissões.
O desenho segue a configuração de isolamento antes da transação descrita na
[documentação SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html).
Ainda falta verificar o comportamento com um PostgreSQL descartável autorizado;
os testes desta tarefa verificam SQL compilado e orquestração simulada.

## Mapeamentos do contrato v1

- IDs são convertidos para strings decimais da origem; não correspondem a IDs
  FootballIQ. source_system=match_tracker; source_instance_id vem de configuração.
- Match.team_id é a equipa analisada. is_home determina home_team/away_team e
  a conversão do resultado interno US/OPPONENT para casa/visitante.
- Match.kickoff_at é convertido para UTC com Z; timezone é a zona IANA de
  apresentação explicitamente configurada. Datas sem offset são rejeitadas.
- CompetitionFixture.internal_match_id resolve competition_id; sem ligação,
  null em all. O fixture é preservado como external_reference tipada.
- Eventos conservam ID, tipo, período, elapsed_seconds e jogadores. minute é
  elapsed_seconds//60, sem fabricar notação 45+2 nem minutos de utilização.
- EventTeam.US torna-se Match.team_id; OPPONENT torna-se opponent_id. O tipo
  OWN_GOAL continua a referir a equipa que o pratica; o beneficiário inverte-se
  na regra reutilizada de live_service.score(). Não são inferidas assistências.
- MatchSquad gera convocatória com ID, inscrição e is_starter. Sem registos,
  squad=null: não se certifica que ninguém foi convocado.
- Inscrições ligadas aos eventos devem existir, pertencer à equipa/época e
  constar da convocatória. IDs ausentes ou contraditórios fazem falhar a adaptação.
- Não são exportados notes, recorded_by_id, credenciais, emails, fotografias
  ou outros campos alheios ao contrato. Nomes existentes só entram nas referências
  de equipas/inscrições; nenhum nome/ID pessoal é inventado.

## Qualidade e resultados: limites reais

Todas as sete categorias são unknown, com evidence=null e assessed_at=null.
O estado FINISHED não demonstra recolha completa. A mera presença de eventos
ou convocatórias também não demonstra que todos os acontecimentos foram registados.

O resultado usa live_service.score(), incluindo autogolos, mas fica unverified,
method=events e verified_at=null. Havendo golos registados, preservam-se as
contagens observadas e os IDs dos eventos como proveniência; não são usados
como resultado competitivo pelo FootballIQ. Sem golos registados, os dois
valores são null: uma lista vazia não certifica um 0–0.

Não há hoje um processo persistido para certificar partial/complete nem para
verificar um resultado manual/oficial no exportador. Por isso o núcleo não
oferece overrides de qualidade e não transforma a captura FPF em certificação
implícita do jogo interno. A cobertura competitiva do consumidor pode permanecer
0/N; isso é esperado e evita números não sustentados.

Para emitir partial/complete ou score verified será necessário aprovar a fonte
de evidência, o responsável e o processo de verificação. Não foi criado esse
processo ou uma nova coluna/migration nesta tarefa. updated_at permanece null;
created_at e exported_at não são substitutos de uma data de alteração real.

## Versões determinísticas

Canonicalização local v1: JSON com chaves ordenadas, UTF-8, ensure_ascii=False,
separadores sem espaços e allow_nan=False. Prefixo sha256: seguido do digest.
Os arrays são serializados na ordem contratual: jogos por kickoff/ID, eventos
por período/tempo/ID e convocatória por ID.

- data_version: hash do conteúdo do jogo antes de acrescentar data_version,
  envolvido por hash_version=1, sistema e instalação. Inclui resultado observado,
  eventos, convocatória, nomes exportados, kickoff, qualidade e ligação competitiva.
- selection_version: hash do conteúdo do rascunho, excluindo exported_at. Serve
  apenas para inspeção do núcleo; não é snapshot_version de um pacote autorizado.
- snapshot_version: hash de hash_version=1, sistema, instalação, scope declarado,
  selection e sequência de pares ID/data_version. Só é montado num pacote completo
  nos testes com scope fictício; a emissão real continua bloqueada.

A hora de exportação não entra nos hashes. Corrigir/apagar eventos, mudar
convocatória, kickoff ou nomes exportados altera a versão correspondente.
Campos não exportados, como notas livres, não integram este contrato.
Reabrir/cancelar/eliminar um jogo exige refazer a seleção completa e pode trazer
outro jogo para a janela. As versões dos jogos restantes não mudam sem motivo.
O cálculo de snapshot deteta um rascunho alterado depois do cálculo dos hashes.
Nenhuma versão é gravada em tabelas nesta implementação.

## Testes seguros e fixture fictícia

Os novos testes estão em backend/export_tests, separados de backend/tests,
cujo conftest contém criação de schemas e migrações. Usam ORM transitório,
PostgreSQL SQL compilation e fakes. As tentativas de ligação real são bloqueadas.
Não usam SQLite como prova de equivalência e não leem TEST_DATABASE_URL.

A fixture `backend/export_tests/fixtures/fictional_package.json` é construída
apenas a partir de objetos sintéticos definidos nos testes. Tem scope fictício,
dois jogos e todos os resultados não verificados. Não é exportação operacional.

Executar a partir de backend no Windows:

```powershell
$env:FOOTBALLIQ_CHECKOUT = 'C:/Users/javai/OneDrive/Ambiente de Trabalho/FootballIQ/footballiq'
.venv/Scripts/python.exe -B -m pytest --confcutdir=export_tests export_tests -p no:cacheprovider -q
```

FOOTBALLIQ_CHECKOUT tem de ser fornecido explicitamente. Sem ele, os testes
cruzados assinalam skip. Com ele, um subprocesso Python -B -I importa apenas
os módulos reais de contrato/análise de FootballIQ/src e valida o JSON pela
classe ExportPackage. Não instala o FootballIQ nem escreve bytecode no checkout.
O processo de testes usa as dependências já disponíveis no ambiente Tracker.

Também é possível validar a fixture pela .venv FootballIQ, apenas por leitura,
a partir da raiz FootballIQ:

```powershell
.venv/Scripts/python.exe -B -c "from pathlib import Path; from footballiq.analytics import analyze_recent_matches; p=Path(r'C:\Users\javai\OneDrive\Ambiente de Trabalho\SUB-19\ccdr-match-tracker\backend\export_tests\fixtures\fictional_package.json'); r=analyze_recent_matches(p.read_text(encoding='utf-8')); print(r.metrics['competitive'].model_dump())"
```

Resultado esperado: total e subtotal competitivos null, covered_matches=0 e
selected_matches=2, com avisos e referências preservadas. Os DTOs verificam
coerência estrutural, não autenticidade ou qualidade real da recolha.

## Próxima entrega e decisões pendentes

1. Aprovar como representar pertenças/permissões por clube/equipa, ou uma
   instalação dedicada explicitamente autorizada. ADMIN global não basta.
2. Definir certificação auditável da qualidade e verificação do resultado.
3. Ensaiar a leitura e concorrência num PostgreSQL descartável autorizado,
   sem recorrer às bases operacionais ou a migrações nesta tarefa.
4. Só depois implementar uma fronteira autenticada de exportação e emissão de
   pacote completo; aplicar autorização antes da consulta e minimização de dados.
5. Definir identidade estável da instalação, retenção, limites do payload,
   revogação e política de utilização dos dados dos jogadores.

Não há ainda exportação real pronta para utilizadores nem novo endpoint público.