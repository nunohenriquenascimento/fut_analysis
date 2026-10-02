# Eliminação e cancelamento seguro de jogos

Foi acrescentada posteriormente uma rota separada para ADMIN eliminar jogos e dados associados: [JOGOS_ELIMINACAO_FORCADA_VALIDACAO.md](JOGOS_ELIMINACAO_FORCADA_VALIDACAO.md). As regras seguras descritas neste documento permanecem inalteradas.

Validação de 2 de outubro de 2026. Usa exclusivamente a sessão HttpOnly, CSRF e as dependências `CurrentUser`/`Admin` já existentes. Sem alterações ao esquema ou migrações; a base permanece em `0006`.

## Endpoints e permissões

| Endpoint | Comportamento |
|---|---|
| GET /matches/{match_id} | Detalhe existente, agora com `can_delete` e `can_cancel`, calculados no servidor para o utilizador autenticado |
| DELETE /matches/{match_id} | Apenas ADMIN; 204 em sucesso, 404 inexistente, 409 quando há estado/histórico/dependências que impedem eliminação |
| POST /matches/{match_id}/cancel | Apenas ADMIN; 200 com detalhe atualizado, 404 inexistente, 409 se já cancelado ou se o relógio ativo estiver inconsistente |

COACH e VIEWER recebem 403 nas duas ações, mesmo enviando cabeçalhos de papel falsos. Sem sessão: 401. Escritas mantêm a validação CSRF/origem existente. Os campos de elegibilidade são ambos falsos para COACH/VIEWER e nunca substituem autorização ou revalidação de uma operação.

O PATCH existente continua limitado aos metadados do jogo: não aceita estados, equipa, época ou campos de elegibilidade. Não existe reabertura de CANCELLED; a sequência de transições Live existente também bloqueia essa tentativa.

## Regras exatas de eliminação

Todas as condições têm de ser verdadeiras:

1. `status == SCHEDULED`.
2. `elapsed_seconds == 0`.
3. `clock_started_at IS NULL`.
4. Não existe nenhuma linha MatchSquad para o jogo, incluindo suplentes e jogadores inativos.
5. Não existe nenhuma linha MatchEvent, independentemente do tipo, equipa ou tempo do evento.
6. Nenhuma outra dependência referencial impede o DELETE.

O endpoint adquire o bloqueio da linha Match usado pelas escritas de convocatória/Live e repete as verificações dentro da transação. Só depois elimina e faz commit. Falhas revertem a transação. Foreign keys restritivas oferecem proteção adicional; qualquer IntegrityError devolve 409 sem apagar dependências. Não se apagam adversários, equipas, épocas, jogadores ou utilizadores.

Na revisão do modelo, MatchSquad e MatchEvent são as únicas tabelas atuais que referenciam Match. FIRST_HALF, HALF_TIME, SECOND_HALF, FINISHED e CANCELLED nunca podem ser apagados fisicamente, mesmo que não tenham eventos ou convocatória. A elegibilidade que o browser recebeu anteriormente pode deixar de ser válida: o DELETE volta sempre a verificá-la.

O modelo atual não guarda um registo de auditoria de convocatórias/eventos previamente removidos nem distingue uma convocatória vazia gravada de uma nunca gravada. A validação usa o histórico atualmente persistido; esta fase não inventa marcadores de histórico nem altera o esquema.

## Cancelamento

ADMIN pode cancelar SCHEDULED, FIRST_HALF, HALF_TIME, SECOND_HALF ou FINISHED. Cancelar um FINISHED preserva os acontecimentos e o placar histórico, retirando-o do resumo competitivo por passar a CANCELLED. Um CANCELLED não pode ser cancelado novamente (409), apagado fisicamente ou reaberto.

Na mesma transação, com bloqueio da linha:

- Calcula o tempo acumulado usando `live_service.elapsed` e `utcnow`, antes de mudar o estado.
- Nas partes em curso, soma o tempo desde clock_started_at; nos estados parados conserva elapsed_seconds.
- Define clock_started_at=NULL e status=CANCELLED.
- Preserva ID, metadados, convocatória, eventos e respetivas autorias. O resultado continua derivado dos mesmos eventos.

Se uma parte em curso não tiver clock_started_at, aplica-se o erro 409 já previsto no cálculo do relógio e a transação não altera o estado. Correções de eventos/convocatória continuam a seguir as regras anteriores; não foram introduzidas novas restrições nessas operações.

## Estatísticas

Sem alteração em `statistics_service.py`:

- Só FINISHED conta para jogos competitivos, vitórias, empates, derrotas, golos e diferença de golos competitivos.
- Os eventos de CANCELLED continuam incluídos na atividade, comparação, estatísticas individuais e rankings conforme a regra atual.
- As convocatórias de CANCELLED continuam incluídas nas contagens atuais de convocados/titulares.
- Estatísticas por jogo e resultado histórico continuam consultáveis.

## Frontend

- Área de gestão no detalhe exclusivamente ADMIN.
- Cancelar jogo aparece quando `can_cancel` é verdadeiro; Eliminar jogo apenas quando `can_delete` é verdadeiro. Ausência destes campos significa ações indisponíveis.
- Eliminação: diálogo explica a permanência; checkbox obrigatório e botão Confirmar eliminação. Abrir/fechar diálogo não envia pedidos.
- Cancelamento: diálogo explica preservação de convocatória/eventos/resultado e exclusão competitiva; botão Confirmar cancelamento.
- DELETE bem-sucedido fecha a confirmação, retira o detalhe eliminado e navega para `/matches`, onde a lista é novamente obtida da API.
- Cancelamento usa o detalhe devolvido pelo servidor para atualizar placar, badge Cancelado (CANCELLED) e elegibilidade.
- DELETE 409 mantém o detalhe, explica que se deve cancelar para preservar histórico e volta a obter a elegibilidade do servidor.
- Guardar metadados ou convocatória volta a obter o detalhe, para não perder o placar e para atualizar elegibilidade.

## Ficheiros desta fase

Modificados:

- `backend/app/api.py`
- `backend/app/match_service.py`
- `backend/app/live_schemas.py`
- `backend/tests/test_matches.py` (novo formato do detalhe)
- `frontend/lib/api.ts`
- `frontend/app/matches/[match_id]/match-detail.tsx`
- `README.md`, `JOGOS_VALIDACAO.md`, `AUTH_VALIDACAO.md` (referências à fase concluída)

Criados:

- `backend/tests/test_auth_match_management.py`
- `frontend/app/matches/[match_id]/management-dialog.tsx`
- `frontend/tests/match-management.spec.ts`
- `JOGOS_ELIMINACAO_VALIDACAO.md`

## Validação

- Python/PostgreSQL: **173 passaram**, incluindo 22 novos casos de gestão de jogos com autenticação real. Schemas de teste descartáveis; dados da aplicação preservados.
- `python -m alembic check`: **passou**, sem operações novas detetadas.
- `alembic current`: **0006 (head)**; nenhuma migração criada ou modificada.
- `npm.cmd run lint`: **passou**.
- `npx.cmd tsc --noEmit`: **passou**.
- `npm.cmd run build`: **passou**.
- E2E: **34 passaram**, incluindo os 27 existentes e 7 novos casos de gestão de jogos.

Backend cobre ADMIN/COACH/VIEWER, 404, sessão/CSRF, estado/convocatória/eventos/relógio, revalidação após um detalhe anteriormente elegível, rollback, todos os estados canceláveis, preservação de dados e atividade estatística, congelamento do relógio, bloqueio de reabertura e exclusão competitiva. Frontend cobre visibilidade, flags do servidor, confirmações, redirect/lista, badge, 409 e diálogos a 360 px.

Os E2E usam respostas HTTP simuladas; o backend usa PostgreSQL e sessões reais. Avisos sem falha: depreciação Starlette/httpx e NO_COLOR/FORCE_COLOR. No Windows, foi necessário terminar apenas o servidor temporário criado pelo Playwright após todas as asserções, para concluir a limpeza do runner.

## Teste manual

Reiniciar backend/frontend com os comandos habituais; não executar nova migração. Entrar como ADMIN e abrir um jogo:

1. SCHEDULED vazio: confirmar que aparecem Cancelar/Eliminar; fechar a confirmação sem atuar; depois eliminar explicitamente e confirmar lista atualizada.
2. SCHEDULED com convocatória: confirmar que Eliminar deixa de aparecer; cancelar e confirmar preservação dos convocados.
3. Parte em curso com eventos: cancelar; confirmar badge, placar e cronómetro parado, incluindo após refresh.
4. FINISHED: cancelar e confirmar que o resultado permanece consultável e que o jogo deixa de contar em V/E/D.
5. Entrar como COACH e VIEWER: confirmar ausência das ações.
6. Repetir os diálogos num viewport de 360 px ou no telemóvel com a configuração LAN já documentada em AUTH_VALIDACAO.md.

Plantel, Live, Estatísticas e Autenticação passaram as regressões existentes. Pronto para teste manual no browser e telemóvel.
