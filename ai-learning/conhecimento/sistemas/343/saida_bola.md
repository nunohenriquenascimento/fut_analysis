# Sistema Tático 3-4-3 — Saída de Bola e Primeira Fase de Construção

## 1. Objetivo do documento

Este documento descreve os princípios universais da saída de bola no sistema 3-4-3.

A saída de bola corresponde ao processo coletivo através do qual uma equipa procura iniciar e desenvolver a posse, normalmente a partir do guarda-redes, dos defesas ou de recuperações em zonas recuadas.

O objetivo não é apenas ultrapassar a primeira linha de pressão.

Uma saída eficaz deve permitir:

- Conservar a posse quando necessário.
- Atrair e ultrapassar pressão.
- Criar linhas de passe.
- Identificar o jogador livre.
- Progredir com controlo.
- Explorar espaço.
- Ligar a primeira fase à progressão.
- Preparar ataques.
- Proteger a equipa perante uma eventual perda.

O assistente de inteligência artificial deve compreender que não existe uma única forma correta de construir no 3-4-3.

A solução depende da organização própria, do comportamento adversário, das características dos jogadores e das condições concretas.

---

# PARTE I — ESTRUTURA E PRINCÍPIOS

## 2. Estrutura nominal do 3-4-3

```text
                         PL

              AE                    AD

       ALA-E       MC-E      MC-D       ALA-D

                DCE    DCC    DCD

                         GR
```

### Legenda

- GR — Guarda-redes.
- DCE — Defesa central esquerdo.
- DCC — Defesa central do meio.
- DCD — Defesa central direito.
- ALA-E — Ala esquerdo.
- ALA-D — Ala direito.
- MC-E — Médio-centro esquerdo.
- MC-D — Médio-centro direito.
- AE — Avançado exterior esquerdo.
- AD — Avançado exterior direito.
- PL — Ponta de lança.

A posição nominal não representa necessariamente a localização real dos jogadores durante a construção.

Por exemplo:

- Um central exterior pode conduzir até ao meio-campo.
- Um ala pode aproximar-se da primeira linha.
- Um médio pode baixar para apoiar.
- Um avançado exterior pode ocupar o corredor interior.
- O PL pode oferecer apoio frontal.
- O guarda-redes pode participar na circulação.

---

## 3. Objetivos da primeira fase de construção

A primeira fase procura criar condições para ultrapassar a pressão inicial.

Os principais objetivos são:

1. Garantir uma primeira opção segura.
2. Identificar o comportamento da pressão.
3. Criar superioridade funcional.
4. Atrair adversários quando existir vantagem em fazê-lo.
5. Abrir linhas de passe.
6. Utilizar o jogador livre.
7. Evitar perdas em zonas críticas.
8. Garantir continuidade após ultrapassar a pressão.
9. Preparar proteção preventiva.

### Regra fundamental

Ultrapassar a primeira linha não é suficiente se o jogador que recebe ficar imediatamente isolado ou pressionado sem continuidade.

---

## 4. Superioridade numérica e superioridade funcional

O 3-4-3 pode apresentar três centrais perante dois avançados adversários.

Numericamente:

**3 contra 2.**

Contudo, a superioridade numérica não garante progressão.

### Exemplo

O adversário pressiona com dois avançados.

- Um condiciona DCE.
- Outro condiciona DCD.
- DCC recebe.
- Os médios adversários bloqueiam MC-E e MC-D.
- Os extremos adversários controlam os alas.

DCC pode ter tempo com bola, mas não possuir uma linha de progressão favorável.

### Consequência

A equipa pode necessitar de:

- Condução.
- Movimento de um médio.
- Aproximação de um ala.
- Desmarcação de um avançado.
- Mudança de corredor.
- Participação do guarda-redes.
- Passe direto.

### Regra para a IA

Não recomendar automaticamente passe para o central livre sem identificar o que esse central poderá fazer a seguir.

---

## 5. Relação entre atração e progressão

Atrair pressão pode criar espaço noutra zona.

Mas a atração só é vantajosa quando a equipa possui uma solução para explorar a reação adversária.

### Exemplo

1. DCE recebe.
2. Um adversário aproxima-se.
3. MC-E ajusta a posição.
4. ALA-E identifica o espaço exterior.
5. AE posiciona-se entre linhas.
6. DCE escolhe a ligação disponível.

### Possíveis resultados

Se o adversário abandonar o corredor exterior, ALA-E pode receber.

Se bloquear ALA-E, pode surgir uma ligação interior.

Se todas as linhas estiverem fechadas, DCE pode circular para DCC ou GR.

### Regra

Atrair pressão sem uma saída funcional pode transformar uma situação controlada numa perda perigosa.

---

## 6. Linhas de passe

Uma linha de passe deve ser avaliada segundo:

- Posição do portador.
- Posição do recetor.
- Posição dos adversários.
- Orientação corporal.
- Distância.
- Velocidade da pressão.
- Trajetória da bola.
- Qualidade da receção.
- Possibilidade de continuidade.

### 6.1. Linha geometricamente aberta

Existe um trajeto sem bloqueio evidente.

### 6.2. Linha funcionalmente disponível

Além de existir trajeto, o recetor consegue receber e realizar uma ação útil.

### 6.3. Linha aparentemente aberta

O trajeto parece livre, mas um adversário pode intercetar ou pressionar imediatamente.

### Regra

A IA deve privilegiar linhas funcionalmente disponíveis.

---

# PARTE II — RESPONSABILIDADES DOS JOGADORES

## 7. Guarda-redes na construção

O guarda-redes pode participar como apoio adicional.

### Funções possíveis

- Iniciar circulação.
- Atrair pressão.
- Alterar corredor.
- Encontrar central livre.
- Executar passe médio ou longo.
- Oferecer apoio recuado.
- Ajudar a criar superioridade numérica.

### Exemplo

1. DCC recebe.
2. Um adversário pressiona.
3. DCC devolve ao GR.
4. GR identifica o posicionamento adversário.
5. Se DCD estiver livre, procura a ligação.
6. DCD avalia progressão.

### Riscos

- Passe atrasado sob pressão.
- GR receber sem tempo.
- Adversário bloquear os centrais.
- Erro técnico próximo da baliza.

### Regra

A participação do GR pode criar superioridade numérica, mas não garante tempo, espaço ou uma saída segura.

---

## 8. Defesa central do meio

O DCC pode ser uma referência central da primeira fase.

### Funções possíveis

- Receber do GR.
- Distribuir para os centrais exteriores.
- Identificar os médios.
- Conduzir.
- Mudar corredor.
- Proteger equilíbrio.
- Executar passe vertical.

### Situação A — DCC livre

Pode:

- Conduzir se existir espaço.
- Procurar MC-E ou MC-D.
- Encontrar avançado interior.
- Circular para outro central.

### Situação B — DCC pressionado

Pode:

- Apoiar-se no GR.
- Circular lateralmente.
- Procurar passe vertical se disponível.
- Utilizar uma solução direta.

### Riscos

- Conduzir até ficar cercado.
- Executar passe central intercetável.
- Sair da linha sem cobertura.
- Perder bola em zona frontal.

### Regra

DCC não deve ser considerado obrigatoriamente um líbero.

A sua função depende do modelo e do momento.

---

## 9. Defesas centrais exteriores

DCE e DCD podem desempenhar funções de construção importantes.

### Funções possíveis

- Abrir largura na primeira linha.
- Receber em posição exterior.
- Conduzir.
- Atrair pressão.
- Procurar médios.
- Encontrar alas.
- Ligar com avançados interiores.
- Mudar corredor.

### Exemplo

1. DCC passa a DCE.
2. DCE recebe orientado.
3. O avançado adversário aproxima-se.
4. MC-E ajusta altura.
5. ALA-E oferece largura.
6. AE procura espaço interior.
7. DCE avalia as opções.

### Riscos

- Pressão junto à linha lateral.
- Passe interior intercetado.
- Condução sem cobertura.
- Falta de apoio.
- Espaço nas costas após perda.

---

## 10. Condução do central exterior

A condução pode ser utilizada para atrair um adversário e alterar as relações numéricas.

### Condições favoráveis

- Espaço à frente.
- Portador orientado.
- Cobertura existente.
- Médio próximo disponível.
- Possibilidade de passe após atração.

### Exemplo

1. DCE recebe sem pressão.
2. Conduz.
3. MC adversário aproxima-se.
4. MC-E ajusta para oferecer apoio.
5. AE identifica espaço deixado pelo adversário.
6. DCE decide entre passe e continuidade.

### Se o adversário não pressionar

DCE pode continuar a progredir, desde que mantenha controlo e equilíbrio.

### Se o adversário pressionar

DCE procura explorar a referência libertada.

### Se não surgir vantagem

DCE pode interromper condução e circular.

### Regra

Conduzir não significa obrigatoriamente ultrapassar um adversário em drible.

Pode servir para provocar uma decisão defensiva.

---

## 11. Duplo pivô na construção

MC-E e MC-D oferecem referências centrais.

### Funções possíveis

- Receber entre linhas de pressão.
- Apoiar centrais.
- Controlar ritmo.
- Ligar corredores.
- Progredir.
- Atrair marcação.
- Criar terceiro homem.
- Garantir equilíbrio.

### Problema possível

Os dois médios podem estar bloqueados pelas referências adversárias.

### Soluções possíveis

- Alterar alturas.
- Alterar distâncias.
- Aproximar-se lateralmente.
- Utilizar apoio de avançado interior.
- Permitir condução de central.
- Criar terceiro homem.

### Regra

Dois médios no centro não significam necessariamente duas linhas de passe disponíveis.

---

## 12. Duplo pivô horizontal

### Organização

MC-E e MC-D ocupam alturas semelhantes.

### Vantagens

- Apoio à circulação.
- Cobertura central.
- Mudança de corredor.
- Relação com centrais exteriores.

### Riscos

- Ambos na sombra de pressão.
- Ambos controlados pela mesma linha.
- Falta de ligação à fase seguinte.
- Distância excessiva aos avançados.

### Exemplo

Se os dois médios estiverem bloqueados:

1. MC-E altera ligeiramente a altura.
2. MC-D mantém referência.
3. DCC avalia a reação adversária.
4. Pode surgir linha para um dos médios.
5. Se não surgir, procurar outra via.

---

## 13. Duplo pivô escalonado

### Organização

Um médio posiciona-se mais baixo e outro mais alto.

### Objetivos

- Criar diferentes linhas.
- Facilitar receção.
- Atrair adversários.
- Melhorar continuidade.
- Preparar progressão.

### Exemplo

1. MC-E baixa.
2. MC-D permanece mais avançado.
3. DCE encontra MC-E.
4. MC-E recebe orientado.
5. Procura MC-D ou AE.

### Riscos

- MC-E pressionado.
- MC-D marcado.
- Distância excessiva.
- Falta de cobertura após perda.

### Regra

O escalonamento deve responder à pressão e não ser aplicado mecanicamente.

---

## 14. Um médio baixa entre os centrais

### Situação

MC-E baixa para integrar a primeira linha.

### Possível transformação

A equipa pode formar temporariamente quatro jogadores na construção, ou reorganizar os três centrais de outra forma.

### Vantagens possíveis

- Criar apoio adicional.
- Libertar central exterior.
- Atrair médio adversário.
- Alterar referências de marcação.

### Riscos

- Retirar um jogador do meio-campo.
- Deixar MC-D isolado.
- Aumentar distância à frente.
- Facilitar pressão sobre o médio restante.
- Criar excesso de jogadores na primeira linha.

### Exemplo

1. MC-E baixa.
2. DCE abre.
3. DCC ajusta.
4. MC-D mantém referência central.
5. AE aproxima-se por dentro.
6. A equipa procura continuidade.

### Regra

Baixar um pivô não deve ser recomendado automaticamente.

É necessário demonstrar que a vantagem na primeira linha compensa a possível perda de presença no meio-campo.

---

## 15. Um médio baixa ao lado de um central exterior

### Situação

MC-E aproxima-se do lado esquerdo da construção.

### Objetivos

- Criar apoio lateral.
- Facilitar circulação.
- Atrair marcação.
- Permitir progressão do central exterior.
- Encontrar ala.

### Exemplo

1. DCE recebe.
2. MC-E aproxima-se numa altura diferente.
3. O adversário decide acompanhar ou manter posição.
4. Se acompanhar, pode abrir espaço interior.
5. Se não acompanhar, MC-E pode receber.
6. DCE escolhe a solução disponível.

### Riscos

- MC-E ficar junto à linha lateral.
- Centro desprotegido.
- Falta de continuidade.
- Pressão lateral.

---

## 16. Papel dos alas na saída de bola

Os alas podem participar em diferentes alturas.

### Ala baixo

Oferece apoio próximo ao central exterior.

### Ala intermédio

Permite ligação entre construção e progressão.

### Ala alto

Fixa adversários e oferece profundidade exterior.

### Regra

O ala não precisa de baixar sempre para ajudar a saída.

Por vezes, permanecer alto cria espaço para o central ou médio receber.

---

## 17. Ala baixo na construção

### Objetivos

- Criar apoio.
- Facilitar circulação.
- Oferecer saída exterior.
- Ajudar perante pressão alta.

### Exemplo

1. DCE recebe.
2. ALA-E aproxima-se.
3. AE ocupa zona mais avançada.
4. MC-E oferece apoio interior.
5. DCE avalia passe para ALA-E.

### Riscos

- ALA-E receber de costas.
- Adversário pressionar junto à linha.
- Falta de profundidade.
- AE ficar isolado.

### Alternativa

Utilizar MC-E ou circulação para DCC.

---

## 18. Ala alto na construção

### Objetivos

- Fixar lateral ou ala adversário.
- Criar espaço intermédio.
- Ameaçar profundidade.
- Impedir subida confortável da pressão.

### Exemplo

1. ALA-E mantém altura.
2. AE ocupa corredor interior.
3. DCE recebe.
4. O adversário tem de controlar ALA-E.
5. MC-E procura espaço.
6. DCE avalia progressão.

### Riscos

- Distância excessiva.
- Passe longo sem apoio.
- Espaço nas costas do ala.
- Dificuldade de recuperação.

---

## 19. Avançados exteriores na saída de bola

AE e AD podem desempenhar funções fundamentais mesmo sem tocar na bola.

### Funções possíveis

- Fixar laterais ou centrais.
- Ocupar corredores interiores.
- Oferecer apoio entre linhas.
- Atacar profundidade.
- Aproximar-se da construção.
- Criar espaço através do movimento.

### Exemplo

AE aproxima-se do corredor interior.

Se o médio adversário acompanhar, pode libertar espaço para MC-E.

Se o central adversário sair, pode surgir profundidade.

Se ninguém acompanhar, AE pode ficar disponível entre linhas.

### Regra

O movimento do avançado exterior deve ser avaliado em relação à reação adversária.

---

## 20. Ponta de lança na saída de bola

O PL pode oferecer:

- Profundidade.
- Apoio frontal.
- Fixação dos centrais.
- Referência para passe direto.
- Ligação com avançados exteriores.
- Apoio para terceiro homem.

### PL em apoio

Pode baixar para receber.

### PL em profundidade

Pode impedir que a defesa adversária suba.

### PL como referência direta

Pode disputar bola e procurar ligação ou segunda bola.

### Riscos

- PL isolado.
- Passe sem apoio.
- Perda de segunda bola.
- Abandono da profundidade.

### Regra

O PL não deve baixar automaticamente quando os médios estão bloqueados.

Pode ser mais útil manter a profundidade.

---

# PARTE III — ESTRUTURAS DE CONSTRUÇÃO

## 21. Construção em 3+2

### Organização

Três centrais e dois médios de apoio.

```text
                 MC-E        MC-D

              DCE     DCC     DCD

                         GR
```

### Vantagens possíveis

- Três referências iniciais.
- Dois apoios centrais.
- Possibilidade de circulação.
- Proteção preventiva.

### Riscos

- Pivôs bloqueados.
- Alas distantes.
- Falta de ligação entre linhas.
- Pressão individualizada.

### Regra

A estrutura 3+2 só é funcional quando os jogadores conseguem criar ligações úteis.

---

## 22. Construção em 3+1

### Organização

Três centrais e um médio próximo da primeira fase.

O outro médio ocupa posição mais avançada.

### Objetivos

- Criar escalonamento.
- Aproximar jogadores entre linhas.
- Atrair marcação.
- Facilitar progressão.

### Riscos

- Médio baixo isolado.
- Falta de apoio lateral.
- Adversário bloquear passe vertical.
- Cobertura insuficiente.

---

## 23. Construção em 4+1

### Organização

Um médio integra a primeira linha.

O outro permanece à frente.

### Possíveis vantagens

- Alterar relações com a pressão.
- Criar apoio adicional.
- Libertar um central exterior.
- Facilitar circulação.

### Riscos

- Excesso de jogadores atrás da pressão.
- Inferioridade na linha seguinte.
- Médio restante marcado.
- Distâncias excessivas.

### Regra

Quatro jogadores na primeira linha não significam necessariamente uma construção melhor.

---

## 24. Construção com ala baixo e ala alto

### Organização

Um ala aproxima-se da construção.

O outro mantém altura.

### Objetivos

- Criar assimetria.
- Facilitar saída num corredor.
- Manter profundidade no outro.
- Adaptar-se à pressão.

### Exemplo

1. ALA-E baixa.
2. ALA-D permanece alto.
3. DCE aproxima-se de ALA-E.
4. MC-E oferece apoio interior.
5. AD e PL mantêm referências avançadas.
6. A equipa procura progressão.

### Riscos

- Desequilíbrio.
- Falta de cobertura.
- Lado contrário distante.
- Mudança de corredor lenta.

---

## 25. Construção com central exterior projetado

### Organização

DCE ou DCD progride para uma altura superior.

### Objetivos

- Atrair médio adversário.
- Criar superioridade no meio-campo.
- Libertar colega.
- Progredir por condução.

### Condições

- Espaço.
- Cobertura.
- Apoio.
- Possibilidade de continuidade.

### Riscos

- Perda durante condução.
- Espaço nas costas.
- Central do meio exposto.
- Pivôs ultrapassados.

---

# PARTE IV — SAÍDA PERANTE DIFERENTES PRESSÕES

## 26. Identificação da pressão adversária

Antes de recomendar uma solução, a IA deve identificar:

1. Quantos jogadores pressionam efetivamente?
2. Quem pressiona o portador?
3. Quem bloqueia os pivôs?
4. Quem controla os alas?
5. Quem controla os avançados interiores?
6. O adversário pressiona individualmente ou por zonas?
7. Existem sombras de pressão?
8. Existe uma armadilha lateral?
9. O guarda-redes está disponível?
10. Existe espaço nas costas da pressão?

### Regra

A formação nominal adversária não determina automaticamente o número de jogadores envolvidos na pressão.

---

## 27. Pressão com um avançado

### Situação

O adversário utiliza uma primeira referência de pressão.

Exemplo possível: 4-1-4-1.

### Relação inicial

Três centrais perante um avançado.

### Possível vantagem

Dois centrais podem ficar sem pressão direta.

### Limitações

O avançado pode orientar circulação.

Os médios adversários podem bloquear pivôs.

Os extremos podem pressionar centrais exteriores.

### Solução possível

1. DCC recebe.
2. PL adversário condiciona uma direção.
3. DCC identifica central disponível.
4. O central exterior recebe.
5. Avalia espaço para conduzir.
6. Procura médio ou ala.
7. A equipa progride se existir continuidade.

### Se o extremo adversário pressionar

O central exterior pode procurar o espaço deixado por esse extremo, desde que exista linha de passe.

### Se o médio adversário bloquear o pivô

Pode ser necessário utilizar ala, avançado interior ou circulação.

### Riscos

- Pressão lateral.
- Pivôs bloqueados.
- Passe vertical intercetado.
- Central conduzir sem cobertura.

---

## 28. Pressão com dois avançados

### Situação

O adversário pressiona com duas referências.

Exemplos possíveis:

- 4-4-2.
- 4-2-3-1 com MO a juntar-se ao PL.
- 3-5-2.

### Relação inicial

Três centrais perante dois avançados.

### Possível vantagem

Um central pode ficar disponível.

### Limitações

Os dois avançados podem utilizar sombras de pressão.

Um médio pode subir.

O adversário pode orientar a bola para um corredor.

### Solução possível

1. DCC recebe.
2. Os avançados condicionam DCE e DCD.
3. DCC avalia condução.
4. Um médio adversário pode sair.
5. MC-E ou MC-D procura nova linha.
6. DCC escolhe a ligação disponível.
7. A equipa procura continuidade.

### Se DCC for pressionado

Pode utilizar GR ou circular.

### Se os pivôs estiverem bloqueados

Pode procurar ala ou avançado interior.

### Se não existir saída curta

Pode utilizar passe direto com organização para segunda bola.

### Riscos

- Superioridade apenas numérica.
- Pivôs marcados.
- Central livre sem progressão.
- Passe interior intercetado.

---

## 29. Pressão com três avançados

### Situação

O adversário utiliza três referências na primeira pressão.

Exemplos possíveis:

- 4-3-3.
- 3-4-3.
- 4-2-3-1 com um jogador adicional a subir.

### Relação inicial

Três centrais perante três avançados.

### Problema

Pode existir igualdade numérica na primeira linha.

### Soluções possíveis

- Utilizar GR.
- Baixar um médio.
- Aproximar um ala.
- Alterar alturas.
- Criar terceiro homem.
- Explorar espaço nas costas.
- Utilizar passe direto.

### Exemplo

1. GR inicia.
2. Os três avançados adversários controlam os centrais.
3. MC-E baixa ligeiramente.
4. MC-D mantém referência.
5. ALA-E oferece largura.
6. GR identifica a solução disponível.
7. A equipa procura ultrapassar pressão.

### Riscos

- Pivôs bloqueados.
- Ala pressionado.
- Passe curto intercetado.
- Falta de continuidade.
- Perda perto da baliza.

### Regra

Não assumir que baixar um médio resolve automaticamente uma pressão de três.

É necessário avaliar o efeito dessa descida sobre o meio-campo.

---

## 30. Pressão com quatro referências avançadas

### Situação

O adversário projeta quatro jogadores para condicionar a primeira construção.

Pode acontecer em estruturas diferentes.

### Problema

Os três centrais e o GR podem ficar pressionados ou condicionados.

### Soluções possíveis

- Movimento de um pivô.
- Ala baixo.
- Passe direto.
- Mudança de corredor.
- Terceiro homem.
- Exploração do espaço deixado atrás da pressão.

### Riscos

- Perda em zona baixa.
- Falta de apoio.
- Passe longo sem segunda bola.
- Jogadores demasiado afastados.

### Regra

Uma pressão numerosa pode libertar espaço noutra zona, mas esse espaço só é explorável se existir uma ligação executável.

---

# PARTE V — PRESSÃO INDIVIDUAL, ZONAL E MISTA

## 31. Pressão individual

### Características

O adversário procura acompanhar referências específicas.

### Problemas possíveis

- Pivôs marcados.
- Alas controlados.
- Centrais pressionados.
- Avançados interiores acompanhados.

### Soluções possíveis

- Movimentos de arrastamento.
- Trocas posicionais.
- Condução.
- Terceiro homem.
- Passe direto.
- Ataque à profundidade.

### Exemplo

1. MC-E é acompanhado.
2. MC-E baixa.
3. O adversário acompanha.
4. AE procura ocupar espaço libertado.
5. DCE avalia passe para AE.
6. A equipa progride se a linha estiver aberta.

### Risco

O adversário pode transferir a marcação e manter o espaço protegido.

### Regra

Movimento de arrastamento não garante libertação de espaço.

---

## 32. Pressão zonal

### Características

O adversário protege espaços e linhas.

### Problemas possíveis

- Pivôs em sombras de pressão.
- Corredor central fechado.
- Circulação orientada.
- Acesso exterior condicionado.

### Soluções possíveis

- Circular para deslocar o bloco.
- Criar escalonamento.
- Atrair e libertar.
- Conduzir.
- Mudar corredor.
- Procurar terceiro homem.

### Riscos

- Circulação lenta.
- Passe previsível.
- Pressão lateral.
- Falta de profundidade.

---

## 33. Pressão mista

### Características

O adversário combina referências individuais e zonais.

### Exemplo

- PL pressiona DCC.
- Extremos condicionam centrais exteriores.
- Um médio marca MC-E.
- Outro médio protege zona central.
- Laterais controlam alas.

### Soluções possíveis

- Identificar referência individual.
- Explorar espaço condicionado por essa marcação.
- Alterar alturas.
- Utilizar apoio de GR.
- Criar superioridade local.

### Riscos

- Confundir jogador aparentemente livre com jogador realmente disponível.
- Passe intercetado.
- Falta de continuidade.

---

# PARTE VI — ARMADILHAS DE PRESSÃO

## 34. Armadilha no corredor lateral

### Situação

O adversário permite circulação para DCE e prepara pressão junto à linha.

### Comportamento adversário possível

1. DCE recebe.
2. Avançado adversário condiciona passe interior.
3. Extremo adversário pressiona.
4. Médio adversário bloqueia MC-E.
5. Lateral adversário controla ALA-E.
6. A equipa fica pressionada junto à linha.

### Soluções possíveis

- Identificar armadilha antes do passe.
- Utilizar GR ou DCC.
- Alterar altura de MC-E.
- Procurar AE se a linha existir.
- Explorar espaço atrás da pressão.
- Evitar receção exterior sem apoio.

### Riscos

- Perda junto à área.
- Passe interior intercetado.
- Ala isolado.
- Passe atrasado pressionado.

### Regra

Não recomendar passe para o ala apenas porque está próximo do central exterior.

---

## 35. Armadilha sobre o pivô

### Situação

O adversário permite o passe para MC-E, mas prepara pressão imediata.

### Problema

MC-E recebe de costas e sem apoio.

### Soluções possíveis

- Preparar terceiro homem.
- Ajustar orientação corporal.
- Criar apoio próximo.
- Utilizar passe de primeira quando viável.
- Evitar passe se a pressão for demasiado forte.

### Exemplo

1. DCE identifica MC-E.
2. MC-E percebe pressão nas costas.
3. MC-D ajusta posição.
4. AE aproxima-se.
5. DCE avalia se existe combinação segura.
6. Se não existir, circula.

### Riscos

- Perda central.
- Passe de primeira intercetado.
- MC-E isolado.
- Falta de cobertura.

---

## 36. Armadilha sobre o guarda-redes

### Situação

O adversário orienta circulação para o GR e acelera pressão.

### Problema

O GR pode ficar sem opções curtas.

### Soluções possíveis

- Antecipar a pressão.
- Preparar saída pelo lado contrário.
- Criar linha com central.
- Utilizar passe médio ou longo.
- Garantir disputa da segunda bola.

### Regra

Não recomendar passe atrasado ao GR se a pressão tornar a receção ou a ação seguinte perigosas.

---

# PARTE VII — MECANISMOS DE PROGRESSÃO

## 37. Central exterior para médio

### Sequência possível

1. DCE recebe.
2. MC-E ajusta altura.
3. O adversário perde acesso direto a MC-E.
4. DCE encontra linha.
5. MC-E recebe orientado.
6. Procura AE, ALA-E ou MC-D.

### Condições

- Linha aberta.
- Recetor disponível.
- Pressão controlável.
- Continuidade.

### Riscos

- Interceção.
- Receção de costas.
- Perda central.

---

## 38. Central exterior para ala

### Sequência possível

1. DCE recebe.
2. ALA-E oferece largura.
3. AE ocupa corredor interior.
4. MC-E aproxima-se.
5. DCE procura ALA-E.
6. ALA-E avalia apoio interior ou progressão.

### Se o lateral adversário pressionar ALA-E

AE pode explorar espaço, se estiver disponível.

### Se o extremo adversário recuperar

ALA-E pode precisar de apoio.

### Riscos

- Ala pressionado.
- Falta de continuidade.
- Armadilha lateral.
- Perda exterior.

---

## 39. Central exterior para avançado interior

### Sequência possível

1. DCE recebe.
2. AE aproxima-se do corredor interior.
3. MC-E fixa ou atrai referência.
4. DCE identifica linha para AE.
5. AE recebe entre linhas.
6. Procura PL, ALA-E ou condução.

### Condições

- Passe executável.
- AE não estar bloqueado.
- Receção funcional.
- Apoio próximo.

### Riscos

- Passe intercetado.
- AE receber pressionado.
- Falta de profundidade.
- Perda central.

---

## 40. Terceiro homem através do pivô

### Exemplo

1. DCE recebe.
2. AE está marcado.
3. MC-E oferece apoio.
4. DCE passa a MC-E.
5. MC-E devolve ou liga para outro jogador.
6. AE desloca-se para nova linha.
7. A equipa procura ultrapassar a referência defensiva.

### Condições

- Apoio disponível.
- Movimento sincronizado.
- Passe de continuidade possível.
- Adversário atraído ou deslocado.

### Regra

O terceiro homem não é uma sequência fixa de três passes.

É um mecanismo para alcançar um jogador através de uma ligação intermédia.

---

## 41. Terceiro homem através do PL

### Exemplo

1. DCC recebe.
2. MC-D está bloqueado.
3. PL baixa para oferecer apoio.
4. DCC encontra PL se a linha estiver aberta.
5. AD movimenta-se.
6. PL procura AD.
7. A equipa progride.

### Riscos

- PL pressionado.
- Passe longo intercetado.
- AD sem espaço.
- Segunda bola perdida.

### Alternativa

Manter circulação ou utilizar outra ligação.

---

## 42. Mudança de corredor

### Objetivo

Explorar o deslocamento da pressão adversária.

### Exemplo

1. DCE recebe.
2. O adversário concentra pressão à esquerda.
3. DCE procura DCC ou GR.
4. A bola circula para DCD.
5. ALA-D identifica espaço.
6. DCD avalia progressão.

### Condições

- Circulação suficientemente rápida.
- Passe seguro.
- Espaço no corredor contrário.
- Apoios disponíveis.

### Riscos

- Passe intercetado.
- Mudança demasiado lenta.
- Adversário reorganizado.
- Falta de continuidade.

---

## 43. Passe direto para o PL

### Objetivo

Ultrapassar pressão através de uma ligação mais longa.

### Condições favoráveis

- PL oferece referência.
- Existe espaço para atacar.
- Há apoio próximo.
- A equipa consegue disputar segunda bola.
- O passe é executável.

### Exemplo

1. GR identifica pressão alta.
2. PL posiciona-se para receber ou disputar.
3. AE e AD aproximam-se de zonas úteis.
4. Um pivô prepara segunda bola.
5. GR executa passe direto.
6. A equipa procura continuidade.

### Riscos

- PL isolado.
- Segunda bola adversária.
- Passe sem direção.
- Equipa demasiado afastada.

### Regra

Passe direto não significa necessariamente perda de controlo.

Pode ser uma solução racional perante pressão.

---

## 44. Passe direto para o ala

### Situação

O adversário concentra pressão central.

### Objetivo

Explorar espaço exterior.

### Exemplo

1. GR recebe.
2. ALA-D mantém altura.
3. AD oferece apoio interior.
4. MC-D prepara segunda bola.
5. GR procura ALA-D se o passe for viável.
6. A equipa procura progressão.

### Riscos

- Ala pressionado.
- Passe longo intercetado.
- Falta de apoio.
- Espaço nas costas após perda.

---

## 45. Ataque ao espaço nas costas da pressão

### Situação

O adversário pressiona alto.

### Possível oportunidade

Existe espaço entre a linha de pressão e a linha defensiva, ou nas costas da última linha.

### Soluções possíveis

- Passe para avançado interior.
- Passe para PL.
- Movimento diagonal.
- Passe para ala alto.
- Condução após ultrapassar pressão.

### Regra

O espaço nas costas da pressão não está necessariamente livre.

É necessário verificar as coberturas adversárias e a trajetória do passe.

---

# PARTE VIII — SAÍDA CONTRA SISTEMAS ESPECÍFICOS

## 46. 3-4-3 contra 4-4-2

### Relações possíveis

- Três centrais perante dois avançados.
- Dois pivôs perante dois médios-centro.
- Alas perante médios exteriores ou laterais.
- Avançados interiores perante referências defensivas.

### Problema possível

Os dois avançados condicionam centrais.

Os dois médios adversários bloqueiam pivôs.

Os extremos adversários preparam pressão lateral.

### Solução possível

1. DCC recebe.
2. Identifica pressão dos dois avançados.
3. Conduz se existir espaço.
4. Um médio adversário pode aproximar-se.
5. MC-E ajusta para criar linha.
6. DCC procura ligação disponível.
7. A equipa procura continuidade.

### Alternativa

Utilizar GR, ala ou passe direto.

### Riscos

- DCC pressionado.
- Pivôs bloqueados.
- Armadilha lateral.
- Passe central intercetado.

---

## 47. 3-4-3 contra 4-3-3

### Relações possíveis

- Três centrais perante três avançados.
- Dois pivôs perante três médios.
- Alas perante laterais ou extremos.

### Problema possível

Igualdade na primeira linha e inferioridade central.

### Soluções possíveis

- Utilizar GR.
- Alterar altura dos pivôs.
- Aproximar avançado interior.
- Utilizar ala.
- Explorar espaço nas costas.
- Criar terceiro homem.

### Exemplo

1. GR inicia.
2. Três avançados condicionam centrais.
3. MC-E ajusta altura.
4. AE aproxima-se do corredor interior.
5. ALA-E mantém largura.
6. GR procura a solução disponível.

### Riscos

- Pivôs bloqueados.
- Avançado interior marcado.
- Ala pressionado.
- Passe curto intercetado.

---

## 48. 3-4-3 contra 4-2-3-1

### Relações possíveis

- PL e MO adversários podem pressionar dois centrais.
- Extremos adversários podem condicionar centrais exteriores.
- Dois pivôs adversários podem controlar médios próprios.
- Laterais adversários podem pressionar alas.

### Problema possível

A pressão pode transformar-se numa primeira linha de quatro referências.

### Soluções possíveis

- Identificar jogador livre.
- Utilizar GR.
- Alterar alturas.
- Criar apoio de ala.
- Explorar espaço deixado pelos extremos.
- Utilizar passe direto.

### Riscos

- Pivôs marcados.
- Pressão sobre central exterior.
- Armadilha lateral.
- Falta de continuidade.

---

## 49. 3-4-3 contra 3-5-2

### Relações possíveis

- Três centrais perante dois avançados.
- Dois médios perante três médios.
- Alas perante alas.
- Avançados próprios perante três centrais.

### Problema possível

Existe superioridade numérica inicial, mas inferioridade central.

### Soluções possíveis

- Condução de central.
- Aproximação de avançado interior.
- Alteração da altura de um pivô.
- Utilização de ala.
- Passe direto.

### Exemplo

1. DCC recebe.
2. Dois avançados adversários condicionam centrais.
3. Um médio adversário pode subir.
4. AE aproxima-se por dentro.
5. MC-E ajusta posição.
6. DCC identifica a melhor ligação.

### Riscos

- Pivôs controlados.
- Ala pressionado.
- Central sair sem cobertura.
- Passe interior intercetado.

---

## 50. 3-4-3 contra 3-4-3

### Relações possíveis

- Três centrais perante três avançados.
- Dois médios perante dois médios.
- Alas perante alas.

### Problema possível

O adversário consegue estabelecer marcações próximas das referências próprias.

### Soluções possíveis

- Utilizar GR.
- Criar assimetria.
- Alterar alturas.
- Movimentos de arrastamento.
- Terceiro homem.
- Passe direto.

### Riscos

- Pressão individualizada.
- Pivôs bloqueados.
- Alas pressionados.
- Falta de cobertura.

---

# PARTE IX — PROTEÇÃO PREVENTIVA

## 51. Equilíbrio durante a saída de bola

A saída de bola deve considerar a possibilidade de perda.

### Perguntas

- Quem protege o corredor central?
- Quem controla profundidade?
- Os centrais estão demasiado afastados?
- Os pivôs estão disponíveis para reagir?
- Os alas estão projetados?
- O adversário possui avançados preparados para contra-atacar?

### Regra

Uma construção com muitos apoios não é necessariamente segura se esses apoios estiverem mal posicionados.

---

## 52. Perda do central exterior

### Situação

DCE perde durante condução.

### Riscos

- Espaço nas costas.
- DCC obrigado a sair.
- DCD exposto.
- Pivô ultrapassado.
- Contra-ataque central.

### Resposta possível

1. Jogador próximo condiciona portador.
2. MC-E protege corredor interior.
3. DCC controla profundidade.
4. DCD ajusta cobertura.
5. ALA-E recupera.
6. A equipa reorganiza.

### Regra

Não recomendar pressão imediata do DCC sem avaliar a cobertura.

---

## 53. Perda de um pivô

### Situação

MC-E perde em zona central.

### Riscos

- Adversário atacar diretamente a última linha.
- MC-D isolado.
- Centrais expostos.
- Avançados adversários atacarem profundidade.

### Resposta possível

- Jogador próximo condiciona.
- MC-D protege centro.
- Centrais ajustam profundidade.
- Alas recuperam.
- A equipa temporiza ou contra-pressiona conforme condições.

### Regra

Perdas centrais podem ser particularmente perigosas pela proximidade ao eixo da baliza.

---

## 54. Perda do ala

### Situação

ALA-D perde junto à linha.

### Riscos

- Contra-ataque exterior.
- DCD obrigado a ajustar.
- Espaço interior.
- Mudança de corredor.

### Resposta possível

- AD condiciona portador.
- MC-D protege interior.
- DCD ajusta cobertura.
- DCC controla profundidade.
- ALA-D recupera.

### Regra

MC-D não deve abandonar automaticamente o centro para ocupar a linha lateral.

---

## 55. Ambos os alas altos

### Situação

ALA-E e ALA-D encontram-se projetados.

### Riscos

- Espaço nas costas.
- Três centrais expostos em grande largura.
- Pivôs ultrapassados.
- Adversário explorar corredores exteriores.

### Soluções possíveis

- Manter pivôs em posições de cobertura.
- Controlar distâncias dos centrais.
- Preparar contra-pressão.
- Ajustar altura de um ala.
- Garantir equilíbrio.

### Regra

A projeção simultânea dos alas pode ser funcional, mas exige proteção preventiva adequada.

---

# PARTE X — CASOS PRÁTICOS COMPLETOS

## 56. Caso A — Central do meio livre perante dois avançados

**Situação:**

O adversário pressiona com dois avançados.

DCC encontra-se momentaneamente livre.

**Objetivo:** progredir com controlo.

**Sequência possível:**

1. GR passa a DCC.
2. DCC identifica espaço.
3. Conduz.
4. Um médio adversário aproxima-se.
5. MC-E ajusta para nova linha.
6. DCC procura MC-E se o passe estiver disponível.
7. MC-E recebe e procura continuidade.

**Se o médio não sair:**

DCC pode continuar a conduzir.

**Se MC-E estiver bloqueado:**

DCC pode procurar ala, outro médio ou circular.

**Riscos:**

- DCC pressionado durante condução.
- Passe central intercetado.
- Falta de cobertura.

---

## 57. Caso B — Pressão alta de três avançados

**Situação:**

O adversário utiliza três avançados contra os três centrais.

**Objetivo:** criar saída funcional.

**Sequência possível:**

1. GR recebe.
2. Os três avançados condicionam os centrais.
3. MC-E aproxima-se da construção.
4. MC-D mantém referência central.
5. ALA-D oferece largura.
6. GR avalia ligação.
7. A equipa procura ultrapassar pressão.

**Se MC-E for acompanhado:**

Pode surgir espaço noutra zona, dependendo da reação adversária.

**Se o adversário bloquear as opções curtas:**

Considerar passe direto.

**Riscos:**

- Inferioridade central.
- Passe curto intercetado.
- Ala pressionado.
- Falta de segunda bola.

---

## 58. Caso C — Armadilha lateral sobre DCE

**Situação:**

O adversário permite passe para DCE e prepara pressão.

**Objetivo:** evitar perda junto à linha.

**Sequência possível:**

1. DCC identifica comportamento adversário.
2. DCE recebe.
3. Extremo adversário aproxima-se.
4. MC-E está bloqueado.
5. ALA-E está controlado.
6. DCE procura GR ou DCC se existir linha segura.
7. A equipa muda corredor.

**Alternativa:**

Procurar AE se estiver disponível entre linhas.

**Riscos:**

- Passe atrasado intercetado.
- Pressão sobre GR.
- Perda exterior.
- Passe interior forçado.

---

## 59. Caso D — Pivôs marcados individualmente

**Situação:**

MC-E e MC-D estão acompanhados.

**Objetivo:** criar nova linha de progressão.

**Sequência possível:**

1. MC-E altera altura.
2. O marcador acompanha.
3. AE aproxima-se do espaço libertado.
4. DCE identifica movimento.
5. DCE procura AE se a linha existir.
6. AE recebe e liga com PL ou ALA-E.

**Se o marcador não acompanhar:**

MC-E pode ficar disponível.

**Se o adversário transferir marcação:**

A equipa deve procurar outra relação.

**Riscos:**

- AE pressionado.
- Passe intercetado.
- Falta de profundidade.
- Espaço central desprotegido.

---

## 60. Caso E — Ala baixo para facilitar saída

**Situação:**

DCD está pressionado.

ALA-D aproxima-se.

**Objetivo:** criar apoio exterior.

**Sequência possível:**

1. DCD recebe.
2. ALA-D baixa.
3. MC-D oferece apoio interior.
4. AD mantém referência mais avançada.
5. DCD procura ALA-D se estiver disponível.
6. ALA-D avalia ligação interior.
7. A equipa procura progressão.

**Se ALA-D for pressionado:**

Pode devolver ou procurar terceiro homem.

**Se não existir continuidade:**

DCD deve evitar passe para uma armadilha.

**Riscos:**

- Ala receber de costas.
- Pressão lateral.
- Passe interior intercetado.

---

## 61. Caso F — Saída direta para PL

**Situação:**

O adversário bloqueia construção curta.

**Objetivo:** ultrapassar pressão.

**Sequência possível:**

1. GR identifica bloqueio.
2. PL posiciona-se.
3. AE e AD aproximam-se de zonas de apoio.
4. MC-E prepara segunda bola.
5. GR executa passe direto.
6. PL procura receção ou disputa.
7. A equipa tenta manter continuidade.

**Se PL ganhar a bola:**

Pode ligar com avançado exterior.

**Se a bola ficar dividida:**

A equipa disputa segunda bola.

**Se não existir apoio:**

A opção direta apresenta maior risco de perda.

---

## 62. Caso G — Central exterior conduz e atrai médio

**Situação:**

DCE recebe com espaço.

**Objetivo:** criar vantagem interior.

**Sequência possível:**

1. DCE conduz.
2. MC adversário aproxima-se.
3. MC-E ajusta posição.
4. AE ocupa corredor interior.
5. DCE identifica jogador livre.
6. Executa passe.
7. A equipa progride.

**Se o médio não pressionar:**

DCE pode continuar a conduzir.

**Se AE estiver marcado:**

Procurar MC-E ou ala.

**Riscos:**

- Perda durante condução.
- Central sair sem cobertura.
- Passe vertical intercetado.

---

## 63. Caso H — Construção contra 3-5-2

**Situação:**

Dois avançados pressionam três centrais.

Três médios adversários controlam dois pivôs e espaços interiores.

**Objetivo:** ultrapassar pressão sem perder controlo central.

**Sequência possível:**

1. DCC recebe.
2. Identifica posicionamento dos avançados.
3. DCE oferece largura.
4. AE aproxima-se do corredor interior.
5. MC-E ajusta altura.
6. DCC procura uma linha funcional.
7. A equipa progride ou circula.

**Se o médio adversário acompanhar AE:**

Pode surgir espaço noutra zona.

**Se o ala adversário pressionar ALA-E:**

Pode existir espaço nas suas costas, sujeito à cobertura do central exterior adversário.

**Riscos:**

- Inferioridade central.
- Ala pressionado.
- Passe interior intercetado.
- Central exterior exposto.

---

## 64. Caso I — Construção assimétrica

**Situação:**

ALA-E baixo e ALA-D alto.

**Objetivo:** facilitar saída à esquerda e manter profundidade à direita.

**Sequência possível:**

1. GR passa a DCE.
2. ALA-E aproxima-se.
3. MC-E oferece apoio.
4. AE ocupa corredor interior.
5. ALA-D mantém altura.
6. DCE procura progressão.
7. A equipa pode mudar corredor se existir vantagem.

**Riscos:**

- Falta de apoio à direita.
- Mudança lenta.
- Lado esquerdo congestionado.
- Falta de proteção.

---

## 65. Caso J — Saída curta ultrapassada, mas sem continuidade

**Situação:**

A equipa consegue encontrar MC-D atrás da primeira pressão.

Contudo, MC-D está isolado.

**Objetivo:** evitar perda na fase seguinte.

**Sequência possível:**

1. DCD passa a MC-D.
2. MC-D recebe.
3. Identifica pressão adversária.
4. AD aproxima-se.
5. ALA-D oferece apoio.
6. MC-D decide entre progressão e conservação.
7. A equipa reorganiza relações.

**Se existir ligação funcional:**

Progredir.

**Se não existir:**

Conservar ou circular.

**Riscos:**

- MC-D pressionado.
- Passe precipitado.
- Perda central.
- Falta de cobertura.

### Regra

A saída de bola não termina no primeiro passe que ultrapassa a pressão.

A equipa precisa de continuidade.

---

# PARTE XI — ERROS FREQUENTES

## 66. Erros na saída de bola do 3-4-3

### 66.1. Assumir que três centrais garantem superioridade

A pressão pode neutralizar a vantagem.

### 66.2. Baixar um médio automaticamente

Pode retirar presença ao meio-campo.

### 66.3. Colocar os dois pivôs na mesma sombra de pressão

Reduz linhas disponíveis.

### 66.4. Projetar ambos os alas sem cobertura

Aumenta risco de contra-ataque.

### 66.5. Procurar sempre o ala

Pode facilitar armadilha lateral.

### 66.6. Procurar sempre passe central

Pode provocar perda perigosa.

### 66.7. Conduzir sem continuidade

O central pode ficar isolado.

### 66.8. Utilizar GR sem avaliar pressão

Pode criar risco junto à baliza.

### 66.9. Utilizar passe direto sem apoio

A segunda bola pode ser perdida.

### 66.10. Ignorar os avançados interiores

A equipa perde possíveis referências entre linhas.

### 66.11. Ignorar a posição do PL

A equipa pode ficar sem profundidade.

### 66.12. Confundir circulação com progressão

Ter posse não significa ultrapassar linhas.

### 66.13. Confundir superioridade numérica com funcional

Mais jogadores não garantem acesso.

### 66.14. Ignorar a fase seguinte

A equipa ultrapassa a pressão, mas perde imediatamente.

---

# PARTE XII — CRITÉRIOS PARA A IA

## 67. Perguntas obrigatórias

Antes de recomendar uma saída de bola, a IA deve identificar:

1. Qual é a estrutura própria?
2. Qual é a estrutura adversária?
3. Quantos adversários pressionam efetivamente?
4. Quem pressiona o portador?
5. Quem bloqueia os centrais?
6. Quem bloqueia os pivôs?
7. Quem controla os alas?
8. Quem controla os avançados interiores?
9. O GR está disponível?
10. Existe superioridade numérica?
11. Existe superioridade funcional?
12. Existem linhas de passe abertas?
13. O recetor consegue orientar-se?
14. Existe possibilidade de condução?
15. Existe possibilidade de terceiro homem?
16. Existe espaço nas costas da pressão?
17. Existe possibilidade de passe direto?
18. Quem disputa segunda bola?
19. Existem coberturas?
20. Os alas estão altos?
21. Os pivôs estão escalonados?
22. Um médio deve baixar?
23. Qual é a consequência dessa descida?
24. Qual é o risco da solução?
25. Existe continuidade?
26. Qual é a alternativa?

---

## 68. Classificação das soluções

### Solução fundamentada

Respeita:

- Pressão real.
- Linhas disponíveis.
- Orientação corporal.
- Distâncias.
- Coberturas.
- Continuidade.
- Equilíbrio.

### Solução condicionada

Depende de:

- Movimento adversário.
- Linha ainda não confirmada.
- Reação à condução.
- Capacidade de receção.
- Apoio adicional.

### Solução contraditória

Exige:

- Passe por linha bloqueada.
- Jogador receber apesar de marcação impeditiva.
- Central sair sem cobertura perante ameaça clara.
- Ala receber sem possibilidade funcional.
- Superioridade inexistente.
- Progressão sem continuidade.

### Informação insuficiente

Faltam dados para avaliar a decisão.

---

## 69. Regras de interpretação para a IA

- Não assumir que três centrais garantem saída fácil.
- Não assumir que um central está livre apenas porque existe superioridade numérica.
- Não recomendar passe vertical sem linha disponível.
- Não recomendar condução sem avaliar pressão e cobertura.
- Não recomendar baixar um pivô sem avaliar a consequência no meio-campo.
- Não assumir que dois pivôs estão automaticamente disponíveis.
- Não recomendar passe para ala quando existe armadilha lateral evidente.
- Não assumir que os avançados exteriores estão sempre abertos.
- Não assumir que PL deve baixar sempre.
- Não assumir que passe direto é uma solução inferior.
- Não recomendar passe direto sem considerar apoio e segunda bola.
- Não assumir que GR oferece sempre superioridade funcional.
- Não confundir ultrapassar primeira pressão com completar a saída.
- Não ignorar a fase seguinte.
- Não ignorar a proteção preventiva.
- Não ignorar os espaços nas costas dos alas.
- Não assumir que a formação nominal determina a pressão real.
- Não assumir que a pressão individual cria automaticamente espaço livre.
- Não assumir que uma mudança de corredor cria automaticamente vantagem.
- Não atribuir capacidades individuais sem informação documentada.
- Explicar condições, movimentos, reações adversárias, riscos, continuidade e alternativas.
- Distinguir conhecimento universal de instruções específicas da equipa.
- Quando faltarem dados, apresentar hipóteses condicionais.

---

## 70. Relação com outros documentos

### Fundamentos

- `conhecimento/fundamentos/fases_jogo.md`
- `conhecimento/fundamentos/principios_ofensivos.md`
- `conhecimento/fundamentos/principios_defensivos.md`
- `conhecimento/fundamentos/superioridades.md`
- `conhecimento/fundamentos/modelos_jogo.md`

### Sistema 3-4-3

- `conhecimento/sistemas/343/organizacao.md`
- `conhecimento/sistemas/343/ataque.md`
- `conhecimento/sistemas/343/defesa.md`
- `conhecimento/sistemas/343/transicoes.md`

### Outros sistemas

- `conhecimento/sistemas/352/saida_bola.md`
- `conhecimento/sistemas/433/saida_bola.md`
- `conhecimento/sistemas/4231/saida_bola.md`

Os documentos ainda não preparados devem ser considerados referências previstas.

---

## 71. Princípio final

A saída de bola no 3-4-3 depende da capacidade para transformar a estrutura inicial numa organização funcional.

Os três centrais podem oferecer diferentes referências de construção.

O duplo pivô pode garantir ligação e equilíbrio.

Os alas podem oferecer largura, apoio ou profundidade.

Os avançados exteriores podem criar linhas interiores, fixar adversários ou atacar espaço.

O PL pode oferecer profundidade, apoio ou referência direta.

Contudo, nenhuma destas funções garante sucesso isoladamente.

Uma saída eficaz exige identificar a pressão real, criar linhas de passe, interpretar as reações adversárias, garantir continuidade e manter proteção preventiva.

O assistente de IA deve recomendar soluções condicionadas às posições reais, à pressão, às coberturas, aos espaços disponíveis e às alternativas existentes.