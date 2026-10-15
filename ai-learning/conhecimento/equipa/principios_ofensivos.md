# Princípios Ofensivos — Sub-19 CCDR Vila Cortez do Mondego

## 1. Objetivo do documento

Este documento define os princípios, comportamentos, mecanismos e critérios de decisão ofensivos pretendidos para os Sub-19 do CCDR Vila Cortez do Mondego.

A sua finalidade é apoiar a equipa técnica e permitir que o assistente de inteligência artificial:

- Compreenda a nossa identidade ofensiva.
- Reconheça as funções e relações entre jogadores.
- Analise a construção, progressão e criação.
- Identifique dificuldades na manutenção da posse.
- Relacione soluções com a organização adversária.
- Recomende correções concretas.
- Preserve o equilíbrio preventivo.
- Diferencie intenções táticas de comportamentos observados.
- Proponha exercícios adequados aos problemas identificados.

O documento não pressupõe que todos os comportamentos já estejam consolidados.

**Princípio central:**

Queremos uma equipa capaz de construir com critério, progredir com apoios e mobilidade, criar vantagens nos corredores interiores e exteriores e finalizar com ocupação coordenada dos espaços, sem comprometer desnecessariamente a proteção perante a perda.

---

# PARTE I — IDENTIDADE OFENSIVA

## 2. Estrutura-base

A referência inicial é o **3-5-2**, com:

- Três centrais.
- Dois alas.
- Dois médios de funções complementares.
- Um médio ofensivo.
- Dois avançados.

Representação funcional:

```text
                    PL1       PL2

                         MO

                  MC-R       MC-C

      ALA-E                              ALA-D

                 DCE     LIB     DCD

                          GR
```

**Legenda:**

- PL1: avançado predominantemente de apoio e ligação.
- PL2: avançado predominantemente de profundidade.
- MO: médio ofensivo.
- MC-R: médio recuperador.
- MC-C: médio construtor/distribuidor.
- ALA-E e ALA-D: alas.
- DCE e DCD: centrais exteriores.
- LIB: líbero.
- GR: guarda-redes.

As posições representam referências, não coordenadas fixas.

---

## 3. Estruturas ofensivas possíveis

A equipa pode assumir diferentes estruturas durante a posse.

### 3-5-2

Mantém dois avançados, três médios e alas exteriores.

### 3-4-1-2

Destaca o MO atrás dos dois PL.

### 3-4-2-1

PL1 e MO ocupam zonas de ligação atrás de PL2.

### 3-4-3

Três referências avançadas, mediante movimentos dos jogadores.

### Regra

A IA deve identificar a estrutura real através das posições e relações observadas.

Não deve concluir que existe uma transformação apenas porque um jogador se deslocou pontualmente.

---

## 4. Objetivos ofensivos prioritários

1. Garantir soluções de passe.
2. Ultrapassar a primeira linha adversária.
3. Manter posse com capacidade de progressão.
4. Ligar construção e ataque.
5. Criar superioridades.
6. Utilizar os cinco corredores verticais.
7. Relacionar MO e avançados.
8. Criar profundidade.
9. Explorar largura através dos alas.
10. Chegar a situações de finalização favoráveis.
11. Preparar a reação à perda.

---

## 5. Posse com intenção

A posse deve permitir controlar, deslocar ou ultrapassar o adversário.

### Circulação útil

- Atrai pressão.
- Cria linha de passe.
- Muda corredor.
- Permite progressão.
- Reorganiza apoios.
- Prepara uma ação posterior.

### Circulação estéril

- Repete passes sem vantagem.
- Não altera a organização adversária.
- Não prepara progressão.
- Aumenta risco desnecessário.

### Regra

Não confundir número de passes com qualidade da posse.

---

## 6. Progressão com critério

A equipa deve procurar avançar quando existir vantagem.

### Critérios

- Linha de passe disponível.
- Recetor orientado.
- Espaço acessível.
- Apoios próximos.
- Continuidade.
- Cobertura preventiva.

### Regra

Progredir não significa forçar constantemente o passe vertical.

---

## 7. Largura e profundidade

A largura pretende:

- Alongar o bloco adversário.
- Criar corredores.
- Facilitar mudanças de flanco.
- Libertar espaços interiores.

A profundidade pretende:

- Fixar a última linha.
- Criar ameaça nas costas.
- Aumentar distância entre setores.
- Abrir espaço para apoios.

### Regra

Largura e profundidade devem ser coordenadas.

---

## 8. Mobilidade funcional

A mobilidade deve produzir vantagem, não apenas movimento.

### Exemplos

- PL1 baixa para ligar.
- PL2 ataca profundidade.
- MO ocupa intervalo.
- MC-C ajusta altura.
- Ala ataca espaço.
- Central exterior conduz.

### Regra

Movimentos simultâneos não devem deixar a mesma zona desocupada sem intenção.

---

## 9. Complementaridade

As funções devem criar relações.

### Relações prioritárias

- DCE–MC-C–ALA-E.
- DCD–MC-C–ALA-D.
- MC-R–MC-C.
- MC-C–MO.
- MO–PL1.
- PL1–PL2.
- MO–PL2.
- Ala–PL–MO.

### Regra

A localização real dos jogadores determina quais as relações disponíveis.

---

## 10. Equilíbrio preventivo

Durante o ataque, a equipa deve conservar capacidade de proteger a perda.

### Observar

- Posicionamento dos centrais.
- Função do líbero.
- Posição do recuperador.
- Projeção dos alas.
- Número de adversários preparados para transição.
- Distâncias entre jogadores.

### Regra

Não definir uma estrutura preventiva fixa sem considerar a ameaça adversária.

---

# PARTE II — PRIMEIRA FASE DE CONSTRUÇÃO

## 11. Objetivo da primeira fase

Ultrapassar a primeira linha de pressão mantendo possibilidade de continuidade.

### Referências

- GR.
- LIB.
- DCE.
- DCD.
- MC-R.
- MC-C.
- Alas quando necessário.

---

## 12. Construção com três centrais

### Organização pretendida

- LIB como referência central.
- DCE aberto à esquerda.
- DCD aberto à direita.
- Médios em alturas complementares.
- Alas como soluções exteriores.

### Objetivos

- Criar linhas de passe.
- Encontrar jogador livre.
- Atrair pressão.
- Preparar progressão.

### Regra

A distância entre centrais deve ajustar-se à pressão e às dimensões do espaço disponível.

---

## 13. Papel do guarda-redes

O GR pode ser utilizado como apoio para:

- Criar superioridade.
- Mudar corredor.
- Ultrapassar pressão.
- Reorganizar construção.

### Condições

- Qualidade técnica demonstrada.
- Linhas disponíveis.
- Pressão controlável.
- Comunicação.

### Alternativa

Se a pressão impedir construção segura, considerar passe mais longo com preparação da segunda bola.

---

## 14. Papel do líbero na construção

### Comportamentos

- Oferecer apoio central.
- Circular.
- Orientar.
- Reconhecer pressão.
- Encontrar central exterior.
- Controlar profundidade.

### Regra

O líbero não deve abandonar automaticamente a sua função de equilíbrio para conduzir.

Pode fazê-lo quando existir compensação.

---

## 15. Papel dos centrais exteriores

### Comportamentos

- Abrir linha de passe.
- Receber orientados.
- Fixar primeiro adversário.
- Conduzir.
- Encontrar médio.
- Ligar com ala.
- Procurar passe vertical.

### Regra

A condução deve ter objetivo.

Conduzir sem atrair adversário ou criar vantagem pode aumentar exposição à perda.

---

## 16. Condução do central exterior

### Sequência possível

1. DCE recebe.
2. Identifica espaço.
3. Conduz.
4. Médio adversário aproxima-se.
5. MC-C oferece apoio.
6. ALA-E mantém largura.
7. MO procura intervalo.
8. DCE decide.

### Alternativas

- Passe interior.
- Passe exterior.
- Mudança de corredor.
- Recuar e circular.

---

## 17. Alturas dos médios

MC-R e MC-C não devem permanecer automaticamente na mesma linha.

### Possibilidade A

MC-C baixa para construir; MC-R mantém equilíbrio.

### Possibilidade B

MC-R oferece apoio curto; MC-C procura receção mais avançada.

### Possibilidade C

Ambos ajustam de forma assimétrica à pressão.

### Regra

A altura depende do espaço e da estrutura adversária.

---

## 18. Médio recuperador na construção

### Funções

- Apoio.
- Proteção.
- Circulação.
- Cobertura.
- Preparação de reação à perda.

### Erros a evitar

- Esconder-se atrás do adversário.
- Aproximar-se sem criar linha.
- Abandonar proteção central sem compensação.

---

## 19. Médio construtor na construção

### Funções

- Criar linha.
- Receber orientado.
- Reconhecer pressão.
- Definir ritmo.
- Mudar corredor.
- Ligar com MO.
- Procurar passe progressivo.

### Erros a evitar

- Receber sem apoio.
- Ficar permanentemente na linha dos centrais.
- Procurar passe difícil sem vantagem.

---

## 20. Ala na primeira fase

O ala pode:

- Manter largura.
- Aproximar-se.
- Oferecer apoio exterior.
- Fixar lateral adversário.
- Atacar espaço após passe.

### Regra

A altura do ala depende da pressão e da cobertura defensiva.

---

## 21. Construção perante um avançado

### Possível vantagem

Três centrais perante um PL podem permitir circulação e progressão.

### Soluções

- Central livre conduz.
- Médio oferece linha.
- Ala fixa largura.
- MO prepara receção.

### Regra

A superioridade numérica não garante progressão se outras linhas adversárias fecharem o espaço.

---

## 22. Construção perante dois avançados

### Possível vantagem

Três centrais perante dois PL.

### Soluções

- Encontrar central livre.
- Utilizar GR.
- Criar apoio do MC-C.
- Conduzir.
- Mudar corredor.

### Riscos

- PL condicionarem linhas interiores.
- Pressão após passe lateral.
- Armadilha sobre central exterior.

---

## 23. Construção perante três avançados

### Problema

Os três centrais podem ser pressionados individualmente.

### Soluções possíveis

- GR como apoio.
- Médio a baixar.
- Terceiro homem.
- Ala como saída.
- Passe mais longo para PL1.
- Ataque à segunda bola.

### Regra

Não forçar passe curto quando a pressão elimina as linhas.

---

## 24. Construção perante pressão alta

### Objetivo

Ultrapassar pressão mantendo equilíbrio.

### Mecanismos

- Atrair e libertar.
- Terceiro homem.
- Mudança de corredor.
- GR.
- Central exterior em condução.
- PL1 em apoio.
- PL2 em profundidade.
- Passe direto condicionado.

---

## 25. Passe direto como alternativa

O jogo direto pode ser utilizado quando oferece vantagem.

### Condições

- PL com possibilidade de disputar.
- Apoios próximos.
- Segunda bola preparada.
- Espaço disponível.
- Equilíbrio defensivo.

### Regra

Jogar direto não significa abdicar do modelo.

---

# PARTE III — SEGUNDA FASE E PROGRESSÃO

## 26. Objetivo da segunda fase

Ligar construção e ataque com continuidade.

Esta é uma área particularmente importante para o desenvolvimento da equipa.

### Problemas a evitar

- Falta de apoio.
- Distância entre setores.
- Perdas imediatas.
- Receções isoladas.
- Passes forçados.
- Ausência de movimentos complementares.

---

## 27. Ocupação dos cinco corredores

Referências:

```text
| Exterior E | Interior E | Central | Interior D | Exterior D |
```

### Possível ocupação

- Alas nos corredores exteriores.
- MO e PL1 nos interiores.
- PL2 na zona central.
- Médios em apoio.

### Regra

A ocupação é dinâmica e não exige um jogador permanente em cada corredor.

---

## 28. Triângulos de apoio

### Exemplo esquerdo

- DCE.
- MC-C.
- ALA-E.

### Exemplo direito

- DCD.
- MC-R ou MC-C.
- ALA-D.

### Objetivos

- Criar alternativas.
- Evitar isolamento.
- Facilitar progressão.
- Preparar terceiro homem.

---

## 29. Terceiro homem

### Sequência possível

1. DCE possui bola.
2. MC-C aproxima-se.
3. MO ocupa espaço entre linhas.
4. DCE passa ao MC-C.
5. MC-C encontra MO.
6. MO dá continuidade.

### Condições

- Temporização.
- Linha de passe.
- Apoio.
- Orientação.
- Espaço.

---

## 30. Fixar e libertar

### Conceito

Atrair um adversário para criar espaço noutro local.

### Exemplo

1. DCD conduz.
2. Médio adversário aproxima-se.
3. MC-C liberta-se.
4. DCD encontra MC-C.
5. MC-C progride.

### Regra

Se o adversário não reagir, não existe necessariamente necessidade de forçar passe.

---

## 31. Atrair para mudar corredor

### Sequência

1. Bola circula à esquerda.
2. Adversário desloca.
3. MC-C ou LIB reconhece espaço contrário.
4. Bola muda de corredor.
5. ALA-D recebe.
6. Equipa procura vantagem.

### Regra

A mudança deve chegar antes de o adversário reorganizar, quando possível.

---

## 32. Passe vertical

### Condições

- Recetor acessível.
- Linha de passe.
- Orientação.
- Apoio.
- Continuidade.

### Riscos

- Interceção.
- Perda central.
- Contra-ataque.

### Regra

Não confundir verticalidade com precipitação.

---

## 33. Condução progressiva

Pode ser realizada por:

- Central exterior.
- Médio construtor.
- MO.
- Ala.

### Objetivo

Criar vantagem ao transportar bola para espaço livre ou fixar adversário.

### Regra

A condução deve respeitar a cobertura.

---

## 34. Relação MC-C–MO

### Objetivo

Ligar a construção à criação.

### Mecanismos

- Passe vertical.
- Terceiro homem.
- Movimento de aproximação.
- Rotação.
- Passe e desmarcação.

### Riscos

- MO marcado.
- Passe intercetado.
- Falta de apoio.

---

## 35. Relação MC-R–MC-C

### Objetivo

Equilibrar proteção e progressão.

### Mecanismos

- Alturas diferentes.
- Cobertura alternada.
- Apoios diagonais.
- Mudança de corredor.
- Compensação após condução.

### Regra

Ambos devem participar nas duas fases, com responsabilidades predominantes diferentes.

---

## 36. Relação MO–PL1

### Objetivo

Criar ligação no corredor central ou interior.

### Mecanismos

- Apoio.
- Devolução.
- Tabela.
- Terceiro homem.
- Rotação.

### Regra

A aproximação de PL1 não deve eliminar toda a profundidade.

---

## 37. Relação MO–PL2

### Objetivo

Criar oportunidades de profundidade e finalização.

### Mecanismos

- Passe incisivo.
- Rutura.
- Movimento em L.
- Diagonal.
- Ataque ao intervalo.

### Condições

- Portador com tempo.
- Linha de passe.
- Sincronização.
- Espaço.

---

## 38. Relação PL1–PL2

### Objetivo

Criar movimentos complementares.

### PL1

- Apoia.
- Liga.
- Atrai.
- Devolve.

### PL2

- Fixa.
- Ataca profundidade.
- Procura intervalo.
- Finaliza.

### Regra

As funções podem alternar conforme o momento.

---

## 39. Rotação entre MO e PL1

### Exemplo

1. PL1 baixa.
2. MO aproxima-se.
3. Central acompanha PL1.
4. MO identifica espaço.
5. PL2 mantém profundidade.
6. Equipa procura ligação.

### Regra

A rotação só produz vantagem se alterar referências defensivas ou criar acesso.

---

## 40. Rotação entre MO e médio

### Possibilidade

MO baixa para apoio e MC-C progride.

### Objetivos

- Criar linha.
- Atrair marcação.
- Alterar referências.
- Encontrar espaço.

### Riscos

- Falta de cobertura.
- Sobreposição de posições.
- Perda de ligação à frente.

---

# PARTE IV — UTILIZAÇÃO DOS ALAS

## 41. Largura ofensiva

Os alas são referências importantes para dar largura.

### Objetivos

- Alongar bloco.
- Criar espaço interior.
- Receber livre.
- Progredir.
- Cruzar ou combinar.

### Regra

Não manter ambos permanentemente na mesma altura sem avaliar equilíbrio.

---

## 42. Ala esquerdo

### Comportamentos possíveis

- Dar largura.
- Receber orientado.
- Combinar com DCE.
- Ligar com MC-C.
- Procurar profundidade.
- Cruzar.
- Procurar passe atrasado.

### Regra

As ações dependem das características demonstradas do jogador.

---

## 43. Ala direito

### Comportamentos possíveis

- Dar largura.
- Receber orientado.
- Combinar com DCD.
- Ligar com médios.
- Procurar profundidade.
- Cruzar.
- Procurar passe atrasado.

### Regra

As ações dependem das características demonstradas do jogador.

---

## 44. Ala do lado da bola

### Possíveis ações

- Receber no pé.
- Atacar espaço.
- Fixar defensor.
- Combinar.
- Cruzar.
- Passar atrasado.

### Regra

Deve reconhecer se existe apoio interior.

---

## 45. Ala do lado contrário

### Possíveis ações

- Manter largura.
- Preparar mudança.
- Ajustar altura.
- Atacar segundo poste.
- Proteger equilíbrio.

### Regra

A ação depende da ameaça adversária e da localização da bola.

---

## 46. Combinação central exterior–ala

### Exemplo

1. DCE recebe.
2. ALA-E oferece largura.
3. MC-C aproxima-se.
4. DCE encontra ALA-E.
5. MC-C oferece apoio interior.
6. Ala decide.

### Alternativas

- Passe interior.
- Devolução.
- Progressão.
- Mudança de corredor.

---

## 47. Combinação ala–MO

### Exemplo

1. ALA-D recebe.
2. MO aproxima-se do corredor interior.
3. PL2 fixa central.
4. Ala encontra MO.
5. MO procura rutura ou devolução.

### Risco

Concentração excessiva junto à linha.

---

## 48. Combinação ala–PL

### Exemplo

1. ALA-E recebe.
2. PL1 desloca-se para apoio.
3. PL2 mantém profundidade.
4. Ala encontra PL1.
5. PL1 devolve ou liga com MO.

---

## 49. Sobreposição exterior

### Condição

Um jogador ataca o corredor exterior nas costas de um colega.

### Possível execução

- Ala ou outro jogador oferece movimento exterior.
- Portador fixa adversário.
- Passe é realizado quando existe vantagem.

### Regra

Não pressupor que o central exterior deve fazer sobreposições frequentes.

---

## 50. Movimento interior do ala

### Possibilidade

O ala aproxima-se do corredor interior.

### Objetivos

- Criar apoio.
- Libertar espaço exterior.
- Participar na construção.
- Criar superioridade.

### Riscos

- Perda de largura.
- Espaço nas costas.
- Congestionamento central.

### Regra

Exige compensação posicional.

---

# PARTE V — MÉDIO OFENSIVO E AVANÇADOS

## 51. MO como referência criativa

O MO pretende:

- Receber entre linhas.
- Ligar setores.
- Criar oportunidades.
- Executar passes incisivos.
- Procurar remate exterior.
- Aproximar-se dos PL.
- Reconhecer espaços.

---

## 52. Receção entre linhas

### Condições

- Espaço.
- Linha.
- Orientação.
- Apoio.
- Continuidade.

### Ações possíveis

- Rodar.
- Passar.
- Conduzir.
- Rematar.
- Ligar com PL.

---

## 53. MO perante marcação individual

### Possíveis soluções

- Mudar altura.
- Mudar corredor interior.
- Arrastar marcador.
- Criar terceiro homem.
- Libertar espaço para colega.

### Regra

Não insistir em encontrar MO quando a linha está fechada.

---

## 54. MO perante marcação zonal

### Possíveis soluções

- Ocupar intervalo.
- Alternar alturas.
- Receber após deslocamento do bloco.
- Combinar com PL1.
- Criar linha diagonal.

---

## 55. Remate de média distância

### Condições

- Espaço frontal.
- Linha de remate.
- Tempo.
- Capacidade demonstrada.
- Cobertura de ressaltos.

### Alternativas

- Passe para PL.
- Passe exterior.
- Condução.
- Circulação.

---

## 56. PL1 — Avançado de apoio

### Comportamentos pretendidos

- Aproximar.
- Receber de costas.
- Proteger.
- Devolver.
- Ligar com MO.
- Arrastar central.
- Atacar área após ligação.

### Regra

Apoiar não significa abandonar permanentemente a área.

---

## 57. PL2 — Avançado de profundidade

### Comportamentos pretendidos

- Fixar centrais.
- Atacar intervalos.
- Fazer diagonais.
- Procurar rutura.
- Finalizar.
- Atacar segunda bola.

### Regra

Profundidade não significa correr sempre nas costas.

---

## 58. Movimento em L

### Objetivo

Criar separação do defensor.

### Sequência possível

1. PL2 ocupa referência.
2. Inicia movimento.
3. Defensor reage.
4. PL2 altera direção.
5. Ataca intervalo.
6. Portador avalia passe.

### Regra

O movimento deve ser sincronizado com a possibilidade real de passe.

---

## 59. Movimento de apoio e rutura

### Exemplo

1. PL1 baixa.
2. Central acompanha.
3. PL2 ataca espaço.
4. MO identifica linha.
5. Passe é realizado se existir vantagem.

### Alternativa

Se o central não acompanhar, PL1 pode receber e ligar.

---

## 60. Terceiro homem com PL1

### Exemplo

1. MC-C encontra PL1.
2. PL1 devolve ao MO.
3. MO encontra PL2.

### Condições

- Apoio.
- Tempo.
- Orientação.
- Espaço.
- Movimento coordenado.

---

## 61. Dois PL perante três centrais

### Problema

Inferioridade numérica nominal na última linha.

### Possíveis soluções

- PL1 baixar.
- MO aproximar.
- Ala atacar espaço.
- Movimentos alternados.
- Fixar central exterior.
- Atacar intervalo.

### Regra

Não concluir que existe inferioridade funcional apenas pela contagem.

---

## 62. Dois PL perante dois centrais

### Possibilidades

- Fixação.
- Apoio e rutura.
- Ataque aos intervalos.
- Movimentos cruzados.
- Ataque à profundidade.

### Riscos

- Cobertura dos laterais.
- Pivô recuperar.
- GR controlar profundidade.

---

# PARTE VI — TRANSFORMAÇÕES OFENSIVAS

## 63. Transformação 3-5-2 para 3-4-1-2

### Estrutura

- Três centrais.
- Dois médios.
- Dois alas.
- Um MO.
- Dois PL.

### Objetivo

Manter referência de ligação atrás dos avançados.

### Regra

Pode corresponder à organização funcional habitual, sem necessidade de mudança estrutural formal.

---

## 64. Transformação para 3-4-2-1

### Estrutura

```text
                         PL2

                    PL1       MO

       ALA-E      MC-R      MC-C      ALA-D

                 DCE      LIB      DCD

                          GR
```

### Objetivos

- Criar duas referências interiores.
- Fixar última linha.
- Facilitar terceiro homem.
- Manter largura exterior.
- Aumentar ligações.

### Riscos

- PL2 isolado.
- Alas demasiado altos.
- Dois médios sobrecarregados após perda.

---

## 65. Transformação para 3-4-3

### Possibilidade

Três referências avançadas.

### Objetivos

- Fixar defensores.
- Criar largura ou ocupação interior.
- Aumentar presença ofensiva.

### Regra

Não assumir que o 3-4-3 exige extremos tradicionais se as referências forem ocupadas por jogadores com funções diferentes.

---

## 66. Quando transformar

A transformação deve responder a:

- Pressão adversária.
- Espaço entre linhas.
- Número de centrais.
- Posição dos laterais.
- Altura do bloco.
- Capacidade dos nossos jogadores.
- Equilíbrio preventivo.

### Regra

Não transformar apenas por preferência estética.

---

## 67. Quando manter 3-5-2

Pode ser adequado quando:

- Existe ligação entre os dois PL.
- MO encontra espaço.
- Alas oferecem largura.
- Médios equilibram.
- Estrutura permite progressão.

---

## 68. Transformações assimétricas

### Exemplo

- Ala esquerdo mais alto.
- Ala direito mais baixo.
- MO desloca-se para um interior.
- MC-C ajusta.
- PL1 baixa.

### Regra

A assimetria deve ter objetivo e compensações.

---

# PARTE VII — CRIAÇÃO E FINALIZAÇÃO

## 69. Objetivo da criação

Transformar progressão em situações de finalização favoráveis.

### Mecanismos

- Combinação interior.
- Rutura.
- Cruzamento.
- Passe atrasado.
- Remate exterior.
- Terceiro homem.
- Mudança de corredor.

---

## 70. Ataque ao intervalo central–lateral

### Condições

- Espaço.
- Movimento.
- Portador com tempo.
- Linha de passe.
- Cobertura preventiva.

### Possíveis jogadores

- PL2.
- PL1.
- MO.
- Ala.

---

## 71. Ataque ao intervalo entre centrais

### Condições

- Separação entre defensores.
- Movimento coordenado.
- Passe possível.
- Controlo do fora de jogo.

### Regra

Não forçar passe quando o espaço é apenas aparente.

---

## 72. Cruzamento exterior

### Verificar

- Cruzador.
- Pressão.
- Ocupação da área.
- Movimento dos PL.
- MO.
- Ala contrário.
- Segunda bola.

---

## 73. Cruzamento atrasado

### Situação

Ala ou outro jogador chega a zona lateral avançada.

### Objetivo

Encontrar jogador em zona frontal ou interior.

### Possíveis referências

- MO.
- Médio de chegada.
- PL que recua.

### Regra

O passe atrasado exige linha disponível e coordenação.

---

## 74. Primeiro poste

### Possíveis referências

- PL1.
- PL2.

### Objetivo

Atacar espaço antes do defensor.

### Regra

A ocupação depende da origem do cruzamento e dos movimentos existentes.

---

## 75. Segundo poste

### Possíveis referências

- PL.
- Ala contrário.
- MO.

### Objetivo

Explorar espaço no lado contrário.

### Riscos

- Defesa controlar.
- GR antecipar.
- Cruzamento demasiado longo.

---

## 76. Zona frontal

### Possíveis referências

- MO.
- MC-C.
- MC-R, em situações específicas.

### Objetivos

- Remate.
- Passe.
- Segunda bola.
- Continuidade.

### Regra

Não projetar ambos os médios sem proteção adequada.

---

## 77. Segunda bola ofensiva

### Objetivos

- Recuperar ressalto.
- Manter ataque.
- Criar nova oportunidade.
- Impedir transição imediata.

### Referências

- Médios.
- MO.
- Jogadores próximos.

---

## 78. Finalização após combinação

### Exemplo

1. MC-C encontra MO.
2. MO encontra PL1.
3. PL1 devolve.
4. PL2 ataca.
5. MO procura passe.
6. PL2 finaliza.

### Regra

A combinação deve adaptar-se à resposta defensiva.

---

## 79. Finalização após transição

### Objetivos

- Aproveitar desorganização.
- Atacar espaço.
- Reconhecer superioridade.
- Finalizar em vantagem.

### Regra

A velocidade não deve eliminar a qualidade de decisão.

---

# PARTE VIII — EQUILÍBRIO E PROTEÇÃO DA PERDA

## 80. Equilíbrio preventivo

A equipa deve procurar manter:

- Cobertura central.
- Controlo da profundidade.
- Capacidade de reação.
- Distâncias adequadas.
- Proteção dos corredores expostos.

---

## 81. Papel do líbero no equilíbrio

### Responsabilidades

- Controlar profundidade.
- Cobrir centrais exteriores.
- Comunicar.
- Ajustar.
- Proteger espaço central.

---

## 82. Papel do recuperador no equilíbrio

### Responsabilidades

- Proteger zona frontal aos centrais.
- Cobrir conduções.
- Controlar primeira ligação adversária.
- Apoiar reação à perda.

---

## 83. Ala projetado

### Situação

Um ala encontra-se alto.

### Verificar

- Central exterior cobre?
- Médio protege?
- Líbero ajusta?
- Ala contrário equilibra?
- Quantos adversários estão preparados para transição?

---

## 84. Centrais exteriores em condução

### Regra

Se um central exterior progride, deve existir compensação adequada.

### Possíveis compensações

- Líbero ajusta.
- Médio recuperador protege.
- Central contrário fecha.
- Ala controla posição.

---

## 85. Perda em corredor central

### Riscos

- Contra-ataque imediato.
- Exposição dos centrais.
- Passe vertical adversário.

### Resposta

- Pressão se existir cobertura.
- Fechar linhas.
- Temporizar.
- Reorganizar.

---

## 86. Perda em corredor exterior

### Riscos

- Transição pelo corredor.
- Passe interior.
- Mudança de corredor.

### Resposta

- Ala reage.
- Médio fecha.
- Central exterior cobre.
- Líbero protege centro.

---

# PARTE IX — ADAPTAÇÕES AOS ADVERSÁRIOS

## 87. Contra pressão alta

### Soluções

- GR.
- Terceiro homem.
- Central exterior livre.
- Médio a baixar.
- PL1 em apoio.
- PL2 em profundidade.
- Passe direto condicionado.

### Regra

Escolher em função da pressão real.

---

## 88. Contra bloco médio

### Soluções

- Circulação com intenção.
- Central exterior em condução.
- MO entre linhas.
- Terceiro homem.
- Mudança de corredor.
- Fixar e libertar.

---

## 89. Contra bloco baixo

### Soluções

- Largura.
- Mobilidade.
- Ocupação interior.
- Combinações.
- Passe atrasado.
- Remate exterior condicionado.
- Segunda bola.

---

## 90. Contra 4-4-2

### Possibilidades

- Três centrais perante dois PL.
- MO entre linhas.
- Ala exterior.
- Superioridade central funcional.
- Terceiro homem.

### Riscos

- Linhas compactas.
- Armadilha exterior.
- Dois PL preparados para transição.

---

## 91. Contra 4-3-3

### Possibilidades

- GR na construção.
- Ajuste dos médios.
- Apoio de PL1.
- Terceiro homem.
- Mudança de corredor.

### Riscos

- Pressão sobre três centrais.
- Perda central.
- Alas pressionados.

---

## 92. Contra 4-2-3-1

### Possibilidades

- Central exterior em condução.
- MO entre linhas.
- Movimentos dos PL.
- Mudança de corredor.
- Apoios dos médios.

### Riscos

- Duplo pivô controlar MO.
- Extremos pressionarem alas.

---

## 93. Contra 3-5-2

### Possibilidades

- Mobilidade do MO.
- Central exterior em condução.
- Movimentos complementares dos PL.
- Mudança de corredor.
- Superioridade funcional.

### Riscos

- Igualdades posicionais.
- Alas isolados.
- Transições exteriores.

---

## 94. Contra 3-4-3

### Possibilidades

- Superioridade central.
- MO entre linhas.
- Terceiro homem.
- Ataque nas costas dos alas.
- Mudança de corredor.

### Riscos

- Três avançados pressionarem construção.
- Centrais exteriores expostos.

---

# PARTE X — PROBLEMAS E CORREÇÕES

## 95. Falta de linhas de passe

### Possíveis causas

- Jogadores escondidos.
- Distâncias.
- Má orientação.
- Falta de mobilidade.
- Pressão adversária.

### Correções possíveis

- Ajustar alturas.
- Criar diagonais.
- Aproximar apoios.
- Utilizar GR.
- Criar terceiro homem.

---

## 96. Perda após primeira fase

### Possíveis causas

- MO isolado.
- PL1 demasiado longe.
- Médios na mesma linha.
- Alas afastados.
- Passe precipitado.

### Correções possíveis

- Aproximar MO.
- Coordenar PL1.
- Criar triângulos.
- Ajustar alturas.
- Preparar terceira ligação.

---

## 97. Falta de profundidade

### Possíveis causas

- Ambos PL baixam.
- Última linha não é fixada.
- Falta de rutura.
- Portador pressionado.

### Correções possíveis

- PL2 mantém ameaça.
- Movimento em L.
- Diagonal.
- Ala ataca espaço.
- Sincronizar passe.

---

## 98. Falta de largura

### Possíveis causas

- Alas fecham simultaneamente.
- MO e PL ocupam mesma zona.
- Ausência de referência exterior.

### Correções possíveis

- Ala mantém largura.
- Compensação.
- Mudança de corredor.
- Rotação.

---

## 99. Ataque previsível

### Possíveis causas

- Sempre o mesmo corredor.
- Dependência do MO.
- Passes verticais forçados.
- Ausência de movimentos alternados.

### Correções possíveis

- Variar circulação.
- Mudar corredor.
- Utilizar central exterior.
- Alternar apoios e ruturas.
- Criar terceiros homens.

---

## 100. Pouca presença na área

### Possíveis causas

- PL1 baixa e não regressa.
- PL2 isolado.
- MO demasiado longe.
- Ala contrário não ajusta.

### Correções possíveis

- Coordenar chegada.
- Definir zonas.
- Preparar segunda bola.
- Manter equilíbrio.

---

## 101. Exposição após perda

### Possíveis causas

- Alas demasiado altos.
- Ambos os médios projetados.
- Central exterior sem compensação.
- Distâncias excessivas.

### Correções possíveis

- Ajustar alturas.
- Reforçar cobertura.
- Proteger centro.
- Melhorar equilíbrio preventivo.

---

# PARTE XI — EXERCÍCIOS DE TREINO

## 102. Exercício de construção com três centrais

### Objetivo

Criar linhas e ultrapassar primeira pressão.

### Organização

- GR.
- Três centrais.
- Dois médios.
- Adversários em pressão.

### Critérios

- Receção orientada.
- Apoios diagonais.
- Identificação de jogador livre.
- Progressão com controlo.

---

## 103. Exercício de terceira ligação

### Objetivo

Manter posse após primeira fase.

### Organização

- Centrais.
- Médios.
- MO.
- PL1.
- Oposição progressiva.

### Critérios

- Distâncias.
- Temporização.
- Terceiro homem.
- Continuidade.

---

## 104. Exercício de apoio e rutura

### Objetivo

Coordenar PL1, PL2 e MO.

### Organização

- Médio passador.
- MO.
- Dois PL.
- Defensores.

### Critérios

- Apoio.
- Devolução.
- Movimento em L.
- Passe de rutura.
- Finalização.

---

## 105. Exercício de mudança de corredor

### Objetivo

Atrair e explorar lado contrário.

### Organização

- Duas zonas laterais.
- Zona central.
- Alas.
- Médios.
- Oposição.

### Critérios

- Atrair.
- Reconhecer espaço.
- Mudar.
- Receber orientado.
- Progredir.

---

## 106. Exercício de finalização

### Objetivo

Coordenar ocupação da área.

### Organização

- Alas.
- MO.
- Dois PL.
- Defensores.
- GR.

### Critérios

- Primeiro poste.
- Segundo poste.
- Zona central.
- Passe atrasado.
- Segunda bola.

---

## 107. Exercício de equilíbrio preventivo

### Objetivo

Atacar mantendo proteção.

### Organização

- Equipa atacante.
- Adversários preparados para transição.
- Regras de recuperação e contra-ataque.

### Critérios

- Posição do recuperador.
- Cobertura do líbero.
- Compensação dos centrais exteriores.
- Reação após perda.

---

# PARTE XII — REGRAS DE ANÁLISE PARA A IA

## 108. Processo obrigatório

A IA deve seguir:

**Observação → Contexto → Princípio ofensivo → Problema ou vantagem → Causa provável → Solução → Risco → Exercício ou recomendação → Reavaliação.**

---

## 109. Perguntas obrigatórias

Antes de recomendar uma ação ofensiva, verificar:

1. Qual é a fase?
2. Qual é a estrutura real?
3. Qual é a pressão adversária?
4. Existe jogador livre?
5. Existe linha de passe?
6. Existe espaço?
7. Existe tempo?
8. Existe apoio?
9. Existe profundidade?
10. Existe largura?
11. Existe continuidade?
12. Qual é o papel do MC-R?
13. Qual é o papel do MC-C?
14. Onde está o MO?
15. Onde está o PL1?
16. Onde está o PL2?
17. Onde estão os alas?
18. Existe cobertura?
19. Qual é o risco?
20. Existe alternativa?
21. A solução respeita o modelo?
22. Existe capacidade demonstrada?
23. Qual é a confiança?

---

## 110. Classificação das recomendações

**Compatível:** respeita os princípios e funções pretendidas.

**Compatível com adaptação:** exige ajuste justificado.

**Contraditória:** viola princípio essencial sem compensação.

**Informação insuficiente:** não existem dados adequados.

---

## 111. Níveis de confiança

### Elevada

Comportamento observado repetidamente e contexto conhecido.

### Moderada

Alguma evidência com limitações.

### Baixa

Hipótese baseada em informação incompleta.

### Insuficiente

Não existe fundamento para recomendar.

### Regra

Não atribuir percentagens arbitrárias de confiança.

---

## 112. Formato de recomendação ofensiva

### Identificação

- Fase:
- Estrutura:
- Adversário:
- Zona:

### Diagnóstico

- Observação:
- Problema:
- Evidência:
- Causa provável:

### Solução

- Princípio:
- Jogadores envolvidos:
- Movimento:
- Passe:
- Espaço pretendido:
- Alternativa:

### Segurança

- Cobertura:
- Risco:
- Adaptação:

### Avaliação

- Indicador:
- Confiança:
- Informação em falta:

---

## 113. Exemplo de resposta da IA

**Situação:** a equipa ultrapassa a primeira pressão, mas perde frequentemente a bola antes de chegar ao último terço.

**Diagnóstico provisório:** pode existir falta de apoio na segunda fase.

**Verificação necessária:** observar a distância entre os médios, o MO e o PL1, bem como a pressão sobre o recetor.

**Solução possível:** aproximar o MO da zona de progressão e coordenar o apoio do PL1, mantendo o PL2 como referência de profundidade.

**Equilíbrio:** o médio recuperador deve avaliar a cobertura da zona central, especialmente quando o construtor progride.

**Exercício:** jogo posicional de progressão com terceiro homem e oposição.

**Confiança:** condicionada à confirmação em vídeo ou observação direta.

---

# PARTE XIII — RELAÇÃO COM OUTROS DOCUMENTOS

## 114. Modelo da equipa

- `conhecimento/equipa/modelo_jogo.md`
- `conhecimento/equipa/principios_defensivos.md`
- `conhecimento/equipa/principios_equipa.md`
- `conhecimento/equipa/caracteristicas_jogadores.md`

## 115. Fundamentos

- `conhecimento/fundamentos/fases_jogo.md`
- `conhecimento/fundamentos/principios_ofensivos.md`
- `conhecimento/fundamentos/superioridades.md`
- `conhecimento/fundamentos/modelos_jogo.md`

## 116. Sistemas táticos

- `conhecimento/sistemas/352/organizacao.md`
- `conhecimento/sistemas/352/saida_bola.md`
- `conhecimento/sistemas/352/ataque.md`
- `conhecimento/sistemas/352/transicoes.md`
- `conhecimento/sistemas/343/organizacao.md`
- `conhecimento/sistemas/343/ataque.md`

## 117. Adversários

- `conhecimento/adversarios/estruturas_taticas.md`
- `conhecimento/adversarios/pressao_alta.md`
- `conhecimento/adversarios/bloco_medio.md`
- `conhecimento/adversarios/bloco_baixo.md`
- `conhecimento/adversarios/analise_vulnerabilidades.md`

---

# PARTE XIV — PRINCÍPIO FINAL

## 118. Princípio central

Os princípios ofensivos dos Sub-19 do CCDR Vila Cortez do Mondego assentam na construção organizada com três centrais, na complementaridade dos dois médios, na largura proporcionada pelos alas, na criatividade do médio ofensivo e na relação entre os dois avançados.

A equipa pretende:

- Construir com critério.
- Ultrapassar pressão quando existem condições.
- Manter continuidade após a primeira fase.
- Criar apoios e terceiros homens.
- Utilizar largura e profundidade.
- Explorar movimentos de apoio e rutura.
- Transformar dinamicamente o 3-5-2.
- Criar oportunidades através de combinações, passes incisivos, cruzamentos e remates favoráveis.
- Preservar equilíbrio preventivo.

A IA deve interpretar estes princípios como **intenções táticas a desenvolver e avaliar**, e não como garantias de execução.

A recomendação ofensiva ideal deve responder a cinco perguntas:

1. **Onde está a vantagem?**
2. **Como podemos aceder a ela?**
3. **Que jogadores devem intervir?**
4. **O que fazemos se a primeira solução estiver fechada?**
5. **Como protegemos a equipa se perdermos a bola?**

**Construir com critério, progredir com ligação, criar com mobilidade, finalizar com vantagem e atacar sem perder o equilíbrio.**