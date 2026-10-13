# Unir jogo de continuação — 13/10/2026

Implementado para ADMIN, com preview obrigatório e confirmação `UNIR JOGOS`.
Nenhuma operação de união foi executada nos jogos reais. Os percursos de teste
usaram exclusivamente registos sintéticos em schemas PostgreSQL descartáveis.
Não houve migração nem alteração de schema.

## Modelo temporal analisado

`Match.elapsed_seconds` contém segundos efetivamente acumulados nas paragens.
Enquanto existe `clock_started_at` numa parte em curso, o relógio acrescenta
a diferença inteira entre a hora UTC atual e essa marca de início.
Terminar uma parte acumula esse tempo e limpa a marca. Intervalos não contam.
Reabrir conserva os segundos e deixa SECOND_HALF com marca NULL; retomar
define uma nova marca de início. O frontend interpola o snapshot do servidor
com tempo monotónico do navegador.

`MatchEvent.elapsed_seconds` é tempo acumulado desde o início do jogo inteiro,
incluindo as partes anteriores, e não tempo relativo à parte.
`MatchEvent.period` guarda 1 ou 2. Não existem campos separados para duração
da primeira parte ou minutos regulamentares. Não se assumem 45/90 minutos.

Com ambos os relógios parados, sejam:

- `P = principal.elapsed_seconds`;
- `C = continuation.elapsed_seconds`;
- `E = evento_da_continuação.elapsed_seconds`.

A transformação é:

```text
tempo final do jogo = P + C
tempo final de cada evento da continuação = P + E
período de cada evento da continuação = 2
clock_started_at final = NULL
```

Exemplo: P=3780 s (63:00), C=900 s (15:00), E=270 s (04:30).
O evento passa para 4050 s (67:30); o tempo final é 4680 s (78:00).
A diferença entre kickoff/encerramento/início dos registos nunca é somada.
Os eventos do principal conservam os seus tempos e períodos originais.
Após a operação, a timeline segue a ordenação existente:
`period + elapsed_seconds + id`.

## Elegibilidade e avisos

São bloqueados IDs iguais, épocas diferentes e equipas principais diferentes.
O principal tem de estar FINISHED ou SECOND_HALF com relógio parado.
A continuação pode estar FINISHED, HALF_TIME ou SECOND_HALF com relógio parado.
SCHEDULED, CANCELLED, FIRST_HALF e relógios com marca de início não são elegíveis.
Um registo FIRST_HALF em curso pode ser parado normalmente para HALF_TIME
antes de gerar o preview. Estas condições evitam absorver tempo que continua
a mudar ou reativar implicitamente um cancelamento.

Bloqueiam também tempos de eventos fora de `[0, elapsed_seconds]`, períodos
inválidos, referências a jogadores fora da convocatória de origem,
convocados de outra equipa/época e valores temporais acima do limite SQL Integer.

Diferenças de adversário, jornada, data/hora, casa/fora e local geram avisos.
Os metadados administrativos do principal prevalecem sempre.
Eventos da primeira parte da continuação são explicitamente apresentados
como conversões para a segunda parte. Períodos mistos geram aviso adicional:
o ADMIN deve confirmar que todos representam tempo posterior ao encerramento.
Não se tenta adivinhar ou eliminar eventos alegadamente duplicados.

## Preview e execução

- `POST /matches/merge/preview`: recebe `principal_id`, `continuation_id`
  e `final_status` (`FINISHED` ou `SECOND_HALF`). Não escreve dados.
- Devolve os dois jogos com adversário, jornada, data/hora, status, resultado,
  tempo acumulado, período, contagem de eventos e convocatória; os eventos
  a transferir com metadata e tempos/períodos previstos; jogadores exclusivos
  da continuação; resultado/tempo finais; avisos e conflitos.
- Um preview sem conflitos inclui um token HMAC ligado ao ADMIN, ao par,
  ao status final e ao conteúdo completo dos jogos/eventos/convocatórias.
  É válido durante 30 minutos. Reiniciar o backend invalida os previews.
- `POST /matches/merge`: recebe a seleção, `preview_token` e
  `confirmation: "UNIR JOGOS"`. Não recebe uma lista de alterações do frontend.
- O backend bloqueia ambos os jogos por ID crescente, recalcula o plano
  dentro da transação e compara-o com o token. Alterações posteriores ao
  preview ou token inválido/expirado devolvem 409, sem mutação.
- ADMIN apenas, com sessão ativa, origem autorizada e CSRF.
  COACH/VIEWER recebem 403; jogos inexistentes recebem 404.
  Confirmação ausente/incorreta ou campos extra recebem 422.
- PATCH genérico não ganhou nenhuma capacidade de alterar estados.

## Dados, convocatória e estatísticas

O ID e todos os metadados do principal são preservados. Os eventos da
continuação são movidos por atualização de `match_id`, `period` e
`elapsed_seconds`. Conservam ID, tipo, equipa, jogadores, assistência/
substituição, autor, notas e `created_at`. Nenhum evento é recriado.

A convocatória do principal é a base. Nos jogadores comuns, conserva-se
o registo e a função do principal; diferenças de titular/suplente aparecem
como aviso. Os registos exclusivos da continuação são movidos, conservando
ID, função e timestamp. Incluem convocados sem eventos, para preservar o
histórico da convocatória. Duplicados são reconciliados sem duplicar chamadas.
Nenhum Player, Team, Season, User ou outro Match é eliminado.

O resultado continua derivado de GOAL/OWN_GOAL pelas regras Live existentes.
As métricas de eventos, assistências e rankings usam os mesmos eventos,
agora associados a uma única partida. Chamadas/titularidades usam a
convocatória reconciliada, uma vez por jogador/jogo.
FINISHED conta como uma partida competitiva; SECOND_HALF fica excluído até
novo encerramento. SECOND_HALF final mantém o relógio parado e pode usar
o endpoint normal de resume.

Antes de eliminar a continuação, a operação faz flush e verifica:

1. IDs, quantidade e conteúdo de todos os eventos esperados;
2. resultado previsto e comparação estatística combinada;
3. ausência de eventos restantes na continuação;
4. convocatória final e funções esperadas.

Só então elimina o Match vazio da continuação. As únicas foreign keys
atuais para Match são `MatchEvent.match_id` e `MatchSquad.match_id`.
Uma dependência adicional ou qualquer falha de flush/validação/commit
provoca rollback completo, incluindo transferências já feitas.

Após commit, publica `live.state_changed` para o principal; clientes Live
recuperam o snapshot atualizado. Também invalida a continuação eliminada.
O logger `app.merge_api`, ao nível INFO, regista principal, continuação e ADMIN.
Os tokens e notificações mantêm o âmbito de um processo da arquitetura Live
atual; não foi introduzida infraestrutura distribuída.

## UI e passos para unir manualmente os jogos reais

1. Entrar como ADMIN e abrir o **detalhe do jogo original**, cujo ID será mantido.
2. Confirmar que este é o principal e que os dois relógios estão parados.
3. Em **Gestão do jogo**, clicar **Unir jogo de continuação**.
4. Selecionar o segundo registo, criado para o restante tempo. A lista inclui
   jogos da mesma equipa e época, com ID, adversário, jornada, data e estado.
5. Escolher **FINISHED — jogo terminado** para o caso histórico, ou
   **SECOND_HALF — 2.ª parte com relógio parado** se ainda precisar de continuar.
6. Clicar **Obter preview**. Rever IDs, convocatórias, todos os eventos,
   `tempo original → tempo final`, períodos, resultado, tempo total e avisos.
7. Se houver bloqueios ou dados inesperados, usar **Voltar ao jogo**.
   O preview não altera nada. Confirmar sobretudo que a continuação contém
   apenas eventos posteriores ao encerramento e não uma cópia de eventos anteriores.
8. Se tudo estiver correto, escrever exatamente **UNIR JOGOS** e clicar
   **Confirmar união dos jogos**. Esta etapa executa a transação e remove
   o segundo Match depois das validações.
9. O ecrã regressa ao principal atualizado. Verificar Live, timeline e
   estatísticas do jogo/época. Se escolheu SECOND_HALF, usar **Retomar 2.ª Parte**
   apenas quando quiser iniciar novamente o relógio.
10. Um 409 exige novo preview e nova confirmação. Alterar a seleção ou o
    estado final também invalida o preview no frontend.

## Ficheiros desta funcionalidade

- Backend: `app/merge_schemas.py`, `app/merge_service.py`, `app/merge_api.py`,
  `app/main.py` (regista as rotas estáticas antes de `/matches/{match_id}`).
- Frontend: `lib/merge.ts`, `app/matches/[match_id]/merge-dialog.tsx`,
  `app/matches/[match_id]/match-detail.tsx`.
- Testes: `backend/tests/test_merge.py`, `backend/tests/test_auth_merge.py`,
  `backend/tests/test_auth_live_browser.py`, `backend/tests/merge_browser.cjs`,
  `frontend/tests/merge.spec.ts`.
- Este relatório. Os ficheiros da reabertura anterior continuam preservados.

## Validação e reprodução

- Suite completa Python/PostgreSQL com navegador e Caddy: **277 passed**.
  Inclui Auth, Live, reopen/resume, WebSockets, Stats e os percursos reais de
  fusão a 360/390 px. Os dois testes defensivos acrescentados no final estão
  incluídos na execução dirigida de **29 passed** para `test_merge.py` e
  `test_auth_merge.py`.
- Frontend Playwright: **53 passed**, incluindo os cinco novos cenários de
  preview, união, 409, permissões e bloqueios; regressão mobile a 360/390 px.
- ESLint, TypeScript (`tsc --noEmit`) e build de produção: passaram.
- Alembic check: **No new upgrade operations detected**.

Os testes específicos verificam preview sem mutações, GOAL, OWN_GOAL,
assistência, remate, cartão, substituição, IDs/autores/metadata, relógio,
períodos mistos, funções diferentes, jogador só na continuação, outros jogos,
FINISHED/SECOND_HALF, estatísticas, permissões, CSRF, tokens, concorrência,
rollback e uma foreign key impeditiva real numa tabela de teste.

O teste real de navegador não simula HTTP ou WebSocket: autentica ADMIN,
gera preview, verifica ausência de mutações, executa a união em dados
sintéticos, confirma os eventos/tempo/convocatória/estatísticas e a atualização
de um segundo dispositivo. Guarda previews visuais em:

- `frontend/artifacts/merge/preview-360.png` e `preview-390.png` (UI simulada);
- `frontend/artifacts/merge/real-preview-360.png` e `real-preview-390.png`
  (API/PostgreSQL reais, dados sintéticos).

Após reforçar a validação pré-eliminação, os dois percursos reais de fusão
foram executados novamente: **2 passed** a 360/390 px.

```powershell
# frontend
npm.cmd run lint
npx.cmd tsc --noEmit
npm.cmd run build
npm.cmd run test:e2e -- --workers=2

# backend: TEST_DATABASE_URL deve permitir schemas descartáveis de teste
$env:RUN_LIVE_BROWSER_E2E = '1'
$env:CADDY_BIN = (Resolve-Path '..\.local-tools\caddy\caddy.exe').Path
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m alembic check
```

O navegador real exige build com a API de desenvolvimento padrão e porta 8000
livre. A base de aplicação não é usada como destino dos pedidos: os fixtures
injetam sessões para schemas temporários `roster_test_<uuid>`.
