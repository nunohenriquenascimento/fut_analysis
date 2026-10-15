# Sistema Tático 3-4-3 — Transições Ofensivas e Defensivas

## 1. Objetivo do documento

Este documento descreve os princípios universais das transições ofensivas e defensivas no sistema 3-4-3.

As transições correspondem aos momentos de mudança de posse de bola, nos quais as equipas precisam de adaptar rapidamente as suas posições, funções e decisões.

A transição ofensiva começa com a recuperação da posse e desenvolve-se até a equipa estabelecer uma organização ofensiva ou terminar a ação.

A transição defensiva começa com a perda da posse e desenvolve-se até a equipa recuperar a bola, estabelecer uma organização defensiva ou sofrer uma finalização ou outra interrupção.

O assistente de inteligência artificial deve conseguir:

1. Identificar o momento e a zona da mudança de posse.
2. Distinguir transição de organização estabelecida.
3. Reconhecer a estrutura real no instante da recuperação ou perda.
4. Avaliar o posicionamento dos três avançados.
5. Interpretar a disponibilidade dos alas.
6. Avaliar a relação entre os dois médios-centro.
7. Identificar a proteção dos três centrais.
8. Reconhecer oportunidades de contra-ataque.
9. Avaliar possibilidades de conservar a posse.
10. Identificar movimentos de apoio e profundidade.
11. Reconhecer superioridades numéricas, posicionais, qualitativas e dinâmicas.
12. Analisar decisões de contra-pressão.
13. Identificar situações que exigem temporização.
14. Avaliar recuperação defensiva.
15. Reconhecer vulnerabilidades nos corredores exteriores e interiores.
16. Analisar o controlo da profundidade.
17. Avaliar a ocupação da área em ataques rápidos.
18. Identificar riscos de perdas consecutivas.
19. Interpretar as adaptações perante diferentes adversários.
20. Propor soluções condicionadas ao contexto.

O 3-4-3 não determina obrigatoriamente um comportamento de transição.

A equipa pode procurar aceleração imediata, conservação, contra-pressão, temporização ou reorganização, conforme a situação.

---

# PARTE I — FUNDAMENTOS DAS TRANSIÇÕES

## 2. As quatro fases do jogo

O jogo pode ser analisado através de quatro fases fundamentais:

1. Organização ofensiva.
2. Transição defensiva.
3. Organização defensiva.
4. Transição ofensiva.

Estas fases estão relacionadas.

Uma equipa que ataca deve preparar-se para perder a bola.

Uma equipa que defende deve preparar-se para a recuperar.

### Regra para a IA

A análise das transições deve considerar as posições e os comportamentos existentes antes da mudança de posse.

---

## 3. Características das transições no 3-4-3

O sistema 3-4-3 pode apresentar:

- Três referências avançadas.
- Dois médios-centro.
- Dois alas com responsabilidades nos dois sentidos.
- Três centrais.
- Possibilidade de ocupação dos cinco corredores.
- Estruturas ofensivas em 3-2-5 ou 3-2-4-1.
- Estruturas defensivas em 5-2-3, 5-4-1 ou 5-2-2-1.

### Potenciais vantagens

- Três referências para atacar após recuperação.
- Possibilidade de explorar largura e profundidade.
- Presença de avançados exteriores para atacar diagonais.
- Três centrais para proteger a zona central.
- Possibilidade de reagir rapidamente à perda.

### Potenciais vulnerabilidades

- Espaço nas costas dos alas.
- Dois médios-centro expostos.
- Distâncias elevadas entre linhas.
- Centrais exteriores obrigados a defender espaços amplos.
- Corredores interiores vulneráveis.
- Dificuldade em recuperar se os três avançados permanecerem altos.

### Princípio

As vantagens e vulnerabilidades dependem da organização real, não apenas da designação 3-4-3.

---

## 4. Variáveis que condicionam a transição

A IA deve analisar:

- Zona da recuperação ou perda.
- Orientação corporal do portador.
- Pressão sobre a bola.
- Posição dos colegas.
- Posição dos adversários.
- Distância até à baliza.
- Espaço disponível.
- Linhas de passe.
- Possibilidade de condução.
- Capacidade de apoio.
- Capacidade de rutura.
- Superioridades e inferioridades.
- Equilíbrio coletivo.
- Estado físico dos jogadores.
- Momento do jogo, quando conhecido.

### Regra

Não recomendar uma transição rápida apenas porque existem jogadores avançados.

É necessário verificar se existe acesso funcional a esses jogadores.

---

## 5. Transição e organização estabelecida

### Transição ofensiva

A equipa recupera e procura explorar a organização adversária ainda em transformação.

### Organização ofensiva

A equipa estabelece referências e relações de ataque mais estáveis.

### Transição defensiva

A equipa perde e procura recuperar, atrasar ou controlar o ataque adversário.

### Organização defensiva

A equipa estabelece uma estrutura coletiva para defender.

### Regra

A transição não possui duração fixa universal.

A mudança de fase deve ser reconhecida através do comportamento coletivo.

---

# PARTE II — TRANSIÇÃO OFENSIVA

## 6. Objetivos da transição ofensiva

Após recuperar a bola, a equipa pode procurar:

- Atacar rapidamente.
- Explorar espaço livre.
- Criar superioridade.
- Encontrar jogadores orientados.
- Atacar profundidade.
- Explorar largura.
- Aproximar jogadores da área.
- Conservar a posse.
- Reorganizar o ataque.

A escolha depende das condições.

---

## 7. Primeira decisão após recuperação

O jogador que recupera deve avaliar:

1. Está pressionado?
2. Consegue orientar-se?
3. Existe espaço para conduzir?
4. Existe passe vertical disponível?
5. Existe apoio próximo?
6. Existem jogadores a atacar profundidade?
7. Existe superioridade?
8. O adversário está equilibrado?
9. Qual é o risco da ação?
10. É preferível conservar?

### Regra

A primeira ação não precisa de ser obrigatoriamente para a frente.

Um passe lateral ou atrasado pode permitir uma progressão posterior mais favorável.

---

## 8. Aceleração imediata

### Condições favoráveis

- Portador orientado.
- Espaço disponível.
- Adversários desequilibrados.
- Linhas de passe abertas.
- Jogadores em movimento.
- Possibilidade de atacar antes da reorganização.

### Riscos

- Passe precipitado.
- Falta de apoio.
- Perda consecutiva.
- Inferioridade após falha.
- Avançados isolados.

### Regra

Acelerar é uma opção condicionada, não uma obrigação.

---

## 9. Conservação após recuperação

### Situações possíveis

- Portador pressionado.
- Ausência de passe vertical.
- Avançados marcados.
- Adversário equilibrado.
- Equipa demasiado afastada.
- Risco elevado de perda.

### Soluções possíveis

- Passe de segurança.
- Apoio de um médio.
- Circulação pelos centrais.
- Mudança de corredor.
- Reorganização ofensiva.

### Regra

Conservar a posse pode representar uma transição ofensiva bem executada.

---

## 10. Contra-ataque

O contra-ataque procura explorar a desorganização adversária após a recuperação.

### Elementos

- Recuperação.
- Primeira ligação.
- Progressão.
- Movimentos de apoio e rutura.
- Decisão no último terço.
- Finalização ou continuidade.

### Regra

Um contra-ataque não exige obrigatoriamente um passe longo.

Pode desenvolver-se através de condução e combinações curtas.

---

# PARTE III — RECUPERAÇÃO EM DIFERENTES ZONAS

## 11. Recuperação no primeiro terço

### Situação

A equipa recupera perto da própria baliza.

### Prioridades

- Garantir controlo da bola.
- Identificar pressão adversária.
- Procurar primeira ligação.
- Avaliar espaço nas costas da pressão.
- Evitar perda imediata.

### Soluções possíveis

- Passe para pivô.
- Ligação com PL.
- Passe para avançado exterior.
- Condução.
- Circulação pelos centrais.
- Passe direto com disputa de segunda bola.

### Riscos

- Perda próxima da baliza.
- Passe interior intercetado.
- PL isolado.
- Falta de apoio.

---

## 12. Recuperação no segundo terço

### Situação

A equipa recupera em zona intermédia.

### Oportunidades

- Explorar espaço entre linhas.
- Atacar profundidade.
- Encontrar avançados exteriores.
- Utilizar alas.
- Criar superioridade dinâmica.

### Exemplo

1. MC-E recupera.
2. Identifica AE entre linhas.
3. PL ameaça profundidade.
4. ALA-E oferece largura.
5. MC-E decide entre passe, condução ou conservação.

### Riscos

- Passe vertical bloqueado.
- Avançado exterior pressionado.
- Pivô abandonar equilíbrio.
- Perda consecutiva.

---

## 13. Recuperação no último terço

### Situação

A equipa recupera perto da baliza adversária.

### Oportunidades

- Finalização rápida.
- Passe para PL.
- Ataque à área.
- Passe atrasado.
- Combinação curta.
- Remate com espaço.

### Riscos

- Decisão precipitada.
- Remate bloqueado.
- Passe intercetado.
- Falta de equilíbrio após nova perda.

### Regra

A proximidade à baliza aumenta a possibilidade de ameaça, mas não garante uma boa oportunidade.

---

## 14. Recuperação no corredor exterior

### Situação

ALA-E ou outro jogador recupera junto à linha.

### Soluções possíveis

- Condução exterior.
- Passe interior.
- Ligação com AE.
- Passe para MC-E.
- Mudança de corredor.
- Conservação.

### Riscos

- Pressão junto à linha.
- Poucas opções.
- Passe interior intercetado.
- Perda consecutiva.

---

## 15. Recuperação no corredor interior

### Situação

AE ou MC-E recupera numa zona interior.

### Oportunidades

- Atacar espaço central.
- Encontrar PL.
- Explorar diagonal.
- Conduzir.
- Combinar com ala.

### Riscos

- Pressão imediata.
- Perda central.
- Passe vertical intercetado.
- Falta de cobertura.

---

## 16. Recuperação no corredor central

### Situação

Um dos pivôs ou centrais recupera no eixo.

### Oportunidades

- Escolher diferentes corredores.
- Encontrar avançados.
- Conduzir.
- Explorar profundidade.

### Riscos

- Perda central.
- Pressão de vários adversários.
- Falta de apoio.
- Exposição da última linha.

### Regra

A recuperação central pode oferecer várias opções, mas exige especial atenção à segurança da primeira ação.

---

# PARTE IV — FUNÇÕES DOS JOGADORES NA TRANSIÇÃO OFENSIVA

## 17. Papel do ponta de lança

O PL pode:

- Atacar profundidade.
- Fixar centrais.
- Oferecer apoio.
- Proteger bola.
- Ligar com avançados exteriores.
- Preparar finalização.

### Regra

O PL não deve executar sempre o mesmo movimento.

A decisão depende da posição dos adversários e dos colegas.

---

## 18. PL em apoio

### Exemplo

1. MC-D recupera.
2. PL aproxima-se.
3. AD inicia diagonal.
4. MC-D procura PL.
5. PL liga com AD se existir linha.
6. AD procura progressão.

### Riscos

- PL pressionado.
- Falta de profundidade.
- Passe intercetado.
- Ausência de apoio.

---

## 19. PL em profundidade

### Exemplo

1. MC-E recupera orientado.
2. PL identifica espaço.
3. Inicia rutura.
4. AE aproxima-se para apoio.
5. MC-E procura passe.
6. PL ataca baliza.

### Riscos

- Fora de jogo.
- Passe indisponível.
- PL isolado.
- Falta de segunda bola.

---

## 20. Papel dos avançados exteriores

AE e AD podem:

- Atacar profundidade.
- Realizar diagonais.
- Oferecer apoio.
- Explorar corredores interiores.
- Oferecer largura.
- Atacar a área.
- Criar situações de um contra um.

### Regra

Os dois avançados exteriores não precisam de realizar movimentos iguais.

---

## 21. Avançado exterior em diagonal

### Exemplo

1. MC-E recupera.
2. AE identifica espaço entre lateral e central.
3. Inicia diagonal.
4. PL fixa central.
5. ALA-E oferece largura.
6. MC-E procura AE.

### Riscos

- Fora de jogo.
- Passe bloqueado.
- Falta de apoio.
- Movimento demasiado cedo.

---

## 22. Avançado exterior em apoio

### Exemplo

1. DCE recupera.
2. AE aproxima-se.
3. MC-E oferece apoio.
4. PL ameaça profundidade.
5. DCE procura AE.
6. AE liga com outro jogador.

### Objetivos

- Facilitar primeira ligação.
- Criar terceiro homem.
- Evitar passe precipitado.
- Preparar aceleração posterior.

---

## 23. Papel dos alas

Os alas podem:

- Atacar espaço exterior.
- Oferecer largura.
- Acompanhar contra-ataque.
- Criar linha de passe.
- Realizar ultrapassagem.
- Aproximar-se da área.
- Permanecer em cobertura.

### Regra

O ala não deve projetar-se automaticamente após cada recuperação.

É necessário avaliar o equilíbrio coletivo.

---

## 24. Ala próximo da recuperação

### Situação

A equipa recupera no corredor esquerdo.

### Possibilidade

ALA-E pode oferecer largura ou profundidade.

### Exemplo

1. MC-E recupera.
2. AE aproxima-se.
3. ALA-E inicia movimento exterior.
4. PL ataca profundidade.
5. MC-E identifica opção.
6. A equipa progride.

### Riscos

- Ala projetado sem cobertura.
- Passe intercetado.
- Espaço nas costas.
- Falta de apoio.

---

## 25. Ala contrário

### Situação

A equipa recupera num corredor.

O ala do lado contrário pode:

- Manter largura.
- Aproximar-se da área.
- Preparar mudança de corredor.
- Permanecer em equilíbrio.
- Atacar segundo poste numa fase posterior.

### Regra

O comportamento depende da velocidade da transição e das responsabilidades defensivas ainda existentes.

---

## 26. Papel do duplo pivô

MC-E e MC-D podem:

- Recuperar.
- Executar primeira ligação.
- Conduzir.
- Encontrar avançados.
- Apoiar progressão.
- Controlar segunda bola.
- Manter equilíbrio.

### Riscos

- Ambos projetarem-se.
- Ambos permanecerem demasiado baixos.
- Falta de ligação.
- Perda central.

---

## 27. Um pivô progride e outro equilibra

### Exemplo

1. MC-E recupera.
2. MC-E conduz.
3. MC-D mantém cobertura.
4. AE procura apoio.
5. PL ameaça profundidade.
6. ALA-E oferece largura.
7. MC-E decide.

### Objetivos

- Criar progressão.
- Manter proteção central.
- Evitar exposição dos centrais.

### Regra

A projeção de um médio deve considerar a posição do outro e a cobertura existente.

---

## 28. Papel dos três centrais

Os centrais podem:

- Recuperar a bola.
- Iniciar contra-ataque.
- Executar passe vertical.
- Conduzir.
- Alterar corredor.
- Manter proteção.
- Controlar profundidade.

### Regra

Nem todos os centrais devem acompanhar a transição ofensiva.

A equipa deve preservar uma estrutura de equilíbrio adequada.

---

## 29. Central exterior em condução

### Situação

DCE recupera e encontra espaço.

### Exemplo

1. DCE recupera.
2. Conduz.
3. MC-E oferece apoio.
4. AE procura corredor interior.
5. ALA-E mantém largura.
6. PL ameaça profundidade.
7. DCE procura progressão.

### Riscos

- Central sair sem cobertura.
- Passe intercetado.
- Espaço nas costas.
- Falta de equilíbrio.

---

# PARTE V — MECANISMOS DE CONTRA-ATAQUE

## 30. Contra-ataque pelo corredor central

### Exemplo

1. MC-D recupera.
2. PL aproxima-se.
3. AE ataca profundidade.
4. AD oferece apoio.
5. MC-D procura PL.
6. PL liga com AE.
7. AE procura finalização.

### Condições

- Linha disponível.
- Movimento coordenado.
- Adversário desequilibrado.
- Continuidade.

### Riscos

- Passe intercetado.
- PL pressionado.
- Falta de largura.
- Perda central.

---

## 31. Contra-ataque pelo corredor exterior

### Exemplo

1. ALA-E recupera.
2. AE aproxima-se.
3. PL ataca profundidade.
4. ALA-E progride.
5. AE procura apoio interior.
6. ALA-E decide entre passe, condução ou conservação.

### Riscos

- Pressão lateral.
- Falta de apoio.
- Passe interior bloqueado.
- Espaço nas costas.

---

## 32. Contra-ataque pelo corredor interior

### Exemplo

1. AE recupera.
2. PL ataca profundidade.
3. ALA-E oferece largura.
4. MC-E aproxima-se.
5. AE conduz.
6. Procura passe de rutura ou combinação.

### Riscos

- Condução pressionada.
- Passe bloqueado.
- Falta de cobertura.
- Perda central.

---

## 33. Contra-ataque com três avançados

### Situação

AE, PL e AD estão disponíveis após recuperação.

### Objetivos

- Criar várias ameaças.
- Explorar diagonais.
- Fixar defensores.
- Atacar profundidade.
- Criar oportunidade.

### Exemplo

1. MC-E recupera.
2. PL fixa central.
3. AE ataca espaço interior.
4. AD oferece largura.
5. MC-E procura a opção mais favorável.
6. A equipa progride.

### Regra

Três avançados perante três defensores não garantem vantagem funcional.

---

## 34. Contra-ataque com participação de um ala

### Exemplo

1. MC-D recupera.
2. AD aproxima-se.
3. ALA-D ataca espaço exterior.
4. PL ameaça profundidade.
5. AE prepara lado contrário.
6. MC-D procura progressão.

### Riscos

- Ala sair sem cobertura.
- Pivô isolado.
- Espaço exterior nas costas.
- Perda consecutiva.

---

## 35. Contra-ataque com mudança de corredor

### Situação

O adversário concentra jogadores no lado da recuperação.

### Exemplo

1. ALA-E recupera.
2. MC-E oferece apoio.
3. A bola chega a MC-D.
4. ALA-D mantém largura.
5. MC-D procura ALA-D.
6. ALA-D progride.

### Riscos

- Passe longo intercetado.
- Mudança lenta.
- Adversário reorganizado.
- Falta de apoio no lado contrário.

---

## 36. Contra-ataque através do terceiro homem

### Exemplo

1. DCE recupera.
2. AE oferece apoio.
3. PL ataca profundidade.
4. DCE passa a MC-E.
5. MC-E encontra AE.
6. AE procura PL.

### Condições

- Ligações disponíveis.
- Movimento coordenado.
- Tempo de execução.
- Continuidade.

### Regra

O terceiro homem só deve ser recomendado quando resolve uma limitação real de acesso.

---

## 37. Contra-ataque através de condução

### Jogadores possíveis

- Central exterior.
- Médio.
- Ala.
- Avançado exterior.

### Objetivos

- Ganhar metros.
- Atrair adversário.
- Criar superioridade dinâmica.
- Abrir linha de passe.

### Riscos

- Perda.
- Falta de apoio.
- Adversário recuperar posição.
- Exposição defensiva.

---

## 38. Ataque rápido à área

### Objetivos

- Criar finalização.
- Explorar espaço antes da reorganização.
- Atacar zonas complementares.

### Ocupação possível

- PL ataca zona central.
- AE procura primeiro poste.
- AD procura segundo poste.
- Um médio aproxima-se da entrada da área.
- Outros jogadores mantêm equilíbrio.

### Regra

A ocupação deve adaptar-se à posição da bola e ao número de jogadores disponíveis.

---

# PARTE VI — TRANSIÇÃO DEFENSIVA

## 39. Objetivos da transição defensiva

Após perder a bola, a equipa pode procurar:

- Recuperar imediatamente.
- Impedir progressão.
- Condicionar primeiro passe.
- Temporizar.
- Proteger centro.
- Controlar profundidade.
- Recuperar posições.
- Estabelecer bloco defensivo.

### Princípio

A reação imediata não significa pressionar obrigatoriamente.

---

## 40. Primeira decisão após perda

A equipa deve avaliar:

1. Onde ocorreu a perda?
2. Quem está próximo?
3. O portador adversário está pressionado?
4. Existem coberturas?
5. Existe possibilidade real de recuperar?
6. O adversário está orientado?
7. Existem linhas de passe perigosas?
8. Os alas estão altos?
9. Os pivôs estão equilibrados?
10. Os centrais controlam profundidade?

### Regra

A decisão deve considerar o risco de a pressão ser ultrapassada.

---

## 41. Contra-pressão

A contra-pressão procura recuperar rapidamente após perda.

### Condições favoráveis

- Jogadores próximos.
- Portador adversário pressionado.
- Linhas de passe limitadas.
- Coberturas disponíveis.
- Equilíbrio coletivo.
- Possibilidade de intervenção.

### Riscos

- Pressão ultrapassada.
- Espaço nas costas.
- Pivôs expostos.
- Centrais isolados.
- Contra-ataque adversário.

---

## 42. Contra-pressão no corredor exterior

### Situação

ALA-E perde a bola alto.

### Exemplo

1. ALA-E procura condicionar portador.
2. AE fecha linha próxima.
3. MC-E protege corredor interior.
4. DCE controla profundidade.
5. DCC ajusta cobertura.
6. A equipa procura recuperar.

### Se a pressão for ultrapassada

A equipa deve reorganizar e proteger espaço nas costas do ala.

### Riscos

- Passe interior.
- Passe nas costas.
- Central exterior isolado.
- Mudança de corredor.

---

## 43. Contra-pressão no corredor interior

### Situação

AE perde a bola entre linhas.

### Exemplo

1. AE reage.
2. MC-E aproxima-se se existir possibilidade.
3. MC-D protege centro.
4. ALA-E controla exterior.
5. Centrais ajustam profundidade.
6. A equipa procura recuperar.

### Riscos

- Passe vertical.
- Pivôs ultrapassados.
- Espaço central.
- Centrais expostos.

---

## 44. Contra-pressão no corredor central

### Situação

MC-E perde a bola.

### Prioridades

- Condicionar portador.
- Proteger passe vertical.
- Controlar profundidade.
- Evitar inferioridade.

### Exemplo

1. MC-E reage.
2. MC-D protege eixo.
3. AE aproxima-se.
4. PL condiciona apoio.
5. Centrais ajustam.
6. Alas recuperam.

### Riscos

- Perda em zona perigosa.
- Pivôs ultrapassados.
- Passe direto para PL.
- Espaço entre linhas.

---

## 45. Contra-pressão após cruzamento intercetado

### Situação

ALA-E cruza e o adversário recupera.

### Possibilidades

- Jogadores próximos pressionam segunda bola.
- Médio controla zona frontal.
- Central exterior protege espaço.
- Ala inicia recuperação.
- Equipa temporiza se não existir possibilidade de recuperar.

### Riscos

- Muitos jogadores na área.
- Pivôs avançados.
- Espaço nas costas dos alas.
- Contra-ataque rápido.

---

# PARTE VII — TEMPORIZAÇÃO E REORGANIZAÇÃO

## 46. Temporização defensiva

Temporizar significa atrasar a progressão adversária para permitir recuperação coletiva.

### Objetivos

- Ganhar tempo.
- Reduzir velocidade adversária.
- Proteger centro.
- Permitir recuperação dos alas.
- Reorganizar linhas.

### Regra

Temporizar não significa recuar sem critério.

O defensor deve controlar espaço, portador e opções de passe.

---

## 47. Quando evitar contra-pressão

A contra-pressão pode ser inadequada quando:

- O adversário recebe orientado.
- Existe grande espaço nas costas.
- Os jogadores estão afastados.
- Os pivôs foram ultrapassados.
- Os centrais estão em inferioridade.
- Não existem coberturas.
- A pressão exigiria abandonar espaços perigosos.

### Soluções possíveis

- Temporizar.
- Proteger corredor central.
- Recuperar posições.
- Controlar profundidade.
- Estabelecer bloco.

---

## 48. Recuperação dos alas

### Situação

Os alas estão altos no momento da perda.

### Objetivos

- Recuperar corredor exterior.
- Proteger profundidade.
- Apoiar central exterior.
- Reconstituir linha defensiva.

### Exemplo

1. ALA-E está projetado.
2. A equipa perde.
3. AE condiciona portador.
4. MC-E protege interior.
5. DCE controla espaço exterior.
6. ALA-E recupera.
7. A equipa reorganiza.

### Riscos

- Ala chegar tarde.
- Central exterior ser arrastado.
- Espaço entre centrais.
- Falta de cobertura.

---

## 49. Recuperação dos avançados exteriores

### Possibilidades

- Pressionar portador.
- Fechar linha interior.
- Recuperar para linha média.
- Condicionar passe exterior.
- Preparar bloco 5-4-1.

### Regra

Os avançados exteriores não devem permanecer necessariamente altos após perda.

O comportamento depende da possibilidade de pressão e da organização pretendida.

---

## 50. Recuperação do ponta de lança

### Funções possíveis

- Condicionar primeiro passe.
- Pressionar portador.
- Bloquear ligação central.
- Atrasar circulação.
- Preparar reorganização.

### Regra

O PL não deve perseguir adversários sem considerar a estrutura coletiva.

---

# PARTE VIII — PROTEÇÃO DOS TRÊS CENTRAIS

## 51. Estrutura de proteção 3+2

Uma organização ofensiva em 3-2-5 pode manter:

- Três centrais.
- Dois médios-centro.

### Objetivos

- Proteger centro.
- Controlar profundidade.
- Preparar reação.
- Recuperar segunda bola.

### Riscos

- Pivôs demasiado altos.
- Centrais afastados.
- Alas projetados.
- Espaço exterior.

### Regra

A presença de cinco jogadores atrás da linha avançada não garante equilíbrio.

---

## 52. Central exterior perante espaço nas costas do ala

### Situação

ALA-E está alto e o adversário recupera.

### Possibilidade

DCE ajusta para controlar corredor exterior.

### Exemplo

1. ALA-E perde.
2. AE condiciona portador.
3. MC-E protege interior.
4. DCE controla profundidade exterior.
5. DCC ajusta cobertura.
6. ALA-E recupera.

### Riscos

- DCE sair demasiado.
- Intervalo entre DCE e DCC.
- PL adversário atacar espaço.
- Falta de cobertura.

---

## 53. Central do meio na transição defensiva

### Funções possíveis

- Proteger eixo.
- Controlar profundidade.
- Cobrir central exterior.
- Ajustar linha.
- Controlar PL adversário.

### Regra

O DCC não deve ser considerado obrigatoriamente um líbero.

A função depende do modelo de jogo e da situação.

---

## 54. Dois centrais exteriores perante corredores abertos

### Situação

Os dois alas estão projetados.

O adversário recupera e procura espaço exterior.

### Riscos

- Centrais exteriores obrigados a deslocamentos amplos.
- DCC isolado.
- Intervalos entre centrais.
- Passe diagonal adversário.

### Soluções possíveis

- Pivô proteger corredor interior.
- Central exterior temporizar.
- DCC controlar profundidade.
- Ala recuperar.
- Avançado exterior ajudar.

---

## 55. Linha defensiva e profundidade

### Fatores

- Pressão sobre portador.
- Orientação adversária.
- Distância à baliza.
- Velocidade dos atacantes.
- Cobertura.
- Posição do GR.
- Espaço nas costas.

### Regra

A linha defensiva não deve subir automaticamente após perda.

A altura deve responder ao controlo da bola e à ameaça de profundidade.

---

# PARTE IX — TRANSIÇÕES CONTRA DIFERENTES SISTEMAS

## 56. 3-4-3 contra 4-4-2

### Transição ofensiva

Oportunidades possíveis:

- Explorar espaço exterior.
- Atacar intervalos entre lateral e central.
- Utilizar avançados exteriores.
- Encontrar PL.

### Transição defensiva

Riscos possíveis:

- Dois PL atacarem profundidade.
- Médio exterior explorar costas do ala.
- Central exterior ser atraído.
- Passe direto.

### Regra

Três centrais perante dois PL não garantem controlo automático.

---

## 57. 3-4-3 contra 4-3-3

### Transição ofensiva

Oportunidades possíveis:

- Explorar espaço nas costas dos laterais.
- Atacar profundidade.
- Utilizar diagonais.
- Encontrar avançados exteriores.

### Transição defensiva

Riscos possíveis:

- Três avançados perante três centrais.
- Dois pivôs perante três médios.
- Extremos atacarem espaço exterior.
- Inferioridade central.

### Soluções possíveis

- Pivô manter centro.
- Avançado exterior recuperar.
- Central exterior temporizar.
- Ala recuperar.

---

## 58. 3-4-3 contra 4-2-3-1

### Transição ofensiva

Oportunidades possíveis:

- Explorar espaço nas costas dos laterais.
- Atacar corredores interiores.
- Encontrar PL.
- Utilizar ala.

### Transição defensiva

Riscos possíveis:

- MO adversário receber entre linhas.
- Extremos atacarem profundidade.
- Pivôs ultrapassados.
- Espaço nas costas dos alas.

### Soluções possíveis

- Proteger centro.
- Controlar MO.
- Temporizar.
- Recuperar alas.
- Ajustar centrais.

---

## 59. 3-4-3 contra 3-5-2

### Transição ofensiva

Oportunidades possíveis:

- Explorar espaço nas costas dos alas.
- Atacar intervalos entre centrais.
- Utilizar diagonais.
- Criar superioridade local.

### Transição defensiva

Riscos possíveis:

- Dois PL atacarem profundidade.
- Três médios perante dois pivôs.
- Alas adversários explorarem largura.
- Centrais exteriores saírem sem cobertura.

### Soluções possíveis

- Proteger centro.
- Recuperar alas.
- Ajustar cobertura.
- Temporizar.

---

## 60. 3-4-3 contra 3-4-3

### Transição ofensiva

Oportunidades possíveis:

- Explorar espaço nas costas dos alas.
- Atacar diagonais.
- Criar vantagem dinâmica.
- Utilizar terceiro homem.

### Transição defensiva

Riscos possíveis:

- Três avançados perante três centrais.
- Alas altos.
- Pivôs ultrapassados.
- Duelos isolados.

### Soluções possíveis

- Manter equilíbrio.
- Controlar profundidade.
- Recuperar alas.
- Ajustar coberturas.

---

# PARTE X — CASOS PRÁTICOS

## 61. Caso A — Recuperação central e contra-ataque

**Situação:**

MC-E recupera em zona intermédia.

**Objetivo:** explorar espaço.

**Sequência possível:**

1. MC-E recupera.
2. PL ameaça profundidade.
3. AE procura diagonal.
4. AD oferece apoio.
5. MC-E identifica linha.
6. Procura passe ou condução.
7. A equipa progride.

**Se o adversário estiver equilibrado:**

Conservar pode ser preferível.

**Riscos:**

- Passe intercetado.
- Falta de apoio.
- Perda central.

---

## 62. Caso B — Recuperação exterior e ataque rápido

**Situação:**

ALA-E recupera junto à linha.

**Objetivo:** explorar corredor.

**Sequência possível:**

1. ALA-E recupera.
2. AE aproxima-se.
3. PL ataca profundidade.
4. MC-E oferece apoio.
5. ALA-E conduz ou passa.
6. A equipa procura progressão.

**Se o corredor estiver bloqueado:**

Pode circular por MC-E.

**Riscos:**

- Pressão lateral.
- Falta de apoio.
- Perda consecutiva.

---

## 63. Caso C — PL baixa e avançado exterior rompe

**Situação:**

MC-D recupera.

**Objetivo:** criar ligação e profundidade.

**Sequência possível:**

1. MC-D recupera.
2. PL aproxima-se.
3. AD inicia diagonal.
4. MC-D encontra PL.
5. PL procura AD.
6. AD ataca espaço.

**Se o central adversário acompanhar PL:**

Pode abrir espaço nas costas, sujeito à cobertura.

**Riscos:**

- PL pressionado.
- Passe intercetado.
- Falta de profundidade.

---

## 64. Caso D — Perda com os dois alas altos

**Situação:**

ALA-E e ALA-D estão projetados.

**Objetivo:** impedir contra-ataque.

**Sequência possível:**

1. A equipa perde.
2. Jogador próximo condiciona portador.
3. MC-E protege centro.
4. MC-D ajusta cobertura.
5. DCE e DCD controlam profundidade exterior.
6. DCC protege eixo.
7. Alas recuperam.

**Se a pressão inicial falhar:**

A equipa deve temporizar e reorganizar.

**Riscos:**

- Espaço nas costas dos alas.
- Centrais exteriores isolados.
- Intervalos.
- Passe diagonal.

---

## 65. Caso E — Perda no corredor interior

**Situação:**

AE perde entre linhas.

**Objetivo:** recuperar ou temporizar.

**Sequência possível:**

1. AE reage.
2. MC-E aproxima-se se existir possibilidade.
3. MC-D protege centro.
4. ALA-E controla exterior.
5. DCE ajusta.
6. DCC controla profundidade.

**Se o adversário receber orientado:**

Temporizar pode ser mais adequado.

**Riscos:**

- Passe vertical.
- Pivôs ultrapassados.
- Espaço central.

---

## 66. Caso F — Contra-pressão após cruzamento

**Situação:**

ALA-E cruza e o adversário recupera.

**Objetivo:** controlar segunda bola.

**Sequência possível:**

1. O adversário interceta.
2. AE aproxima-se se existir possibilidade.
3. MC-E controla zona frontal.
4. MC-D protege centro.
5. DCE controla espaço.
6. ALA-E inicia recuperação.

**Se o adversário sair da pressão:**

A equipa deve reorganizar.

**Riscos:**

- Muitos jogadores avançados.
- Espaço exterior.
- Pivôs ultrapassados.
- Contra-ataque.

---

## 67. Caso G — Recuperação baixa sob pressão

**Situação:**

DCC recupera perto da própria área.

**Objetivo:** sair da pressão.

**Sequência possível:**

1. DCC recupera.
2. MC-E oferece apoio.
3. DCE abre linha.
4. PL oferece referência.
5. DCC avalia pressão.
6. Procura passe seguro.
7. A equipa tenta progredir.

**Se o passe interior estiver bloqueado:**

Pode utilizar central exterior ou passe direto.

**Riscos:**

- Perda perto da baliza.
- Passe intercetado.
- Falta de segunda bola.

---

## 68. Caso H — Recuperação alta e finalização

**Situação:**

AD recupera perto da área adversária.

**Objetivo:** criar oportunidade.

**Sequência possível:**

1. AD recupera.
2. PL procura zona central.
3. AE aproxima-se.
4. ALA-D oferece apoio exterior.
5. AD avalia remate, passe ou condução.
6. A equipa procura finalização.

**Se não existir oportunidade:**

Conservar e reorganizar.

**Riscos:**

- Remate precipitado.
- Passe intercetado.
- Perda consecutiva.

---

## 69. Caso I — Contra-ataque adversário pelo corredor exterior

**Situação:**

A equipa perde e o adversário ataca nas costas do ALA-E.

**Objetivo:** controlar progressão.

**Sequência possível:**

1. ALA-E inicia recuperação.
2. DCE ajusta exterior.
3. MC-E protege corredor interior.
4. DCC controla profundidade central.
5. AE recupera se possível.
6. A equipa procura temporizar.

**Se DCE for ultrapassado:**

DCC deve ajustar cobertura, preservando o controlo do eixo.

**Riscos:**

- Central exterior isolado.
- Espaço entre centrais.
- Cruzamento.
- Passe atrasado.

---

## 70. Caso J — Contra-ataque com mudança de corredor

**Situação:**

A equipa recupera à esquerda e encontra espaço à direita.

**Objetivo:** explorar lado contrário.

**Sequência possível:**

1. MC-E recupera.
2. AE oferece apoio.
3. MC-D aproxima-se.
4. ALA-D mantém largura.
5. MC-E procura MC-D.
6. MC-D procura ALA-D.
7. ALA-D progride.

**Se o adversário recuperar posição:**

A equipa pode conservar.

**Riscos:**

- Mudança lenta.
- Passe intercetado.
- Falta de apoio.

---

## 71. Caso K — Contra-pressão ultrapassada

**Situação:**

A equipa tenta recuperar imediatamente, mas o adversário encontra passe vertical.

**Objetivo:** evitar finalização.

**Sequência possível:**

1. A pressão é ultrapassada.
2. MC-D protege eixo.
3. DCC controla profundidade.
4. DCE e DCD ajustam.
5. Alas recuperam.
6. Avançados exteriores regressam.
7. A equipa procura estabelecer bloco.

**Se o portador estiver livre e orientado:**

A linha defensiva deve considerar a ameaça de passe nas costas.

**Riscos:**

- Pivôs ultrapassados.
- Centrais expostos.
- Espaço exterior.
- Falta de comunicação.

---

## 72. Caso L — Recuperação perante adversário desequilibrado

**Situação:**

O adversário possui vários jogadores à frente da bola.

**Objetivo:** explorar espaço disponível.

**Sequência possível:**

1. DCE recupera.
2. MC-E oferece primeira ligação.
3. PL fixa centrais.
4. AE inicia diagonal.
5. AD mantém alternativa.
6. MC-E procura progressão.
7. A equipa ataca espaço.

**Se a primeira ligação não estiver disponível:**

Conservar ou utilizar alternativa.

**Riscos:**

- Passe forçado.
- Falta de apoio.
- Perda consecutiva.
- Exposição defensiva.

---

# PARTE XI — ERROS FREQUENTES

## 73. Erros nas transições do 3-4-3

### 73.1. Acelerar sempre após recuperação

Pode provocar perdas desnecessárias.

### 73.2. Contra-pressionar sempre após perda

Pode expor a equipa.

### 73.3. Projetar os dois alas sem avaliar equilíbrio

Pode abrir os corredores exteriores.

### 73.4. Ambos os pivôs acompanharem o ataque

Pode deixar o centro desprotegido.

### 73.5. Os três avançados atacarem a mesma zona

Reduz complementaridade.

### 73.6. PL baixar sem movimento de profundidade

Pode eliminar ameaça nas costas.

### 73.7. Avançados exteriores permanecerem sempre altos

Pode dificultar reorganização.

### 73.8. Central exterior sair sem cobertura

Pode abrir espaço central.

### 73.9. DCC abandonar eixo sem compensação

Pode expor a baliza.

### 73.10. Ignorar primeira ligação

Pode impedir progressão.

### 73.11. Ignorar segunda bola

Pode provocar perda consecutiva.

### 73.12. Confundir velocidade com eficácia

Uma ação rápida não é necessariamente melhor.

### 73.13. Ignorar orientação do portador

Pode levar a recomendações impossíveis.

### 73.14. Ignorar a recuperação dos alas

Pode deixar corredores exteriores livres.

### 73.15. Ignorar proteção central

Pode permitir contra-ataque direto.

---

# PARTE XII — CRITÉRIOS PARA A IA

## 74. Perguntas obrigatórias

Antes de recomendar uma solução de transição, a IA deve verificar:

1. A equipa recuperou ou perdeu a bola?
2. Onde ocorreu a mudança de posse?
3. Qual era a estrutura anterior?
4. Qual é a estrutura atual?
5. O portador está pressionado?
6. O portador está orientado?
7. Existem linhas de passe?
8. Existe espaço para condução?
9. Existe possibilidade de progressão?
10. Existe superioridade numérica?
11. Existe superioridade funcional?
12. Existe vantagem qualitativa documentada?
13. Existe vantagem dinâmica?
14. Onde está o PL?
15. Onde estão AE e AD?
16. Onde estão os alas?
17. Como estão organizados os pivôs?
18. Quem oferece apoio?
19. Quem oferece profundidade?
20. Quem oferece largura?
21. Quem protege centro?
22. Quem controla profundidade?
23. Existe possibilidade de contra-ataque?
24. Existe possibilidade de conservação?
25. Existe possibilidade de contra-pressão?
26. Existe necessidade de temporização?
27. Existem coberturas?
28. O adversário está equilibrado?
29. O adversário pode explorar espaço exterior?
30. O adversário pode explorar espaço interior?
31. Qual é o risco da decisão?
32. Existe alternativa?

---

## 75. Classificação das soluções

### Solução fundamentada

Respeita:

- Momento da mudança de posse.
- Estrutura real.
- Orientação do portador.
- Linhas disponíveis.
- Movimentos.
- Coberturas.
- Equilíbrio.
- Continuidade.

### Solução condicionada

Depende de:

- Reação adversária.
- Movimento ainda não confirmado.
- Espaço disponível.
- Cobertura adicional.
- Capacidade individual.

### Solução contraditória

Exige:

- Passe por linha bloqueada.
- Jogador ocupar posições incompatíveis.
- Ala projetar-se sem considerar ameaça evidente.
- Pivôs abandonarem centro sem compensação.
- Central sair sem cobertura.
- Contra-pressão sem possibilidade de intervenção.
- Superioridade inexistente.

### Informação insuficiente

Faltam dados para avaliar a decisão.

---

## 76. Regras de interpretação para a IA

- Não assumir que toda a recuperação exige contra-ataque.
- Não assumir que toda a perda exige contra-pressão.
- Não assumir que os três avançados estão sempre disponíveis.
- Não assumir que os alas devem atacar imediatamente.
- Não assumir que os alas devem recuar sempre da mesma forma.
- Não assumir que o PL deve baixar ou romper obrigatoriamente.
- Não assumir que dois pivôs garantem proteção suficiente.
- Não assumir que três centrais garantem equilíbrio automático.
- Não recomendar passe vertical sem linha disponível.
- Não recomendar condução sem avaliar pressão.
- Não recomendar mudança de corredor sem avaliar tempo e continuidade.
- Não recomendar contra-pressão sem coberturas.
- Não recomendar central exterior sair sem avaliar profundidade.
- Não assumir que DCC é obrigatoriamente líbero.
- Não assumir que igualdade numérica significa igualdade funcional.
- Não ignorar a orientação do portador.
- Não ignorar a posição do adversário.
- Não ignorar a segunda bola.
- Não ignorar os corredores interiores.
- Não ignorar os espaços nas costas dos alas.
- Não ignorar a proteção central.
- Não atribuir capacidades individuais sem informação documentada.
- Explicar condições, movimentos, reações adversárias, riscos e alternativas.
- Distinguir conhecimento universal de instruções específicas da equipa.
- Quando faltarem dados, apresentar hipóteses condicionais.

---

## 77. Relação com outros documentos

### Fundamentos

- `conhecimento/fundamentos/fases_jogo.md`
- `conhecimento/fundamentos/principios_ofensivos.md`
- `conhecimento/fundamentos/principios_defensivos.md`
- `conhecimento/fundamentos/superioridades.md`
- `conhecimento/fundamentos/modelos_jogo.md`

### Sistema 3-4-3

- `conhecimento/sistemas/343/organizacao.md`
- `conhecimento/sistemas/343/saida_bola.md`
- `conhecimento/sistemas/343/ataque.md`
- `conhecimento/sistemas/343/defesa.md`

### Outros sistemas

- `conhecimento/sistemas/352/transicoes.md`
- `conhecimento/sistemas/433/transicoes.md`
- `conhecimento/sistemas/4231/transicoes.md`

---

## 78. Princípio final

As transições no 3-4-3 dependem da capacidade coletiva de reconhecer rapidamente as condições criadas pela recuperação ou perda da bola.

Na transição ofensiva, os três avançados podem oferecer profundidade, apoio e diferentes direções de progressão.

Os alas podem explorar largura e espaço exterior, mas devem considerar o equilíbrio coletivo.

O duplo pivô pode facilitar a primeira ligação e sustentar o ataque, mantendo proteção adequada.

Os três centrais podem iniciar progressão e controlar profundidade.

Na transição defensiva, a equipa deve decidir entre contra-pressionar, temporizar e reorganizar.

Os jogadores próximos da bola podem procurar recuperação, enquanto os restantes protegem espaços, linhas de passe e profundidade.

A eficácia das transições não depende apenas da velocidade.

Depende da qualidade da primeira decisão, da coordenação dos movimentos, da disponibilidade de apoios, do equilíbrio coletivo e da capacidade de adaptação ao adversário.

O assistente de IA deve interpretar as transições no 3-4-3 como processos dinâmicos e condicionais, explicando quando acelerar, quando conservar, quando pressionar, quando temporizar e como proteger a equipa perante os riscos existentes.