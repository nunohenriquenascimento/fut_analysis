# Diagnóstico temporário de autenticação mobile

O plano posterior de migração está em [RAILWAY_SAME_ORIGIN.md](RAILWAY_SAME_ORIGIN.md): um domínio, API `/api`, WS `/ws` e cookie Lax. O diagnóstico reconhece também o prefixo `/api`; as flags permanecem desligadas por defeito. Os domínios abaixo descrevem o incidente anterior.

Frontend: `https://fut-analysis.vercel.app`. Backend: `https://futanalysis-production.up.railway.app`. Investiga login 200 seguido de `/auth/me` 401, sem alterar cookies, SameSite, CORS autorizado, CSRF, permissões ou regras de sessão.

## Ativar e desativar

No serviço **backend Railway**, configurar `AUTH_DEBUG_LOGGING=true` e aplicar/redeploy para carregar a variável. Default `false`. Não alterar DATABASE_URL ou cookies durante a recolha.

Na **Vercel**, configurar `NEXT_PUBLIC_AUTH_DEBUG=true` no ambiente Production e fazer novo build/deploy manual: é uma variável incorporada no bundle. Default `false`.

Reproduzir o problema uma vez no mobile e, para comparação, no desktop. Consultar logs Railway filtrando `AUTH_LOGIN` e `AUTH_ME`, sobretudo `phase=response`. Na consola browser, procurar `AUTH_DEBUG` e `AUTH_DEBUG_API`. Usar o `X-Request-ID` da resposta para encontrar o mesmo pedido no backend; o CORS expõe apenas esse header adicional. Cada pedido tem um ID aleatório gerado no servidor; não é um identificador de sessão e não reutiliza headers enviados pelo cliente.

Concluída a recolha, voltar **ambas as flags a false**, redeploy Railway e rebuild/redeploy Vercel. Restringir acesso aos logs e apagar/exportar apenas os excertos necessários conforme a política de retenção da equipa. Nenhuma flag de produção foi ativada automaticamente nesta implementação.

## Dados registados e proteção

Logging backend JSON, com timestamp UTC, request_id, método/path sem query, origem, host, classificação de browser, origem na lista autorizada, resultado/status e atributos do cookie. Email totalmente mascarado (`***`). user_id/role apenas quando a autenticação é válida. User-Agent é classificado como Mobile/Desktop Safari/Chrome/Firefox/Edge/Other; texto bruto não é registado.

O cookie esperado é identificado pelo nome e presença. Apenas os nomes conhecidos `ccdr_session` e `__Host-ccdr_session` podem aparecer; outros cookies são apenas contados. Não são registados valores. A origem/host são validados como origem URL, sem credenciais, path, query ou fragmento; entradas inválidas ficam `<invalid>`.

**Nunca são registados** password, token de sessão, cookie completo, Authorization, DATABASE_URL, CSRF, bodies HTTP, respostas JSON de autenticação ou erros com dados internos. O identificador primário de AuthSession é o próprio hash do token: também não é registado. `session_db_id_logged=false` indica essa exclusão. O registo de sucesso é emitido depois de commit e de preparar Set-Cookie; `set_cookie_header_present` confirma a existência do header, sem ler o seu valor para logging.

Frontend regista origem da API, fases request/response/fetch_error, estado HTTP, request_id válido, classificação do browser, online e location.origin. Nunca imprime email/password, request/response body nem o objeto/mensagem do erro fetch. `fetch_failed` significa falha de rede/CORS indistinguível para JavaScript; consultar Network e o servidor.

## Exemplos seguros

Excertos ilustrativos; os logs reais incluem outros campos não sensíveis:

```json
{"event":"AUTH_LOGIN","phase":"response","request_id":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","origin":"https://fut-analysis.vercel.app","user_agent":"Mobile Safari","credentials_valid":true,"session_created":true,"cookie_name":"__Host-ccdr_session","cookie_secure":true,"cookie_httponly":true,"cookie_samesite":"none","cookie_path":"/","cookie_domain":"<host-only>","cookie_max_age_present":true,"set_cookie_header_present":true,"status":200}
{"event":"AUTH_ME","phase":"response","request_id":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","session_cookie_present":false,"session_found":false,"reason":"session_cookie_missing","status":401}
```

```json
{"event":"AUTH_ME","phase":"response","session_cookie_present":true,"session_found":false,"session_revoked":null,"reason":"session_not_found","status":401}
{"event":"AUTH_ME","phase":"response","session_cookie_present":true,"session_found":true,"session_expired":true,"reason":"session_expired","status":401}
{"event":"AUTH_ME","phase":"response","session_cookie_present":true,"session_found":false,"session_revoked":true,"reason":"session_revoked","status":401}
```

Cada pedido tem uma linha `phase=request` antes da validação e outra `phase=response` com resultado final. Não comparar `session_created=false` da linha inicial com o sucesso final. Set-Cookie preparado não prova que o browser o aceitou.

## Interpretar

| Observação | Interpretação |
|---|---|
| Login 200, sessão criada, Set-Cookie presente; me sem cookie | O browser não devolveu o cookie esperado. Verificar aceitação/bloqueio de cookies de terceiros, atributos e host chamado; servidor não consegue provar armazenamento no browser |
| Cookie presente; `session_not_found` | Sessão ausente na base consultada. Verificar configuração/ambiente/persistência; também pode ter sido removida antes deste processo observar a revogação |
| `session_expired` | Registo encontrado mas prazo ultrapassado |
| `session_revoked` | Sessão removida por uma revogação observada neste processo com diagnóstico ativo |
| `user_not_found` / `user_inactive` | Sessão não autoriza um utilizador existente/ativo |
| Sessão válida, utilizador ativo, resposta 401 | Investigar inconsistência de validação, outra camada ou resposta de outro pedido. Comparar request_id; não concluir bug apenas pela presença de cookie |
| Origin não autorizada / validação de Origin falhou | Verificar URL frontend exata e CORS. Login continua a rejeitar a origem; `/auth/me` GET não ganhou uma nova regra de Origin |
| Fetch falha sem status | Pode ser rede/TLS/CORS; verificar se o pedido chegou ao backend |

Razões internas adicionais: `session_cookie_invalid` para formato inválido, `validation_inconsistent` se a leitura de diagnóstico contradiz a validação principal, `diagnostic_lookup_failed` se a leitura adicional não conseguiu concluir. Não alteram o texto público do 401.

`origin_allowed` representa pertença à configuração atual. `origin_validation_passed=null` significa que não foi executada a validação de Origin da dependência, como em GET `/auth/me`; não é aprovação nem rejeição. O browser ainda aplica CORS. Cookies HttpOnly não aparecem em `document.cookie`; essa API não é usada no diagnóstico. `Set-Cookie` também não é acessível ao JavaScript da página.

## Limite da distinção de revogação

O modelo atual elimina AuthSession ao revogar. Não foi adicionada coluna, tabela, tombstone persistida nem migração. Para diagnóstico existe uma cache temporária, protegida por lock, de no máximo 1024 **hashes já existentes**, sem tokens brutos e sem logging desses hashes, durante até 24 horas de classificação. Só regista operações observadas com flag ativa depois de commit: logout, substituição de sessão e revogação pela gestão de utilizadores. Não participa na autorização.

Após restart, remoção externa, limpeza de sessões expiradas ou revogação não observada, a ausência devolve `session_not_found`, com `session_revoked=null` (desconhecido). Não é possível recuperar a causa histórica com o esquema atual. Valores `null` nos campos de diagnóstico significam desconhecido, nunca uma prova negativa.

## Validação

Testes backend cobrem flag false sem logs detalhados, login persistido, atributos do cookie, request_id, cookie ausente, sessão inexistente/expirada/revogada, utilizador inativo, Origin rejeitada, cache limitada e ausência de password/token/hash/CSRF/Authorization/URL da base nos logs. Testes frontend verificam flag on/off, logging permitido e `credentials: "include"` para login, me e logout, mesmo perante opções que tentem substituir include.

Resultados: **230 testes Python/PostgreSQL passaram**, incluindo 9 novos; **43 testes frontend/Playwright passaram**, incluindo 3 novos. Lint, TypeScript, build e Alembic check passaram. Build inicialmente bloqueado no download das fontes Google pelo sandbox; aprovado após permitir rede, sem alteração de fontes. Aviso de depreciação TestClient/httpx existente, sem falhas. Nenhuma migração criada.

Criados: `backend/app/auth_debug.py`, `backend/tests/test_auth_debug.py`, `frontend/lib/auth-debug.ts`, `frontend/tests/auth-diagnostic.spec.ts` e este documento.

Modificados: `backend/app/config.py`, `backend/app/auth.py`, `backend/app/auth_api.py`, `backend/app/main.py`, `frontend/lib/api.ts`, exemplos `.env.example` e `.env.production.example` de ambos os serviços, e `README.md`.

Nenhuma alteração da estratégia de autenticação. Ativação e publicação ficam a cargo do operador; não foi efetuado deployment nesta fase.
