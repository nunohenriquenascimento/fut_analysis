# Modelo de Jogo — Sub-19 CCDR Vila Cortez do Mondego

## 1. Objetivo do documento

Este documento define a identidade tática, a organização coletiva, os comportamentos por posição e os princípios gerais do modelo de jogo pretendido para a equipa Sub-19 do CCDR Vila Cortez do Mondego.

Serve como referência principal para um assistente de inteligência artificial que deverá:

- Compreender a identidade da equipa.
- Interpretar a organização ofensiva e defensiva.
- Identificar as funções dos jogadores.
- Analisar comportamentos individuais e coletivos.
- Reconhecer diferenças entre modelo pretendido e execução observada.
- Identificar problemas táticos.
- Propor correções.
- Analisar adversários em função do nosso modelo.
- Recomendar adaptações sem descaracterizar a equipa.
- Apoiar a preparação dos treinos e dos jogos.

O modelo de jogo não deve ser confundido com uma formação fixa.

Uma mesma equipa pode apresentar estruturas diferentes em organização ofensiva, organização defensiva e transições, mantendo princípios comuns.

**Princípio fundamental:**

O sistema organiza as posições iniciais. O modelo de jogo define os comportamentos e as relações entre os jogadores.

---

# PARTE I — IDENTIDADE DA EQUIPA

## 2. Identificação

**Clube:** CCDR Vila Cortez do Mondego

**Escalão:** Sub-19

**Estrutura-base pretendida:** 3-5-2

**Transformações ofensivas possíveis:** 3-4-3 e 3-4-2-1

**Organização defensiva de referência:** bloco médio, com adaptações à estrutura adversária.

**Referências centrais:**

- Três centrais com funções diferenciadas.
- Um central central com função de líbero.
- Dois centrais exteriores capazes de participar na construção.
- Alas com responsabilidades ofensivas e defensivas.
- Dois médios com funções complementares de recuperação e construção.
- Um médio ofensivo de ligação e criação.
- Dois avançados com movimentos complementares.
- Proteção central sem bola.
- Mobilidade e ligação entre setores com bola.

Estas referências descrevem a intenção tática, não garantem a sua execução.

---

## 3. Identidade pretendida

A equipa pretende apresentar:

1. Organização coletiva.
2. Capacidade de construir desde trás quando existirem condições.
3. Progressão através de apoios e movimentos coordenados.
4. Ocupação equilibrada da largura e dos corredores interiores.
5. Mobilidade entre médios e avançados.
6. Complementaridade entre os dois avançados.
7. Proteção central sem bola.
8. Bloco defensivo compacto.
9. Transições ofensivas objetivas.
10. Reação coordenada à perda.
11. Capacidade de adaptação ao adversário.
12. Equilíbrio entre ambição ofensiva e segurança defensiva.

### Regra

A IA não deve transformar estas intenções em afirmações de desempenho observado.

---

## 4. Hierarquia das decisões táticas

As recomendações devem respeitar a seguinte ordem:

1. Segurança e regras do jogo.
2. Informação efetivamente observada.
3. Princípios fundamentais do futebol.
4. Identidade coletiva definida.
5. Funções individuais pretendidas.
6. Características demonstradas dos jogadores.
7. Comportamento adversário.
8. Contexto do jogo.
9. Alternativas táticas disponíveis.

### Nota

Esta ordem não é uma fórmula rígida. Em determinadas situações, o contexto e as características dos jogadores podem justificar uma adaptação ao comportamento habitual.

A IA deve explicar essas adaptações.

---

## 5. Estrutura-base 3-5-2

Representação funcional:

```text
                    PL1       PL2

                         MO

                MC-R          MC-C

       ALA-E                           ALA-D

                DCE     LIB     DCD

                          GR
```

**Legenda:**

- GR: guarda-redes.
- DCE: defesa-central esquerdo.
- LIB: líbero.
- DCD: defesa-central direito.
- ALA-E: ala esquerdo.
- ALA-D: ala direito.
- MC-R: médio recuperador.
- MC-C: médio construtor/distribuidor.
- MO: médio ofensivo.
- PL1: avançado de apoio.
- PL2: avançado de profundidade.

O desenho é esquemático e não representa distâncias fixas.

---

## 6. Estruturas dinâmicas

O 3-5-2 pode assumir diferentes disposições ao longo do jogo.

### Organização ofensiva

- 3-5-2.
- 3-4-1-2.
- 3-4-3.
- 3-4-2-1.

### Organização defensiva

- 5-3-2.
- 5-2-1-2.
- 5-4-1 em situações específicas.
- Estruturas assimétricas de contenção.

### Transições

A estrutura depende de:

- Posição da bola.
- Localização dos alas.
- Projeção dos médios.
- Movimentos dos avançados.
- Equilíbrio preventivo.
- Reação do adversário.

### Regra

A IA deve identificar a estrutura efetivamente apresentada e não atribuir automaticamente uma formação a toda a fase do jogo.

---

# PARTE II — ORGANIZAÇÃO OFENSIVA

## 7. Objetivos ofensivos

A equipa pretende:

- Sair da primeira fase de construção com controlo.
- Criar linhas de passe.
- Progredir sem perder equilíbrio.
- Encontrar jogadores em zonas interiores.
- Utilizar os alas para dar largura.
- Criar ligações entre médios e avançados.
- Explorar movimentos complementares dos PL.
- Chegar a zonas de finalização com ocupação adequada.
- Manter capacidade de reagir à perda.

---

## 8. Primeira fase de construção

A primeira fase pode envolver:

- GR.
- Três centrais.
- Médio construtor.
- Médio recuperador.
- Alas, conforme a pressão.

### Princípios

1. Criar linhas de passe.
2. Evitar jogadores alinhados na mesma linha de pressão.
3. Reconhecer o adversário livre.
4. Atrair pressão quando existir possibilidade de a ultrapassar.
5. Proteger o corredor central.
6. Preparar a ligação à segunda fase.

### Regra

Construir desde trás não significa insistir em passes curtos quando não existem condições.

---

## 9. Participação do guarda-redes

O GR deve funcionar como apoio à construção quando as suas capacidades e a pressão adversária o permitirem.

### Comportamentos pretendidos

- Oferecer linha de passe.
- Reconhecer o central livre.
- Identificar pressão.
- Circular quando existe vantagem.
- Procurar alternativa mais longa quando necessário.
- Comunicar com a linha defensiva.

### Riscos

- Passe central sob pressão.
- Receção sem apoio.
- Circulação previsível.
- Falta de profundidade defensiva.

### Regra

A IA não deve pressupor elevada qualidade de jogo com os pés sem evidência.

---

## 10. Função dos três centrais na construção

### DCE

- Abrir linha de passe à esquerda.
- Participar na circulação.
- Conduzir quando existe espaço.
- Procurar ligações com ala, médio ou avançado.
- Manter atenção à transição.

### LIB

- Organizar a linha.
- Garantir cobertura.
- Oferecer apoio central.
- Facilitar mudança de corredor.
- Controlar profundidade.

### DCD

- Abrir linha de passe à direita.
- Participar na circulação.
- Conduzir quando existe espaço.
- Procurar ligações com ala, médio ou avançado.
- Manter atenção à transição.

### Regra

Os centrais exteriores não devem conduzir simultaneamente sem compensação.

---

## 11. Papel do líbero

O líbero é a referência central da última linha.

### Responsabilidades pretendidas

- Garantir cobertura aos centrais exteriores.
- Controlar profundidade.
- Coordenar posicionamentos.
- Proteger o espaço central.
- Antecipar quando existe cobertura e vantagem.
- Apoiar circulação.
- Comunicar ajustamentos.

### Princípio

O líbero deve privilegiar a proteção do espaço e a cobertura, em vez de procurar marcação individual permanente.

### Exceção

Pode intervir diretamente sobre um adversário quando a situação o exige e a cobertura permite.

### Erro a evitar

Abandonar o espaço central sem compensação.

---

## 12. Centrais exteriores

Os centrais exteriores possuem responsabilidades na construção e na defesa dos corredores adjacentes.

### Com bola

- Abrir.
- Receber orientados.
- Conduzir.
- Fixar adversário.
- Encontrar médio.
- Ligar com ala.
- Explorar passe vertical.

### Sem bola

- Controlar atacante próximo.
- Cobrir corredor exterior.
- Proteger intervalo.
- Comunicar com líbero.
- Ajustar perante subida do ala.

### Regra

A saída à marcação deve depender da cobertura existente.

---

## 13. Médio recuperador

O médio recuperador é uma referência de proteção e equilíbrio.

### Com bola

- Oferecer apoio.
- Circular de forma segura.
- Proteger zona central.
- Facilitar continuidade.
- Reconhecer pressão.

### Sem bola

- Proteger espaço à frente dos centrais.
- Intercetar.
- Condicionar progressão.
- Apoiar pressão.
- Cobrir zonas libertadas.
- Preparar reação à perda.

### Regra

Ser recuperador não significa ficar permanentemente afastado da construção.

---

## 14. Médio construtor/distribuidor

O médio construtor é uma referência de ligação e organização.

### Com bola

- Aproximar-se da construção.
- Receber orientado.
- Definir ritmo.
- Procurar passes progressivos.
- Mudar corredor.
- Ligar com MO.
- Encontrar alas.
- Identificar movimentos dos PL.

### Sem bola

- Fechar espaço central.
- Apoiar recuperação.
- Manter proximidade.
- Cobrir zonas.
- Participar na compactação.

### Regra

Ser construtor não significa estar dispensado de tarefas defensivas.

---

## 15. Complementaridade dos dois médios

A equipa pretende utilizar:

- Um médio predominantemente recuperador.
- Um médio predominantemente construtor.

### Princípios

1. Evitar ambos na mesma altura sem necessidade.
2. Criar linhas de passe diferentes.
3. Garantir cobertura.
4. Permitir progressão.
5. Coordenar movimentos.
6. Ajustar ao posicionamento dos alas.

### Exemplo

Se o construtor baixar para receber, o recuperador pode manter posição de equilíbrio.

Se o recuperador sair à pressão, o construtor deve avaliar a proteção do espaço libertado.

### Regra

As funções são complementares, não totalmente exclusivas.

---

## 16. Papel dos alas

Os alas são responsáveis por grande parte da largura ofensiva e por importantes ajustamentos defensivos.

### Com bola

- Oferecer largura.
- Receber em progressão.
- Atacar espaço.
- Combinar com médios.
- Procurar cruzamento ou passe atrasado.
- Reconhecer quando devem manter posição.

### Sem bola

- Recuperar para a linha defensiva.
- Fechar espaço interior.
- Controlar adversário exterior.
- Saltar à pressão quando existe cobertura.
- Coordenar com central exterior.

### Regra

A altura dos alas deve depender da fase e do equilíbrio coletivo.

---

## 17. Ala do lado da bola

### Comportamentos possíveis

- Dar largura.
- Aproximar para apoio.
- Atacar profundidade.
- Combinar com médio.
- Procurar cruzamento.
- Fixar defensor.

### Riscos

- Receção isolada.
- Pressão lateral.
- Falta de cobertura.
- Perda e transição.

---

## 18. Ala do lado contrário

### Comportamentos possíveis

- Manter largura para mudança de corredor.
- Ajustar altura.
- Preparar chegada ao segundo poste.
- Proteger equilíbrio quando necessário.
- Reconhecer transição.

### Regra

O ala contrário não deve atacar sempre a área nem permanecer sempre recuado.

---

## 19. Médio ofensivo

O MO funciona como referência de ligação e criação.

### Funções pretendidas

- Receber entre linhas.
- Aproximar-se dos médios.
- Ligar com os PL.
- Procurar passes incisivos.
- Identificar movimentos de rutura.
- Criar oportunidades.
- Explorar remate de média distância quando existe vantagem.
- Apoiar pressão defensiva.

### Regra

O MO deve procurar espaços funcionais, não apenas posicionar-se nominalmente atrás dos avançados.

---

## 20. Médio ofensivo entre linhas

### Condições para receber

- Espaço.
- Linha de passe.
- Orientação corporal.
- Apoio.
- Continuidade.

### Possíveis ações

- Rodar.
- Passar.
- Conduzir.
- Rematar.
- Ligar com PL.
- Mudar corredor.

### Riscos

- Pressão nas costas.
- Passe intercetado.
- Falta de profundidade.
- Perda central.

---

## 21. Complementaridade dos avançados

A equipa pretende dois PL com funções complementares.

### PL1 — Apoio e ligação

- Aproximar-se da bola.
- Receber de costas.
- Proteger.
- Devolver.
- Ligar com MO.
- Arrastar marcador quando possível.

### PL2 — Profundidade e finalização

- Fixar centrais.
- Atacar intervalos.
- Procurar rutura.
- Ocupar área.
- Finalizar.
- Reagir a segundas bolas.

### Regra

As funções podem alternar durante o jogo.

Não devem ser atribuídas rigidamente apenas pela posição inicial.

---

## 22. Movimento de apoio do PL

### Sequência possível

1. Médio possui bola.
2. PL1 aproxima-se.
3. Central adversário decide acompanhar ou manter.
4. PL1 oferece apoio.
5. MO aproxima-se.
6. PL2 prepara rutura.
7. Portador escolhe solução.

### Objetivos

- Criar ligação.
- Atrair defensor.
- Facilitar terceiro homem.
- Libertar espaço.

---

## 23. Movimento em L do PL

O movimento em L é uma referência pretendida para o avançado de profundidade.

### Conceito

O avançado altera a direção do deslocamento para criar separação relativamente ao defensor e atacar um espaço.

### Sequência possível

1. PL2 ocupa posição de referência.
2. Faz deslocamento inicial para condicionar ou afastar defensor.
3. Altera direção.
4. Ataca intervalo ou profundidade.
5. Procura receber em vantagem.

### Condições

- Espaço.
- Sincronização.
- Portador com tempo.
- Linha de passe.
- Controlo do fora de jogo.

### Regra

A forma do movimento deve adaptar-se à posição do defensor.

Não existe trajetória em L universal.

---

## 24. Relação PL1–PL2–MO

A ligação entre os dois avançados e o médio ofensivo é central para a identidade ofensiva.

### Combinação possível

1. MC-C encontra MO.
2. MO liga com PL1.
3. PL1 devolve.
4. PL2 ataca espaço.
5. MO procura passe de rutura.

### Alternativa

Se a linha de profundidade estiver fechada, procurar ala ou circulação.

### Regra

Não forçar combinações quando o adversário controla o espaço.

---

## 25. Transformação ofensiva em 3-4-3

Uma possibilidade é criar três referências avançadas através de movimentos do MO ou de um dos PL.

### Objetivos

- Fixar última linha.
- Aumentar ocupação ofensiva.
- Criar largura ou corredores interiores.
- Explorar profundidade.

### Regra

A transformação deve ser identificada pelas posições reais e não apenas pelo número de jogadores projetados.

---

## 26. Transformação ofensiva em 3-4-2-1

A equipa pode criar:

- Três referências na última linha de construção.
- Dois médios centrais.
- Dois alas.
- Dois jogadores entre linhas.
- Um avançado de referência.

### Exemplo funcional

```text
                         PL2

                  PL1           MO

       ALA-E       MC-R     MC-C       ALA-D

                  DCE     LIB     DCD

                          GR
```

### Objetivos

- Ocupação dos corredores interiores.
- Ligações curtas.
- Apoio ao PL.
- Possibilidade de terceiro homem.
- Largura através dos alas.

### Regra

A equipa não deve transformar-se automaticamente nesta estrutura em todas as posses.

---

## 27. Progressão pelo corredor central

### Objetivos

- Encontrar MO.
- Ligar com PL1.
- Criar terceiro homem.
- Atacar intervalos.
- Preparar remate.

### Condições

- Linha de passe.
- Pressão controlada.
- Apoios.
- Cobertura.
- Continuidade.

### Riscos

- Perda central.
- Interceção.
- Transição adversária.

---

## 28. Progressão pelo corredor exterior

### Recursos

- Ala.
- Central exterior.
- Médio próximo.
- PL que se desloca.
- MO.

### Soluções

- Triângulo exterior.
- Passe e desmarcação.
- Terceiro homem.
- Cruzamento.
- Passe atrasado.
- Mudança de corredor.

### Riscos

- Armadilha lateral.
- Falta de apoio.
- Espaço nas costas do ala.

---

## 29. Mudança de corredor

### Objetivo

Explorar o lado contrário ao da concentração defensiva.

### Possíveis ligações

- DCE → LIB → DCD.
- DCE → MC-C → ALA-D.
- ALA-E → MC-C → ALA-D.
- MO → médio → ala contrário.

### Regra

A mudança deve procurar vantagem, não ser executada apenas para circular.

---

## 30. Terceiro homem

### Exemplo

1. DCE possui bola.
2. MC-C oferece apoio.
3. MO posiciona-se entre linhas.
4. DCE encontra MC-C.
5. MC-C liga com MO.
6. MO procura continuidade.

### Regra

O terceiro homem deve ser procurado quando existe relação temporal e espacial favorável.

---

## 31. Ataque à profundidade

### Recursos

- PL2.
- PL1 em movimento.
- MO.
- Alas.
- Central exterior com passe.

### Condições

- Espaço.
- Portador com tempo.
- Movimento sincronizado.
- Linha de passe.
- Cobertura preventiva.

---

## 32. Ocupação da área

### Zonas

- Primeiro poste.
- Zona central.
- Segundo poste.
- Entrada da área.
- Segunda bola.

### Possíveis referências

- PL1.
- PL2.
- MO.
- Ala contrário.
- Médio de chegada.

### Regra

A ocupação deve ser equilibrada e evitar concentração de todos os jogadores na mesma zona.

---

## 33. Cruzamentos

### Condições

- Cruzador com tempo.
- Jogadores em zonas de finalização.
- Movimento coordenado.
- Vantagem perante defesas.

### Alternativas

- Passe atrasado.
- Combinação interior.
- Mudança de corredor.
- Circulação.

### Regra

Não cruzar automaticamente apenas porque a bola chegou ao ala.

---

## 34. Remate exterior do MO

O remate de média distância é uma possibilidade importante para o MO.

### Condições

- Espaço frontal.
- Linha de remate.
- Tempo.
- Capacidade individual.
- Preparação para ressalto.

### Regra

Não recomendar remate se existir bloqueio evidente ou oportunidade claramente superior.

---

# PARTE III — ORGANIZAÇÃO DEFENSIVA

## 35. Objetivos defensivos

A equipa pretende:

1. Proteger corredor central.
2. Manter compactação.
3. Controlar profundidade.
4. Orientar circulação adversária.
5. Pressionar com cobertura.
6. Evitar espaços entre linhas.
7. Proteger zonas libertadas pelos alas.
8. Recuperar em condições favoráveis.
9. Preparar transição ofensiva.

---

## 36. Bloco médio como referência

A equipa pretende utilizar frequentemente bloco médio.

### Características

- Linhas próximas.
- Proteção central.
- Pressão seletiva.
- Controlo de corredores interiores.
- Reação a gatilhos.
- Cobertura da última linha.

### Regra

A altura deve adaptar-se ao adversário, ao resultado e à fase do jogo.

---

## 37. Estrutura defensiva 5-3-2

Representação funcional:

```text
                    PL1       PL2

                MC-R     MO     MC-C

       ALA-E    DCE     LIB     DCD    ALA-D

                          GR
```

### Princípios

- Cinco referências na última linha.
- Três médios a proteger o centro.
- Dois avançados a condicionar construção.
- Compactação.
- Coberturas.

### Nota

O MO pode subir para pressionar com os PL, alterando temporariamente a estrutura.

---

## 38. Estrutura defensiva 5-2-1-2

### Situação

O MO aproxima-se dos avançados ou posiciona-se entre estes e os dois médios.

```text
                    PL1       PL2

                         MO

                   MC-R      MC-C

       ALA-E    DCE     LIB     DCD    ALA-D

                          GR
```

### Objetivos

- Condicionar pivô.
- Apoiar pressão.
- Manter dois médios centrais.
- Proteger última linha.

### Riscos

- Espaço entre MO e médios.
- Dois médios sobrecarregados.
- Dificuldade em controlar três interiores.

---

## 39. Primeira linha de pressão

### Referências

- PL1.
- PL2.
- MO em apoio.

### Objetivos

- Condicionar centrais.
- Fechar passe interior.
- Orientar circulação.
- Reconhecer gatilho.
- Evitar pressão individual descoordenada.

---

## 40. Papel defensivo do MO

O MO deve apoiar a pressão dos avançados e a proteção central.

### Comportamentos

- Controlar pivô.
- Fechar linha interior.
- Aproximar-se do portador quando existe gatilho.
- Recuperar para a linha média.
- Comunicar.

### Regra

Não deve permanecer permanentemente alto se a equipa perder proteção central.

---

## 41. Papel defensivo dos médios

### MC-R

- Proteger zona central.
- Recuperar.
- Intercetar.
- Cobrir corredor libertado.
- Apoiar pressão.

### MC-C

- Fechar linhas.
- Controlar espaço.
- Recuperar.
- Apoiar coberturas.
- Preparar primeira ligação após recuperação.

### Regra

A responsabilidade defensiva é coletiva.

---

## 42. Papel defensivo dos alas

### Princípio pretendido

Os alas devem fechar por dentro para proteger os corredores interiores, ajustando a largura conforme a bola e a posição do adversário.

### Comportamentos

- Recuperar.
- Fechar espaço interior.
- Controlar extremo.
- Saltar ao lateral adversário quando existe gatilho.
- Coordenar com central exterior.
- Proteger profundidade.

### Regra

Fechar por dentro não significa abandonar permanentemente o corredor exterior.

---

## 43. Ala a pressionar lateral adversário

### Sequência possível

1. Bola chega ao lateral adversário.
2. Ala reconhece gatilho.
3. Ala aproxima-se.
4. Central exterior controla espaço nas costas.
5. Médio do lado ajusta.
6. PL condiciona retorno.
7. Equipa procura recuperação.

### Riscos

- Ala sair demasiado cedo.
- Central exterior ficar isolado.
- Médio não cobrir.
- Passe nas costas.

---

## 44. Central exterior a sair à marcação

### Condições

- Adversário recebe na zona.
- Existe cobertura do líbero.
- Médio ajusta.
- Ala controla espaço exterior.
- O risco de profundidade é aceitável.

### Regra

Não transformar os centrais exteriores em marcadores individuais permanentes.

---

## 45. Líbero em cobertura

### Princípio

O líbero mantém responsabilidade prioritária sobre o espaço central e a profundidade.

### Ações

- Ajustar.
- Cobrir.
- Antecipar.
- Coordenar.
- Controlar movimentos.
- Comunicar.

### Regra

A saída do líbero deve ser excecional ou compensada.

---

## 46. Proteção dos corredores interiores

### Referências

- Médios.
- Alas a fechar.
- Centrais exteriores.
- Líbero.

### Objetivos

- Impedir passe vertical.
- Reduzir espaço entre linhas.
- Controlar diagonais.
- Proteger intervalos.

---

## 47. Proteção do corredor exterior

### Situação

Adversário procura progressão pela ala.

### Possíveis respostas

- Ala pressiona.
- Central exterior cobre.
- Médio ajusta.
- Líbero protege centro.
- Ala contrário fecha.

### Regra

A resposta depende da altura da bola e da estrutura adversária.

---

## 48. Compactação vertical

### Objetivo

Manter proximidade entre:

- PL e MO.
- MO e médios.
- Médios e defesas.

### Riscos

- MO demasiado alto.
- Médios demasiado baixos.
- Avançados isolados.
- Espaço entre linhas.

---

## 49. Compactação horizontal

### Objetivo

Proteger centro e permitir deslocamento coordenado.

### Riscos

- Ala contrário demasiado afastado.
- Central exterior isolado.
- Médio não acompanhar.
- Espaço no corredor contrário.

---

## 50. Gatilhos de pressão

Possíveis gatilhos:

- Passe para lateral.
- Passe atrasado.
- Receção de costas.
- Mau controlo.
- Passe lento.
- Jogador isolado.
- Linha interior fechada.

### Regra

O gatilho deve ativar comportamento coletivo, não apenas corrida de um jogador.

---

## 51. Pressão após passe lateral

### Sequência

1. PL condiciona circulação.
2. Bola chega ao lateral.
3. Ala aproxima-se.
4. Médio fecha apoio interior.
5. Central exterior cobre profundidade.
6. MO ajusta.
7. Equipa procura recuperação.

### Riscos

- Passe interior.
- Passe nas costas.
- Mudança de corredor.
- Pressão descoordenada.

---

## 52. Defesa de cruzamentos

### Prioridades

- Pressionar cruzador.
- Controlar primeiro poste.
- Proteger zona central.
- Controlar segundo poste.
- Preparar segunda bola.
- Coordenar GR e defesas.

### Regra

A defesa do cruzamento começa antes da execução.

---

## 53. Defesa da profundidade

### Responsabilidades

- Líbero controla espaço central.
- Centrais exteriores ajustam.
- Alas recuperam.
- Médios protegem primeira ligação.
- GR coordena quando possível.

### Regra

A última linha não deve subir ou recuar sem coordenação.

---

# PARTE IV — TRANSIÇÃO OFENSIVA

## 54. Objetivo da transição ofensiva

Após recuperar a bola, a equipa pretende reconhecer rapidamente se existe possibilidade de progressão vantajosa.

### Prioridades

1. Proteger a primeira posse.
2. Identificar espaço.
3. Reconhecer pressão.
4. Encontrar apoio ou profundidade.
5. Explorar desorganização adversária.
6. Evitar perdas precipitadas.

---

## 55. Recuperação em zona baixa

### Soluções possíveis

- Passe seguro.
- Ligação ao médio construtor.
- Apoio do PL1.
- Passe para ala livre.
- Ataque à profundidade quando existe espaço.

### Regra

Não procurar contra-ataque direto sem condições.

---

## 56. Recuperação em zona intermédia

### Soluções possíveis

- Passe vertical para MO.
- PL1 em apoio.
- PL2 em profundidade.
- Ala em progressão.
- Mudança de corredor.

### Riscos

- Perda imediata.
- Falta de apoio.
- Passe intercetado.

---

## 57. Recuperação em zona alta

### Objetivos

- Explorar proximidade da baliza.
- Identificar finalização.
- Encontrar jogador livre.
- Atacar antes da reorganização.

### Regra

A velocidade de decisão deve ser acompanhada por qualidade.

---

## 58. Primeira ligação após recuperação

### Referências

- MC-C.
- MO.
- PL1.
- Ala.
- PL2 em profundidade.

### Regra

A melhor primeira ligação depende da pressão e das linhas disponíveis.

---

## 59. Relação entre PL1 e PL2 na transição

### PL1

- Aproximar.
- Receber.
- Proteger.
- Ligar.

### PL2

- Atacar espaço.
- Fixar central.
- Procurar rutura.
- Preparar finalização.

### Regra

As funções podem inverter-se conforme a recuperação.

---

# PARTE V — TRANSIÇÃO DEFENSIVA

## 60. Objetivo da transição defensiva

Após perder a bola, a equipa pretende impedir que o adversário explore a desorganização momentânea.

### Prioridades

1. Reconhecer localização da perda.
2. Proteger centro.
3. Avaliar recuperação imediata.
4. Controlar profundidade.
5. Temporizar se necessário.
6. Reorganizar.

---

## 61. Contra-pressão

### Condições

- Jogadores próximos.
- Cobertura.
- Distâncias adequadas.
- Possibilidade de recuperação.
- Risco aceitável.

### Regra

A contra-pressão não deve ser automática quando expõe a última linha.

---

## 62. Temporização

### Objetivo

Atrasar a progressão adversária.

### Comportamentos

- Condicionar portador.
- Proteger passe interior.
- Controlar profundidade.
- Recuperar posições.
- Evitar duelo precipitado.

---

## 63. Reorganização para 5-3-2

### Sequência possível

1. Perda da bola.
2. Médios protegem centro.
3. Alas recuperam.
4. Centrais ajustam.
5. MO regressa à linha média.
6. PL condicionam construção.
7. Equipa recupera compactação.

### Regra

A reorganização depende da posição real dos jogadores no momento da perda.

---

## 64. Cobertura do espaço nas costas dos alas

### Situação

Ala encontra-se projetado quando a equipa perde a bola.

### Possíveis compensações

- Central exterior controla corredor.
- Médio próximo fecha.
- Líbero ajusta.
- Ala recupera.
- Restantes jogadores protegem centro.

### Regra

O central exterior não deve abandonar o centro sem considerar a cobertura.

---

## 65. Proteção dos centrais

### Objetivos

- Evitar igualdade numérica desfavorável.
- Controlar profundidade.
- Reduzir duelos isolados.
- Proteger corredor central.

### Regra

A proteção deve começar antes da perda através do equilíbrio preventivo.

---

# PARTE VI — COMPORTAMENTOS POR ZONA

## 66. Zona defensiva central

### Com bola

- Circular.
- Criar apoios.
- Reconhecer pressão.
- Preparar progressão.

### Sem bola

- Proteger baliza.
- Controlar profundidade.
- Cobrir.
- Comunicar.

---

## 67. Corredores defensivos

### Com bola

- Criar linha exterior.
- Ligar com ala.
- Evitar isolamento.

### Sem bola

- Controlar profundidade.
- Coordenar ala e central exterior.
- Proteger espaço interior.

---

## 68. Zona intermédia central

### Com bola

- Criar linhas.
- Receber orientado.
- Ligar setores.
- Preparar progressão.

### Sem bola

- Fechar linhas.
- Proteger espaço.
- Apoiar pressão.
- Recuperar.

---

## 69. Corredores intermédios

### Com bola

- Triângulos.
- Apoios.
- Progressão.
- Mudança de corredor.

### Sem bola

- Compactação.
- Cobertura.
- Pressão seletiva.
- Controlo de diagonais.

---

## 70. Último terço

### Com bola

- Ocupação entre linhas.
- Movimentos de apoio.
- Rutura.
- Cruzamento condicionado.
- Passe atrasado.
- Remate.

### Sem bola

- Pressão após gatilho.
- Proteção central.
- Preparação de recuperação.
- Equilíbrio.

---

# PARTE VII — ADAPTAÇÕES AOS ADVERSÁRIOS

## 71. Perante 4-4-2

### Problemas possíveis

- Dois PL condicionam construção.
- Duas linhas de quatro.
- Proteção central.

### Soluções possíveis

- Terceiro central livre.
- MC-C em apoio.
- MO entre linhas.
- Ala em largura.
- PL1 em apoio e PL2 em profundidade.

### Riscos

- Passe interior bloqueado.
- Pressão sobre ala.
- Contra-ataque por dois PL.

---

## 72. Perante 4-3-3

### Problemas possíveis

- Três avançados pressionam centrais.
- Pivô controlado.
- Alas pressionados.

### Soluções possíveis

- GR como apoio.
- Movimentos dos médios.
- Terceiro homem.
- PL1 em apoio.
- Passe direto condicionado.

### Riscos

- Perda central.
- Pressão coordenada.
- Espaço nas costas dos alas.

---

## 73. Perante 4-2-3-1

### Problemas possíveis

- PL condiciona construção.
- MO controla pivô.
- Duplo pivô protege espaço central.

### Soluções possíveis

- Central exterior em condução.
- MC-C ajustar altura.
- MO entre linhas.
- Ala com largura.
- Movimento complementar dos PL.

### Riscos

- Duplo pivô controlar MO.
- Extremos pressionarem alas.
- Perda central.

---

## 74. Perante 3-5-2

### Problemas possíveis

- Estruturas semelhantes.
- Alas em confronto direto.
- Três médios centrais.
- Dois PL.

### Soluções possíveis

- Mobilidade do MO.
- Movimentos alternados dos PL.
- Central exterior em condução.
- Mudança de corredor.
- Superioridade funcional exterior.

### Riscos

- Igualdades posicionais.
- Alas isolados.
- Transição nas costas.

---

## 75. Perante 3-4-3

### Problemas possíveis

- Três avançados.
- Dois médios centrais.
- Alas altos.
- Três centrais.

### Soluções possíveis

- Superioridade central.
- MO entre linhas.
- Terceiro homem.
- Ataque nas costas do ala.
- Mudança de corredor.

### Riscos

- Pressão dos três avançados.
- Perda central.
- Centrais exteriores expostos.

---

# PARTE VIII — PROBLEMAS A MONITORIZAR

## 76. Dificuldade na saída de bola

Este é um dos aspetos anteriormente identificados como preocupação da equipa técnica.

### Possíveis causas a investigar

- Distâncias inadequadas.
- Médios escondidos.
- Centrais sem linhas.
- Alas demasiado altos.
- Falta de apoio do GR.
- Pressão adversária.
- Receções sem orientação.

### Regra

A IA não deve atribuir a dificuldade a uma causa sem observação.

---

## 77. Dificuldade após a primeira fase

Outro aspeto identificado é a manutenção da posse após ultrapassar a construção inicial.

### Possíveis causas

- Falta de apoios.
- Distância entre setores.
- MO isolado.
- PL sem ligação.
- Médios na mesma altura.
- Alas afastados.
- Progressão precipitada.

### Soluções a avaliar

- Apoio do PL1.
- Aproximação do MO.
- Terceiro homem.
- Circulação.
- Movimentos alternados.
- Melhor ocupação interior.

---

## 78. Intensidade coletiva

A intensidade deve ser avaliada em diferentes dimensões.

### Intensidade física

- Acelerações.
- Recuperações.
- Repetição de esforços.

### Intensidade tática

- Velocidade de reação.
- Coordenação.
- Ocupação.
- Coberturas.

### Intensidade técnica

- Velocidade de execução.
- Qualidade sob pressão.
- Orientação.

### Regra

Não reduzir intensidade apenas à quantidade de corrida.

---

## 79. Distâncias entre setores

### Observar

- Centrais e médios.
- Médios e MO.
- MO e PL.
- Ala e central exterior.
- Ala e médio próximo.

### Problemas possíveis

- Falta de apoio.
- Passe demasiado longo.
- Pressão sobre recetor.
- Falta de cobertura.
- Espaço entre linhas.

---

## 80. Equilíbrio ofensivo

### Observar

- Quantos jogadores atacam.
- Quem protege centro.
- Quem controla profundidade.
- Qual é a posição dos alas.
- Qual é a posição dos centrais exteriores.
- Qual é a cobertura do líbero.

### Regra

A estrutura preventiva deve ser adequada à ameaça adversária.

---

# PARTE IX — INDICADORES DE AVALIAÇÃO

## 81. Indicadores ofensivos

Podem incluir:

- Saídas de bola concluídas.
- Progressões para segunda fase.
- Perdas na construção.
- Receções entre linhas.
- Ligações com MO.
- Apoios dos PL.
- Mudanças de corredor eficazes.
- Entradas no último terço.
- Entradas na área.
- Oportunidades de finalização.

### Regra

Os indicadores devem ser definidos operacionalmente antes da recolha.

---

## 82. Indicadores defensivos

Podem incluir:

- Recuperações por zona.
- Passes interiores concedidos.
- Situações entre linhas.
- Cruzamentos permitidos.
- Remates concedidos.
- Duelos defensivos.
- Coberturas.
- Transições sofridas.
- Profundidade concedida.

---

## 83. Indicadores das transições

### Transição ofensiva

- Tempo até primeira ligação.
- Progressão após recuperação.
- Contra-ataques.
- Perdas imediatas.

### Transição defensiva

- Reação após perda.
- Recuperações rápidas.
- Progressões adversárias.
- Situações de inferioridade.
- Reorganização.

### Regra

Não inventar valores, médias ou percentagens.

---

## 84. Avaliação por vídeo

Sempre que existir vídeo, a análise deve procurar:

1. Identificar o momento.
2. Descrever a estrutura.
3. Reconhecer comportamento.
4. Comparar com o modelo.
5. Identificar desvio.
6. Avaliar consequência.
7. Formular hipótese.
8. Propor correção.
9. Identificar alternativa.

---

## 85. Avaliação por eventos

Se apenas existirem eventos, a IA pode identificar padrões estatísticos, mas deve evitar afirmar posicionamentos ou coberturas não observados.

### Exemplo

Várias perdas no corredor direito podem justificar investigação.

Não provam, por si só, que o ala direito esteja mal posicionado.

---

# PARTE X — CASOS PRÁTICOS

## 86. Caso A — Saída perante dois avançados

**Situação:** adversário pressiona com dois PL.

**Objetivo:** encontrar jogador livre.

**Sequência possível:**

1. LIB possui bola.
2. DCE e DCD oferecem largura.
3. MC-C ajusta posição.
4. GR oferece apoio.
5. Adversário condiciona.
6. LIB avalia central exterior ou médio.

**Risco:** passe central intercetado.

---

## 87. Caso B — Central exterior em condução

**Situação:** adversário permite espaço.

**Objetivo:** atrair médio.

**Sequência possível:**

1. DCE recebe.
2. Identifica espaço.
3. Conduz.
4. Médio adversário aproxima-se.
5. MC-C oferece linha.
6. ALA-E mantém largura.
7. DCE decide.

**Risco:** perda sem cobertura.

---

## 88. Caso C — PL1 em apoio e PL2 em rutura

**Situação:** equipa procura ligação interior.

**Objetivo:** criar profundidade.

**Sequência possível:**

1. MC-C possui bola.
2. PL1 aproxima-se.
3. MO oferece apoio.
4. PL2 prepara movimento em L.
5. PL1 recebe.
6. Devolve ao MO.
7. MO procura PL2.

**Risco:** passe intercetado ou fora de jogo.

---

## 89. Caso D — MO com espaço frontal

**Situação:** adversário recua.

**Objetivo:** criar finalização.

**Sequência possível:**

1. PL fixa central.
2. MO recebe.
3. Identifica espaço.
4. Avalia remate.
5. Se não existir linha, procura passe.

**Risco:** remate bloqueado.

---

## 90. Caso E — Ala a pressionar lateral

**Situação:** adversário circula para lateral.

**Objetivo:** recuperar ou condicionar.

**Sequência possível:**

1. PL condiciona retorno.
2. ALA-E salta.
3. MC-R fecha interior.
4. DCE cobre profundidade.
5. LIB protege centro.

**Risco:** passe nas costas do ala.

---

## 91. Caso F — Líbero em cobertura

**Situação:** DCD sai para pressionar.

**Objetivo:** proteger espaço central.

**Sequência possível:**

1. DCD aproxima-se.
2. LIB ajusta.
3. DCE fecha.
4. MC-R protege frente.
5. ALA-D recupera.

**Risco:** deslocamento descoordenado.

---

## 92. Caso G — Recuperação em bloco médio

**Situação:** MC-R recupera bola.

**Objetivo:** explorar transição.

**Sequência possível:**

1. MC-R recupera.
2. MC-C oferece apoio.
3. PL1 aproxima-se.
4. PL2 ataca profundidade.
5. MO procura ligação.
6. Portador decide.

**Risco:** perda imediata.

---

## 93. Caso H — Perda com alas altos

**Situação:** equipa perde bola no último terço.

**Objetivo:** impedir contra-ataque.

**Sequência possível:**

1. Portador perde.
2. MC-R protege centro.
3. Central exterior controla corredor.
4. LIB controla profundidade.
5. Ala recupera.
6. Equipa avalia contra-pressão ou temporização.

**Risco:** central exterior ficar isolado.

---

## 94. Caso I — 3-4-2-1 em ataque

**Situação:** PL1 baixa para corredor interior.

**Objetivo:** criar ligação.

**Sequência possível:**

1. PL2 fixa centrais.
2. PL1 ocupa espaço interior.
3. MO ocupa corredor interior contrário.
4. Alas mantêm largura.
5. Médios equilibram.
6. Central procura progressão.

**Risco:** perda de presença na área ou desequilíbrio.

---

## 95. Caso J — Adversário em bloco baixo

**Situação:** adversário protege área.

**Objetivo:** criar oportunidade.

**Sequência possível:**

1. Equipa circula.
2. Ala mantém largura.
3. PL1 aproxima-se.
4. MO ocupa espaço frontal.
5. PL2 fixa.
6. Equipa procura combinação.
7. Avalia passe atrasado ou remate.

**Risco:** contra-ataque.

---

## 96. Caso K — Adversário pressiona três centrais

**Situação:** adversário utiliza três referências avançadas.

**Objetivo:** ultrapassar pressão.

**Sequência possível:**

1. GR identifica pressão.
2. MC-C ajusta.
3. MC-R oferece linha alternativa.
4. PL1 prepara apoio.
5. Ala procura espaço.
6. Equipa avalia terceiro homem ou jogo direto.

**Risco:** perda central.

---

## 97. Caso L — Falta de ligação após construção

**Situação:** equipa ultrapassa primeira linha mas perde posse na segunda fase.

**Objetivo:** melhorar continuidade.

**Sequência possível:**

1. DCE progride.
2. MC-C oferece apoio.
3. MO aproxima-se.
4. PL1 baixa.
5. PL2 mantém profundidade.
6. ALA-E mantém largura.
7. Equipa procura ligação.

**Risco:** concentração de jogadores no mesmo espaço.

---

# PARTE XI — REGRAS PARA O ASSISTENTE DE IA

## 98. Modelo pretendido versus modelo observado

A IA deve distinguir:

**Modelo pretendido:** comportamentos definidos pela equipa técnica.

**Modelo observado:** comportamentos efetivamente identificados.

**Desvio:** diferença entre intenção e execução.

**Adaptação:** alteração contextual deliberada.

### Regra

Nem toda a diferença relativamente ao modelo é um erro.

---

## 99. Classificação das recomendações

### Compatível

Respeita os princípios e funções pretendidas.

### Compatível com adaptação

Exige ajuste justificado, mas mantém a identidade coletiva.

### Contraditória

Viola um princípio central sem compensação.

### Informação insuficiente

Não existem dados para avaliar.

---

## 100. Perguntas obrigatórias

Antes de recomendar uma alteração, a IA deve verificar:

1. Qual é a fase do jogo?
2. Qual é a estrutura real?
3. Qual é a estrutura adversária?
4. Qual é o problema observado?
5. Existe evidência?
6. O problema é individual ou coletivo?
7. Qual é o princípio afetado?
8. Qual é a função pretendida?
9. O jogador tem capacidade demonstrada?
10. Existe espaço?
11. Existe linha de passe?
12. Existe apoio?
13. Existe cobertura?
14. Existe profundidade?
15. Existe largura?
16. Qual é o risco?
17. Qual é a alternativa?
18. A solução respeita o modelo?
19. Exige treino?
20. Qual é o grau de confiança?

---

## 101. Recomendações de treino

A IA pode sugerir exercícios relacionados com problemas observados.

### Exemplos

**Problema:** falta de apoio na segunda fase.

**Possível exercício:** jogo posicional com zonas de ligação e terceiro homem.

**Problema:** ala salta sem cobertura.

**Possível exercício:** situação lateral com ala, médio e central exterior.

**Problema:** PL1 e PL2 não coordenam movimentos.

**Possível exercício:** combinação de apoio, devolução e rutura.

### Regra

A proposta deve especificar objetivo, organização, regras, critérios de sucesso e progressão.

---

## 102. Recomendações durante o jogo

Devem ser:

- Curtas.
- Claras.
- Aplicáveis.
- Ligadas a uma observação.
- Compatíveis com o contexto.

### Exemplo

"Quando o central exterior tiver espaço, pode conduzir para atrair o médio. O construtor oferece apoio e o recuperador mantém cobertura."

---

## 103. Recomendações pós-jogo

Devem apresentar:

1. Situação observada.
2. Evidência.
3. Princípio pretendido.
4. Desvio ou adaptação.
5. Consequência.
6. Possível causa.
7. Correção.
8. Exercício.
9. Indicador de avaliação.

---

## 104. Informação insuficiente

A IA deve reconhecer limites quando:

- Não existe vídeo.
- Não existem dados posicionais.
- A descrição é incompleta.
- Não se conhecem capacidades.
- Não se conhece a intenção da equipa técnica.
- Não existe evidência de repetição.

### Regra

Não inventar características de jogadores nem situações de jogo.

---

## 105. Hierarquia dos documentos da equipa

Este documento define a identidade geral.

Os restantes documentos aprofundam:

- Princípios ofensivos.
- Princípios defensivos.
- Princípios transversais.
- Características dos jogadores.

Em caso de aparente contradição, a IA deve:

1. Identificar o conflito.
2. Verificar se corresponde a uma adaptação contextual.
3. Priorizar instruções explícitas e atuais da equipa técnica.
4. Explicar a interpretação.
5. Solicitar esclarecimento quando necessário.

---

# PARTE XII — RELAÇÃO COM OUTROS DOCUMENTOS

## 106. Fundamentos

- `conhecimento/fundamentos/fases_jogo.md`
- `conhecimento/fundamentos/principios_ofensivos.md`
- `conhecimento/fundamentos/principios_defensivos.md`
- `conhecimento/fundamentos/superioridades.md`
- `conhecimento/fundamentos/modelos_jogo.md`

## 107. Sistemas táticos

- `conhecimento/sistemas/352/organizacao.md`
- `conhecimento/sistemas/352/saida_bola.md`
- `conhecimento/sistemas/352/ataque.md`
- `conhecimento/sistemas/352/defesa.md`
- `conhecimento/sistemas/352/transicoes.md`
- `conhecimento/sistemas/343/organizacao.md`
- `conhecimento/sistemas/343/ataque.md`
- `conhecimento/sistemas/343/defesa.md`
- `conhecimento/sistemas/343/transicoes.md`

## 108. Adversários

- `conhecimento/adversarios/estruturas_taticas.md`
- `conhecimento/adversarios/pressao_alta.md`
- `conhecimento/adversarios/bloco_medio.md`
- `conhecimento/adversarios/bloco_baixo.md`
- `conhecimento/adversarios/analise_vulnerabilidades.md`

## 109. Documentos específicos da equipa

- `conhecimento/equipa/principios_ofensivos.md`
- `conhecimento/equipa/principios_defensivos.md`
- `conhecimento/equipa/principios_equipa.md`
- `conhecimento/equipa/caracteristicas_jogadores.md`

---

# PARTE XIII — PRINCÍPIO FINAL

## 110. Princípio central

O modelo de jogo dos Sub-19 do CCDR Vila Cortez do Mondego assenta numa estrutura-base 3-5-2, com funções complementares entre jogadores e capacidade de adaptação às diferentes fases do jogo.

Os elementos centrais são:

- Líbero responsável pela cobertura e proteção da profundidade.
- Centrais exteriores participantes na construção e na proteção dos corredores.
- Dois médios complementares: recuperador e construtor.
- Alas responsáveis pela largura ofensiva e recuperação defensiva.
- Médio ofensivo responsável pela ligação, criação, passes incisivos e possibilidade de remate exterior.
- Dois avançados complementares, com movimentos de apoio e rutura.
- Transformações ofensivas possíveis para 3-4-3 ou 3-4-2-1.
- Organização defensiva frequentemente em bloco médio, com referência ao 5-3-2.
- Proteção central, compactação e pressão coordenada.
- Transições condicionadas à vantagem e ao equilíbrio coletivo.

A IA deve utilizar este modelo para interpretar comportamentos, diagnosticar problemas e propor soluções.

Não deve confundir intenções com resultados observados, nem considerar que todos os jogadores possuem automaticamente as capacidades necessárias.

O objetivo final é apoiar a equipa técnica na construção de uma identidade coletiva reconhecível, eficaz, treinável e adaptável ao adversário.