# Eliminação explícita de jogo e dados associados

Validada em 2 de outubro de 2026. A eliminação segura original e o cancelamento mantêm as regras descritas em JOGOS_ELIMINACAO_VALIDACAO.md.

## Dependências verificadas

Revisão de models.py, migrações, SQLAlchemy Inspector e catálogo PostgreSQL pg_constraint:

| Dependência | Foreign key | Política atual |
|---|---|---|
| MatchEvent / match_events | match_id → matches.id | NO ACTION, sem cascade |
| MatchSquad / match_squads | match_id → matches.id | NO ACTION, sem cascade |

O catálogo foi consultado para referências às tabelas matches, match_events e match_squads, incluindo tabelas referenciadoras noutros schemas. Não existem outras referências atuais, nem dependências adicionais dos eventos/convocatórias. Dados de relógio estão no próprio Match. Estatísticas são calculadas a partir de Match, MatchSquad e MatchEvent; não há agregados persistidos para eliminar.

## Endpoint e transação

`DELETE /matches/{match_id}/force`, com JSON:

```json
{"confirmation":"ELIMINAR"}
```

Somente ADMIN autenticado, usando a dependência Admin existente, cookie, origem autorizada e CSRF. Nenhuma identidade ou autorização é obtida do JSON ou de cabeçalhos livres. COACH/VIEWER recebem 403; sem sessão, 401. Confirmação ausente/incorreta ou campos extra: 422.

A operação adquire o bloqueio existente da linha Match, que também é usado nas escritas Live/convocatória. Elimina explicitamente, sem cascade:

1. MatchEvent filtrados por match_id.
2. MatchSquad filtrados por match_id.
3. O próprio Match, incluindo o histórico do relógio.
4. Commit único.

Sucesso: 204; jogo inexistente: 404. Qualquer erro reverte toda a transação, incluindo eventos/convocatória já eliminados pelos comandos anteriores. IntegrityError: 409, sem eliminação parcial. Uma nova dependência impeditiva exige revisão explícita da operação; não é apagada automaticamente.

Não há restrição de estado nesta rota: SCHEDULED, FIRST_HALF, HALF_TIME, SECOND_HALF, FINISHED e CANCELLED são permitidos. Jogadores, equipas, adversário, época, utilizadores e dados de outros jogos são preservados.

`DELETE /matches/{match_id}` permanece inalterado: só SCHEDULED, sem eventos/convocatória, com elapsed_seconds=0 e clock_started_at=NULL. Não foi introduzido um parâmetro force nessa rota. POST /matches/{match_id}/cancel também mantém as regras anteriores.

## Frontend

No detalhe, apenas ADMIN vê a área **Eliminação destrutiva**, com o botão **Eliminar jogo e dados associados**. Está disponível mesmo quando o DELETE seguro não é elegível, incluindo jogos cancelados. Usa a rota /force exclusivamente.

O diálogo explica que convocatória, eventos, resultado e relógio serão apagados definitivamente, e que as estatísticas deixarão de incluir o jogo. Exige checkbox e escrita exata de ELIMINAR antes de ativar Confirmar eliminação de todos os dados. Abrir/fechar não elimina dados; os controlos ficam bloqueados durante o pedido.

Após sucesso fecha o diálogo, remove o detalhe eliminado e regressa a /matches, com nova leitura da lista. A confirmação e os erros são apresentados no diálogo. A ação é visualmente distinta de Cancelar jogo, que continua a preservar histórico.

## Ficheiros

Modificados: backend/app/api.py, backend/app/schemas.py, frontend/lib/api.ts, frontend/app/matches/[match_id]/match-detail.tsx, frontend/app/matches/[match_id]/management-dialog.tsx, frontend/tests/match-management.spec.ts, README.md e JOGOS_ELIMINACAO_VALIDACAO.md.

Criados: backend/tests/test_auth_force_delete.py e este documento.

## Resultados

- Python/PostgreSQL: **186 passaram**, incluindo 13 novos casos de eliminação forçada e todas as regressões anteriores.
- Alembic check: **passou**, sem novas operações; base em **0006 (head)**.
- Lint: **passou**.
- TypeScript: **passou**.
- Build: **passou**.
- E2E: **35 passaram**, incluindo confirmação reforçada a 360 px, rota distinta, redirect/lista e visibilidade ADMIN/COACH/VIEWER.

Testes backend usam sessões reais e schemas PostgreSQL descartáveis. Cobrem todos os estados pedidos, SCHEDULED com convocatória/eventos, preservação de entidades partilhadas e dados completos de outro jogo, recálculo das estatísticas sem o jogo removido, 404/403/401/422, CSRF e rollback de falhas de integridade/runtime. Os E2E simulam HTTP; testes anteriores de DELETE seguro/cancelamento continuam a passar.

Avisos sem falha: depreciação Starlette/httpx e NO_COLOR/FORCE_COLOR. Após todas as asserções E2E, foi terminado apenas o servidor temporário Playwright para concluir a limpeza do runner Windows.

Nenhuma migração ou alteração ao esquema. Nenhum jogo real do workspace foi eliminado durante a implementação. Reiniciar os servidores habituais, entrar como ADMIN e usar a opção no detalhe do jogo de teste. Pronto para teste manual no browser/telemóvel.
