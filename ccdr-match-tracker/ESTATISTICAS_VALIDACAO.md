# Estatísticas — validação de 1 de outubro de 2026

Estatísticas por jogo, jogador e época implementadas. Não foram alterados modelos, migrações ou lógica do Jogo ao Vivo. Sem novas dependências, tabelas agregadas, autenticação, multiutilizador, WebSockets, offline, mapas de remate, posse de bola, xG, percentagens avançadas ou exportações.

## Endpoints e âmbito

| Método | Caminho | Resposta |
| --- | --- | --- |
| GET | `/matches/{match_id}/stats` | Jogo, equipa/adversário, resultado, comparação, total de eventos e timeline |
| GET | `/statistics/season` | Contexto, resumo competitivo, comparação de atividade, jogadores e rankings |
| GET | `/statistics/players` | Contexto, jogadores e rankings individuais |

Os endpoints da época resolvem `2026/27` e `CCDR Vila Cortez do Mondego` por nome, sem IDs fixos no frontend. Nesta fase não existe seletor de outras épocas. Época/equipa não configuradas devolvem 404; executar o seed. Uma época configurada sem jogos devolve 200 e totais zero. Jogo inexistente devolve 404.

O campo `scope` declara:

```json
{
  "competitive": "FINISHED",
  "events": "ALL_MATCHES_WITH_EVENTS",
  "callups": "ALL_MATCHES_INCLUDING_SCHEDULED"
}
```

### Resumo competitivo

Apenas jogos `FINISHED` da equipa e época: jogos terminados, vitórias, empates, derrotas, golos marcados, sofridos e diferença. O resultado é derivado dos eventos de cada jogo. Um jogo terminado sem golos conta como empate 0–0. Jogos em curso, cancelados e agendados não entram neste resumo. `total_matches` indica separadamente todos os jogos registados.

### Atividade e comparação

Todos os eventos dos jogos da equipa e época, independentemente do estado, incluindo cancelados com eventos. `matches_with_events` conta jogos distintos com pelo menos um evento; `total_events` conta todos os tipos, incluindo substituições e autogolos.

Valores de cada lado: golos, remates à baliza, fora, bloqueados, totais, cantos, livres, faltas, foras de jogo, penáltis, amarelos, vermelhos e defesas. Na época, o lado “Adversários” soma os eventos adversários de todos os jogos.

Remates totais = `SHOT_ON_TARGET + SHOT_OFF_TARGET + SHOT_BLOCKED`. GOAL não acrescenta remates. PENALTY não acrescenta golos. Não se deduzem relações implícitas entre eventos.

O resultado reutiliza a função do Jogo ao Vivo: GOAL soma à equipa indicada; OWN_GOAL à contrária. Os golos da comparação seguem o resultado, embora os restantes indicadores contem eventos da equipa indicada. Por isso os golos de atividade podem diferir dos golos competitivos: os âmbitos são diferentes e estão identificados no ecrã.

### Jogadores

Apenas inscrições da nossa equipa na época, incluindo inativos e jogadores sem atividade. São mostrados convocatórias, titularidades, golos, assistências, três tipos de remate, total de remates, amarelos, vermelhos, faltas e foras de jogo.

- Convocado/titular conta `MatchSquad` de todos os jogos da época, incluindo agendados e cancelados. Não significa participação efetiva em campo.
- As convocatórias são contadas separadamente dos eventos, evitando multiplicar presenças quando existem vários acontecimentos.
- Golos individuais contam apenas GOAL US com `player_id`. Assistências contam apenas `related_player_id` de GOAL US.
- Autogolos não contam como golos individuais nem assistências. O golo creditado por autogolo adversário não é atribuído a um jogador nosso.
- Substituição não gera assistência. Eventos sem jogador contam para a equipa, sem atribuição individual.
- Não há minutos jogados nem suposição de 90 minutos para titulares.

### Rankings

Melhores marcadores, mais assistências, mais remates totais, mais amarelos e mais vermelhos. Usam todos os eventos da época, incluem jogadores inativos, excluem valores zero e ordenam pelo valor decrescente. Empates são ordenados pelo nome normalizado sem distinção de maiúsculas/acentos, seguido do nome original e ID para estabilidade. Não existem percentagens ou métricas derivadas adicionais.

## Interface

- Homepage: Estatísticas abre `/statistics`.
- Detalhe do jogo: **Ver estatísticas** abre `/matches/{match_id}/stats`.
- Época: cartões competitivos, âmbito explícito, tabela comparativa, cinco rankings e fichas expansíveis por jogador para evitar tabelas demasiado largas no telemóvel.
- Jogo: equipa/adversário, resultado final apenas quando FINISHED (nos restantes, resultado atual), comparação, total de eventos e timeline por período, segundos e ID, com nomes e assistências.
- Loading, erro, estados vazios e botão **Atualizar estatísticas**. Se uma atualização falhar, os dados anteriores são identificados como potencialmente desatualizados.

As respostas são calculadas em cada pedido e o cliente usa `cache: no-store`. Editar/apagar eventos altera as estatísticas na consulta seguinte, sem recalcular ou atualizar tabelas agregadas. Um ecrã já aberto deve ser atualizado ou reaberto para mostrar as alterações; não há polling/WebSockets.

## Arquitetura

`statistics_service.py` contém consultas, contagens e rankings. `statistics_schemas.py` define respostas Pydantic; `statistics_api.py` mantém os endpoints simples. O cálculo reutiliza a regra de resultado existente, sem modificar o serviço ao vivo.

`Match`, `MatchSquad` e `MatchEvent` são as fontes dos valores; `Season`, `Team` e `Player` fornecem contexto e identificação. Não há escrita nos endpoints de estatísticas. **Não foi criada migração; a base continua em `0004`.**

## Testes e resultados

- **104 testes Python/PostgreSQL aprovados, zero ignorados**, incluindo 5 testes novos de estatísticas e toda a regressão das fases anteriores.
- Cobertura: comparação de jogo, resultado US/OPPONENT, autogolos, três tipos de remate e total sem golos, cartões e outros indicadores, timeline ordenada, FINISHED/V/E/D, atividade de jogos em curso/cancelados, isolamento por equipa/época, convocado/titular, assistências, jogadores inativos, rankings e empates por nome, época vazia e jogo inexistente.
- Editar um golo para remate remove o golo/assistência, muda vitória para empate e acrescenta o remate; apagar o remate remove-o dos rankings e totais. Exercitado através dos endpoints reais de edição/eliminação.
- `python -m alembic check`: **No new upgrade operations detected**. Revisão: **0004 (head)**.
- Lint, TypeScript e build: **aprovados**.
- **14 testes de browser aprovados**: 4 de Estatísticas e 10 de regressão. Cobrem homepage → época, cartões, comparação, rankings, jogador, detalhe → estatísticas do jogo, timeline, loading/erro/retry, época/jogo sem dados e 404. Percursos a 360 e 1280 px sem overflow horizontal.

Testes backend em PostgreSQL real, com esquemas temporários isolados. Testes de browser no Microsoft Edge com HTTP controlado. Não foi realizado teste em telemóvel físico nem teste integrado browser–API real.

Avisos não bloqueantes: descontinuação futura do transporte `httpx` no Starlette e cores do terminal Playwright. O build usa fontes Google e pode precisar de acesso à rede.

## Comandos manuais

Partindo de `ccdr-match-tracker`, com o `.env` existente. Reiniciar o backend para carregar os endpoints novos. Nesta fase não há migração adicional a aplicar.

```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic check
.\.venv\Scripts\python.exe -c "import os; from app.config import get_settings; os.environ['TEST_DATABASE_URL']=get_settings().database_url.get_secret_value(); import pytest; raise SystemExit(pytest.main(['-q','-p','no:cacheprovider']))"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Os testes criam e removem esquemas próprios; o utilizador da base precisa de permissão CREATE. Pode usar uma base dedicada definindo `TEST_DATABASE_URL` e executar `python -m pytest -q` no ambiente virtual.

Noutro terminal, partindo da raiz:

```powershell
cd frontend
npm.cmd run lint
npx.cmd tsc --noEmit
npm.cmd run build
npm.cmd run test:e2e
npm.cmd run dev
```

Os testes de browser exigem Edge e porta 3100 livre. Abrir `http://localhost:3000/statistics` ou entrar num jogo e escolher **Ver estatísticas**.

Verificação manual recomendada: comparar um jogo terminado com os seus eventos, conferir GOAL/OWN_GOAL, editar/apagar um golo no Jogo ao Vivo, atualizar Estatísticas e confirmar resultado/ranking. Confirmar que um jogo ainda em curso aparece na atividade mas não em V/E/D.

No telemóvel, usar a configuração LAN já documentada em [PLANTEL_VALIDACAO.md](PLANTEL_VALIDACAO.md): URL da API com IP do PC, origem frontend nos CORS e servidores em `0.0.0.0`. Abrir `http://IP_DO_PC:3000/statistics`.

## Limitações

- Estatísticas refletem apenas o que foi registado. Golos e remates são eventos separados; não se infere um remate a partir de um golo.
- Convocatória não prova que o jogador entrou em campo. Não há minutos jogados.
- Eventos de cancelados continuam na atividade, conforme o âmbito explícito; não entram no resumo competitivo.
- Os dados são recalculados por pedido; não há atualização automática num ecrã já aberto nem garantia de snapshot global entre consultas durante edições simultâneas. Multiutilizador fica fora desta fase.
- A época é `2026/27`, resolvida no backend. Não existe seletor de época nem exportação.
- O cálculo carrega os eventos da época em memória; adequado ao âmbito atual, sem otimização validada para volumes de múltiplas épocas/clubes.
- Mantém-se a ausência de autenticação para desenvolvimento local.

## Ficheiros

Criados:

- `backend/app/statistics_schemas.py`
- `backend/app/statistics_service.py`
- `backend/app/statistics_api.py`
- `backend/tests/test_statistics.py`
- `frontend/lib/statistics.ts`
- `frontend/app/statistics/page.tsx`
- `frontend/app/statistics/comparison-table.tsx`
- `frontend/app/matches/[match_id]/stats/page.tsx`
- `frontend/app/matches/[match_id]/stats/match-statistics.tsx`
- `frontend/tests/statistics.spec.ts`
- `ESTATISTICAS_VALIDACAO.md`

Modificados:

- `backend/app/main.py`
- `frontend/app/page.tsx`
- `frontend/app/matches/[match_id]/match-detail.tsx`
- `frontend/README.md`
- `README.md`

Inventário relativo ao início desta fase; o backend continua fora do repositório Git. Não foram alteradas migrações, modelos, lógica do Jogo ao Vivo ou dependências.

**Estatísticas prontas para teste manual no browser e no telemóvel**, sujeito à configuração LAN. Não se avançou para autenticação nem multiutilizador.
