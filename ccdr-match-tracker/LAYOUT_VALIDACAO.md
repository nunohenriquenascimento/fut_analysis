# Layout, identidade visual e imagens — 2 de outubro de 2026

Fase dedicada à apresentação e referências de imagens locais. As regras do Plantel, Jogos, Convocatórias, relógio/eventos do Jogo ao Vivo e cálculos de Estatísticas foram preservadas. Sem autenticação, WebSockets, upload, storage cloud, offline, novos indicadores ou bibliotecas de gráficos. Sem dependências adicionais.

## Revisão e plano visual

Antes das alterações foram revistas todas as páginas, formulários e clientes do frontend. Foram identificados cartões brancos no Plantel/Jogos e cartões escuros nas Estatísticas/Live, definições repetidas de cores, botões, campos, loading e erros, larguras limitadas a telemóvel em desktop e ausência de suporte a imagens.

A primeira passagem usou uma paleta temporária escura. A personalização final usa agora as cores fornecidas pelo utilizador, inspiradas no emblema: vermelho, azul e amarelo, fundo claro, cartões brancos e texto escuro. Foram mantidos os componentes, cartões que passam a duas colunas em tablet/desktop e alvos de toque de pelo menos 44 px (botões principais e campos: 48 px; eventos: pelo menos 72 px).

## Personalização das cores e identidade

Editar o bloco `:root` em `frontend/app/globals.css`:

| Variável | Uso |
| --- | --- |
| `--primary`, `--primary-hover`, `--on-primary` | Ação principal e respetivo texto |
| `--secondary` | Ações secundárias e avatares |
| `--on-secondary`, `--secondary-surface` | Texto branco no azul e superfícies azuis claras |
| `--accent` | Destaque e foco |
| `--on-accent`, `--focus` | Texto escuro no amarelo e contorno azul do foco |
| `--background` | Fundo geral |
| `--surface`, `--surface-raised` | Cartões e superfícies |
| `--foreground`, `--muted` | Texto principal/secundário |
| `--success`, `--success-surface` | Sucesso/ativo/titular |
| `--warning`, `--warning-surface` | Aviso/suplente |
| `--error`, `--error-surface` | Erro/cancelado/eliminação |
| `--border`, `--disabled`, `--overlay` | Bordas, desativados e backdrop |
| `--field-border`, `--shadow`, `--shadow-raised` | Contorno de campos e sombras |

Tokens finais: `primary #D90000`, `primary-hover #B80000`, `on-primary #FFFFFF`, `secondary #101C8C`, `on-secondary #FFFFFF`, `secondary-surface #EEF0FC`, `accent #F2E51D`, `on-accent #141414`, `focus #101C8C`, `background #F6F7F9`, `surface #FFFFFF`, `surface-raised #F1F3F5`, `foreground #141414`, `muted #606775`, `border #D9DDE3`, `field-border #87909E`, `success #16803A`, `success-surface #EEF9F1`, `warning #8A6100`, `warning-surface #FFF8DD`, `error #C62828`, `error-surface #FFF0F0`, `disabled #606775`, `overlay #14141499`. Sombras: `0 4px 18px #14141408` e `0 10px 30px #101C8C0D`.

O dourado de texto e o texto secundário foram escurecidos para contraste sobre superfícies claras. O amarelo de destaque mantém o valor proposto. O foco combina contorno azul com halo amarelo. Verde identifica apenas estados positivos funcionais; estados intermédios usam dourado e texto explícito. Botões de eventos usam azul/neutro, sem verde decorativo.

As classes Tailwind usam tokens semânticos; os componentes não espalham cores literais. `frontend/lib/brand.ts` centraliza nome, abreviatura, escalão, época e ficheiro padrão do emblema. Se alterar o fundo geral, ajustar também `THEME_BACKGROUND` nesse ficheiro: o manifesto usa esse valor, porque os metadados não leem CSS variables. Não foi acrescentada funcionalidade PWA.

## Componentes partilhados

- `AppHeader`: identidade e navegação, página atual, link para saltar para conteúdo.
- `PageHeader`, `PageContainer`: cabeçalhos, margens e larguras; destino de foco do skip link.
- `Card`, `SectionHeader`: superfícies e títulos.
- `PrimaryButton`, `SecondaryButton`, `DangerButton`: ações, foco e desativados.
- `StatusBadge`, `MatchStatusBadge`: estados com texto, sem depender só de cor.
- `EmptyState`, `LoadingState`: estados sem dados e carregamento.
- `PlayerAvatar`, `TeamCrest`: imagens ou fallback acessível.
- `MatchScoreboard`: emblemas, nomes, resultado e estado; aceita o relógio existente como conteúdo.
- `.form-field`: estilo central dos campos de Plantel, Jogos e eventos.

## Páginas

Homepage com área do clube e quatro cartões de navegação. Plantel com foto/iniciais, número, posição e badge ativo/inativo; formulário recolhido quando já existem jogadores, aberto no plantel vazio e ao criar/editar. O formulário permite associar ou remover um caminho de foto.

Jogos com emblemas, jornada, data/hora, casa/fora, badge de estado e resultado quando disponível. Os resultados são consultados no endpoint de detalhe existente, sem novo cálculo backend. Detalhe do jogo partilha placar, metadados e ações. Convocatória inclui fotos, badges Titular/Suplente/Não convocado, bordas distintas e contadores existentes.

Live mantém cálculo de tempo, transições, gravação/edição/eliminação e regras de seleção. O placar e cronómetro têm destaque; os eventos estão agrupados em Ofensivos, Bolas paradas, Disciplina, Defensivos e Substituição. A timeline explicita minuto, tipo, equipa, jogador e assistência. Os seletores nativos mantêm-se; depois de selecionar, mostra-se a foto/avatar do jogador e do assistente/jogador que entra.

Estatísticas mantém os âmbitos e métricas anteriores: cards competitivos, comparação, cinco rankings e fichas expansíveis. Rankings e fichas incluem fotos/avatares. Estatísticas do jogo usa o placar comum.

## Estrutura e associação de imagens

O emblema real do CCDR está em `frontend/public/clubs/ccdr-vila-cortez/crest.png` e foi usado sem modificar a imagem. Não foram inventadas fotos ou emblemas. O fallback da equipa é uma superfície neutra com um traço; o do jogador são iniciais. Ficheiros em falta ou inválidos têm fallback, incluindo erros ocorridos antes da hidratação React.

| Asset | Ficheiro no disco | Valor público |
| --- | --- | --- |
| Clube | `frontend/public/clubs/ccdr-vila-cortez/crest.png` | `/clubs/ccdr-vila-cortez/crest.png` |
| Adversário | `frontend/public/teams/adversario.png` | `/teams/adversario.png` |
| Jogador | `frontend/public/players/jogador-8.webp` | `/players/jogador-8.webp` |

Para trocar o placeholder do CCDR, colocar o emblema real **com o nome `crest.png`** na pasta indicada. O cabeçalho/homepage usam esse caminho padrão; os jogos também o usam como fallback do nosso clube quando o campo persistido não está definido. Para persistir a associação, atualizar a equipa pela API abaixo. Emblemas de adversários são sempre associados à respetiva equipa pelo campo persistido.

Usar nomes simples sem espaços/acentos. Formatos aceites: `png`, `jpg`, `jpeg`, `webp`, `avif`, `svg`, com extensão em minúsculas. Recomenda-se PNG transparente para emblemas e WebP/JPEG quadrado para fotos. Imagens são servidas pelo frontend; a API não verifica se o ficheiro existe.

Nunca incluir `frontend/public` no valor guardado, URLs remotas ou caminhos absolutos Windows. `null` remove a associação sem apagar o ficheiro.

### Jogador

No Plantel, escolher **Editar**, preencher **Caminho da foto (opcional)** e guardar. Deixar vazio remove a referência. Também é possível usar `POST /players` ou `PATCH /players/{id}` com `photo_path`.

```powershell
$playerId = 8 # substituir pelo ID real, não pelo número da camisola
$body = @{ photo_path = "/players/jogador-8.webp" } | ConvertTo-Json
Invoke-RestMethod -Method Patch -Uri "http://localhost:8000/players/$playerId" -ContentType "application/json" -Body $body
```

### Equipa

Listar equipas com `GET /teams?limit=200&offset=0` (paginação por offset se necessário), ou usar `team_id` do contexto e `opponent_id` do jogo. Atualizar exclusivamente o emblema com `PATCH /teams/{id}`:

```powershell
Invoke-RestMethod "http://localhost:8000/teams?limit=200&offset=0"
$teamId = 23 # substituir pelo ID real
$body = @{ crest_path = "/clubs/ccdr-vila-cortez/crest.png" } | ConvertTo-Json
Invoke-RestMethod -Method Patch -Uri "http://localhost:8000/teams/$teamId" -ContentType "application/json" -Body $body

$opponentId = 24 # substituir pelo ID real
$body = @{ crest_path = "/teams/adversario.png" } | ConvertTo-Json
Invoke-RestMethod -Method Patch -Uri "http://localhost:8000/teams/$opponentId" -ContentType "application/json" -Body $body
```

Não existe upload nem formulário de gestão de emblemas nesta fase. Não é necessário apagar/recriar equipas ou jogadores. Depois de adicionar ficheiros, reiniciar o frontend; se usar produção, repetir o build para incluir os assets novos.

## Backend e migração

- `Player.photo_path`: `VARCHAR(500) NULL`.
- `Team.crest_path`: `VARCHAR(500) NULL`.
- Caminhos validados por `app/media.py`; nomes, posições, números e regras existentes mantêm-se.
- `PlayerRead` propaga fotos para Plantel, convocatória, Live e Estatísticas.
- `MatchRead` propaga `team_crest_path` e `opponent_crest_path`; contextos incluem `team_crest_path`.
- `GET /teams` e `PATCH /teams/{team_id}` permitem identificar equipas e guardar/remover o emblema.
- `0005_media_assets.py`, com `down_revision = 0004`, acrescenta apenas os dois campos. Não foram modificadas `0001` a `0004`.

Upgrade/downgrade testados em PostgreSQL com equipas, jogador inativo, jogo terminado, convocatória e golo existentes, comparando todos os valores e timestamps anteriores. O downgrade preserva esses dados, mas remove as referências de media dos dois campos novos; os ficheiros no frontend permanecem.

**A base local foi atualizada para `0005 (head)` nesta fase.** Antes/depois do upgrade foram comparados os campos existentes de equipas, jogadores, jogos, convocatórias e eventos: preservados. `alembic check` não detetou operações adicionais.

## Validação

- Backend: **114 testes passaram, zero ignorados**. Incluem nove casos novos de persistência/propagação, caminhos inválidos e migração, mais a regressão das fases anteriores.
- Lint, TypeScript e build: aprovados.
- Browser: **20 E2E passaram** no Microsoft Edge, incluindo os 14 de regressão e seis de layout/media.
- Percursos por homepage, Plantel, Jogos, detalhe/convocatória, Live, Estatísticas e estatísticas de jogo a **360, 390, 430, 768 e 1280 px**, sem overflow horizontal.
- Fotos/emblemas presentes, ausentes e com 404; inativos; avatar no seletor de eventos, rankings e fichas; contadores da convocatória; alvos de toque; foco/skip link; contraste de texto mínimo 4.5:1 nos pares semânticos verificados.
- Capturas em `frontend/artifacts/layout/{largura}/` (sete páginas por largura). As imagens de teste são pixels sintéticos servidos pelo mock, sem emblemas/fotos inventados em `public`.
- Inspeção visual das capturas mobile e desktop. Não foi usado dispositivo físico nem realizado teste E2E browser–API real; os testes backend usam PostgreSQL real em esquemas isolados e os E2E usam HTTP controlado.

Neste ambiente Windows restrito, o encerramento automático do servidor temporário Playwright pode ficar pendente após todos os testes. Nas execuções foi parado apenas o processo Next iniciado pela própria suite, permitindo terminar o comando. Mantida a configuração Playwright existente. Avisos não bloqueantes: Starlette/httpx e cores do terminal.

## Comandos

Partindo de `ccdr-match-tracker`, com o `.env` existente:

```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic check
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -c "import os; from app.config import get_settings; os.environ['TEST_DATABASE_URL']=get_settings().database_url.get_secret_value(); import pytest; raise SystemExit(pytest.main(['-q','-p','no:cacheprovider']))"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

O upgrade já foi aplicado localmente; repeti-lo é idempotente. Testes de downgrade executam-se em esquemas isolados; não executar downgrade na base de utilização para validar esta fase. O utilizador dos testes precisa de permissão CREATE SCHEMA.

Noutro terminal:

```powershell
cd frontend
npm.cmd run lint
npx.cmd tsc --noEmit
npm.cmd run build
npm.cmd run test:e2e
npm.cmd run dev
```

E2E requerem Microsoft Edge e porta 3100 livre. O build pode precisar de rede para as fontes Google existentes. Abrir `http://localhost:3000`. Para telemóvel, seguir a configuração LAN de [PLANTEL_VALIDACAO.md](PLANTEL_VALIDACAO.md): API com IP do PC, origem LAN nos CORS e ambos os servidores em `0.0.0.0`.

## Ficheiros desta fase

Criados:

- `backend/app/media.py`
- `backend/alembic/versions/0005_media_assets.py`
- `backend/tests/test_media_assets.py`
- `frontend/components/app-header.tsx`
- `frontend/components/ui.tsx`
- `frontend/components/media.tsx`
- `frontend/components/match-scoreboard.tsx`
- `frontend/lib/brand.ts`
- `frontend/tests/layout.spec.ts`
- `frontend/public/clubs/ccdr-vila-cortez/README.md`
- `frontend/public/teams/README.md`
- `frontend/public/players/README.md`
- `LAYOUT_VALIDACAO.md`

Modificados:

- `backend/app/models.py`, `backend/app/schemas.py`, `backend/app/api.py`
- `backend/app/statistics_service.py` (apenas campo de emblema no contexto)
- `backend/tests/test_players.py` (resposta de contexto com campo opcional)
- `frontend/app/globals.css`, `frontend/app/layout.tsx`, `frontend/app/page.tsx`, `frontend/app/manifest.ts`
- `frontend/app/players/page.tsx`
- `frontend/app/matches/page.tsx`, `frontend/app/matches/match-form.tsx`
- `frontend/app/matches/[match_id]/match-detail.tsx`
- `frontend/app/matches/[match_id]/live/live-match.tsx`, `frontend/app/matches/[match_id]/live/event-dialog.tsx`
- `frontend/app/matches/[match_id]/stats/match-statistics.tsx`
- `frontend/app/statistics/page.tsx`, `frontend/app/statistics/comparison-table.tsx`
- `frontend/lib/api.ts`
- `frontend/tests/players.spec.ts`, `frontend/tests/matches.spec.ts`, `frontend/tests/live.spec.ts`, `frontend/tests/statistics.spec.ts` (seletores/contexto da navegação nova)
- `frontend/.gitignore`, `frontend/README.md`, `README.md`

Inventário relativo a esta fase, sem incluir alterações pré-existentes de dependências ou ficheiros gerados. O frontend tem repositório Git próprio; backend e documentos pertencem ao repositório exterior de `SUB-19`. Capturas/build/test-results são artefactos locais, ignorados pelo Git.

## Limitações e estado final

- Paleta final baseada nas cores fornecidas e no emblema real; fotos de jogadores e emblemas de adversários continuam a depender dos assets fornecidos pelo utilizador.
- Assets locais têm de ser copiados manualmente, incluídos no build quando aplicável e associados pelos caminhos públicos; a API não guarda binários.
- Cabeçalho/homepage usam o emblema padrão configurado em `brand.ts`; emblemas dos jogos vêm dos campos persistidos, com fallback do nosso clube.
- A listagem de jogos consulta o detalhe dos jogos não agendados para obter resultados: pedidos adicionais por jogo. Se esse pedido falhar, o cartão continua disponível sem resultado; o detalhe pode ser reaberto.
- Os seletores Live são nativos, com preview após selecionar; não são galerias de fotos dentro das opções do sistema operativo.
- A acessibilidade foi verificada nos critérios indicados; não foi feita auditoria completa com leitor de ecrã ou matriz de dispositivos/browsers.
- Mantém-se a atualização manual das Estatísticas e a ausência de autenticação para desenvolvimento local.

**Personalização visual final concluída e layout pronto para teste manual no browser/telemóvel**, após configurar LAN para acesso pelo telemóvel. Não se avançou para autenticação.

## Personalização visual final — 2 de outubro de 2026

Homepage com emblema maior, faixa de identidade e navegação em cartões brancos; jogadores com avatares maiores, número destacado e estado textual; jornadas com etiqueta azul e placares com emblemas maiores. Convocatória mantém badges textuais, com borda verde para titulares, dourada para suplentes e tracejada para não convocados. Live tem placar branco, resultado azul e cronómetro escuro de grande dimensão, botões grandes e timeline mais legível. Estatísticas usa números azuis, cartões de resumo, rankings com valores destacados e linhas alternadas nas tabelas.

Validação desta personalização: lint, TypeScript e build aprovados; **20 E2E existentes aprovados**, cobrindo 360, 390, 430, 768 e 1280 px sem overflow. O teste de contraste foi adaptado aos pares da paleta clara, mantendo o mínimo 4.5:1 e aceitando cores hexadecimais abreviadas pelo minificador. Os restantes testes ficaram intactos. A homepage com o emblema real também foi verificada a 360 e 1280 px, com imagem carregada e sem overflow; capturas em `frontend/artifacts/layout/ccdr-home-{largura}.png`.

Alterações desta etapa: `frontend/app/globals.css`, `frontend/lib/brand.ts`, classes de apresentação nas páginas de Plantel, Jogos, detalhe, Live, Estatísticas e estatísticas de jogo, `frontend/app/statistics/comparison-table.tsx`, `frontend/tests/layout.spec.ts` e documentação. Não foram alterados handlers, pedidos HTTP, cálculos, backend, endpoints, migrações, dependências ou funcionalidades. Os hashes dos ficheiros backend/migrações foram comparados antes/depois e mantiveram-se. A revisão da base permanece `0005`.
