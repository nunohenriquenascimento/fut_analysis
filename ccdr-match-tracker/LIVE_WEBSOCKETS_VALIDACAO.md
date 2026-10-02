# Jogo ao Vivo — sincronização entre utilizadores

Implementação limitada à página `/matches/{match_id}/live`. Não há alterações ao esquema, migrações, regras de eventos, cálculo do resultado, relógio persistido ou Estatísticas. A base continua em `0006`.

## Ficheiros desta fase

Criados:
- `backend/app/live_socket.py`: protocolo, hub por jogo, autenticação e ligação WebSocket.
- `backend/tests/test_auth_live_socket.py`: integração com sessões reais e PostgreSQL.
- `frontend/lib/live-socket.ts`: ligação, validação das mensagens, heartbeat e reconexão.
- `frontend/lib/use-live-socket.ts`: integração e limpeza no ciclo de vida React.
- `frontend/tests/live-socket.spec.ts`: duas páginas, reconexão e HTTP independente.
- `LIVE_WEBSOCKETS_VALIDACAO.md`: este documento.

Modificados:
- `backend/app/auth.py`: reutilização da mesma validação de sessão em HTTP e WebSocket.
- `backend/app/main.py`: registo da rota WebSocket.
- `backend/app/live_api.py`: notificações após commit de transições e eventos.
- `backend/app/api.py`: notificação de cancelamento e eliminação do jogo.
- `frontend/lib/api.ts`: exportação do endereço da API para construir o endereço WebSocket.
- `frontend/app/matches/[match_id]/live/live-match.tsx`: refetch coordenado e indicador de ligação.
- `README.md` e `LIVE_VALIDACAO.md`: referência à sincronização.

## Endpoint e protocolo

`WS /ws/matches/{match_id}/live`, no mesmo backend da API. A URL não inclui credenciais.

```json
{"type":"live.event_created","match_id":31,"version":1,"actor_id":7,"data":{}}
```

Tipos: `live.snapshot`, `live.state_changed`, `live.event_created`, `live.event_updated`, `live.event_deleted`, `live.match_updated`, `live.cancelled`, `live.ping`.

`version: 1` identifica o protocolo, não uma revisão do jogo. O snapshot inicial inclui o estado Live completo em `data`, consultado com lock do jogo. Nas notificações, `data` é vazio; `actor_id` vem do utilizador autenticado e pode ser nulo. Não são enviados emails, cookies, tokens ou passwords. `live.match_updated` identifica a eliminação; nesse caso, a verificação de existência fecha a ligação com 4404 e o frontend refaz GET, apresentando jogo não encontrado. Não sincroniza edições de metadados fora do Live.

O hub subscreve antes de obter o snapshot, evitando perder uma alteração durante a abertura. Cada alteração HTTP publica apenas depois de commit. Filas por ligação limitadas a 32 notificações descartam a mais antiga quando cheias: são invalidações, não diferenças incrementais.

O frontend refaz `GET /matches/{match_id}/live` e substitui o snapshot completo. Agrupa notificações durante um GET, ignora respostas ultrapassadas e espera pelo fim de uma gravação própria antes de atualizar novamente. IDs e ordenação existentes preservam a timeline sem duplicados. Modais e seleções abertas permanecem; gravações continuam sujeitas às regras HTTP atuais. Escritas concorrentes mantêm os locks existentes do backend.

## Autenticação e permissões

Cookie HttpOnly existente, SameSite existente e configuração Secure existente. Valida sessão persistida, prazo, utilizador ativo, jogo e Origin presente na lista exata `CORS_ORIGINS`. Não aceita identidade ou permissões pela query/string ou mensagem. ADMIN, COACH e VIEWER podem subscrever; apenas ADMIN/COACH podem escrever por HTTP. CSRF e dependências de autorização HTTP mantidos. `recorded_by_id` continua a vir do backend autenticado.

Sessão revalidada antes de cada notificação e a cada 15 segundos em repouso. Logout, expiração ou desativação encerram ligações; a revogação não depende apenas da próxima reconexão. Uma resposta já em trânsito pode chegar antes do encerramento. O socket só aceita `pong`; qualquer tentativa de mutação encerra com 1008.

Códigos: 4401 sessão inválida, 4403 Origin inválida, 4404 jogo inexistente, 4409 outra rejeição, 1013 indisponibilidade temporária. Uma rejeição antes de aceitar o handshake pode aparecer no browser como 1006; os GET HTTP autenticados continuam a resolver a sessão e o redirect para login.

## Reconexão e funcionamento sem WebSocket

Backoff de 1, 2, 4, 8, 16 e 30 segundos, com jitter até 20%; tentativas posteriores mantêm o limite. Após falhas repetidas, indicador “Sem tempo real”; as tentativas continuam. Snapshot após reconexão provoca novo GET, recuperando alterações perdidas. Voltar ao separador ou ficar online também atualiza o estado.

Heartbeat em repouso a cada 15 segundos; frontend responde `pong` e fecha/reconecta após 45 segundos sem mensagens válidas. Não são enviados ticks de relógio. O cronómetro continua a interpolar localmente o snapshot do servidor.

Indicador “Tempo real ligado”, “A reconectar” ou “Sem tempo real”. Se o socket falhar, HTTP permanece funcional e existe “Atualizar estado”. Se HTTP também estiver indisponível, não há gravações offline, fila local nem garantia de envio posterior. Falha de notificação depois de commit não transforma uma gravação bem sucedida em erro HTTP.

## Validação

- Python/PostgreSQL: 201 testes, incluindo 15 novos de sockets. Autenticação de todos os papéis; sessão ausente, expirada, revogada e utilizador inativo; Origin; jogo inexistente; isolamento por jogo; duas ligações recebem criação/edição/eliminação/transições/cancelamento; VIEWER 403; logout encerra e bloqueia reconexão; mensagens não executam mutações; escritores concorrentes preservam ambos os eventos; falha de publicação preserva commit.
- `python -m alembic check`: sem novas operações. Nenhuma migração criada.
- `npm run lint`, `npx tsc --noEmit`, `npm run build`: aprovados.
- E2E Microsoft Edge: 38 testes, incluindo 3 novos. Duas páginas a 360 px, resultado e timeline, formulário preservado, partes e cancelamento, mensagens repetidas/desordenadas, reconexão com recuperação e HTTP sem socket. Regressões existentes de login, roles, Plantel, Jogos, Estatísticas, layout, Live e gestão destrutiva incluídas.

Os E2E usam API e WebSocket simulados; integração de WebSocket com PostgreSQL e autenticação real coberta no backend. Dois equipamentos físicos ainda exigem teste manual. Aviso de depreciação do TestClient/httpx na suite Python não impede os testes.

## Execução e teste em dois equipamentos

Backend, a partir de `backend`, com o PostgreSQL habitual disponível:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

Frontend, a partir de `frontend`:

```powershell
npm.cmd run dev -- --hostname 0.0.0.0
```

Para telemóvel na mesma rede, configurar `NEXT_PUBLIC_API_URL=http://IP_DO_PC:8000` no frontend e incluir `http://IP_DO_PC:3000` em `CORS_ORIGINS` no backend; reiniciar ambos (rebuild se produção). Abrir ambos pelo mesmo hostname/IP, para que o cookie do backend seja enviado. Não usar localhost no telemóvel. Reutilizar a configuração LAN/firewall da fase de autenticação.

Entrar com duas contas distintas, abrir o mesmo jogo Live e verificar golo, correção, eliminação, intervalo, segunda parte e fim. Confirmar relógio nas duas páginas; abrir formulário numa delas e criar evento na outra. Suspender/reabrir separador ou rede e verificar recuperação. VIEWER consulta sem ações de edição. Cancelamento por ADMIN no detalhe atualiza Live.

Para repetir validações:

```powershell
# backend; TEST_DATABASE_URL deve apontar para PostgreSQL de testes
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m alembic check
# frontend
npm.cmd run lint
npx.cmd tsc --noEmit
npm.cmd run build
npm.cmd run test:e2e
```

## Limites de deployment

Hub em memória: **um processo/worker e uma instância backend**. Vários workers/instâncias não distribuem notificações entre si; sticky sessions não resolvem todas as mutações. Pub/sub partilhado é necessário antes de escalar; Redis não foi introduzido. Restart perde notificações em memória, recuperadas por snapshot/GET após reconexão. Não há log persistente de notificações nem revisão incremental.

Em produção HTTPS, seguir [PRODUCAO_DEPLOY.md](PRODUCAO_DEPLOY.md): Secure, SameSite explícito adequado aos domínios, CORS/Origin exato e API HTTPS/WSS. Os domínios independentes Vercel/Railway exigem None e cookies de terceiros permitidos; subdomínios próprios same-site permitem Lax. Proxy deve permitir upgrade WebSocket. Mantém-se um worker/instância.

Referências técnicas: [WebSockets FastAPI](https://fastapi.tiangolo.com/advanced/websockets/) e [AnyIO: threads](https://anyio.readthedocs.io/en/stable/threads.html).

Pronto para teste manual em dois dispositivos, respeitando a configuração LAN/HTTPS e o limite de uma instância. Nenhuma sincronização adicionada a Plantel, convocatórias, Estatísticas ou gestão de contas.
