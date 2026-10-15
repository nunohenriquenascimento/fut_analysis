# FPF: capturas HTML no Campeonato existente

Não há integração HTTP de ponta a ponta demonstrada: o acesso observado devolve
403. Não contornar o bloqueio. A aplicação preserva a última captura gravada.
Os testes usam os HTML fornecidos e uma base PostgreSQL temporária.

## Estruturas confirmadas

- Competição 30369, época 106 (2026-2027), série 99718.
- Oito classificadas; 14 links de jornadas descobertos no HTML.
- A página fornecida mostra apenas quatro jogos agendados da jornada 3.
  O ano não está nos cartões: `17 out 16:00` é conservado como texto,
  sem inventar um instante UTC, resultados, IDs de jogo ou calendário completo.
- Ficha 2682548: Seia Fc 2–1 V. Cortez Mondego-Guarda, 10-10-2026, 16:00,
  Estadio Municipal Seia; golos 13/46/69; plantéis, cartões, substituições,
  equipa técnica e arbitragem extraídos separadamente dos eventos internos.
- As colunas técnicas têm marcação de equipa ambígua no original: conservar
  coluna e função, com lado desconhecido. Não atribuir automaticamente ao CCDR.
- Nenhum parser de resposta AJAX foi presumido: essa captura ainda falta.

## Persistência e migração

`0008` acrescenta somente `competitions.fpf_data` (JSON nullable), sem criar
ou duplicar tabelas, equipas, jogadores, convocatórias ou eventos. Não editar
`0007`; não disponibilizar este código contra um esquema sem `0008`.
O downgrade recusa descartar capturas existentes. Não foi aplicado em bases reais.

A captura guarda a classificação oficial observada e as fichas oficiais em
separado da classificação local provisória em `/standings`. Não soma eventos
oficiais aos eventos internos nem trata a ordem oficial como regulamento validado.
`mode=captured_html` identifica importação de ficheiro, sem afirmar atualização
automática ou certificação da proveniência. O HTML bruto não é executado nem
guardado na base; conservar a captura original sob controlo do operador.

## Operações existentes e novas

Todas requerem sessão; escritas FPF são ADMIN com origem/CSRF existentes.

- `GET /competitions/{id}/fpf`: última captura, origem, modo e cobertura.
- `POST /competitions/{id}/fpf/documents`: identificar e analisar ficheiros
  como texto, sem gravar; recusa documentos repetidos e reporta formatos não
  suportados. Máximo nove ficheiros, 2 MB por ficheiro e 4 MB por lote.
- `POST /competitions/{id}/fpf/preview`: analisar e preparar, sem gravar.
- `PUT /competitions/{id}/fpf`: revalidar sob lock e aplicar atomicamente.
- `POST /competitions/{id}/fpf/sync`: obter a página inicial usando os IDs
  previamente associados; 403 → 503 sanitizado, sem alterar a última captura.
  Não percorre jornadas AJAX cujo formato não foi verificado.

Payload de preview: `competition_html`, `series_id`, `team_mapping`,
`match_htmls` (opcional), `match_rounds` (opcional), `internal_match_links`
(opcional). Aplicação exige ainda `confirmation="SINCRONIZAR FPF"`.
Refresh aceita apenas essa confirmação.
Uma ficha posterior pode omitir `competition_html` quando já existe uma captura
associada. O preview devolve diferenças e `state_token`; a interface envia-o
como `expected_state`. Alterações concorrentes provocam 409 e exigem nova revisão.
Este hash é uma condição de concorrência, não uma autorização ou assinatura.

`team_mapping` associa cada designação exata observada a um Team.id existente,
sem criar equipas por semelhança de nome. Todos os IDs têm de ser distintos,
incluir a nossa equipa e corresponder à época da competição. O mapeamento e
a origem não podem ser reassociados automaticamente depois da primeira gravação.
Participantes em falta podem ser associados; nunca são retirados automaticamente.

O preview fornece chaves estáveis por época/competição/série/fixtureId/par
de equipas. Para os jogos do CCDR, `internal_match_links` associa essa chave a
um Match.id compatível. Sem ligação, o jogo fica pendente, apenas na captura;
não se cria um jogo interno. Com ligação, nunca se importam golos externos.

As fichas não informam a jornada no HTML fornecido: `match_rounds` associa
explicitamente um matchId textual a um fixtureId descoberto. Sem essa revisão,
a ficha fica só na captura. Não deduzir jornada pela data.

Os jogos externos aplicáveis usam a mesma validação de lotes do importador
manual. Conflitos de identidade, calendário ou correções manuais provocam 409
e rollback. Não apagar resultados conhecidos quando a captura apenas agenda
o jogo. Não eliminar dados por ausência numa página parcial.

## Interface FPF

Disponível em `/competitions/{id}/fpf`, na navegação do Campeonato, mantendo
classificação e gestão locais. COACH/VIEWER consultam; só ADMIN importa.
Apresenta identificação, data de importação da última captura, classificação
publicada, jornadas disponíveis/parciais/em falta e fichas expansíveis com
plantéis, eventos, equipa técnica e arbitragem. Data de importação não é garantia
da data ou atualidade do conteúdo. Não é efetuado um diagnóstico remoto ao abrir.

Fluxo: selecionar ficheiros → validar/identificar no backend → rever extração →
mapear equipas existentes e, opcionalmente, fichas/jogos internos → rever diferenças
→ escrever `SINCRONIZAR FPF` → aplicar. Editar uma associação invalida o preview.
Uma leitura inicial tardia não repõe as escolhas já feitas pelo operador.
As capturas de jornadas já disponíveis são conservadas no mesmo campo JSON.

Os ficheiros não são inseridos no DOM nem executados. A identificação de um
fragmento como jornada não aprova o seu parser: enquanto faltar a captura AJAX
real, a interface explica a limitação e impede aplicar esse lote.

## Pendências

- Acesso HTTP autorizado sem 403 e captura AJAX real para cobrir outras jornadas.
- Revisão dos mapeamentos/associações pelo operador; nenhuma importação real
  foi efetuada. Os IDs internos dos testes não servem para produção.
- A classificação local provisória permanece separada da secção oficial FPF;
  nenhum critério oficial é inferido a partir das posições publicadas.
- Carregamento remoto de fichas e agendamento periódico ainda não ativados.
  `FPFClient.match` conhece apenas o endpoint confirmado; não implica que o
  acesso esteja operacional.

## Validação executada nesta etapa

- Suite backend completa durante a implementação: 366 aprovados, zero falhas,
  erros ou skips, incluindo navegador, WebSocket e Caddy reais com dados de teste.
- Após os ajustes finais e novos casos, execução dirigida FPF/Campeonato:
  67 aprovados, zero falhas, erros ou skips. Inclui idempotência, correção de
  resultado externo (mutação sintética explicitamente identificada), permissões,
  CSRF, conflito manual, rollback, preservação interna, 403 e migração 0008.
- Cluster PostgreSQL 18.6 novo e exclusivo em cada execução, com identidade
  verificada antes de escrita. Alembic até 0008 e check aprovados. Ambos os
  servidores foram encerrados; capturas e relatórios temporários preservados.
- Os testes com HTML real não têm skips. A primeira página cobre só a jornada
  visível; isso não é prova de extração do calendário completo nem do AJAX.
- Nenhuma chamada HTTP FPF foi necessária nos testes: transporte simulado,
  parsing de capturas reais e escrita apenas na base isolada. Não há alegação
  de sincronização remota bem-sucedida. Um aviso de depreciação Starlette/httpx
  permanece, sem falha de teste.

## Validação da interface FPF

- Frontend: lint, TypeScript e build Next.js aprovados; 74 testes Playwright
  aprovados. Estes testes de interface usam respostas HTTP simuladas e HTML real.
- Backend: a execução completa de 380 testes terminou com 378 aprovados e duas
  falhas nos seletores do novo teste de navegador. O seletor contava também as
  jornadas do preview, além das jornadas da captura aplicada. Após delimitar a
  consulta à captura aplicada, ambos os testes foram repetidos e aprovados.
  Não houve testes ignorados nessa execução completa ou na repetição dirigida.
- Os dois testes de navegador usam Next.js, FastAPI e PostgreSQL reais, sem
  mocks HTTP, nas larguras 360 e 390 px. Importam os dois HTML fornecidos,
  confirmam mapeamentos e associação interna, repetem a importação e comparam
  os registos internos antes/depois. A repetição não cria jogos adicionais.
- Dois testes adicionais, sem base de dados, aprovados após reforçar o limite
  de upload no servidor: ficheiro multibyte acima de 2 MB e lote acima de 4 MB.
  Total de casos distintos aprovados nas execuções finais: 382; não é uma
  alegação de execução única da suite de 382 testes.
- PostgreSQL 18 exclusivamente temporário: diretório, PID/executável, porta,
  endereço loopback e identificador do cluster confirmados antes das escritas.
  Alembic até 0008 e check aprovados na execução completa. Ambos os clusters
  foram encerrados e os artefactos sintéticos temporários preservados.
- Mantém-se o aviso de depreciação Starlette/httpx. Nenhuma base existente foi
  utilizada, nem houve chamada à FPF ou alteração de dados reais nesta etapa.

A interface requer o esquema 0008 antes da ativação autorizada. O acesso
automático à fonte não está demonstrado: permanece o HTTP 403 anteriormente
observado. A captura AJAX real continua necessária para implementar e testar
o parser de outras jornadas; um fragmento identificado é recusado por enquanto.
