# FPF — execução local e importação pelo navegador

Estes comandos destinam-se ao operador e não foram executados contra a base de
desenvolvimento. Nesta validação, todas as escritas ocorreram em PostgreSQL
temporário. Não usar este procedimento para Railway/produção.

## Resultado da validação ponta a ponta — 15/10/2026

- Backend completo: **383 aprovados, zero falhas, zero erros e zero ignorados**
  numa única execução (279,02 s). PostgreSQL 18 novo, autenticação própria,
  base `ccdr_fpf_ui_tests`, porta temporária e apenas loopback. Diretório,
  PID/executável e identidade do cluster verificados antes das escritas.
- Cadeia Alembic até 0008 e `alembic check` aprovados. O teste específico
  atualiza 0007 com dados sintéticos, confirma preservação dos registos e
  recusa downgrade quando existem capturas. A base de desenvolvimento existente
  não foi inspecionada; compatibilidade física dessa base não foi certificada.
- Importação real pelo navegador, sem mocks HTTP, aprovada a 360, 390 e
  1440 px: ambos os HTML, mapeamento, associação explícita de jogo interno,
  confirmação e importação repetida. Os fingerprints de jogos, eventos,
  convocatórias e jogadores mantiveram-se. Quatro fixtures após repetição,
  sem duplicação. COACH/VIEWER recebem 403 nos endpoints de escrita.
- Frontend Playwright: primeira execução com oito workers teve 73 aprovados
  e um timeout no teste Live de reabertura. Repetição integral com dois workers:
  **74 aprovados, zero falhas**, sem alterar timeouts ou código da aplicação.
  Esta suite frontend simula respostas HTTP; complementa os testes reais acima.
  A causa do timeout intermitente não ficou comprovada nem resolvida.
- Permanece um aviso de depreciação Starlette/httpx. O PostgreSQL temporário
  foi encerrado e a ausência do seu pidfile confirmada; artefactos sintéticos
  preservados fora do projeto. Nenhuma base existente ou serviço Railway foi
  contactado. Sem commit, push, merge ou deploy.

## 1. Destino de desenvolvimento e migração

Partir de `ccdr-match-tracker`, com dependências Python e Node já instaladas.
Antes de alterar uma base de desenvolvimento com dados importantes, ter uma
cópia de segurança recuperável e fechar os processos da aplicação que a usam.
Não substituir nem publicar `.env`.

```powershell
cd backend
```

Confirmar que a configuração efetiva aponta apenas para o destino local
pretendido, sem mostrar a ligação ou credenciais. Este exemplo recusa outro
nome, porta, host ou parâmetros de ligação; não remover as verificações para
ultrapassar uma falha. Uma variável de processo pode prevalecer sobre `.env`.

```powershell
.\.venv\Scripts\python.exe -c "from app.config import get_settings; from sqlalchemy.engine import make_url; s=get_settings(); u=make_url(s.database_url.get_secret_value()); assert s.app_env=='development'; assert u.host in ('localhost','127.0.0.1'); assert (u.port or 5432)==5432; assert u.database=='ccdr_match_tracker'; assert not u.query; print('Destino configurado: desenvolvimento local confirmado; sem credenciais na saída')"
if ($LASTEXITCODE -ne 0) { throw 'Parar: destino não confirmado' }
.\.venv\Scripts\python.exe -m alembic current
if ($LASTEXITCODE -ne 0) { throw 'Parar: revisão não confirmada' }
```

Confirmar manualmente que existe uma única revisão `0006`, `0007` ou `0008`.
Revisão ausente, múltipla ou inesperada exige investigação. Se já for `0008`,
não repetir a atualização. Caso seja `0006` ou `0007`, depois de confirmar o
destino e a cópia de segurança:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade 0008
if ($LASTEXITCODE -ne 0) { throw 'Parar: migração falhou' }
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic check
```

Exigir revisão `0008` e ausência de alterações de esquema pendentes. A migração
0008 acrescenta `competitions.fpf_data` JSON nullable; se partir de 0006, aplica
também 0007. Não fazer downgrade como correção automática.

## 2. Arrancar a aplicação

Com a configuração local já confirmada, no terminal backend:

```powershell
$env:APP_ENV = 'development'
$env:AUTH_COOKIE_SECURE = 'false'
$env:CORS_ORIGINS = '["http://localhost:3000","http://127.0.0.1:3000"]'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Noutro PowerShell, a partir de `ccdr-match-tracker`:

```powershell
cd frontend
$env:NEXT_PUBLIC_API_URL = 'http://localhost:8000'
npm.cmd run dev -- --hostname 127.0.0.1 --port 3000
```

Abrir `http://localhost:3000/login`. Usar o ADMIN de desenvolvimento existente.
Apenas numa instalação nova, se faltar época/clube, executar `python -m app.seed`
com o Python do venv; se faltar ADMIN, executar `python -m app.create_admin`
interativamente. Ambos escrevem dados: nunca executar por rotina numa base
existente nem usar contas ou passwords dos testes automatizados.

## 3. Testar a importação

1. Entrar como ADMIN e abrir Campeonato. Selecionar a competição 2026/27
   existente; se ainda não existir, criá-la com o clube interno correto.
2. Garantir que as oito equipas têm registos locais únicos. O formulário
   Criar competição permite adicionar equipas adversárias; reutilizar sempre
   as existentes. Não criar jogos internos artificiais para resolver ligações.
3. Abrir **FPF · Oficial**. Selecionar simultaneamente:
   `backend/tests/fixtures/fpf/competition_30369_season_106.html` e
   `backend/tests/fixtures/fpf/match_2682548.html`.
4. Premir **Validar e identificar ficheiros**. Confirmar competição 30369,
   época FPF 106, oito equipas, catorze jornadas e ficha 2682548:
   Seia FC 2–1 Vila Cortez, golos aos 13', 46' e 69'.
5. Mapear explicitamente cada equipa FPF para o registo local correspondente.
   Não atribuir uma jornada à ficha por suposição: conservar a opção de guardar
   apenas a ficha oficial quando a jornada não estiver confirmada.
6. Premir **Rever diferenças e ligações**. Rever participantes, jogos,
   classificação e ligações pendentes. Associar apenas jogos internos que
   correspondam efetivamente à jornada e equipas; rever novamente após alterar.
7. Escrever `SINCRONIZAR FPF` e premir **Confirmar importação FPF**. Conferir a
   captura aplicada, as oito linhas da classificação e a ficha oficial.
8. Repetir a revisão e confirmação dos mesmos ficheiros: não devem surgir
   equipas/jogos adicionais. Comparar o jogo interno, convocatória, eventos,
   resultado e estatísticas antes/depois: devem manter-se.
9. Entrar como COACH e VIEWER: a consulta oficial fica acessível, mas os
   controlos de importação não. O backend também recusa escritas com HTTP 403.
10. Repetir a consulta/importação com viewport 360/390 px e desktop 1440 px.

Se houver conflito ou dados alterados após preview, parar e rever: não forçar
associações nem eliminar dados para desbloquear a importação. Um erro mantém a
última captura válida. Um HTML de jornada AJAX ainda não suportado é recusado.

## Limites

O HTML da competição contém apenas os jogos da jornada apresentada, apesar de
identificar catorze jornadas. Não equivale ao calendário integral importado.
O HTTP 403 anteriormente observado continua a impedir declarar sincronização
automática operacional. Importar ficheiros manualmente não comprova uma ligação
HTTP funcional à FPF nem a autenticidade de um ficheiro alterado pelo operador.
