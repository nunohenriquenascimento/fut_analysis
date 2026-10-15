# Estruturas Táticas dos Adversários — Identificação, Interpretação e Análise

## 1. Objetivo do documento

Este documento estabelece os princípios universais para identificar, interpretar e analisar as estruturas táticas utilizadas por equipas adversárias.

A estrutura tática corresponde à distribuição e às relações posicionais dos jogadores em determinado momento do jogo.

O sistema nominal, normalmente apresentado antes do encontro, constitui apenas uma referência inicial.

Durante o jogo, uma equipa pode assumir diferentes estruturas na construção, no ataque, na defesa e nas transições.

O assistente de inteligência artificial deve conseguir:

1. Identificar o sistema nominal do adversário.
2. Reconhecer a estrutura efetivamente utilizada.
3. Distinguir posições de funções.
4. Identificar transformações estruturais.
5. Analisar a organização da primeira fase de construção.
6. Reconhecer a distribuição dos médios.
7. Identificar a ocupação dos corredores.
8. Analisar a altura e a largura dos laterais ou alas.
9. Reconhecer movimentos dos extremos.
10. Interpretar o posicionamento dos avançados.
11. Identificar a estrutura defensiva.
12. Distinguir pressão alta, bloco médio e bloco baixo.
13. Reconhecer relações de superioridade e inferioridade.
14. Identificar possíveis vulnerabilidades.
15. Analisar comportamentos de pressão.
16. Reconhecer coberturas e compensações.
17. Identificar alterações durante o jogo.
18. Comparar estruturas entre diferentes fases.
19. Distinguir observações de hipóteses.
20. Produzir recomendações táticas fundamentadas.

A IA não deve assumir que duas equipas com o mesmo sistema nominal possuem o mesmo modelo de jogo.

---

# PARTE I — FUNDAMENTOS DA ANÁLISE ESTRUTURAL

## 2. Sistema tático nominal

O sistema nominal representa a distribuição inicial dos jogadores.

Exemplos:

- 4-4-2.
- 4-3-3.
- 4-2-3-1.
- 3-5-2.
- 3-4-3.
- 4-1-4-1.
- 4-3-1-2.
- 4-4-2 losango.
- 5-3-2.
- 5-4-1.

### Exemplo

Uma equipa apresentada em 4-3-3 pode:

- Construir em 3-2-5.
- Atacar em 2-3-5.
- Defender em 4-1-4-1.
- Pressionar em 4-4-2.

Estas transformações dependem dos movimentos reais dos jogadores.

### Regra

O sistema nominal não deve ser utilizado como prova suficiente da estrutura em cada fase.

---

## 3. Estrutura tática real

A estrutura real corresponde às posições e relações observadas num momento específico.

### Elementos

- Número de jogadores na primeira linha.
- Distribuição dos médios.
- Ocupação dos corredores exteriores.
- Ocupação dos corredores interiores.
- Presença entre linhas.
- Referências de profundidade.
- Distâncias entre setores.
- Altura da última linha.
- Coberturas.
- Equilíbrio.

### Regra

A estrutura real deve ser identificada a partir de observações e não apenas da ficha de jogo.

---

## 4. Sistema, estrutura e modelo de jogo

### Sistema

Referência organizativa geral.

### Estrutura

Distribuição dos jogadores numa situação concreta.

### Modelo de jogo

Conjunto de princípios, comportamentos e relações que orientam a equipa.

### Exemplo

Duas equipas em 4-3-3 podem apresentar:

**Equipa A**

- Construção curta.
- Laterais interiores.
- Extremos abertos.
- Pressão alta.
- Recuperação imediata.

**Equipa B**

- Construção direta.
- Laterais baixos.
- Extremos interiores.
- Bloco médio.
- Transição rápida.

### Regra

O sistema não determina automaticamente o modelo.

---

## 5. Posição nominal e função real

Um jogador pode desempenhar uma função diferente da posição indicada.

### Exemplos

- Lateral que entra no meio-campo.
- Central que conduz até à linha média.
- Extremo que recebe por dentro.
- Avançado que baixa entre linhas.
- Médio que integra a primeira construção.
- Ala que atua como extremo.
- Médio ofensivo que pressiona ao lado do PL.

### Regra

A IA deve identificar a função observada, mesmo quando não coincide com a posição nominal.

---

## 6. Estruturas estáticas e dinâmicas

### Estrutura estática

Representação da posição dos jogadores num instante.

### Estrutura dinâmica

Interpretação das movimentações, relações e alterações ao longo da jogada.

### Exemplo

Um lateral pode começar aberto e depois entrar por dentro.

A imagem inicial não descreve toda a ação.

### Regra

A análise deve considerar sequências e não apenas fotografias isoladas.

---

## 7. Estruturas simétricas e assimétricas

### Estrutura simétrica

Apresenta distribuição relativamente semelhante nos dois corredores.

### Estrutura assimétrica

Apresenta funções ou alturas diferentes entre os lados.

### Exemplo

- Lateral esquerdo sobe.
- Lateral direito permanece baixo.
- Extremo esquerdo entra por dentro.
- Extremo direito mantém largura.

### Regra

A assimetria pode ser intencional e não deve ser classificada automaticamente como erro.

---

# PARTE II — REFERÊNCIAS ESPACIAIS

## 8. Divisão longitudinal do campo

O campo pode ser dividido em:

1. Primeiro terço.
2. Segundo terço.
3. Último terço.

### Primeiro terço

Zona próxima da baliza da equipa analisada.

### Segundo terço

Zona intermédia.

### Último terço

Zona próxima da baliza adversária.

### Regra

A localização deve ser sempre interpretada relativamente à equipa analisada.

---

## 9. Cinco corredores verticais

O campo pode ser dividido em:

1. Corredor exterior esquerdo.
2. Corredor interior esquerdo.
3. Corredor central.
4. Corredor interior direito.
5. Corredor exterior direito.

### Objetivos da análise

- Identificar largura.
- Reconhecer ocupação interior.
- Avaliar linhas de passe.
- Localizar superioridades.
- Identificar espaços livres.

### Regra

O número de jogadores por corredor não determina sozinho a qualidade da ocupação.

---

## 10. Linhas horizontais

As estruturas podem ser analisadas através de linhas.

### Exemplos

- Primeira linha de construção.
- Linha de apoio.
- Linha de criação.
- Linha de profundidade.
- Primeira linha de pressão.
- Linha média defensiva.
- Última linha defensiva.

### Regra

As linhas são referências analíticas.

Os jogadores podem movimentar-se entre elas.

---

## 11. Espaço entre linhas

Corresponde ao espaço existente entre setores adversários.

### Exemplos

- Entre avançados e médios.
- Entre médios e defesas.

### Importância

- Receção orientada.
- Progressão.
- Ligação.
- Criação de oportunidades.

### Regra

Um espaço aparentemente livre só é explorável se existir acesso funcional e possibilidade de continuidade.

---

## 12. Intervalos entre jogadores

Os intervalos correspondem aos espaços existentes entre referências da mesma linha.

### Exemplos

- Entre lateral e central.
- Entre dois centrais.
- Entre central e ala.
- Entre dois médios.

### Regra

A existência de um intervalo não significa automaticamente vulnerabilidade.

É necessário avaliar cobertura, pressão e capacidade de exploração.

---

## 13. Largura e profundidade

### Largura

Distribuição horizontal dos jogadores.

### Profundidade

Distribuição longitudinal e ameaça ao espaço nas costas.

### Regra

Uma equipa pode apresentar largura sem conseguir progredir.

Também pode apresentar profundidade sem existir linha de passe disponível.

---

## 14. Altura das linhas

A análise deve identificar:

- Altura da primeira pressão.
- Altura da linha média.
- Altura da última linha.
- Distâncias entre linhas.

### Riscos possíveis

- Linha defensiva alta sem pressão na bola.
- Linha média distante dos avançados.
- Última linha demasiado baixa.
- Espaços entre setores.

---

# PARTE III — IDENTIFICAÇÃO DOS SISTEMAS NOMINAIS

## 15. Sistema 4-4-2

### Estrutura

```text
                 PL       PL

       ME       MC       MC       MD

       DE       DC       DC       DD

                       GR
```

### Características possíveis

- Dois avançados.
- Dois médios centrais.
- Dois médios exteriores.
- Quatro defesas.

### Comportamentos possíveis

- Pressão com dois avançados.
- Bloco médio compacto.
- Defesa em duas linhas de quatro.
- Ataque exterior.
- Jogo direto.
- Construção com dois centrais.

### Vulnerabilidades possíveis

- Inferioridade central perante três médios.
- Espaço entre linhas.
- Dificuldade em controlar laterais interiores.
- Espaço entre lateral e central.

### Regra

Estas vulnerabilidades não são automáticas.

---

## 16. Sistema 4-3-3

### Estrutura

```text
          EE           PL           ED

               MC             MC

                       MDC

       DE       DC       DC       DD

                       GR
```

### Características possíveis

- Três avançados.
- Três médios.
- Quatro defesas.
- Ocupação dos corredores exteriores e interiores.

### Comportamentos possíveis

- Pressão com três avançados.
- Construção em 2-3 ou 3-2.
- Extremos abertos ou interiores.
- Laterais altos ou interiores.
- Defesa em 4-1-4-1.

### Vulnerabilidades possíveis

- Espaço nas costas dos laterais.
- MDC isolado.
- Intervalos entre central e lateral.
- Espaço entre linhas.

---

## 17. Sistema 4-2-3-1

### Estrutura

```text
                       PL

          EE           MO           ED

                 MDC       MDC

       DE       DC       DC       DD

                       GR
```

### Características possíveis

- Um PL.
- Três jogadores na linha ofensiva intermédia.
- Dois pivôs.
- Quatro defesas.

### Comportamentos possíveis

- Construção com duplo pivô.
- MO entre linhas.
- Extremos interiores.
- Laterais projetados.
- Pressão em 4-4-2.
- Defesa em 4-4-1-1.

### Vulnerabilidades possíveis

- Espaço nas costas dos laterais.
- Distância entre PL e médios.
- Duplo pivô pressionado.
- Espaço entre extremos e laterais.

---

## 18. Sistema 3-5-2

### Estrutura

```text
                   PL       PL

                        MC

             MC                  MC

       ALA-E                          ALA-D

                DCE    DCC    DCD

                         GR
```

A disposição exata dos três médios pode variar.

### Características possíveis

- Três centrais.
- Dois alas.
- Três médios.
- Dois avançados.

### Comportamentos possíveis

- Construção com três centrais.
- Alas altos.
- Superioridade central.
- Dois PL com movimentos complementares.
- Defesa em 5-3-2.

### Vulnerabilidades possíveis

- Espaço nas costas dos alas.
- Corredores exteriores.
- Centrais exteriores obrigados a sair.
- Dificuldade perante extremos abertos.

---

## 19. Sistema 3-4-3

### Estrutura

```text
           AE           PL           AD

       ALA-E       MC       MC       ALA-D

                DCE    DCC    DCD

                         GR
```

### Características possíveis

- Três centrais.
- Dois alas.
- Dois médios.
- Três avançados.

### Comportamentos possíveis

- Construção com três centrais.
- Avançados exteriores interiores.
- Alas altos.
- Pressão com três avançados.
- Defesa em 5-2-3 ou 5-4-1.

### Vulnerabilidades possíveis

- Inferioridade central perante três médios.
- Espaço nas costas dos alas.
- Centrais exteriores expostos.
- Distância entre linha avançada e pivôs.

---

## 20. Sistema 4-1-4-1

### Estrutura

```text
                       PL

        ME       MC       MC       MD

                       MDC

       DE       DC       DC       DD

                       GR
```

### Características possíveis

- Um pivô defensivo.
- Quatro médios à frente.
- Um avançado.

### Comportamentos possíveis

- Proteção central.
- Bloco médio.
- Pressão a partir da linha média.
- Transformação ofensiva em 4-3-3.

### Vulnerabilidades possíveis

- MDC isolado.
- PL distante.
- Espaço entre linhas.
- Dificuldade em pressionar vários centrais.

---

## 21. Sistema 4-4-2 losango

### Estrutura

```text
                   PL       PL

                        MO

                  MC         MC

                        MDC

          DE       DC       DC       DD

                         GR
```

### Características possíveis

- Quatro médios em losango.
- Dois avançados.
- Pouca largura natural no meio-campo.
- Laterais com responsabilidades exteriores.

### Vantagens possíveis

- Densidade central.
- Combinações interiores.
- Controlo entre linhas.

### Vulnerabilidades possíveis

- Espaço exterior.
- Laterais expostos.
- Dificuldade perante largura elevada.

### Regra

A largura pode ser compensada por movimentos dos laterais ou dos médios.

---

## 22. Sistema 4-3-1-2

### Estrutura

```text
                   PL       PL

                        MO

              MC        MC        MC

          DE       DC       DC       DD

                         GR
```

### Características possíveis

- Dois avançados.
- Um médio ofensivo.
- Três médios.
- Quatro defesas.

### Diferença face ao losango

A distinção depende da altura e das funções dos três médios.

### Regra

Não classificar estruturas apenas pela disposição gráfica.

---

## 23. Sistema 5-3-2

### Estrutura

```text
                    PL       PL

                MC     MC     MC

       ALA-E    DCE    DCC    DCD    ALA-D

                         GR
```

### Características possíveis

- Cinco referências na última linha.
- Três médios.
- Dois avançados.

### Comportamentos possíveis

- Bloco médio ou baixo.
- Proteção central.
- Transição através de dois PL.
- Pressão com dois avançados.

### Vulnerabilidades possíveis

- Espaço exterior intermédio.
- Dificuldade em pressionar laterais.
- Alas obrigados a grandes deslocamentos.
- Distância entre linhas.

---

## 24. Sistema 5-4-1

### Estrutura

```text
                         PL

          ME        MC       MC        MD

       ALA-E    DCE    DCC    DCD    ALA-D

                         GR
```

### Características possíveis

- Cinco defesas.
- Quatro médios.
- Um avançado.

### Comportamentos possíveis

- Proteção de corredores interiores.
- Defesa da área.
- Bloco baixo.
- Transição através do PL.

### Vulnerabilidades possíveis

- PL isolado.
- Pressão reduzida na primeira construção.
- Dificuldade em sair.
- Espaço para circulação adversária.

---

# PARTE IV — ESTRUTURAS DE CONSTRUÇÃO

## 25. Construção com dois jogadores

### Estrutura possível

```text
                DC       DC
                     GR
```

### Características

- Dois jogadores principais na primeira linha.
- Apoio potencial do GR.
- Médios podem oferecer ligação.

### Riscos possíveis

- Pressão sobre os dois centrais.
- Pivô bloqueado.
- Laterais sem linha de passe.

### Regra

A presença do GR pode alterar a relação numérica.

---

## 26. Construção com três jogadores

### Estrutura possível

```text
              DCE     DCC     DCD
                       GR
```

### Origem possível

- Três centrais nominais.
- Um pivô baixa entre centrais.
- Um lateral permanece baixo.
- Estrutura assimétrica.

### Regra

A IA deve identificar como a linha de três é formada.

---

## 27. Construção com quatro jogadores

### Estrutura possível

```text
          DE       DC       DC       DD
```

### Características

- Quatro referências na primeira linha.
- Possibilidade de circulação exterior.
- Apoios centrais em linhas superiores.

### Regra

Quatro jogadores na primeira linha não garantem melhor construção.

---

## 28. Construção em 3-2

### Estrutura

```text
                  MC       MC

              DCE     DCC     DCD
```

### Características

- Três referências na primeira linha.
- Dois apoios centrais.
- Possibilidade de largura exterior em linhas superiores.

### Riscos

- Pivôs bloqueados.
- Espaço entre linhas.
- Falta de progressão.
- Pressão individual.

---

## 29. Construção em 2-3

### Estrutura

```text
              DE       MDC       DD

                   DC       DC
```

### Características

- Dois centrais.
- Três referências de apoio.
- Laterais podem entrar por dentro.
- Pivô pode ocupar centro.

### Riscos

- Espaço nas costas dos laterais.
- Pivô pressionado.
- Perda central.
- Falta de profundidade.

---

## 30. Construção em 3-1

### Estrutura

```text
                       MDC

              DCE     DCC     DCD
```

### Características

- Três referências na primeira linha.
- Um apoio central principal.
- Outros médios podem posicionar-se mais altos.

### Riscos

- Pivô isolado.
- Linha vertical bloqueada.
- Falta de apoio próximo.

---

## 31. Construção assimétrica

### Exemplo

- Lateral esquerdo sobe.
- Lateral direito fica.
- MDC aproxima-se.
- Extremo esquerdo entra por dentro.
- Extremo direito mantém largura.

### Possível estrutura

3-2 ou 3-1-2, dependendo da distribuição real.

### Regra

A estrutura deve ser identificada pelo posicionamento e não pela posição nominal.

---

# PARTE V — ESTRUTURAS OFENSIVAS

## 32. Ataque em 2-3-5

### Estrutura

```text
       EE       MC       PL       MC       ED

              DE       MDC       DD

                   DC       DC
```

### Características

- Cinco referências na última linha ofensiva.
- Três jogadores de apoio.
- Dois jogadores de equilíbrio.

### Riscos possíveis

- Perda central.
- Espaço nas costas.
- Defesas isolados.
- Falta de cobertura.

---

## 33. Ataque em 3-2-5

### Estrutura

```text
       AE       MO       PL       MO       AD

                   MC       MC

              DCE     DCC     DCD
```

### Características

- Cinco referências avançadas.
- Dois jogadores centrais de apoio.
- Três referências de equilíbrio.

### Riscos possíveis

- Espaço nas costas dos alas.
- Pivôs ultrapassados.
- Centrais exteriores expostos.

---

## 34. Ataque em 3-2-4-1

### Estrutura

```text
                         PL

          AE        MO       MO        AD

                   MC       MC

              DCE     DCC     DCD
```

### Características

- Um jogador mais avançado.
- Quatro referências de criação.
- Dois apoios.
- Três jogadores de equilíbrio.

### Regra

A distribuição não determina automaticamente quem ocupa cada função.

---

## 35. Ataque em 3-1-6

### Características

- Seis referências avançadas.
- Um apoio central.
- Três jogadores de equilíbrio.

### Oportunidades possíveis

- Ocupação da última linha.
- Presença na área.
- Fixação adversária.

### Riscos

- Pivô isolado.
- Distâncias elevadas.
- Perda central.
- Transição defensiva.

### Regra

O 3-1-6 exige análise rigorosa do equilíbrio.

---

## 36. Ataque em 2-4-4

### Características

- Dois jogadores de equilíbrio.
- Quatro referências intermédias.
- Quatro jogadores avançados.

### Riscos possíveis

- Última linha de proteção reduzida.
- Espaço nas costas.
- Dificuldade perante contra-ataque.

### Regra

O número de jogadores por linha não determina automaticamente a segurança da estrutura.

---

# PARTE VI — ESTRUTURAS DEFENSIVAS

## 37. Defesa em 4-4-2

### Características

- Duas linhas de quatro.
- Dois avançados.
- Proteção central.
- Possibilidade de pressão com dois.

### Vulnerabilidades possíveis

- Espaço entre linhas.
- Inferioridade central.
- Corredores interiores.
- Distância entre avançados e médios.

---

## 38. Defesa em 4-1-4-1

### Características

- Um pivô defensivo.
- Quatro médios à frente.
- Um PL.
- Quatro defesas.

### Vulnerabilidades possíveis

- MDC isolado.
- Espaço nas costas da linha média.
- PL distante.
- Pressão inicial limitada.

---

## 39. Defesa em 4-4-1-1

### Características

- Um PL.
- Um segundo avançado ou MO atrás.
- Duas linhas de quatro.

### Objetivos possíveis

- Controlar pivô adversário.
- Proteger centro.
- Preparar transição.

### Riscos

- Espaço entre linhas.
- Pressão sobre construção.
- Distância entre referências.

---

## 40. Defesa em 5-3-2

### Características

- Cinco jogadores na última linha.
- Três médios.
- Dois avançados.

### Vulnerabilidades possíveis

- Espaço exterior intermédio.
- Laterais adversários livres.
- Distância entre avançados e médios.
- Alas pressionados.

---

## 41. Defesa em 5-4-1

### Características

- Cinco jogadores na última linha.
- Quatro médios.
- Um avançado.

### Vulnerabilidades possíveis

- PL isolado.
- Circulação adversária.
- Dificuldade em pressionar centrais.
- Transição ofensiva distante.

---

## 42. Defesa em 5-2-3

### Características

- Cinco jogadores na última linha.
- Dois médios.
- Três avançados.

### Vulnerabilidades possíveis

- Inferioridade central.
- Espaço entre linhas.
- Pivôs expostos.
- Corredores interiores.

---

## 43. Defesa em 4-2-3-1

### Características

- Quatro defesas.
- Dois pivôs.
- Três referências intermédias.
- Um PL.

### Regra

A classificação depende da altura real dos três jogadores intermédios.

---

# PARTE VII — IDENTIFICAÇÃO DE SUPERIORIDADES

## 44. Superioridade numérica

Existe quando uma equipa possui mais jogadores do que o adversário numa zona relevante.

### Exemplo

Três jogadores perante dois.

### Regra

A superioridade numérica não garante progressão.

---

## 45. Superioridade posicional

Existe quando a distribuição permite ocupar espaços favoráveis.

### Exemplo

Um jogador recebe entre linhas sem oposição imediata.

### Regra

É necessário avaliar acesso à bola e possibilidade de continuidade.

---

## 46. Superioridade qualitativa

Existe quando um jogador possui vantagem individual relevante perante o adversário.

### Exemplos

- Maior velocidade.
- Melhor capacidade de drible.
- Melhor jogo aéreo.
- Melhor resistência à pressão.

### Regra

Não atribuir vantagens qualitativas sem dados ou observações.

---

## 47. Superioridade dinâmica

Existe quando o movimento e o tempo da ação criam vantagem.

### Exemplo

Um jogador ataca um espaço enquanto o defensor ainda ajusta a posição.

### Regra

A vantagem pode desaparecer se a execução for lenta.

---

## 48. Superioridade funcional

Corresponde à capacidade efetiva de explorar uma vantagem.

### Exemplo

Uma equipa possui três jogadores perante dois, mas as linhas de passe estão bloqueadas.

Existe superioridade numérica, mas pode não existir superioridade funcional.

### Regra

A IA deve distinguir quantidade de jogadores e capacidade real de progressão.

---

# PARTE VIII — LEITURA DAS RELAÇÕES ENTRE SISTEMAS

## 49. Três centrais contra dois avançados

### Possibilidade

Três centrais podem controlar duas referências e manter cobertura.

### Limitações

- Um avançado pode baixar.
- Outro pode atacar profundidade.
- Um central pode ser atraído.
- A cobertura pode desaparecer.

### Regra

Não assumir superioridade funcional automática.

---

## 50. Dois médios contra três médios

### Possibilidade

A equipa com três médios pode criar superioridade central.

### Limitações

- Um avançado pode baixar.
- Um pivô pode ser bloqueado.
- Os médios podem ocupar alturas diferentes.
- A pressão pode impedir receção.

### Regra

A superioridade deve ser avaliada em função da posição e da capacidade de acesso.

---

## 51. Ala contra lateral e extremo

### Problema possível

Um ala pode enfrentar duas referências exteriores.

### Soluções possíveis

- Avançado exterior recuperar.
- Pivô ajustar.
- Central exterior cobrir.
- Ala temporizar.

### Regra

O ala não deve ser considerado automaticamente responsável por controlar dois jogadores.

---

## 52. Três avançados contra quatro defesas

### Possibilidades

- Fixar centrais.
- Atacar intervalos.
- Explorar diagonais.
- Criar superioridade local.

### Limitações

- Defesa pode manter cobertura.
- Pivô pode ajudar.
- Laterais podem fechar.
- Avançados podem ficar isolados.

---

## 53. Dois avançados contra três centrais

### Possibilidades

- Movimentos complementares.
- Um PL baixa.
- Outro ataca profundidade.
- Arrastamento de central.
- Ataque a intervalos.

### Regra

A relação numérica deve ser analisada em conjunto com os movimentos.

---

# PARTE IX — TRANSFORMAÇÕES ESTRUTURAIS

## 54. Transformação 4-3-3 para 3-2-5

### Possibilidade

- Um lateral entra na primeira linha.
- Outro lateral projeta-se.
- Dois médios oferecem apoio.
- Cinco referências ocupam zonas avançadas.

### Regra

A transformação pode ocorrer através de diferentes movimentos.

---

## 55. Transformação 4-2-3-1 para 4-4-2

### Possibilidade

- MO sobe para pressionar ao lado do PL.
- Extremos recuam.
- Duplo pivô protege centro.

### Objetivos

- Pressionar dois centrais.
- Controlar largura.
- Proteger zona central.

---

## 56. Transformação 3-5-2 para 5-3-2

### Possibilidade

- Alas baixam.
- Três médios mantêm proteção central.
- Dois PL permanecem avançados.

### Regra

A altura dos alas e a posição dos médios determinam a estrutura real.

---

## 57. Transformação 3-4-3 para 5-4-1

### Possibilidade

- Alas baixam.
- Avançados exteriores integram linha média.
- PL permanece avançado.

### Objetivos

- Proteger centro.
- Controlar corredores.
- Reduzir espaço entre linhas.

---

## 58. Transformações assimétricas

### Exemplo

- Um lateral entra por dentro.
- Outro lateral sobe.
- Um extremo mantém largura.
- Outro extremo entra no corredor interior.

### Regra

A IA deve descrever a assimetria e identificar as funções, em vez de forçar uma classificação rígida.

---

# PARTE X — IDENTIFICAÇÃO DE VULNERABILIDADES

## 59. Vulnerabilidades na primeira construção

Possíveis sinais:

- Central sem apoio.
- Pivô bloqueado.
- GR pressionado.
- Laterais sem linha.
- Distâncias excessivas.
- Passe previsível.

### Regra

Uma vulnerabilidade só deve ser considerada explorável quando existe mecanismo de pressão ou progressão adequado.

---

## 60. Vulnerabilidades no meio-campo

Possíveis sinais:

- Inferioridade central.
- Espaço entre linhas.
- Pivô isolado.
- Médios demasiado afastados.
- Falta de cobertura.
- Receções orientadas do adversário.

---

## 61. Vulnerabilidades nos corredores exteriores

Possíveis sinais:

- Lateral isolado.
- Ala demasiado alto.
- Espaço nas costas.
- Extremo sem recuperação.
- Central exterior obrigado a sair.

---

## 62. Vulnerabilidades nos corredores interiores

Possíveis sinais:

- Intervalo entre lateral e central.
- Pivô afastado.
- Central atraído.
- Médio adversário livre.
- Falta de cobertura.

---

## 63. Vulnerabilidades na última linha

Possíveis sinais:

- Centrais afastados.
- Linha demasiado alta sem pressão.
- Falta de cobertura.
- Movimentos de arrastamento.
- Espaço nas costas.

---

## 64. Vulnerabilidades nas transições

Possíveis sinais:

- Laterais ou alas projetados.
- Pivôs ultrapassados.
- Poucos jogadores de equilíbrio.
- Centrais isolados.
- Falta de reação à perda.

---

# PARTE XI — METODOLOGIA DE OBSERVAÇÃO

## 65. Primeira observação

Identificar:

- Sistema nominal.
- Distribuição inicial.
- Número de defesas.
- Número de médios.
- Número de avançados.
- Funções aparentes.

### Regra

A primeira observação deve produzir hipóteses, não conclusões definitivas.

---

## 66. Observação da construção

Verificar:

1. Quantos jogadores formam a primeira linha?
2. O GR participa?
3. Algum pivô baixa?
4. Algum lateral entra por dentro?
5. Os laterais estão altos ou baixos?
6. Onde estão os médios?
7. Existe largura?
8. Existem jogadores entre linhas?
9. Como reage à pressão?
10. Existem alternativas?

---

## 67. Observação do ataque

Verificar:

1. Quantos jogadores ocupam a última linha?
2. Quem oferece largura?
3. Quem ocupa corredores interiores?
4. Quem ataca profundidade?
5. Quem oferece apoio?
6. Existem movimentos complementares?
7. Como é protegida a perda?
8. Existem assimetrias?

---

## 68. Observação da defesa

Verificar:

1. Qual é a altura do bloco?
2. Quantos jogadores pressionam?
3. Qual é a primeira linha?
4. Quantos jogadores existem no meio-campo?
5. Como é protegida a última linha?
6. Os extremos recuperam?
7. Os alas baixam?
8. Existe pressão individual, zonal ou mista?
9. Quais são os gatilhos?
10. Existem espaços exploráveis?

---

## 69. Observação das transições

### Após recuperação

- Acelera?
- Conserva?
- Procura PL?
- Explora largura?
- Ataca profundidade?
- Utiliza condução?

### Após perda

- Contra-pressiona?
- Temporiza?
- Recupera?
- Reorganiza?
- Protege centro?
- Controla profundidade?

---

## 70. Observação repetida

Uma ação isolada pode resultar de:

- Erro individual.
- Adaptação momentânea.
- Condição específica.
- Movimento não coordenado.
- Comportamento intencional.

### Regra

A IA deve distinguir:

- Comportamento isolado.
- Comportamento recorrente.
- Padrão consistente.
- Hipótese ainda não confirmada.

---

# PARTE XII — CASOS PRÁTICOS

## 71. Caso A — Adversário nominalmente em 4-3-3

**Observação:**

- Lateral direito entra por dentro.
- Lateral esquerdo sobe.
- Dois centrais permanecem.
- Extremos mantêm largura.
- Um médio aproxima-se dos centrais.

**Análise:**

A estrutura pode assumir uma configuração de três jogadores na primeira linha e dois apoios.

**Conclusão condicionada:**

Possível 3-2-5.

**Verificação necessária:**

- Altura dos restantes médios.
- Ocupação da última linha.
- Continuidade do comportamento.

---

## 72. Caso B — Adversário nominalmente em 4-2-3-1

**Observação:**

- MO sobe ao lado do PL.
- Extremos baixam.
- Duplo pivô mantém posição.
- Quatro defesas permanecem.

**Análise:**

A equipa pode defender em 4-4-2.

**Implicação:**

A primeira linha de pressão passa a ter duas referências.

**Verificação:**

- Quem condiciona pivô?
- Quem controla laterais?
- Qual é a altura do bloco?

---

## 73. Caso C — Adversário nominalmente em 3-5-2

**Observação:**

- Alas baixam.
- Três médios mantêm posições centrais.
- Dois PL permanecem avançados.

**Análise:**

Possível organização defensiva em 5-3-2.

**Implicações:**

- Cinco referências na última linha.
- Três médios centrais.
- Dois avançados disponíveis.

**Riscos possíveis para o adversário:**

- Espaço exterior intermédio.
- Dificuldade em pressionar laterais.

---

## 74. Caso D — Adversário nominalmente em 3-4-3

**Observação:**

- Alas baixam.
- Avançados exteriores recuam.
- Dois pivôs protegem centro.
- PL permanece avançado.

**Análise:**

Possível 5-4-1.

**Implicações:**

- Maior densidade defensiva.
- Menor pressão inicial.
- PL isolado.

**Verificação:**

- Distâncias entre linhas.
- Gatilhos de pressão.
- Capacidade de transição.

---

## 75. Caso E — Adversário com lateral interior

**Observação:**

- Lateral esquerdo abandona corredor exterior.
- Aproxima-se do pivô.
- Extremo esquerdo mantém largura.

**Análise:**

O adversário procura apoio central adicional.

**Possíveis objetivos:**

- Facilitar construção.
- Criar superioridade.
- Melhorar circulação.
- Proteger transição.

**Vulnerabilidades possíveis:**

- Espaço exterior na perda.
- Lateral longe da posição defensiva.

**Regra:**

A vulnerabilidade depende da cobertura existente.

---

## 76. Caso F — Adversário com extremos interiores

**Observação:**

- EE e ED aproximam-se dos corredores interiores.
- Laterais oferecem largura.
- PL fixa centrais.

**Análise:**

O adversário procura ocupação interior.

**Riscos defensivos para quem enfrenta:**

- Receções entre linhas.
- Ataque a intervalos.
- Combinações centrais.

**Possíveis vulnerabilidades adversárias:**

- Espaço nas costas dos laterais.
- Dependência da largura dos laterais.

---

## 77. Caso G — Adversário com dois PL móveis

**Observação:**

- Um PL baixa.
- Outro ataca profundidade.
- Médios procuram ligação.

**Análise:**

Os movimentos podem criar dilema para os centrais.

**Perguntas:**

- Quem acompanha?
- Quem cobre?
- Existe médio a proteger?
- Existe espaço nas costas?

**Regra:**

A IA não deve recomendar acompanhamento individual sem avaliar cobertura.

---

## 78. Caso H — Adversário em bloco baixo

**Observação:**

- Cinco jogadores na última linha.
- Quatro médios.
- Um PL.

**Análise:**

Possível 5-4-1.

**Implicações:**

- Proteção central.
- Menor espaço entre linhas.
- Menor pressão inicial.

**Possíveis oportunidades:**

- Circulação para deslocar bloco.
- Mudança de corredor.
- Exploração de espaços após movimentos.

**Regra:**

Não assumir que um bloco baixo é automaticamente vulnerável a cruzamentos.

---

## 79. Caso I — Adversário com pressão alta

**Observação:**

- Três avançados pressionam.
- Médios acompanham referências.
- Última linha sobe.

**Análise:**

Possível pressão alta com três referências.

**Implicações:**

- Menor tempo de decisão.
- Linhas de passe condicionadas.
- Espaço potencial nas costas.

**Verificação:**

- GR cria superioridade?
- Existem apoios interiores?
- Existe espaço para passe direto?
- Existe cobertura da profundidade?

---

## 80. Caso J — Adversário com estrutura assimétrica

**Observação:**

- Lateral esquerdo alto.
- Lateral direito baixo.
- Extremo esquerdo interior.
- Extremo direito aberto.

**Análise:**

Estrutura assimétrica.

**Possíveis objetivos:**

- Criar superioridade local.
- Explorar corredor específico.
- Proteger transição.
- Alterar referências de marcação.

**Regra:**

A IA deve descrever os movimentos e os espaços antes de atribuir uma formação rígida.

---

# PARTE XIII — REGRAS DE INTERPRETAÇÃO PARA A IA

## 81. Perguntas obrigatórias

Antes de classificar uma estrutura adversária, a IA deve verificar:

1. Qual é o sistema nominal?
2. Qual é a fase do jogo?
3. Qual é a localização da bola?
4. Qual é a estrutura real?
5. Quantos jogadores existem na primeira linha?
6. Quantos jogadores existem no meio-campo?
7. Quantos jogadores ocupam a última linha?
8. Quem oferece largura?
9. Quem ocupa corredores interiores?
10. Quem oferece profundidade?
11. Existem laterais interiores?
12. Existem alas altos?
13. Existem extremos interiores?
14. Existe um pivô que baixa?
15. Existe um avançado que baixa?
16. Existem movimentos assimétricos?
17. Qual é a altura do bloco?
18. Qual é a estrutura defensiva?
19. Qual é a primeira linha de pressão?
20. Existem coberturas?
21. Existem espaços entre linhas?
22. Existem superioridades numéricas?
23. Existem superioridades posicionais?
24. Existem superioridades qualitativas comprovadas?
25. Existem superioridades dinâmicas?
26. Existe superioridade funcional?
27. Existem vulnerabilidades?
28. As vulnerabilidades são exploráveis?
29. O comportamento é recorrente?
30. Existem dados suficientes?
31. Qual é o grau de confiança?
32. Qual é a alternativa interpretativa?

---

## 82. Classificação da confiança

### Confiança elevada

- Estrutura observada repetidamente.
- Funções identificadas.
- Movimentos consistentes.
- Relações claras.
- Evidência suficiente.

### Confiança moderada

- Estrutura observada em algumas situações.
- Funções parcialmente identificadas.
- Existem alternativas plausíveis.

### Confiança reduzida

- Observação isolada.
- Informação incompleta.
- Jogadores parcialmente ocultos.
- Fase de jogo ambígua.
- Possibilidade de interpretação alternativa.

### Regra

A confiança deve refletir a qualidade da evidência.

Não deve ser atribuída apenas pela familiaridade da IA com o sistema.

---

## 83. Observação, inferência e recomendação

A IA deve separar três níveis.

### Observação

O que foi efetivamente identificado.

**Exemplo:**

O lateral direito aproxima-se do pivô durante a construção.

### Inferência

O que esse comportamento pode significar.

**Exemplo:**

A equipa pode procurar superioridade central.

### Recomendação

Como responder ao comportamento.

**Exemplo:**

Avaliar pressão sobre o lateral interior, preservando cobertura exterior.

### Regra

Uma inferência não deve ser apresentada como facto confirmado.

---

## 84. Classificação das conclusões

### Conclusão fundamentada

Baseada em observações consistentes e relações verificáveis.

### Conclusão condicionada

Depende de informação adicional ou reação adversária.

### Conclusão contraditória

Não corresponde às posições, movimentos ou relações observadas.

### Informação insuficiente

Não existem dados suficientes para classificar a estrutura.

---

## 85. Erros de interpretação a evitar

A IA não deve:

- Confundir sistema nominal com estrutura real.
- Assumir que um 4-3-3 constrói sempre com dois centrais.
- Assumir que um 3-5-2 defende sempre em 5-3-2.
- Assumir que um 3-4-3 defende sempre em 5-2-3.
- Assumir que laterais permanecem sempre abertos.
- Assumir que extremos permanecem sempre exteriores.
- Assumir que três centrais garantem superioridade.
- Assumir que três médios garantem controlo central.
- Assumir que um ala consegue defender dois adversários simultaneamente.
- Assumir que uma estrutura assimétrica é um erro.
- Assumir que espaço livre é automaticamente explorável.
- Assumir que igualdade numérica significa igualdade funcional.
- Atribuir características individuais sem evidência.
- Classificar uma estrutura com base numa única imagem ambígua.
- Ignorar a localização da bola.
- Ignorar a altura das linhas.
- Ignorar a pressão sobre o portador.
- Ignorar as coberturas.
- Ignorar as transições.
- Confundir hipótese com observação.
- Recomendar soluções sem explicar riscos.
- Forçar uma classificação quando existem dados insuficientes.

---

# PARTE XIV — MODELO DE RESPOSTA DA IA

## 86. Estrutura recomendada de análise

Quando o utilizador apresentar um adversário, a IA deve organizar a resposta da seguinte forma:

### 1. Sistema nominal

Identificar a formação declarada.

### 2. Estrutura ofensiva observada

Descrever a distribuição com bola.

### 3. Estrutura defensiva observada

Descrever a distribuição sem bola.

### 4. Transformações

Explicar os movimentos que provocam alterações.

### 5. Relações espaciais

Identificar:

- Largura.
- Profundidade.
- Corredores interiores.
- Espaços entre linhas.
- Coberturas.

### 6. Superioridades

Identificar vantagens numéricas, posicionais, qualitativas ou dinâmicas, quando sustentadas.

### 7. Vulnerabilidades

Apresentar fragilidades possíveis e condições para as explorar.

### 8. Recomendações

Propor soluções compatíveis com a equipa analisada.

### 9. Riscos

Explicar como o adversário pode reagir.

### 10. Confiança

Indicar o grau de confiança e a informação em falta.

---

## 87. Exemplo de resposta fundamentada

**Informação disponível:**

- Adversário nominalmente em 4-3-3.
- Lateral esquerdo projeta-se.
- Lateral direito entra por dentro.
- Extremo esquerdo aproxima-se do corredor interior.
- Extremo direito mantém largura.
- Pivô oferece apoio central.

**Análise:**

O adversário apresenta uma organização ofensiva assimétrica.

O lateral direito aproxima-se do meio-campo, enquanto o esquerdo procura oferecer largura ou profundidade.

O extremo esquerdo ocupa zonas interiores e o direito mantém uma referência exterior.

A estrutura pode procurar criar superioridade central e diferentes alturas nos corredores.

**Vulnerabilidade possível:**

O espaço deixado pelo lateral esquerdo pode ser explorado após recuperação.

**Condição:**

É necessário verificar se existe cobertura e se a equipa consegue realizar a primeira ligação.

**Recomendação condicionada:**

Preparar uma referência para atacar esse espaço, preservando equilíbrio defensivo.

**Risco:**

Se o adversário mantiver cobertura adequada, a tentativa pode provocar perda e nova pressão.

**Confiança:**

Moderada, caso os movimentos tenham sido observados em várias ações, mas a estrutura completa não esteja confirmada.

---

# PARTE XV — RELAÇÃO COM OUTROS DOCUMENTOS

## 88. Fundamentos

- `conhecimento/fundamentos/fases_jogo.md`
- `conhecimento/fundamentos/principios_ofensivos.md`
- `conhecimento/fundamentos/principios_defensivos.md`
- `conhecimento/fundamentos/superioridades.md`
- `conhecimento/fundamentos/modelos_jogo.md`

## 89. Sistemas táticos

- `conhecimento/sistemas/352/organizacao.md`
- `conhecimento/sistemas/433/organizacao.md`
- `conhecimento/sistemas/4231/organizacao.md`
- `conhecimento/sistemas/343/organizacao.md`

As restantes componentes dos sistemas complementam a análise de construção, ataque, defesa e transições.

## 90. Análise dos adversários

- `conhecimento/adversarios/pressao_alta.md`
- `conhecimento/adversarios/bloco_medio.md`
- `conhecimento/adversarios/bloco_baixo.md`
- `conhecimento/adversarios/analise_vulnerabilidades.md`

Estes documentos aprofundam os comportamentos e as oportunidades identificadas na análise estrutural.

---

# PARTE XVI — PRINCÍPIO FINAL

## 91. Princípio central

A análise de um adversário deve começar pela observação da sua organização real.

O sistema nominal fornece uma referência inicial, mas não explica, por si só, os comportamentos coletivos.

A IA deve identificar:

- Como o adversário constrói.
- Como ocupa o meio-campo.
- Como ataca.
- Como defende.
- Como pressiona.
- Como reage às mudanças de posse.
- Como transforma a sua estrutura.
- Onde cria superioridades.
- Onde pode apresentar vulnerabilidades.

A interpretação deve considerar as posições, os movimentos, as coberturas, a localização da bola, a pressão e a capacidade de exploração dos espaços.

A IA deve evitar classificações rígidas, conclusões automáticas e recomendações baseadas exclusivamente na formação.

O objetivo final é transformar observações táticas em conhecimento útil para preparar jogos, adaptar estratégias e apoiar decisões fundamentadas.