# Sistema Tático 4-3-3 — Transições Ofensivas e Defensivas

## 1. Objetivo do documento

Este documento descreve os princípios, comportamentos e mecanismos das transições ofensivas e defensivas no sistema 4-3-3, utilizando como referência uma estrutura com um médio defensivo, dois médios interiores, dois extremos e um ponta de lança.

O objetivo é permitir que o assistente de inteligência artificial:

- Reconheça os momentos de transição ofensiva e defensiva.
- Analise a organização coletiva no instante da recuperação ou perda.
- Distinga transição ofensiva rápida de ataque organizado.
- Distinga contra-pressão de recuperação defensiva.
- Identifique oportunidades para explorar a desorganização adversária.
- Reconheça quando acelerar, temporizar ou conservar a posse.
- Analise as responsabilidades dos diferentes jogadores.
- Avalie a ocupação dos corredores e o controlo da profundidade.
- Reconheça superioridades e inferioridades funcionais.
- Analise a proteção preventiva antes da perda.
- Identifique riscos de contra-ataque.
- Proponha soluções táticas com condições, continuidade e alternativas.
- Avalie a reorganização coletiva após cada transição.

Este documento apresenta conhecimento universal sobre o 4-3-3.

Não determina que todas as equipas devam utilizar contra-pressão imediata, contra-ataque rápido ou os mesmos mecanismos de reorganização.

---

# PARTE I — FUNDAMENTOS DAS TRANSIÇÕES

## 2. Conceito de transição

A transição corresponde à mudança de comportamento coletivo provocada pela alteração da posse de bola.

Existem dois momentos principais:

1. Transição ofensiva: a equipa recupera a posse.
2. Transição defensiva: a equipa perde a posse.

A transição não é definida apenas por um período fixo de segundos.

Depende da capacidade de uma ou ambas as equipas reorganizarem as suas estruturas.

### 2.1. Transição ofensiva

Começa quando a equipa conquista controlo da bola ou condições para iniciar uma ação ofensiva.

Pode originar:

- Contra-ataque.
- Ataque rápido.
- Conservação da posse.
- Reorganização ofensiva.
- Ligação direta.
- Progressão através de combinações.

### 2.2. Transição defensiva

Começa quando a equipa perde a posse ou deixa de controlar a bola e o adversário passa a ter possibilidade de atacar.

Pode originar:

- Contra-pressão.
- Contenção imediata.
- Temporização.
- Recuperação de posições.
- Proteção da profundidade.
- Reorganização em bloco.

### 2.3. Princípio fundamental

A melhor decisão não é necessariamente a mais rápida.

A decisão deve considerar a organização das duas equipas, os espaços disponíveis, as coberturas e o risco associado.

---

## 3. Estrutura nominal do 4-3-3

```text
       EE              PL              ED

              MC-E          MC-D

                      MDC

       LE       DCE        DCD       LD

                       GR
```

Durante as transições, os jogadores podem encontrar-se em posições muito diferentes das posições nominais.

Exemplos:

- Um lateral pode estar projetado.
- Um extremo pode estar numa posição interior.
- Um interior pode estar dentro da área adversária.
- O médio defensivo pode estar próximo dos centrais.
- O ponta de lança pode ter baixado para participar na construção.

Por isso, a análise deve começar pelas posições reais no momento da mudança de posse.

---

## 4. Fatores que determinam a transição

A IA deve considerar:

1. Zona da recuperação ou perda.
2. Identidade e posição do jogador que recupera ou perde.
3. Orientação corporal do portador.
4. Pressão imediata sobre a bola.
5. Distância entre os jogadores.
6. Número de adversários próximos.
7. Organização da linha defensiva adversária.
8. Espaço disponível nas costas.
9. Ocupação dos corredores.
10. Disponibilidade dos apoios.
11. Capacidade de progressão.
12. Proteção preventiva.
13. Superioridades ou inferioridades funcionais.
14. Possibilidade de reorganização.
15. Contexto competitivo e modelo de jogo.

A ausência de dados deve originar hipóteses condicionais, e não afirmações definitivas.

---

# PARTE II — TRANSIÇÃO OFENSIVA

## 5. Objetivos da transição ofensiva

Após recuperar a bola, a equipa pode procurar:

- Explorar espaços deixados pelo adversário.
- Progredir antes da reorganização defensiva.
- Criar superioridade numérica ou posicional.
- Encontrar um jogador livre.
- Atacar profundidade.
- Criar oportunidade de finalização.
- Conservar a posse quando não existe vantagem.
- Preparar uma organização ofensiva estável.

### 5.1. Princípio de decisão

A equipa deve procurar reconhecer se existe uma vantagem transitória.

Se existir, pode acelerar.

Se não existir, pode ser preferível assegurar a posse e reorganizar.

---

## 6. Primeiro momento após recuperação

O primeiro jogador com controlo da bola deve avaliar:

- Existe pressão imediata?
- Posso conduzir?
- Existe passe vertical?
- Existe apoio próximo?
- Existe espaço nas costas?
- Há superioridade ofensiva?
- Existe risco de perda imediata?
- Qual é a melhor continuidade?

### 6.1. Recuperação com espaço

Pode permitir:

- Condução.
- Passe vertical.
- Mudança de corredor.
- Ataque rápido.

### 6.2. Recuperação sob pressão

Pode exigir:

- Proteção da bola.
- Passe de segurança.
- Apoio frontal.
- Terceiro homem.
- Temporização.

### 6.3. Regra

Não recomendar automaticamente um passe vertical após qualquer recuperação.

A linha de passe e as condições de receção devem existir.

---

## 7. Contra-ataque

### 7.1. Conceito

O contra-ataque procura explorar a desorganização adversária após recuperação.

### 7.2. Objetivos

- Progredir rapidamente.
- Explorar espaços livres.
- Atacar a última linha.
- Criar oportunidade antes da reorganização.

### 7.3. Jogadores possíveis

- PL como referência central.
- EE e ED em profundidade.
- MC-E e MC-D como apoios ou jogadores em chegada.
- MDC como primeira ligação ou cobertura.
- Laterais em apoio, conforme a posição inicial.

### 7.4. Riscos

- Passe precipitado.
- Avançado isolado.
- Falta de apoio.
- Perda em inferioridade.
- Exposição a uma nova transição defensiva.

### 7.5. Regra

Um contra-ataque deve ser recomendado quando existe uma oportunidade funcional, não apenas porque a equipa recuperou a bola.

---

## 8. Contra-ataque pelo corredor central

### 8.1. Situação

A equipa recupera a bola numa zona central.

### 8.2. Soluções possíveis

- Condução.
- Passe para PL.
- Passe para interior em progressão.
- Combinação de terceiro homem.
- Passe de rutura.
- Abertura para extremo.

### 8.3. Exemplo

1. MDC recupera a bola.
2. MC-D procura oferecer apoio.
3. PL fixa ou movimenta a última linha.
4. ED ameaça profundidade.
5. MDC identifica a opção disponível.
6. A equipa procura explorar a vantagem.

### 8.4. Alternativa

Se o corredor central estiver fechado, a equipa pode procurar um extremo ou conservar a posse.

### 8.5. Riscos

- Passe vertical intercetado.
- Falta de apoio.
- MDC perder novamente a bola.
- Espaço central desprotegido.

---

## 9. Contra-ataque pelo corredor lateral

### 9.1. Situação

A recuperação ocorre junto à linha lateral.

### 9.2. Soluções possíveis

- Extremo conduz.
- Interior oferece apoio diagonal.
- PL ataca profundidade.
- Lateral acompanha.
- Mudança de corredor.
- Passe interior.

### 9.3. Exemplo

1. LE recupera a bola.
2. EE procura receber.
3. MC-E oferece apoio interior.
4. PL movimenta-se para criar profundidade.
5. LE escolhe a ligação disponível.
6. A equipa procura progredir.

### 9.4. Alternativa

Se EE estiver pressionado, LE pode procurar MC-E ou uma ligação de segurança.

### 9.5. Riscos

- Armadilha de pressão.
- Passe junto à linha intercetado.
- Falta de apoio.
- Espaço nas costas de LE.

---

## 10. Contra-ataque através dos extremos

Os extremos podem ser referências importantes nas transições ofensivas.

### 10.1. Extremo em largura

Pode explorar espaço exterior.

### 10.2. Extremo em profundidade

Pode atacar as costas da linha defensiva.

### 10.3. Extremo interior

Pode explorar espaços entre central e lateral.

### 10.4. Extremo em apoio

Pode aproximar-se para facilitar a primeira ligação.

### 10.5. Riscos

- Extremo isolado.
- Passe longo sem condições.
- Falta de ocupação da área.
- Ausência de segunda vaga.

### 10.6. Regra

A posição nominal de extremo não determina obrigatoriamente que o jogador deva correr para o corredor lateral.

O movimento deve responder ao espaço disponível.

---

## 11. Papel do ponta de lança na transição ofensiva

### 11.1. Fixação

Pode condicionar os centrais adversários.

### 11.2. Apoio frontal

Pode receber e devolver para um interior.

### 11.3. Profundidade

Pode atacar espaço nas costas.

### 11.4. Movimento lateral

Pode libertar espaço central.

### 11.5. Terceiro homem

Pode participar em combinações.

### 11.6. Exemplo

1. MC-E recupera a bola.
2. PL oferece apoio.
3. MC-E procura PL se a linha estiver disponível.
4. PL pode devolver para MC-D.
5. MC-D procura progredir.

### 11.7. Riscos

- Receção de costas sob pressão.
- Falta de apoio.
- Passe intercetado.
- Movimento que elimina profundidade sem alternativa.

---

## 12. Papel dos médios interiores na transição ofensiva

### 12.1. Apoio próximo

Podem facilitar a primeira ligação.

### 12.2. Condução

Podem transportar a bola.

### 12.3. Passe vertical

Podem procurar referências avançadas.

### 12.4. Rutura

Podem atacar espaço nas costas.

### 12.5. Segunda vaga

Podem chegar à entrada da área.

### 12.6. Cobertura

Um interior pode permanecer numa posição equilibrada.

### 12.7. Regra

Os dois interiores não precisam de executar o mesmo movimento.

A complementaridade pode permitir que um apoie e outro ataque profundidade.

---

## 13. Papel do médio defensivo na transição ofensiva

### 13.1. Primeira ligação

Pode receber após recuperação.

### 13.2. Distribuição

Pode procurar:

- Interior.
- Extremo.
- PL.
- Lateral.
- Mudança de corredor.

### 13.3. Temporização

Pode conservar a bola quando não existe vantagem imediata.

### 13.4. Cobertura preventiva

Pode permanecer numa posição de proteção.

### 13.5. Riscos

- Abandonar o centro.
- Passe vertical forçado.
- Perda em zona perigosa.
- Falta de proteção após progressão.

### 13.6. Regra

O MDC não deve ser obrigado a participar diretamente em todos os contra-ataques.

Pode ser mais importante assegurar o equilíbrio coletivo.

---

## 14. Papel dos laterais na transição ofensiva

### 14.1. Apoio exterior

Podem oferecer largura.

### 14.2. Progressão

Podem conduzir quando existe espaço.

### 14.3. Apoio interior

Podem aproximar-se do meio-campo.

### 14.4. Cobertura

Podem permanecer recuados para proteger a equipa.

### 14.5. Riscos

- Ambos projetarem-se sem cobertura.
- Espaço nas costas.
- Falta de proteção central.
- Perda durante progressão.

### 14.6. Regra

A projeção dos laterais deve depender da posição da bola, dos adversários e da proteção disponível.

---

## 15. Recuperação no meio-campo defensivo

### 15.1. Oportunidades

- Espaço nas costas da pressão.
- Extremos em profundidade.
- PL como referência.
- Interiores em apoio.

### 15.2. Riscos

- Recuperação sob pressão.
- Passe vertical intercetado.
- Falta de apoio.
- Nova perda perto da baliza.

### 15.3. Regra

A distância até à baliza adversária não impede necessariamente um contra-ataque.

Mas a progressão deve ser sustentável.

---

## 16. Recuperação no meio-campo ofensivo

### 16.1. Oportunidades

- Proximidade da baliza.
- Adversário desorganizado.
- Possibilidade de remate.
- Passe de rutura.
- Combinação curta.

### 16.2. Riscos

- Pressão imediata adversária.
- Passe precipitado.
- Falta de cobertura.
- Perda e contra-ataque.

### 16.3. Regra

Recuperar perto da baliza não significa que o remate imediato seja sempre a melhor solução.

---

## 17. Recuperação no corredor lateral

### 17.1. Objetivo

Sair da zona de pressão e encontrar progressão.

### 17.2. Soluções

- Passe interior.
- Condução exterior.
- Combinação com extremo.
- Apoio do interior.
- Mudança de corredor.
- Passe de segurança.

### 17.3. Riscos

- Linha lateral limitar opções.
- Pressão de dois adversários.
- Passe interior intercetado.
- Falta de continuidade.

---

## 18. Recuperação na área defensiva

### 18.1. Prioridade

Reconhecer o nível de pressão e risco.

### 18.2. Soluções possíveis

- Passe curto seguro.
- Ligação ao médio.
- Passe exterior.
- Passe longo.
- Condução se existir espaço.

### 18.3. Riscos

- Perda perto da baliza.
- Passe central intercetado.
- Falta de apoio.
- Tentativa de progressão sem condições.

### 18.4. Regra

A IA deve evitar recomendar risco elevado sem identificar uma vantagem que o justifique.

---

## 19. Conservação da posse após recuperação

### 19.1. Situação

A equipa recupera a bola, mas não encontra vantagem imediata.

### 19.2. Objetivos

- Evitar perda.
- Reorganizar posições.
- Criar apoios.
- Preparar ataque organizado.
- Controlar o ritmo.

### 19.3. Soluções possíveis

- Passe de segurança.
- Circulação.
- Apoio do MDC.
- Apoio dos centrais.
- Mudança de corredor.

### 19.4. Regra

Conservar a posse pode ser uma decisão ofensiva positiva.

Não deve ser automaticamente classificada como falta de ambição.

---

# PARTE III — TRANSIÇÃO DEFENSIVA

## 20. Objetivos da transição defensiva

Após perder a bola, a equipa pode procurar:

1. Impedir progressão imediata.
2. Recuperar a bola.
3. Proteger o corredor central.
4. Controlar profundidade.
5. Reduzir superioridades adversárias.
6. Ganhar tempo para reorganização.
7. Recuperar posições defensivas.
8. Impedir oportunidade de finalização.

### 20.1. Decisões possíveis

- Contra-pressionar.
- Conter.
- Temporizar.
- Recuperar.
- Proteger espaço.
- Reorganizar em bloco.

A decisão depende das condições existentes.

---

## 21. Primeiro momento após perda

A equipa deve avaliar:

- Onde ocorreu a perda?
- Quem está mais próximo?
- O adversário tem controlo?
- O adversário está orientado para progredir?
- Existem coberturas?
- Há superioridade local?
- O corredor central está protegido?
- Existe espaço nas costas?
- Os jogadores conseguem recuperar posição?

### 21.1. Regra

Não recomendar contra-pressão automática sem avaliar o contexto.

---

## 22. Contra-pressão

### 22.1. Conceito

A contra-pressão procura recuperar ou condicionar a bola imediatamente após a perda, antes de o adversário conseguir explorar a transição.

### 22.2. Objetivos

- Recuperar a posse.
- Impedir passe vertical.
- Reduzir tempo de decisão.
- Forçar erro.
- Ganhar tempo para reorganização.

### 22.3. Condições favoráveis

- Vários jogadores próximos.
- Distâncias curtas.
- Cobertura.
- Adversário pressionável.
- Espaços interiores controlados.
- Capacidade de reação coletiva.

### 22.4. Condições desfavoráveis

- Jogadores afastados.
- Adversário com espaço.
- Bola descoberta.
- Inferioridade local.
- Linha defensiva exposta.
- Falta de cobertura.

### 22.5. Regra

A contra-pressão deve ser avaliada como comportamento coletivo.

Um jogador isolado a perseguir o portador não constitui necessariamente contra-pressão eficaz.

---

## 23. Papel dos extremos após perda

### 23.1. Pressão imediata

Podem pressionar o adversário mais próximo.

### 23.2. Fecho de linhas

Podem impedir passes exteriores ou interiores.

### 23.3. Recuperação defensiva

Podem recuar para apoiar os laterais.

### 23.4. Proteção do corredor

Podem controlar a projeção dos laterais adversários.

### 23.5. Riscos

- Pressão sem apoio.
- Falta de recuperação.
- Lateral exposto.
- Espaço nas costas.

---

## 24. Papel do ponta de lança após perda

### 24.1. Pressão ao primeiro recetor

Pode tentar condicionar a saída adversária.

### 24.2. Fecho de linhas

Pode dificultar ligação com médios.

### 24.3. Temporização

Pode atrasar a circulação.

### 24.4. Preparação para reorganização

Pode recuperar uma posição que permita orientar a pressão seguinte.

### 24.5. Riscos

- Pressão isolada.
- Adversário ultrapassar facilmente.
- Falta de compactação.
- Distância excessiva ao meio-campo.

---

## 25. Papel dos médios interiores após perda

### 25.1. Pressão próxima

Podem aproximar-se do portador.

### 25.2. Fecho interior

Podem proteger linhas de passe centrais.

### 25.3. Cobertura

Podem apoiar o colega que pressiona.

### 25.4. Recuperação

Podem regressar às posições defensivas.

### 25.5. Riscos

- Ambos avançarem sem cobertura.
- MDC isolado.
- Espaço nas costas.
- Passe vertical adversário.

### 25.6. Regra

Um interior pode pressionar enquanto o outro protege uma zona relevante.

A decisão depende das posições reais.

---

## 26. Papel do médio defensivo após perda

O médio defensivo pode constituir uma referência essencial de equilíbrio.

### 26.1. Proteção central

Pode impedir progressão pelo centro.

### 26.2. Contenção

Pode pressionar o portador quando existem condições.

### 26.3. Cobertura dos centrais

Pode proteger espaços à frente da defesa.

### 26.4. Controlo do número 10

Pode impedir receção entre linhas.

### 26.5. Reorganização

Pode facilitar a recuperação da estrutura.

### 26.6. Riscos

- Ser atraído para o corredor lateral.
- Abandonar o centro.
- Ficar isolado.
- Ser ultrapassado por condução.
- Não controlar a profundidade.

### 26.7. Regra

O MDC não deve abandonar automaticamente a posição central para perseguir a bola.

---

## 27. Papel dos laterais após perda

### 27.1. Lateral próximo da bola

Pode:

- Contra-pressionar.
- Conter.
- Recuperar posição.
- Controlar o extremo adversário.

### 27.2. Lateral contrário

Pode:

- Ajustar posição interior.
- Controlar profundidade.
- Proteger segundo poste.
- Preparar cobertura.

### 27.3. Riscos

- Lateral projetado sem recuperação.
- Espaço nas costas.
- Central obrigado a sair.
- Corredor interior exposto.

---

## 28. Papel dos centrais após perda

### 28.1. Controlo da profundidade

Devem reconhecer movimentos adversários nas costas.

### 28.2. Contenção

Um central pode aproximar-se do portador quando existe cobertura.

### 28.3. Cobertura mútua

Devem proteger os espaços entre si.

### 28.4. Reorganização

Podem ajustar a linha segundo a pressão sobre a bola.

### 28.5. Riscos

- Ambos saírem à pressão.
- Espaço central aberto.
- Adversário atacar profundidade.
- Falta de cobertura.

### 28.6. Regra

A decisão de um central sair deve considerar a posição do outro central, dos laterais e do MDC.

---

# PARTE IV — PROTEÇÃO PREVENTIVA

## 29. Conceito de proteção preventiva

A proteção preventiva corresponde à organização da equipa durante a posse para responder a uma eventual perda.

É particularmente relevante quando:

- Os laterais estão projetados.
- Os interiores ocupam posições avançadas.
- Os extremos estão altos.
- A equipa ataca com muitos jogadores.
- O adversário mantém referências preparadas para contra-atacar.

### 29.1. Objetivos

- Controlar profundidade.
- Proteger o corredor central.
- Impedir progressão imediata.
- Garantir coberturas.
- Preparar contra-pressão ou recuperação.

---

## 30. Proteção preventiva numa estrutura 2-3-5

### 30.1. Estrutura possível

Dois centrais permanecem recuados.

Três jogadores ocupam uma linha intermédia de apoio e proteção.

### 30.2. Vantagens possíveis

- Presença central.
- Apoios próximos.
- Possibilidade de contra-pressão.
- Controlo de segundas bolas.

### 30.3. Riscos

- Centrais isolados.
- Laterais demasiado avançados.
- Espaço nas costas.
- Inferioridade perante dois ou mais avançados.

### 30.4. Regra

A proteção não deve ser considerada adequada apenas porque existem cinco jogadores fora da linha avançada.

É necessário avaliar posições, distâncias e referências adversárias.

---

## 31. Proteção preventiva numa estrutura 3-2-5

### 31.1. Estrutura possível

Três jogadores permanecem numa linha recuada.

Dois jogadores ocupam posições intermédias.

### 31.2. Vantagens possíveis

- Três referências de cobertura.
- Dois jogadores para controlar zonas centrais.
- Possibilidade de reação à perda.
- Maior variedade de coberturas.

### 31.3. Riscos

- Dois médios ultrapassados.
- Espaços exteriores.
- Falta de compactação.
- Avançados adversários em vantagem posicional.

### 31.4. Regra

A estrutura 3-2-5 não garante automaticamente maior segurança do que 2-3-5.

A eficácia depende da distribuição real e do adversário.

---

## 32. Laterais projetados simultaneamente

### 32.1. Situação

LE e LD encontram-se em posições avançadas.

### 32.2. Problema potencial

Podem surgir espaços nos dois corredores defensivos.

### 32.3. Soluções possíveis

- MDC mantém cobertura central.
- Centrais ajustam posicionamento.
- Um interior permanece equilibrado.
- A equipa prepara contra-pressão.
- Um lateral pode recuperar mais cedo.

### 32.4. Riscos

- Contra-ataque exterior.
- Centrais arrastados.
- Espaço central.
- Inferioridade defensiva.

### 32.5. Regra

Não proibir universalmente a projeção simultânea dos laterais.

A IA deve avaliar a proteção existente.

---

# PARTE V — REORGANIZAÇÃO DEFENSIVA

## 33. Quando não existe condição para contra-pressão

### 33.1. Situação

O adversário recupera com espaço e possibilidade de progressão.

### 33.2. Objetivo

Ganhar tempo e proteger zonas perigosas.

### 33.3. Soluções possíveis

- Contenção.
- Temporização.
- Recuperação de posições.
- Proteção central.
- Controlo da profundidade.
- Reorganização do bloco.

### 33.4. Regra

A recuperação defensiva pode ser a decisão mais adequada mesmo quando existe vontade de recuperar imediatamente a bola.

---

## 34. Reorganização para 4-1-4-1

### 34.1. Situação

A equipa perde a bola e procura recuperar uma estrutura compacta.

### 34.2. Comportamentos possíveis

1. Extremos recuperam para a linha média.
2. Interiores ajustam distâncias.
3. MDC protege espaço à frente dos centrais.
4. Laterais recuperam posições.
5. PL condiciona a circulação.
6. Centrais controlam profundidade.

### 34.3. Riscos

- Recuperação tardia dos extremos.
- MDC isolado.
- Espaço entre linhas.
- Adversário acelerar antes da reorganização.

---

## 35. Reorganização para 4-5-1

### 35.1. Objetivo

Aumentar a densidade no meio-campo.

### 35.2. Comportamentos possíveis

- Extremos recuam.
- Interiores aproximam-se.
- MDC ajusta altura.
- Defesa mantém compactação.
- PL permanece como referência avançada.

### 35.3. Riscos

- Falta de pressão.
- PL isolado.
- Adversário controlar posse.
- Dificuldade em recuperar território.

---

## 36. Temporização defensiva

### 36.1. Conceito

Um jogador procura atrasar a progressão adversária para permitir recuperação coletiva.

### 36.2. Objetivos

- Ganhar tempo.
- Reduzir velocidade.
- Orientar o portador.
- Proteger linhas de passe.
- Permitir recuperação dos colegas.

### 36.3. Riscos

- Portador ultrapassar contenção.
- Espaço nas costas.
- Falta de apoio.
- Adversário encontrar passe vertical.

### 36.4. Regra

Temporizar não significa necessariamente recuar de forma passiva.

Pode envolver aproximação controlada e orientação da progressão.

---

# PARTE VI — TRANSIÇÕES CONTRA DIFERENTES ADVERSÁRIOS

## 37. Transição ofensiva contra defesa com quatro jogadores

### 37.1. Oportunidades possíveis

- Espaço entre lateral e central.
- Extremos em profundidade.
- PL a fixar centrais.
- Interiores em chegada.

### 37.2. Riscos

- Linha defensiva compacta.
- Passe de rutura intercetado.
- Fora de jogo.
- Falta de apoio.

### 37.3. Regra

A IA deve avaliar a posição real dos quatro defesas.

---

## 38. Transição ofensiva contra defesa com três centrais

### 38.1. Oportunidades possíveis

- Espaços nas costas dos alas.
- Corredores exteriores.
- Movimentos diagonais dos extremos.
- Interiores em progressão.

### 38.2. Riscos

- Três centrais controlarem profundidade.
- PL isolado.
- Falta de apoio.
- Inferioridade em zonas centrais.

### 38.3. Regra

Não assumir que três centrais eliminam todas as oportunidades de contra-ataque.

---

## 39. Transição defensiva contra dois avançados

### 39.1. Situação

O adversário mantém dois avançados preparados para atacar profundidade.

### 39.2. Questões

- Quantos jogadores estão recuados?
- Existe cobertura central?
- O MDC está disponível?
- Os laterais estão projetados?
- Existe pressão sobre a bola?

### 39.3. Soluções possíveis

- Contenção do portador.
- Proteção da profundidade.
- Cobertura entre centrais.
- Recuperação de laterais.
- MDC protege espaço central.

### 39.4. Riscos

- Dois centrais em igualdade numérica.
- Espaço nas costas.
- Passe diagonal.
- Falta de cobertura.

---

## 40. Transição defensiva contra extremos rápidos

### 40.1. Situação

O adversário procura explorar os corredores exteriores após recuperação.

### 40.2. Soluções possíveis

- Pressionar o primeiro passador.
- Proteger linhas de passe exteriores.
- Laterais recuperam posição.
- Centrais ajustam cobertura.
- MDC protege o centro.
- Extremos da equipa recuperam.

### 40.3. Riscos

- Passe longo nas costas.
- Central arrastado.
- Inferioridade exterior.
- Falta de cobertura.

### 40.4. Regra

Não assumir características de velocidade sem informação documentada.

Quando não existem dados, referir apenas a ameaça de profundidade.

---

# PARTE VII — ERROS FREQUENTES

## 41. Erros na transição ofensiva

### 41.1. Passe vertical automático

A equipa tenta progredir sem avaliar linhas.

### 41.2. Avançados sem apoio

O portador procura referências isoladas.

### 41.3. Todos os jogadores aceleram

A equipa perde equilíbrio.

### 41.4. Falta de ocupação dos corredores

A progressão torna-se previsível.

### 41.5. Falta de segunda vaga

O ataque não tem continuidade.

### 41.6. Perda após recuperação

A equipa assume risco sem vantagem identificável.

### 41.7. Não reconhecer oportunidade

A equipa conserva a posse quando existe vantagem clara que poderia explorar.

---

## 42. Erros na transição defensiva

### 42.1. Contra-pressão isolada

Um jogador pressiona sem apoio.

### 42.2. Todos perseguem a bola

O corredor central fica desprotegido.

### 42.3. MDC abandona posição

Surgem espaços entre linhas.

### 42.4. Laterais não recuperam

Os corredores ficam expostos.

### 42.5. Centrais saem sem cobertura

A profundidade fica vulnerável.

### 42.6. Falta de temporização

O adversário progride sem oposição.

### 42.7. Reorganização tardia

A equipa não recupera compactação.

### 42.8. Linha defensiva sobe com bola descoberta

O adversário explora espaço nas costas.

---

# PARTE VIII — CASOS PRÁTICOS

## 43. Caso A — Recuperação do MDC e contra-ataque central

**Situação:**

MDC recupera a bola no meio-campo.

**Objetivo:** explorar a desorganização adversária.

**Solução possível:**

1. MDC controla a bola.
2. MC-E aproxima-se para apoio.
3. PL fixa a última linha.
4. ED procura profundidade.
5. MDC avalia passe vertical ou condução.
6. A equipa procura progredir se existir vantagem.

**Alternativa:**

Se não existir linha de passe, MDC pode conservar e reorganizar a posse.

**Riscos:**

- Passe intercetado.
- Perda central.
- Falta de cobertura.
- Contra-ataque adversário.

---

## 44. Caso B — Recuperação do lateral e progressão exterior

**Situação:**

LE recupera a bola junto à linha.

**Objetivo:** iniciar transição ofensiva.

**Solução possível:**

1. LE identifica pressão.
2. EE oferece largura ou profundidade.
3. MC-E aproxima-se interiormente.
4. PL movimenta-se.
5. LE procura a melhor ligação.
6. A equipa progride se existir espaço.

**Alternativa:**

Passe para MC-E ou DCE e reorganização ofensiva.

**Riscos:**

- Perda junto à linha.
- Pressão adversária.
- Falta de apoio.
- Espaço nas costas de LE.

---

## 45. Caso C — Perda com laterais projetados

**Situação:**

A equipa perde a bola enquanto LE e LD estão avançados.

**Objetivo:** impedir contra-ataque.

**Solução possível:**

1. Jogador próximo avalia contra-pressão.
2. MDC protege corredor central.
3. Centrais controlam profundidade.
4. Laterais iniciam recuperação.
5. Interiores ajustam coberturas.
6. A equipa procura reorganizar-se.

**Alternativa:**

Se não existir condição para contra-pressão, temporizar e recuperar posições.

**Riscos:**

- Espaços exteriores.
- Inferioridade defensiva.
- Passe de rutura.
- Centrais isolados.

---

## 46. Caso D — Perda no corredor interior

**Situação:**

MC-D perde a bola numa zona interior.

**Objetivo:** impedir progressão central.

**Solução possível:**

1. MC-D reage à perda.
2. MDC protege o espaço central.
3. LD ajusta cobertura.
4. DCD controla profundidade.
5. ED aproxima-se se existir condição para contra-pressão.
6. A equipa decide entre recuperar e reorganizar.

**Alternativa:**

Se o adversário ultrapassar a primeira reação, a equipa recupera para bloco médio.

**Riscos:**

- Passe vertical.
- MDC ultrapassado.
- Espaço nas costas de LD.
- Linha defensiva exposta.

---

## 47. Caso E — Recuperação alta e oportunidade de finalização

**Situação:**

EE recupera a bola perto da área adversária.

**Objetivo:** explorar a desorganização.

**Solução possível:**

1. EE controla a bola.
2. PL procura posição de finalização.
3. MC-E oferece apoio.
4. ED aproxima-se da zona de finalização.
5. EE avalia remate, passe ou condução.
6. A equipa procura criar oportunidade.

**Alternativa:**

Se não existir vantagem, conservar e reorganizar.

**Riscos:**

- Remate precipitado.
- Passe intercetado.
- Falta de cobertura.
- Nova transição defensiva.

---

## 48. Caso F — Contra-pressão após perda exterior

**Situação:**

ED perde a bola junto ao corredor direito.

**Objetivo:** recuperar ou impedir progressão.

**Solução possível:**

1. ED reage à perda.
2. LD aproxima-se se existir cobertura.
3. MC-D fecha apoio interior.
4. MDC protege o centro.
5. DCD controla profundidade.
6. A equipa procura recuperar ou temporizar.

**Alternativa:**

Se o adversário ultrapassar a pressão, reorganizar defensivamente.

**Riscos:**

- Espaço nas costas de LD.
- Passe interior.
- Mudança de corredor.
- Falta de cobertura.

---

## 49. Caso G — Contra-ataque adversário com dois avançados

**Situação:**

A equipa perde a bola e o adversário procura ligar com dois avançados.

**Objetivo:** controlar profundidade e reduzir perigo.

**Solução possível:**

1. Jogador próximo procura condicionar o primeiro passe.
2. MDC protege espaço central.
3. DCE e DCD ajustam distâncias.
4. Laterais recuperam ou mantêm coberturas.
5. A equipa procura temporizar.
6. O bloco reorganiza-se.

**Alternativa:**

Se existir superioridade local e cobertura, pode procurar-se recuperação imediata.

**Riscos:**

- Dois contra dois.
- Passe diagonal.
- Espaço nas costas.
- Falta de cobertura.

---

# PARTE IX — REGRAS DE ANÁLISE PARA A IA

## 50. Critérios de avaliação da transição ofensiva

Ao analisar uma recuperação de bola, verificar:

1. Onde ocorreu a recuperação?
2. Quem recuperou?
3. Existe controlo efetivo da posse?
4. Qual é a orientação corporal?
5. Existe pressão imediata?
6. Quem oferece apoio?
7. Quem oferece profundidade?
8. Quem assegura largura?
9. Existem linhas de passe?
10. Existem superioridades?
11. O adversário está desorganizado?
12. Existe espaço nas costas?
13. O PL está disponível?
14. Os extremos podem progredir?
15. Os interiores podem apoiar ou romper?
16. O MDC deve participar ou proteger?
17. Existem condições para contra-atacar?
18. É preferível conservar a posse?
19. Qual é a continuidade da jogada?
20. Como fica a proteção preventiva?

---

## 51. Critérios de avaliação da transição defensiva

Ao analisar uma perda, verificar:

1. Onde ocorreu a perda?
2. Quem perdeu?
3. O adversário tem controlo?
4. Existe pressão imediata?
5. Quantos jogadores estão próximos?
6. Existem coberturas?
7. Existe superioridade local?
8. O corredor central está protegido?
9. Onde está o MDC?
10. Onde estão os interiores?
11. Onde estão os laterais?
12. Como estão posicionados os centrais?
13. Existe espaço nas costas?
14. O portador adversário pode executar passe profundo?
15. Existem referências adversárias avançadas?
16. A contra-pressão é viável?
17. É preferível temporizar?
18. A equipa consegue recuperar posições?
19. Qual é a estrutura defensiva de reorganização?
20. Qual é a alternativa se a primeira ação falhar?

---

## 52. Classificação das soluções

**Solução fundamentada:** existe coerência entre posições, espaços, linhas de passe, coberturas e continuidade.

**Solução condicionada:** depende de uma reação adversária ou condição ainda não confirmada.

**Solução contraditória:** exige um passe ou movimento incompatível com a situação descrita.

**Informação insuficiente:** faltam dados para avaliar a decisão.

---

## 53. Regras de interpretação para o assistente de IA

- Não assumir que toda a recuperação deve originar contra-ataque.
- Não assumir que toda a perda deve originar contra-pressão.
- Não recomendar passes sem linhas disponíveis.
- Não recomendar rutura sem espaço ou condições de passe.
- Não recomendar condução quando existe pressão incompatível.
- Não considerar superioridade numérica automaticamente funcional.
- Não assumir que os extremos estão sempre abertos.
- Não assumir que os laterais estão sempre recuados.
- Não assumir que o MDC deve participar em todos os contra-ataques.
- Não recomendar que todos os jogadores pressionem a bola.
- Não recomendar que ambos os centrais abandonem posições sem cobertura.
- Não recomendar subida da linha com bola descoberta.
- Não ignorar os espaços nas costas dos laterais.
- Não ignorar a proteção do corredor central.
- Não ignorar a proteção preventiva.
- Não confundir contra-pressão com pressão alta organizada.
- Não confundir transição ofensiva com ataque posicional.
- Não assumir características individuais sem informação documentada.
- Explicar sempre condições, vantagens, riscos, continuidade e alternativas.
- Distinguir conhecimento universal de instruções específicas da equipa.
- Quando faltarem dados, apresentar hipóteses condicionais.

---

## 54. Princípio final

As transições do 4-3-3 dependem da capacidade coletiva para reconhecer rapidamente as condições criadas pela recuperação ou perda da bola.

Na transição ofensiva, a equipa deve identificar se existe vantagem para acelerar ou se é preferível conservar e reorganizar a posse.

Na transição defensiva, deve decidir entre contra-pressionar, conter, temporizar e recuperar posições, garantindo proteção central, coberturas e controlo da profundidade.

O assistente de IA deve avaliar cada transição segundo as posições reais, a organização adversária, as linhas de passe, as distâncias, as superioridades funcionais e os riscos associados.