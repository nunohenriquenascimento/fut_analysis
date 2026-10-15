# Sistema Tático 4-2-3-1 — Transições Ofensivas e Defensivas

## 1. Objetivo do documento

Este documento descreve os princípios universais das transições ofensivas e defensivas no sistema 4-2-3-1.

A estrutura nominal inclui:

- Um guarda-redes.
- Dois defesas centrais.
- Dois laterais.
- Dois médios de apoio, formando o duplo pivô.
- Um médio ofensivo, habitualmente designado número 10.
- Dois extremos.
- Um ponta de lança.

O objetivo é permitir que o assistente de inteligência artificial:

- Identifique o momento de recuperação ou perda de bola.
- Distinga transição de organização estabilizada.
- Analise as condições para contra-atacar.
- Reconheça quando é preferível conservar a posse.
- Avalie os movimentos do ponta de lança, número 10 e extremos.
- Compreenda o papel do duplo pivô nas duas transições.
- Analise a participação dos laterais.
- Identifique superioridades numéricas, posicionais, qualitativas, dinâmicas e temporais.
- Avalie a possibilidade de contra-pressão.
- Reconheça quando é necessário temporizar ou recuar.
- Identifique riscos associados a perdas centrais e exteriores.
- Analise a proteção da profundidade.
- Reconheça vulnerabilidades criadas por laterais projetados.
- Compreenda os ajustamentos perante diferentes sistemas adversários.
- Proponha decisões condicionadas às posições reais, às coberturas e às reações adversárias.

O documento apresenta conhecimento tático universal.

Não define obrigatoriamente o modelo de transições de uma equipa específica.

---

# PARTE I — FUNDAMENTOS DAS TRANSIÇÕES

## 2. Conceito de transição

Uma transição ocorre quando a posse de bola muda de equipa.

Existem dois momentos principais:

1. Transição ofensiva: recuperação da posse.
2. Transição defensiva: perda da posse.

A mudança de posse altera imediatamente as responsabilidades dos jogadores.

Uma equipa que estava a atacar passa a ter de defender.

Uma equipa que estava a defender passa a poder atacar.

### 2.1. Característica fundamental

A transição acontece frequentemente antes de ambas as equipas conseguirem reorganizar as suas estruturas.

Por esse motivo, podem existir:

- Espaços temporariamente disponíveis.
- Jogadores fora das posições habituais.
- Referências defensivas desorganizadas.
- Superioridades momentâneas.
- Distâncias excessivas.
- Possibilidades de progressão rápida.
- Riscos elevados de perda ou contra-ataque.

### 2.2. Regra para a IA

Não assumir que qualquer recuperação deve originar um contra-ataque.

Não assumir que qualquer perda deve originar contra-pressão.

A decisão depende das condições reais.

---

## 3. Estrutura nominal do 4-2-3-1

```text
                         PL

          EE             MO             ED

                   MDC-E    MDC-D

          LE        DCE    DCD        LD

                         GR
```

Durante uma transição, esta estrutura pode estar completamente alterada.

Por exemplo:

- Um lateral pode estar próximo da área adversária.
- Um pivô pode encontrar-se à frente da bola.
- O MO pode estar próximo do PL.
- Um extremo pode estar no corredor interior.
- O PL pode ter baixado para apoiar.
- Os centrais podem estar afastados.
- O outro lateral pode estar numa posição interior de cobertura.

### 3.1. Consequência

A análise deve partir da posição efetiva dos jogadores no momento da mudança de posse.

---

## 4. Diferença entre transição e ataque rápido

Nem todo o ataque rápido é uma transição ofensiva.

Uma equipa pode atacar rapidamente durante uma fase de organização ofensiva.

Da mesma forma, uma transição ofensiva não implica obrigatoriamente velocidade máxima.

### 4.1. Transição ofensiva rápida

Procura explorar a desorganização adversária imediatamente após a recuperação.

### 4.2. Transição ofensiva de conservação

A equipa recupera e decide manter a bola para organizar o ataque.

### 4.3. Regra

A IA deve identificar a origem da posse e as condições de reorganização adversária antes de classificar a ação.

---

## 5. Variáveis fundamentais de decisão

Após recuperar ou perder a bola, devem ser avaliadas:

1. Zona do campo.
2. Localização do portador.
3. Orientação corporal.
4. Pressão sobre a bola.
5. Número de jogadores próximos.
6. Número de adversários próximos.
7. Espaço disponível.
8. Profundidade disponível.
9. Distância à baliza.
10. Posição dos extremos.
11. Posição do MO.
12. Posição do PL.
13. Posição dos pivôs.
14. Posição dos laterais.
15. Coberturas existentes.
16. Capacidade de recuperação defensiva.
17. Linhas de passe.
18. Possibilidade de condução.
19. Risco de perda.
20. Continuidade da ação.

A decisão deve resultar da combinação destes fatores.

---

# PARTE II — TRANSIÇÃO OFENSIVA

## 6. Conceito de transição ofensiva

A transição ofensiva começa quando a equipa recupera a posse.

O objetivo pode ser:

- Explorar espaço.
- Ultrapassar adversários desorganizados.
- Atacar profundidade.
- Criar superioridade.
- Aproximar-se da baliza.
- Finalizar.
- Conservar a posse.
- Reorganizar o ataque.

### 6.1. Princípio fundamental

A recuperação cria uma oportunidade de decisão, não uma obrigação de acelerar.

---

## 7. Primeira decisão após recuperação

O jogador que recupera deve identificar:

- Existe pressão imediata?
- Consegue orientar-se para a frente?
- Existe passe vertical?
- Existe espaço para conduzir?
- Existe apoio próximo?
- Existem jogadores em profundidade?
- O adversário está equilibrado?
- A equipa mantém proteção suficiente?

### 7.1. Árvore de decisão

**Se existe espaço, orientação favorável e apoio:**

Procurar progressão rápida.

**Se existe passe vertical seguro e vantajoso:**

Procurar a ligação.

**Se o portador está pressionado:**

Procurar apoio, proteção ou passe de segurança.

**Se o adversário já recuperou a organização:**

Considerar circulação e ataque organizado.

**Se não existem coberturas para uma ação arriscada:**

Avaliar conservação da posse.

### 7.2. Regra

O primeiro passe após recuperação não tem de ser vertical.

Deve ser o passe que melhor permite explorar ou preservar a vantagem disponível.

---

## 8. Recuperação em zona alta

### 8.1. Situação

A equipa recupera perto da baliza adversária.

### 8.2. Oportunidades possíveis

- Finalização imediata.
- Passe para MO.
- Passe para PL.
- Ataque rápido à área.
- Aproveitamento de defensores desorganizados.
- Remate após recuperação.

### 8.3. Exemplo

1. ED recupera a bola junto ao lateral adversário.
2. MO aproxima-se pelo corredor interior.
3. PL ocupa uma referência de finalização.
4. EE identifica possibilidade de atacar o segundo poste.
5. ED avalia passe interior, condução ou finalização.
6. A equipa procura criar oportunidade antes da reorganização adversária.

### 8.4. Riscos

- Passe interior intercetado.
- Remate precipitado.
- Excesso de jogadores à frente da bola.
- Falta de proteção perante nova perda.

### 8.5. Alternativa

Se a recuperação não permitir uma oportunidade favorável, conservar a bola e reorganizar o ataque.

---

## 9. Recuperação em zona média

### 9.1. Situação

A equipa recupera no meio-campo.

### 9.2. Oportunidades possíveis

- Explorar espaço nas costas dos médios adversários.
- Encontrar MO entre linhas.
- Atacar através dos extremos.
- Utilizar PL em apoio.
- Conduzir para atrair defensores.
- Criar superioridade temporária.

### 9.3. Exemplo

1. MDC-E interceta um passe.
2. MO posiciona-se à frente da recuperação.
3. PL ameaça profundidade.
4. EE e ED procuram espaços disponíveis.
5. MDC-E identifica linha de passe.
6. Se MO puder receber orientado, procura a ligação.
7. MO decide entre condução, passe de rutura ou apoio.

### 9.4. Riscos

- MO marcado.
- Passe vertical intercetado.
- Pivô recuperador pressionado.
- Perda central.
- Falta de cobertura.

### 9.5. Alternativa

Se a progressão central estiver fechada, utilizar um extremo, outro pivô ou apoio recuado.

---

## 10. Recuperação em zona baixa

### 10.1. Situação

A equipa recupera perto da própria área.

### 10.2. Objetivos possíveis

- Sair da pressão.
- Explorar espaço nas costas do adversário.
- Encontrar PL.
- Ligar ao MO.
- Utilizar extremos.
- Conservar a posse.
- Evitar nova perda perigosa.

### 10.3. Exemplo

1. DCE recupera a bola.
2. MDC-E aproxima-se para apoiar.
3. MO procura espaço à frente.
4. PL oferece apoio ou profundidade.
5. EE identifica espaço exterior.
6. DCE avalia passe curto, médio ou longo.
7. A equipa procura uma saída funcional.

### 10.4. Riscos

- Passe curto sob pressão.
- PL isolado.
- Extremos demasiado distantes.
- Segunda bola adversária.
- Nova perda junto à área.

### 10.5. Regra

Não recomendar saída curta automaticamente após recuperação em zona baixa.

A decisão depende da pressão e das linhas disponíveis.

---

# PARTE III — PAPEL DOS JOGADORES NA TRANSIÇÃO OFENSIVA

## 11. Ponta de lança na transição ofensiva

O PL pode assumir diferentes funções.

### 11.1. Ataque à profundidade

Procura explorar espaço nas costas dos centrais.

### 11.2. Apoio frontal

Baixa para receber e ligar com MO ou extremos.

### 11.3. Fixação

Mantém referências defensivas ocupadas.

### 11.4. Movimento diagonal

Procura explorar intervalos entre defensores.

### 11.5. Ataque à área

Ocupa zonas de finalização.

### 11.6. Riscos

- Fora de jogo.
- Isolamento.
- Receção sem apoio.
- Movimento para zona ocupada.
- Falta de presença central.

### 11.7. Regra

O PL não deve atacar sempre profundidade.

A sua função depende do espaço, do portador e das posições dos colegas.

---

## 12. Médio ofensivo na transição ofensiva

O número 10 pode ser a principal ligação entre recuperação e ataque.

### 12.1. Funções possíveis

- Receber entre linhas.
- Conduzir.
- Distribuir.
- Encontrar passe de rutura.
- Combinar com PL.
- Ligar aos extremos.
- Atacar área.
- Finalizar.
- Atrair adversários.

### 12.2. MO recebe orientado

Se recebe de frente para a baliza, pode acelerar a progressão.

### 12.3. MO recebe de costas

Pode precisar de apoio, proteção ou combinação.

### 12.4. MO está marcado

A equipa pode procurar outro jogador ou utilizar o movimento do MO para criar espaço.

### 12.5. Riscos

- Perda central.
- Condução excessiva.
- Passe precipitado.
- Falta de apoio.
- Distância excessiva aos pivôs.

---

## 13. Extremos na transição ofensiva

### 13.1. Funções possíveis

- Atacar profundidade.
- Manter largura.
- Realizar diagonal interior.
- Conduzir.
- Criar um contra um.
- Atacar área.
- Receber mudança de corredor.
- Oferecer apoio.

### 13.2. Extremo aberto

Pode explorar espaço exterior e obrigar a linha adversária a ajustar largura.

### 13.3. Extremo interior

Pode atacar o intervalo entre lateral e central.

### 13.4. Extremo do lado contrário

Pode:

- Atacar segundo poste.
- Oferecer largura.
- Aproximar-se para combinação.
- Preparar segunda bola.

### 13.5. Riscos

- Movimento demasiado antecipado.
- Fora de jogo.
- Isolamento.
- Falta de presença central.
- Passe indisponível.

---

## 14. Duplo pivô na transição ofensiva

### 14.1. Funções possíveis

- Recuperar a bola.
- Executar primeiro passe.
- Apoiar progressão.
- Conduzir.
- Mudar corredor.
- Controlar segunda bola.
- Garantir proteção preventiva.
- Aproximar-se da jogada.

### 14.2. Complementaridade

Um pivô pode avançar para apoiar a transição.

O outro pode manter cobertura.

### 14.3. Riscos

- Ambos avançarem.
- Falta de proteção central.
- Distâncias excessivas.
- Perda após passe vertical.
- Centrais expostos.

### 14.4. Regra

A IA deve avaliar a posição real de ambos os pivôs, e não presumir que um deles permanece sempre recuado.

---

## 15. Laterais na transição ofensiva

### 15.1. Funções possíveis

- Apoiar circulação.
- Oferecer largura.
- Projetar-se.
- Realizar ultrapassagem.
- Manter equilíbrio.
- Controlar profundidade defensiva.

### 15.2. Lateral próximo da recuperação

Pode oferecer apoio imediato.

### 15.3. Lateral contrário

Pode permanecer equilibrado ou avançar, dependendo da cobertura disponível.

### 15.4. Riscos

- Ambos os laterais projetarem-se.
- Espaço nas costas.
- Falta de proteção preventiva.
- Contra-ataque após nova perda.

---

# PARTE IV — MECANISMOS DE CONTRA-ATAQUE

## 16. Contra-ataque pelo corredor central

### 16.1. Objetivo

Explorar espaços interiores antes da reorganização adversária.

### 16.2. Referências possíveis

- MO.
- PL.
- Pivô em condução.
- Extremo interior.

### 16.3. Exemplo

1. MDC-D recupera.
2. MO recebe entre linhas.
3. PL fixa centrais.
4. ED ataca intervalo.
5. MO identifica o movimento.
6. Se existir linha, executa passe.
7. ED procura finalização ou assistência.

### 16.4. Riscos

- Passe intercetado.
- MO pressionado.
- PL e extremo atacarem o mesmo espaço.
- Falta de cobertura.

### 16.5. Alternativa

Se o centro estiver fechado, procurar corredor exterior ou conservar a bola.

---

## 17. Contra-ataque pelo corredor lateral

### 17.1. Objetivo

Explorar espaço exterior.

### 17.2. Exemplo

1. MDC-E recupera.
2. EE oferece largura.
3. MO aproxima-se do corredor interior.
4. PL ameaça profundidade.
5. MDC-E procura EE.
6. EE avalia condução, combinação ou passe.
7. A equipa procura atacar área.

### 17.3. Riscos

- EE isolado.
- Lateral adversário recuperar posição.
- Falta de apoio interior.
- Cruzamento sem referências.

### 17.4. Alternativa

Se o corredor exterior estiver fechado, EE pode procurar MO ou apoio recuado.

---

## 18. Contra-ataque através do PL em apoio

### 18.1. Objetivo

Utilizar o PL como ligação.

### 18.2. Exemplo

1. DCE recupera.
2. PL aproxima-se.
3. MO procura posição de apoio.
4. ED ameaça profundidade.
5. DCE procura PL se a linha estiver aberta.
6. PL recebe e combina com MO.
7. MO procura ED em profundidade.

### 18.3. Reação adversária

Se o central acompanhar PL, pode surgir espaço nas costas.

Se não acompanhar, PL pode receber à frente da linha, dependendo da pressão dos médios.

### 18.4. Riscos

- PL pressionado.
- Passe longo sem precisão.
- MO distante.
- ED sem espaço.
- Segunda bola perdida.

---

## 19. Contra-ataque com MO como terceiro homem

### 19.1. Objetivo

Ultrapassar uma referência defensiva através de combinação.

### 19.2. Exemplo

1. MDC-E recupera.
2. MO está marcado.
3. MDC-E encontra PL.
4. PL recebe em apoio.
5. MO desloca-se para nova linha.
6. PL procura MO.
7. MO acelera a jogada.

### 19.3. Condições

- Passe para PL disponível.
- PL capaz de ligar.
- MO com espaço para receber.
- Sincronização.
- Cobertura.

### 19.4. Riscos

- PL pressionado.
- MO continuar marcado.
- Passe intercetado.
- Falta de continuidade.

---

## 20. Contra-ataque com dois extremos em profundidade

### 20.1. Situação

Os extremos encontram espaços disponíveis nas costas dos laterais adversários.

### 20.2. Objetivo

Criar diferentes ameaças.

### 20.3. Possíveis movimentos

- EE ataca corredor exterior.
- ED ataca corredor interior.
- PL fixa centrais.
- MO conduz ou distribui.

### 20.4. Riscos

- MO sem linha de passe.
- Extremos demasiado distantes.
- PL isolado.
- Falta de proteção.
- Fora de jogo.

### 20.5. Regra

Não assumir que os dois extremos devem atacar simultaneamente a profundidade.

A complementaridade pode exigir que um ofereça apoio.

---

## 21. Condução após recuperação

### 21.1. Objetivo

Explorar espaço e atrair defensores.

### 21.2. Jogadores possíveis

- Pivô.
- MO.
- Extremo.
- Lateral.
- Central, em situações específicas.

### 21.3. Exemplo

1. MO recupera.
2. Existe espaço à frente.
3. MO conduz.
4. Um defensor aproxima-se.
5. PL e extremos ajustam movimentos.
6. MO avalia passe ou continuidade.

### 21.4. Riscos

- Perda central.
- Condução excessiva.
- Passe tardio.
- Falta de cobertura.

---

## 22. Mudança de corredor na transição

### 22.1. Objetivo

Explorar deslocamento defensivo adversário.

### 22.2. Exemplo

1. A recuperação ocorre à esquerda.
2. O adversário concentra jogadores.
3. MDC-E procura apoio.
4. MDC-D posiciona-se para receber.
5. A bola pode circular para a direita.
6. ED procura explorar espaço.

### 22.3. Riscos

- Passe intercetado.
- Mudança lenta.
- Lado contrário já controlado.
- Perda central.

### 22.4. Regra

A mudança de corredor só é vantajosa se existir espaço ou outra vantagem explorável.

---

# PARTE V — QUANDO NÃO CONTRA-ATACAR

## 23. Conservação após recuperação

### 23.1. Situações possíveis

- Portador pressionado.
- Adversário equilibrado.
- Ausência de profundidade.
- Falta de apoio.
- Inferioridade local.
- Risco elevado de nova perda.

### 23.2. Objetivos

- Garantir posse.
- Reorganizar jogadores.
- Recuperar distâncias.
- Preparar ataque.
- Evitar perda perigosa.

### 23.3. Exemplo

1. MDC-D recupera.
2. MO está marcado.
3. PL está isolado.
4. Extremos estão distantes.
5. MDC-D procura DCD.
6. A equipa reorganiza circulação.
7. Inicia ataque organizado.

### 23.4. Regra

Conservar a posse após recuperação pode ser uma decisão ofensiva correta.

---

## 24. Contra-ataque interrompido

### 24.1. Situação

A equipa inicia transição rápida, mas o adversário reorganiza-se.

### 24.2. Resposta possível

- Reduzir velocidade.
- Garantir apoios.
- Reorganizar largura.
- Reposicionar pivôs.
- Encontrar MO.
- Preparar circulação.

### 24.3. Riscos

- Insistir em passe impossível.
- Forçar remate.
- Perder com muitos jogadores projetados.
- Falta de cobertura.

---

# PARTE VI — TRANSIÇÃO DEFENSIVA

## 25. Conceito de transição defensiva

A transição defensiva começa quando a equipa perde a posse.

Os objetivos podem ser:

- Recuperar imediatamente.
- Impedir progressão.
- Condicionar primeiro passe.
- Proteger corredor central.
- Controlar profundidade.
- Temporizar.
- Reorganizar bloco.
- Evitar oportunidade adversária.

### 25.1. Princípio fundamental

A primeira reação deve considerar a relação entre pressão, cobertura e risco.

---

## 26. Primeira decisão após perda

### 26.1. Perguntas

- Onde ocorreu a perda?
- Quem está próximo da bola?
- O adversário recebe orientado?
- Existem jogadores disponíveis para pressionar?
- Existe cobertura?
- O centro está protegido?
- Os laterais estão projetados?
- O adversário tem profundidade?
- Existe inferioridade defensiva?
- A equipa consegue reorganizar-se?

### 26.2. Possíveis decisões

- Contra-pressionar.
- Condicionar o portador.
- Fechar passe interior.
- Temporizar.
- Recuperar posições.
- Proteger profundidade.
- Reorganizar bloco.

### 26.3. Regra

Não recomendar contra-pressão quando a equipa não possui condições coletivas para a sustentar.

---

# PARTE VII — CONTRA-PRESSÃO

## 27. Conceito de contra-pressão

A contra-pressão consiste na tentativa coordenada de recuperar a bola rapidamente após a perda.

### 27.1. Objetivos

- Recuperar posse.
- Impedir contra-ataque.
- Condicionar primeiro passe.
- Aproveitar proximidade dos jogadores.
- Manter pressão territorial.

### 27.2. Condições favoráveis

- Jogadores próximos.
- Portador adversário pressionável.
- Coberturas disponíveis.
- Linhas interiores controladas.
- Distâncias curtas.
- Proteção da profundidade.

### 27.3. Condições desfavoráveis

- Jogadores distantes.
- Adversário orientado para a frente.
- Falta de cobertura.
- Inferioridade defensiva.
- Laterais muito projetados.
- Espaço central aberto.

---

## 28. Contra-pressão com MO e extremos

### 28.1. Situação

A perda ocorre em zona avançada.

### 28.2. Resposta possível

1. Jogador mais próximo pressiona.
2. MO condiciona ligação interior.
3. Extremo próximo controla apoio exterior.
4. PL impede uma saída disponível, se possível.
5. Pivô próximo oferece cobertura.
6. Outro pivô protege zona central.
7. Linha defensiva controla profundidade.

### 28.3. Riscos

- MO e extremo pressionarem a mesma referência.
- Passe interior livre.
- Pivô sair sem cobertura.
- Passe longo nas costas.

### 28.4. Regra

A contra-pressão deve criar uma rede de contenção e coberturas, não apenas uma concentração de jogadores sobre a bola.

---

## 29. Contra-pressão com duplo pivô

### 29.1. Situação

A perda ocorre no meio-campo.

### 29.2. Organização possível

- Pivô próximo pressiona.
- Outro pivô protege centro.
- MO condiciona apoio.
- Extremos recuperam posições.
- Linha defensiva ajusta profundidade.

### 29.3. Riscos

- Ambos os pivôs avançarem.
- Centro desprotegido.
- Passe vertical ultrapassar pressão.
- Centrais isolados.

### 29.4. Regra

Os dois pivôs devem desempenhar funções complementares conforme a situação.

---

## 30. Quando abandonar a contra-pressão

### 30.1. Indicadores

- Adversário ultrapassa primeira pressão.
- Portador recebe orientado.
- Não existe cobertura.
- A equipa está em inferioridade.
- Existe ameaça clara de profundidade.
- Distâncias tornaram-se excessivas.

### 30.2. Resposta possível

1. Jogador próximo temporiza.
2. Restantes recuperam posições.
3. Pivôs protegem centro.
4. Laterais ajustam profundidade.
5. Centrais controlam referências.
6. A equipa reorganiza o bloco.

### 30.3. Regra

Persistir numa contra-pressão ultrapassada pode aumentar o risco de sofrer uma oportunidade.

---

# PARTE VIII — TEMPORIZAÇÃO E RECUPERAÇÃO DEFENSIVA

## 31. Conceito de temporização

Temporizar significa condicionar o ataque adversário para ganhar tempo de reorganização.

### 31.1. Objetivos

- Reduzir velocidade adversária.
- Impedir passe imediato.
- Proteger centro.
- Permitir recuperação dos colegas.
- Evitar isolamento dos defensores.

### 31.2. Comportamentos possíveis

- Controlar distância.
- Orientar condução.
- Fechar linha interior.
- Evitar ser ultrapassado.
- Recuar de forma controlada.

### 31.3. Riscos

- Recuo excessivo.
- Portador ganhar espaço para rematar.
- Passe de rutura.
- Falta de apoio.

---

## 32. Recuperação das posições

### 32.1. Prioridades

1. Proteger baliza.
2. Controlar corredor central.
3. Controlar profundidade.
4. Recuperar coberturas.
5. Reorganizar linha média.
6. Reorganizar linha defensiva.

A ordem prática pode variar segundo a ameaça imediata.

### 32.2. Regra

O jogador não deve regressar mecanicamente à posição nominal se existir uma ameaça mais urgente que precise de ser controlada.

---

# PARTE IX — PERDAS EM DIFERENTES ZONAS

## 33. Perda em zona alta

### 33.1. Situação

A equipa perde perto da área adversária.

### 33.2. Oportunidades defensivas

- Contra-pressão.
- Condicionamento do primeiro passe.
- Recuperação imediata.
- Bloqueio de saída central.

### 33.3. Riscos

- Adversário encontrar passe vertical.
- Laterais projetados.
- Pivôs ultrapassados.
- Centrais expostos.

### 33.4. Alternativa

Se a contra-pressão não for viável, reorganizar rapidamente a estrutura.

---

## 34. Perda em zona média

### 34.1. Situação

A equipa perde no meio-campo.

### 34.2. Riscos

- Adversário atacar diretamente a defesa.
- MO e extremos ficarem à frente da bola.
- Pivôs serem ultrapassados.
- Laterais fora de posição.

### 34.3. Resposta possível

- Pivô próximo condiciona.
- Outro pivô protege centro.
- MO recupera posição.
- Extremos ajudam corredores.
- Centrais controlam profundidade.

### 34.4. Regra

Uma perda central pode exigir proteção imediata da baliza em vez de tentativa agressiva de recuperação.

---

## 35. Perda em zona baixa

### 35.1. Situação

A equipa perde perto da própria área.

### 35.2. Prioridades

- Impedir remate.
- Proteger zona central.
- Controlar passe de rutura.
- Defender área.
- Recuperar posse se existir oportunidade.

### 35.3. Riscos

- Finalização imediata.
- Passe atrasado.
- Remate exterior.
- Segunda bola.
- Desorganização da linha defensiva.

### 35.4. Regra

A resposta deve priorizar a proteção da baliza e das ameaças imediatas.

---

# PARTE X — PERDAS COM LATERAIS PROJETADOS

## 36. Perda com lateral direito projetado

### 36.1. Situação

LD está avançado quando a equipa perde.

### 36.2. Problema

Pode existir espaço no corredor exterior direito defensivo.

### 36.3. Respostas possíveis

- MDC-D protege corredor interior direito.
- DCD ajusta cobertura.
- DCE controla zona central e profundidade.
- LE estreita posição, se necessário.
- LD procura recuperar.
- ED pode condicionar primeiro passe.

### 36.4. Riscos

- MDC-D deslocar-se demasiado para fora.
- Espaço central.
- DCD sair e abrir intervalo.
- Mudança de corredor.
- Inferioridade na última linha.

### 36.5. Regra

O pivô não deve assumir automaticamente a posição de lateral.

Pode ser mais importante proteger o espaço interior e permitir que o central controle o exterior de forma temporária.

---

## 37. Perda com lateral esquerdo projetado

### 37.1. Situação

LE está avançado.

### 37.2. Respostas possíveis

- MDC-E protege corredor interior esquerdo.
- DCE ajusta posição.
- DCD controla profundidade.
- LD estreita, se necessário.
- LE recupera.
- EE condiciona saída adversária.

### 37.3. Riscos

- Espaço entre DCE e DCD.
- Pivô abandonar centro.
- Adversário explorar corredor exterior.
- Mudança de corredor.

---

## 38. Perda com ambos os laterais projetados

### 38.1. Situação

LE e LD encontram-se avançados.

### 38.2. Problema

Os dois centrais podem ficar responsáveis por grande largura e profundidade.

### 38.3. Respostas possíveis

- Um ou dois pivôs recuperam posições de cobertura.
- Jogadores próximos tentam condicionar o primeiro passe.
- Centrais controlam profundidade.
- Laterais recuperam.
- Equipa temporiza se não houver condições de recuperação imediata.

### 38.4. Riscos

- Dois centrais perante dois ou três atacantes.
- Corredores exteriores livres.
- Passe de rutura.
- Pivôs ultrapassados.
- Falta de proteção central.

### 38.5. Regra

A projeção simultânea dos laterais não implica necessariamente erro, mas exige mecanismos preventivos adequados.

---

# PARTE XI — PERDAS COM PIVÔ PROJETADO

## 39. Um pivô à frente da bola

### 39.1. Situação

MDC-E avançou para apoiar ataque.

A equipa perde.

### 39.2. Respostas possíveis

- MDC-D protege centro.
- MDC-E procura condicionar ou recuperar.
- MO ajusta reação.
- Laterais e centrais controlam profundidade.

### 39.3. Riscos

- MDC-D isolado.
- Passe central.
- MO adversário livre.
- Centrais expostos.

---

## 40. Ambos os pivôs ultrapassados

### 40.1. Situação

A perda ocorre com ambos os pivôs à frente da bola ou fora da zona de proteção.

### 40.2. Problema

Pode existir acesso direto à linha defensiva.

### 40.3. Resposta possível

- Jogador próximo temporiza.
- Pivôs recuperam pelo corredor mais útil.
- Laterais ajustam posição.
- Centrais protegem profundidade.
- Equipa procura reorganizar.

### 40.4. Riscos

- Ataque frontal.
- Passe de rutura.
- Superioridade adversária.
- Falta de cobertura.

### 40.5. Regra

Não recomendar pressão agressiva dos centrais sem avaliar a profundidade e a cobertura.

---

# PARTE XII — TRANSIÇÕES PERANTE DIFERENTES SISTEMAS

## 41. Transições contra 4-4-2

### 41.1. Transição ofensiva

Possíveis oportunidades:

- MO encontrar espaço entre linhas.
- Explorar laterais projetados.
- Utilizar PL em apoio.
- Criar progressão através dos pivôs.

### 41.2. Transição defensiva

Riscos:

- Dois avançados adversários atacarem centrais.
- Passe direto.
- Segunda bola.
- Corredores exteriores expostos.

### 41.3. Resposta

Controlar a relação entre os dois avançados e os dois centrais, mantendo cobertura do duplo pivô ou de outros jogadores disponíveis.

---

## 42. Transições contra 4-3-3

### 42.1. Transição ofensiva

Possíveis oportunidades:

- Explorar espaço nas costas dos laterais.
- Encontrar MO entre linhas.
- Atacar corredores interiores.
- Utilizar extremos em profundidade.

### 42.2. Transição defensiva

Riscos:

- Três avançados atacarem quatro defesas.
- Extremos isolarem laterais.
- Interiores adversários chegarem de trás.
- Pivôs próprios ficarem em inferioridade central.

### 42.3. Resposta

Proteger centro, controlar profundidade e reorganizar coberturas exteriores.

---

## 43. Transições contra 4-2-3-1

### 43.1. Transição ofensiva

Possíveis oportunidades:

- Explorar espaço entre pivôs.
- Atacar laterais projetados.
- Utilizar MO para ligação.
- Criar situações de um contra um.

### 43.2. Transição defensiva

Riscos:

- MO adversário receber entre linhas.
- Extremos atacarem profundidade.
- PL fixar centrais.
- Pivôs adversários conduzirem.

### 43.3. Resposta

Controlar MO adversário, proteger corredor central e coordenar coberturas laterais.

---

## 44. Transições contra 3-5-2

### 44.1. Transição ofensiva

Possíveis oportunidades:

- Explorar espaço nas costas dos alas.
- Encontrar extremos em largura.
- Utilizar MO entre linhas.
- Atacar intervalos entre central exterior e ala.

### 44.2. Transição defensiva

Riscos:

- Dois avançados fixarem centrais.
- Alas atacarem corredores.
- Três médios criarem superioridade central.
- Passe direto para avançados.

### 44.3. Resposta

Proteger centro e profundidade, coordenando laterais, pivôs e centrais.

### 44.4. Regra

Não assumir que os espaços nas costas dos alas estão sempre disponíveis.

Dependem da posição real dos alas e das coberturas dos centrais exteriores.

---

## 45. Transições contra 3-4-3

### 45.1. Transição ofensiva

Possíveis oportunidades:

- Explorar espaço nas costas dos alas.
- Atacar corredores interiores.
- Utilizar MO entre os dois médios.
- Criar ligações com extremos.

### 45.2. Transição defensiva

Riscos:

- Três avançados atacarem última linha.
- Alas projetados.
- Extremos adversários isolarem laterais.
- Pivôs próprios ultrapassados.

### 45.3. Resposta

Controlar profundidade, proteger centro e ajustar responsabilidades exteriores.

---

# PARTE XIII — CASOS PRÁTICOS COMPLETOS

## 46. Caso A — Recuperação alta com MO disponível

**Situação:**

A equipa recupera perto da área adversária.

**Objetivo:** criar oportunidade imediata.

**Solução possível:**

1. ED recupera.
2. MO aproxima-se pelo corredor interior.
3. PL ocupa referência central.
4. EE identifica espaço do lado contrário.
5. ED procura MO se a linha estiver aberta.
6. MO avalia remate ou passe.
7. A equipa procura finalizar.

**Alternativa:**

Se MO estiver marcado, ED pode conduzir, procurar PL ou conservar a bola.

**Riscos:**

- Passe interior intercetado.
- Remate precipitado.
- Falta de proteção após nova perda.

---

## 47. Caso B — Recuperação média e contra-ataque central

**Situação:**

MDC-E recupera no meio-campo.

**Objetivo:** explorar desorganização adversária.

**Solução possível:**

1. MDC-E recupera.
2. MO oferece linha.
3. PL ameaça profundidade.
4. ED procura intervalo.
5. MDC-E passa a MO se possível.
6. MO avalia movimento de ED.
7. A equipa procura finalização.

**Alternativa:**

Se MO estiver marcado, procurar extremo ou apoio do outro pivô.

**Riscos:**

- Passe vertical intercetado.
- MO pressionado.
- Falta de cobertura.
- Movimento sem sincronização.

---

## 48. Caso C — Recuperação baixa e PL em apoio

**Situação:**

DCD recupera perto da área.

**Objetivo:** sair da pressão.

**Solução possível:**

1. DCD recupera.
2. MDC-D oferece apoio.
3. PL baixa.
4. MO aproxima-se.
5. ED ameaça profundidade.
6. DCD procura a opção disponível.
7. A equipa progride ou conserva.

**Alternativa:**

Se não existir ligação segura, procurar circulação ou outra saída funcional.

**Riscos:**

- Passe curto intercetado.
- PL isolado.
- Segunda bola perdida.
- Nova perda perigosa.

---

## 49. Caso D — Perda com LD projetado

**Situação:**

LD encontra-se avançado.

A equipa perde no corredor direito.

**Objetivo:** impedir contra-ataque.

**Solução possível:**

1. ED condiciona portador, se estiver em condições.
2. MDC-D protege corredor interior.
3. DCD ajusta cobertura.
4. DCE controla profundidade.
5. LE estreita, se necessário.
6. LD recupera.
7. A equipa reorganiza bloco.

**Alternativa:**

Se a pressão imediata não for possível, temporizar e proteger centro.

**Riscos:**

- Espaço nas costas de LD.
- DCD sair sem cobertura.
- Pivô abandonar centro.
- Passe de rutura.

---

## 50. Caso E — Perda central com ambos os pivôs avançados

**Situação:**

A equipa perde no corredor central.

Os pivôs estão à frente da bola.

**Objetivo:** proteger a última linha.

**Solução possível:**

1. Jogador próximo condiciona.
2. MO tenta fechar passe central, se estiver em posição.
3. Pivôs recuperam.
4. Centrais controlam profundidade.
5. Laterais ajustam posições.
6. A equipa temporiza e reorganiza.

**Alternativa:**

Se existir possibilidade real de recuperação imediata com cobertura, tentar contra-pressão coordenada.

**Riscos:**

- Passe frontal.
- Superioridade adversária.
- Central sair sem cobertura.
- Finalização.

---

## 51. Caso F — Contra-pressão ultrapassada

**Situação:**

A equipa perde em zona alta e tenta recuperar, mas o adversário ultrapassa a primeira pressão.

**Objetivo:** impedir progressão perigosa.

**Solução possível:**

1. Jogadores avançados recuperam.
2. Pivô próximo condiciona receção.
3. Outro pivô protege centro.
4. Laterais controlam profundidade.
5. Centrais ajustam referências.
6. A equipa reorganiza bloco médio ou baixo.

**Alternativa:**

Se o adversário abrandar e ficar pressionável, a equipa pode voltar a pressionar coletivamente.

**Riscos:**

- Passe de rutura.
- Pivô ultrapassado.
- Linha defensiva isolada.
- Falta de compactação.

---

## 52. Caso G — Contra-ataque contra 3-5-2

**Situação:**

O adversário utiliza alas projetados.

A equipa recupera no meio-campo.

**Objetivo:** explorar espaço exterior.

**Solução possível:**

1. MDC-D recupera.
2. ED identifica posição do ala adversário.
3. MO oferece apoio central.
4. PL fixa centrais.
5. MDC-D procura ED se existir espaço.
6. ED ataca corredor disponível.
7. MO e PL aproximam-se para continuidade.

**Alternativa:**

Se o central exterior adversário controlar o corredor, ED pode procurar MO ou conservar a bola.

**Riscos:**

- Ala recuperar posição.
- Central exterior controlar ED.
- PL isolado.
- Falta de cobertura.

---

## 53. Caso H — Recuperação e conservação

**Situação:**

A equipa recupera, mas o adversário já está equilibrado.

**Objetivo:** manter posse.

**Solução possível:**

1. MDC-E recupera.
2. MO está marcado.
3. PL está isolado.
4. Extremos não têm profundidade disponível.
5. MDC-E procura DCE ou MDC-D.
6. A equipa reorganiza largura.
7. Prepara ataque organizado.

**Alternativa:**

Se surgir espaço durante a circulação, procurar progressão.

**Riscos:**

- Passe de segurança intercetado.
- Circulação sem apoio.
- Pressão adversária.
- Falta de organização.

---

## 54. Caso I — Perda no corredor esquerdo com LE e MDC-E projetados

**Situação:**

LE e MDC-E encontram-se à frente da bola.

A equipa perde no corredor esquerdo.

**Objetivo:** proteger centro e profundidade.

**Solução possível:**

1. EE condiciona portador, se estiver próximo.
2. MO procura fechar passe interior.
3. MDC-D protege corredor central.
4. DCE ajusta cobertura exterior.
5. DCD controla profundidade.
6. LD estreita posição.
7. LE e MDC-E recuperam.

**Alternativa:**

Se o adversário conseguir ultrapassar a primeira pressão, temporizar e reorganizar.

**Riscos:**

- DCE sair e abrir espaço.
- MDC-D ficar isolado.
- Passe de rutura.
- Mudança de corredor.

---

## 55. Caso J — Recuperação com PL isolado e extremos distantes

**Situação:**

A equipa recupera em zona baixa.

PL está distante dos restantes jogadores.

**Objetivo:** decidir entre progressão e conservação.

**Solução possível:**

1. DCE recupera.
2. Avalia pressão.
3. PL oferece apoio ou profundidade.
4. MO procura aproximar-se.
5. Pivôs oferecem linhas.
6. Se PL estiver isolado, a equipa evita passe forçado.
7. Procura saída funcional.

**Alternativa:**

Se existir espaço claro nas costas e passe executável, pode procurar PL diretamente.

**Riscos:**

- PL perder duelo.
- Segunda bola adversária.
- Equipa demasiado distante.
- Nova perda.

---

# PARTE XIV — ERROS FREQUENTES

## 56. Erros na transição ofensiva

### 56.1. Passe vertical obrigatório

A equipa força progressão sem vantagem.

### 56.2. MO recebe sempre

A equipa ignora marcação e linhas fechadas.

### 56.3. PL ataca sempre profundidade

A equipa perde apoio frontal.

### 56.4. Extremos atacam o mesmo espaço

A complementaridade diminui.

### 56.5. Ambos os pivôs avançam

A proteção preventiva pode desaparecer.

### 56.6. Laterais projetam-se sem cobertura

A equipa fica exposta após nova perda.

### 56.7. Condução excessiva

A vantagem temporal desaparece.

### 56.8. Contra-ataque sem continuidade

A equipa perde a bola ou cria oportunidade de baixa qualidade.

---

## 57. Erros na transição defensiva

### 57.1. Contra-pressão automática

A equipa pressiona sem condições.

### 57.2. Todos os jogadores procuram a bola

O centro e a profundidade ficam desprotegidos.

### 57.3. Ambos os pivôs pressionam

A cobertura central desaparece.

### 57.4. Central sai sem cobertura

O adversário explora profundidade.

### 57.5. Lateral recupera mecanicamente

Pode ignorar ameaça mais próxima.

### 57.6. Falta de temporização

O adversário progride rapidamente.

### 57.7. Persistência numa pressão ultrapassada

A equipa aumenta a exposição.

### 57.8. Falta de controlo do lado contrário

O adversário explora mudança de corredor.

---

# PARTE XV — CRITÉRIOS PARA A IA

## 58. Perguntas obrigatórias na transição ofensiva

1. Onde ocorreu a recuperação?
2. Quem recuperou?
3. O portador está pressionado?
4. Está orientado para a frente?
5. Existe espaço para conduzir?
6. Existe passe vertical?
7. O MO está disponível?
8. O PL oferece apoio ou profundidade?
9. Os extremos estão abertos ou interiores?
10. Existem movimentos complementares?
11. O adversário está desorganizado?
12. Existe superioridade temporária?
13. Existem coberturas?
14. A equipa pode finalizar?
15. É preferível conservar?
16. Qual é o risco da ação?
17. Qual é a alternativa?

---

## 59. Perguntas obrigatórias na transição defensiva

1. Onde ocorreu a perda?
2. Quem está próximo da bola?
3. O adversário está orientado?
4. Existe possibilidade de contra-pressão?
5. Existem coberturas?
6. Como estão posicionados os pivôs?
7. Os laterais estão projetados?
8. Os centrais estão protegidos?
9. Existe ameaça de profundidade?
10. O corredor central está protegido?
11. Existem jogadores adversários livres?
12. É necessário temporizar?
13. A pressão foi ultrapassada?
14. A equipa consegue reorganizar-se?
15. Qual é a estrutura defensiva mais adequada?
16. Qual é o risco imediato?
17. Qual é a alternativa?

---

## 60. Classificação das soluções

**Solução fundamentada:** respeita posições, espaços, linhas de passe, coberturas, ameaças e continuidade.

**Solução condicionada:** depende de reação adversária ou condição não confirmada.

**Solução contraditória:** exige movimentos ou passes incompatíveis com a situação.

**Informação insuficiente:** faltam dados para avaliar a decisão.

---

## 61. Regras de interpretação para a IA

- Não assumir que toda a recuperação deve originar contra-ataque.
- Não assumir que toda a perda deve originar contra-pressão.
- Não recomendar passe vertical sem linha disponível.
- Não assumir que MO está sempre livre.
- Não assumir que PL deve atacar sempre profundidade.
- Não assumir que extremos devem realizar movimentos iguais.
- Não assumir que dois pivôs garantem proteção automática.
- Não recomendar projeção simultânea dos pivôs sem avaliar cobertura.
- Não recomendar subida dos laterais sem avaliar risco.
- Não assumir que os centrais conseguem controlar qualquer inferioridade.
- Não recomendar pressão agressiva sem cobertura.
- Não recomendar que um central abandone posição sem compensação.
- Não ignorar a orientação corporal do adversário.
- Não ignorar a profundidade.
- Não ignorar a segunda bola.
- Não ignorar a possibilidade de conservar a posse.
- Não confundir transição ofensiva com qualquer ataque rápido.
- Não confundir contra-pressão com pressão desorganizada.
- Não atribuir características individuais sem informação documentada.
- Explicar sempre condições, movimentos, reações adversárias, riscos, continuidade e alternativas.
- Distinguir conhecimento universal de instruções específicas da equipa.
- Quando faltarem dados, apresentar hipóteses condicionais.

---

## 62. Relação com outros documentos

### Fundamentos

- `conhecimento/fundamentos/fases_jogo.md`
- `conhecimento/fundamentos/principios_ofensivos.md`
- `conhecimento/fundamentos/principios_defensivos.md`
- `conhecimento/fundamentos/superioridades.md`
- `conhecimento/fundamentos/modelos_jogo.md`

### Sistema 4-2-3-1

- `conhecimento/sistemas/4231/organizacao.md`
- `conhecimento/sistemas/4231/saida_bola.md`
- `conhecimento/sistemas/4231/ataque.md`
- `conhecimento/sistemas/4231/defesa.md`

### Outros sistemas

- `conhecimento/sistemas/352/organizacao.md`
- `conhecimento/sistemas/433/organizacao.md`
- `conhecimento/sistemas/343/organizacao.md`

Os documentos ainda não preparados devem ser considerados referências previstas.

---

## 63. Princípio final

As transições no 4-2-3-1 dependem da capacidade coletiva para interpretar a mudança de posse.

Na transição ofensiva, o número 10 pode ligar a recuperação ao ataque, o ponta de lança pode oferecer apoio ou profundidade, os extremos podem explorar espaços e o duplo pivô pode garantir progressão e equilíbrio.

Na transição defensiva, a equipa deve avaliar a possibilidade de contra-pressão, a proteção do corredor central, as coberturas disponíveis e a necessidade de temporização.

Nenhum destes comportamentos deve ser aplicado automaticamente.

O assistente de IA deve interpretar cada transição segundo a posição real dos jogadores, a organização adversária, os espaços disponíveis, a pressão sobre a bola, as ameaças e as alternativas existentes.