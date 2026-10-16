# Importação FPF para o calendário local

A captura oficial e os jogos locais eram persistidos separadamente. Uma ficha
sem jornada era guardada apenas em `fpf_data`; jogos da nossa equipa sem ligação
interna eram omitidos. Os links para 14 jornadas não representam 14 jornadas
descarregadas. A tabela oficial agregada não permite reconstruir resultados.

## Fluxo corrigido

1. O upload envia texto para `/fpf/documents`, sem executar HTML ou scripts.
2. São identificadas páginas de competição, fichas e páginas de jornada com URL
   canónico FPF e estrutura reconhecida. Fragmentos sem identidade são recusados.
3. O ADMIN confirma o mapeamento completo para IDs de equipas existentes.
4. Uma ficha usa a jornada do mesmo ID FPF encontrado no HTML da jornada, a
   associação persistida ou uma jornada explicitamente confirmada pelo ADMIN.
   Não é inferida pelo nome do ficheiro, por datas aproximadas ou pela posição
   na classificação. Sem jornada, aparece como ignorada com a razão.
5. O preview mostra criações, atualizações, registos sem alterações e omissões.
   A confirmação revalida o estado; conflitos rejeitam todo o lote.
6. A transação grava `competition_fixtures`, participantes novos na competição e
   a captura oficial. Nenhum jogador, jogo interno, evento ou convocatória é criado.
7. Calendário e resultados leem essas fixtures. A classificação é calculada em
   cada GET a partir dos jogos terminados e das regras locais; não existe cache
   materializada a invalidar. A navegação volta a consultar os endpoints.

Jogos sem resultado permanecem agendados, com golos nulos. Um resultado reconhecido
com ID FPF alimenta o resultado externo. A ficha mantém a data/hora em Lisboa.
Horários sem ano na lista de jogos não dão origem a uma data inventada.

## Preservação e compatibilidade

- O ID FPF identifica fichas novas; fixtures antigas mantêm chave e ID local.
  A reconciliação usa o ID da origem e a combinação exata de jornada e IDs das
  equipas; contradições são recusadas. Uma reimportação não duplica jogos.
- Resultados conhecidos não são apagados por uma captura apenas com horários.
- Uma correção manual não é substituída silenciosamente.
- Se existir exatamente um jogo interno compatível por época, jornada, IDs e
  casa/fora, é associado sem alterar o jogo. O resultado continua derivado dos
  seus eventos. Vários candidatos exigem confirmação explícita.
- Sem jogo interno, um encontro da nossa equipa pode existir apenas como fixture
  externa do campeonato. A exceção é exclusiva do fluxo FPF validado, não da API
  de importação manual. Uma importação posterior pode ligá-lo ao jogo interno.
- As estatísticas individuais internas continuam baseadas nos eventos internos;
  a importação não fabrica eventos individuais a partir do resultado FPF.

Não é necessária nova migração: exige-se o esquema existente até `0008`.
Capturas antigas podem ser reimportadas e revistas; nada é convertido por tarefa
automática de arranque, migração ou deployment.

## Limites dos ficheiros disponíveis

As capturas originais comprovam a competição, quatro jogos agendados da jornada 3
e a ficha 2682548. A ficha não declara jornada: necessita de associação confirmada
quando não há uma página de jornada com o seu ID.

Os ficheiros adicionais chamados `Jornada 2.html`, `Jornada 4.html` até
`Jornada 14.html` encontrados durante esta investigação também declaram a jornada
3 e os mesmos jogos. Não comprovam as restantes jornadas. O importador respeita
o conteúdo, não o nome do ficheiro.

Os testes de páginas de jornada com URL canónico e resultados são contratos com
HTML sintético explicitamente identificado, usando o resultado da ficha real.
Uma captura real de resposta AJAX continua necessária para validar eventuais
variações de estrutura do site FPF; estruturas desconhecidas são rejeitadas.
