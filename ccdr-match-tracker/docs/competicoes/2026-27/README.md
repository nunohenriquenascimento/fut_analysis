# Preparação da Liga Dappin 2026/27

`draft.json` é um documento de trabalho, **não um payload de importação**.
Contém apenas a identificação fornecida pelo utilizador. Não contém nomes de
adversários, datas, resultados ou critérios oficiais inventados.

Antes de carregar dados reais, são necessários:

1. Lista oficial das oito equipas, incluindo a designação exata de cada uma.
2. Época, série e fase, calendário oficial e fonte/data de consulta.
3. Mapeamento revisto de cada equipa para o respetivo `Team.id`. Não criar
   duplicados por variações de nome; uma equipa pode existir noutras épocas.
4. `season_id` e `internal_team_id` confirmados pelo contexto da aplicação.
5. Chave externa estável por jogo. Conservar a chave ao reimportar/corrigir;
   uma chave não pode ser reutilizada para outro par, jornada ou jogo interno.
6. Fonte específica por resultado em `source`; datas com offset e local,
   quando conhecidos. Resultado desconhecido: ambos os golos ausentes/NULL,
   nunca 0–0 para representar ausência de informação.
7. Para os jogos do CCDR: ID interno correspondente, mesma época/jornada,
   adversário e casa/fora. Não enviar golos externos nesses jogos. Os eventos
   internos continuam a ser a única fonte do resultado.
8. Regulamento aplicável a 2026/2027 e artigos de pontuação/desempate. Até
   confirmação, a política é provisória e os empates não resolvidos são visíveis.

Depois de autorizar a ativação, preparar separadamente:

- Criação/associação dos participantes e da competição, com IDs reais revistos.
- Payloads de calendário/resultados no formato `{"fixtures":[...]}`, até 200
  jogos por lote. O rascunho não deve ser enviado diretamente ao endpoint.
- Revisão na interface de chaves, equipas, jornadas, horas e fontes, antes da
  confirmação de cada lote. A revisão JSON é local; o backend valida o lote
  completo na gravação e reverte-o integralmente se houver conflitos.

Reimportar as mesmas chaves atualiza os mesmos jogos, sem duplicar partidas.
As regras já testadas de idempotência e proteção interna foram preservadas.
Não existe importação automática a partir de websites nesta preparação.

Gestão posterior de participantes: só ADMIN. O preview não grava. A gravação
exige `ALTERAR PARTICIPANTES` e a lista anterior esperada; uma revisão
desatualizada devolve 409. Equipas com jogos no calendário/resultados da
competição ou jogos internos da mesma época ficam protegidas contra remoção,
mesmo que o jogo interno ainda não tenha sido ligado ao calendário. A nossa
equipa permanece e a competição mantém pelo menos dois participantes.

O procedimento operacional de backup e upgrade está em
[MIGRACAO_0007.md](../../MIGRACAO_0007.md). Nenhuma autorização de carregamento
de dados reais se encontra implícita neste rascunho ou no ensaio sintético.
