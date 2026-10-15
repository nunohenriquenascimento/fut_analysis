# Análise de Vulnerabilidades Adversárias — Diagnóstico, Priorização e Recomendações Táticas

## 1. Objetivo do documento

Este documento define um método sistemático para analisar vulnerabilidades táticas dos adversários no futebol.

O objetivo é permitir que um assistente de inteligência artificial transforme observações do jogo em diagnósticos e recomendações que possam ser utilizados pela equipa técnica.

A análise deve considerar:

- Estrutura nominal e organização real.
- Fases e momentos do jogo.
- Princípios ofensivos e defensivos.
- Comportamentos individuais e coletivos.
- Ocupação e controlo dos espaços.
- Relações entre jogadores e setores.
- Superioridades e inferioridades.
- Padrões repetidos.
- Qualidade da evidência.
- Capacidade da própria equipa para explorar a situação.
- Risco associado à solução proposta.

Uma vulnerabilidade não é simplesmente um espaço vazio, um jogador isolado ou uma inferioridade numérica.

É uma condição observável que pode aumentar a probabilidade de o adversário ser ultrapassado, perder o controlo de uma zona ou conceder uma oportunidade, desde que a equipa atacante consiga explorá-la.

**Princípio fundamental:**

A IA deve distinguir sempre entre:

1. Espaço aparentemente disponível.
2. Fragilidade potencial.
3. Vulnerabilidade observada.
4. Vulnerabilidade repetida.
5. Vulnerabilidade explorável pela própria equipa.
6. Vulnerabilidade efetivamente explorada.

Estas classificações não são equivalentes.

---

# PARTE I — FUNDAMENTOS DA ANÁLISE

## 2. O que é uma vulnerabilidade tática?

Uma vulnerabilidade tática é uma condição individual, coletiva, espacial ou temporal que pode comprometer a eficácia de uma organização perante determinadas ações adversárias.

Pode resultar de:

- Posicionamento.
- Distâncias.
- Orientação corporal.
- Falta de cobertura.
- Falta de coordenação.
- Atraso de reação.
- Dificuldade de deslocamento.
- Inferioridade funcional.
- Erro técnico recorrente.
- Problema de comunicação.
- Desajustamento estrutural.
- Comportamento previsível.

### Exemplo

Um lateral adversário sobe frequentemente sem cobertura.

Isto constitui uma fragilidade potencial.

Torna-se uma vulnerabilidade explorável quando:

- Existe espaço nas suas costas.
- A recuperação defensiva é insuficiente.
- A equipa atacante consegue chegar à zona.
- Existe um jogador capaz de atacar a profundidade.
- O risco da ação é aceitável.

### Regra para a IA

Não transformar automaticamente uma observação isolada numa conclusão definitiva.

---

## 3. Vulnerabilidade estrutural

Resulta da forma como a equipa ocupa e organiza o espaço.

### Exemplos possíveis

- Dois médios perante três referências interiores.
- Grande distância entre lateral e central.
- Espaço entre linhas.
- Ala sem cobertura.
- Última linha exposta.
- Falta de presença numa zona de segunda bola.

### Regra

Uma inferioridade estrutural pode ser compensada por posicionamento, pressão, coberturas ou capacidade individual.

---

## 4. Vulnerabilidade comportamental

Resulta de padrões de decisão ou execução.

### Exemplos

- Central abandona frequentemente a posição.
- Médio não acompanha movimentos.
- Extremo demora a recuperar.
- Lateral pressiona sem cobertura.
- Avançado não condiciona o pivô.
- Linha defensiva reage tarde à profundidade.

### Regra

A IA deve procurar repetição e contexto antes de concluir que o comportamento é habitual.

---

## 5. Vulnerabilidade individual

Está associada a dificuldades observadas de um jogador.

### Exemplos

- Dificuldade perante mudanças de direção.
- Receção sob pressão.
- Passe com o pé menos utilizado.
- Controlo da profundidade.
- Duelos aéreos.
- Orientação corporal.
- Recuperação após ultrapassagem.

### Regra

Não inferir capacidades individuais apenas pela posição, idade, altura ou aparência.

---

## 6. Vulnerabilidade coletiva

Resulta da interação inadequada entre jogadores.

### Exemplos

- Pressão sem cobertura.
- Linhas demasiado afastadas.
- Basculação descoordenada.
- Falha na passagem de marcação.
- Contra-pressão incompleta.
- Má proteção de segundas bolas.

### Regra

Uma dificuldade coletiva não deve ser atribuída automaticamente a um único jogador.

---

## 7. Vulnerabilidade espacial

Está associada a zonas insuficientemente controladas.

### Exemplos

- Espaço entre linhas.
- Corredor interior desprotegido.
- Intervalo entre central e lateral.
- Espaço nas costas do ala.
- Zona frontal da área.
- Segundo poste.
- Espaço nas costas da última linha.

### Regra

Espaço livre não significa necessariamente espaço acessível.

---

## 8. Vulnerabilidade temporal

Surge durante um intervalo limitado de tempo.

### Exemplos

- Após perda da bola.
- Durante mudança de corredor.
- Após saída de um central.
- Durante recuperação do lateral.
- Depois de uma pressão ultrapassada.
- Após um cruzamento afastado.

### Regra

A IA deve identificar quando a vulnerabilidade aparece e durante quanto tempo permanece explorável.

---

## 9. Vulnerabilidade técnica

Resulta de dificuldades de execução observadas.

### Exemplos

- Primeiro toque inconsistente.
- Passes pressionados imprecisos.
- Alívios frequentes para zonas perigosas.
- Dificuldade em receber orientado.
- Erros recorrentes de temporização.

### Regra

Um erro isolado não comprova uma limitação técnica permanente.

---

## 10. Vulnerabilidade física

Pode estar relacionada com dificuldades observáveis de:

- Aceleração.
- Velocidade.
- Resistência.
- Mudança de direção.
- Capacidade de repetição de esforços.
- Disputa física.

### Regra

A IA não deve diagnosticar fadiga, lesões ou limitações físicas sem informação suficiente.

Deve descrever o comportamento observado.

---

## 11. Vulnerabilidade contextual

Uma fragilidade pode surgir apenas em determinadas condições.

### Exemplos

- Adversário em vantagem.
- Adversário em desvantagem.
- Pressão alta.
- Bloco baixo.
- Inferioridade numérica.
- Substituições.
- Alteração de sistema.
- Final do jogo.

### Regra

Não generalizar uma vulnerabilidade identificada num contexto para todos os momentos do jogo.

---

# PARTE II — RECOLHA E QUALIDADE DA EVIDÊNCIA

## 12. Fontes de informação

A análise pode utilizar:

- Observação direta.
- Vídeo.
- Eventos de jogo.
- Dados posicionais.
- Estatísticas.
- Relatórios técnicos.
- Registos de scouting.
- Observações dos treinadores.

Cada fonte possui limitações próprias.

### Regra

A IA deve identificar a origem da informação sempre que possível.

---

## 13. Observação direta

Permite identificar:

- Comportamentos.
- Comunicação.
- Ajustamentos.
- Relações entre setores.
- Reações à bola.
- Movimentos sem bola.

### Limitações

- Ângulo de observação.
- Atenção seletiva.
- Falta de repetição.
- Dificuldade em acompanhar todos os jogadores.

---

## 14. Análise de vídeo

Permite:

- Rever sequências.
- Confirmar movimentos.
- Identificar padrões.
- Comparar situações.
- Avaliar decisões.

### Limitações

- Câmara pode não mostrar todo o campo.
- Movimentos fora da imagem podem ser desconhecidos.
- O vídeo pode não revelar instruções táticas.

### Regra

Não inferir a posição de jogadores fora do enquadramento.

---

## 15. Estatísticas

Podem ajudar a identificar:

- Zonas de perda.
- Frequência de cruzamentos.
- Recuperações.
- Remates concedidos.
- Passes progressivos.
- Duelos.
- Transições.

### Regra

Uma estatística isolada não explica necessariamente a causa tática.

---

## 16. Eventos de jogo

Os eventos permitem analisar:

- Perdas.
- Recuperações.
- Passes.
- Remates.
- Cruzamentos.
- Faltas.
- Interceções.

### Limitação

Sem informação posicional ou vídeo, pode ser impossível confirmar a organização coletiva.

---

## 17. Observação única

Uma ocorrência isolada pode justificar uma hipótese.

### Exemplo

Um central sai da posição e deixa espaço.

### Classificação

Fragilidade potencial, ainda não confirmada como padrão.

### Regra

Não atribuir elevada confiança apenas por existir um exemplo.

---

## 18. Observações repetidas

A repetição de um comportamento em situações comparáveis reforça a hipótese.

### Verificar

- Número de ocorrências.
- Número de oportunidades.
- Contextos.
- Resposta adversária.
- Consequências.
- Contraexemplos.

### Regra

A frequência deve ser relacionada com as oportunidades de ocorrência.

---

## 19. Contraexemplos

Uma análise rigorosa deve procurar situações em que a vulnerabilidade não surgiu.

### Exemplo

O lateral sobe frequentemente, mas o médio cobre corretamente em várias situações.

### Consequência

A vulnerabilidade pode depender da ausência pontual de cobertura, não da subida do lateral.

---

## 20. Informação insuficiente

A IA deve declarar informação insuficiente quando:

- Não existe vídeo ou descrição adequada.
- A estrutura é desconhecida.
- Não se conhecem as coberturas.
- Não existe evidência de repetição.
- Não se observa o lado contrário.
- Não é possível avaliar o risco.
- A própria equipa não tem capacidades conhecidas para executar a solução.

### Regra

Não inventar observações para completar o diagnóstico.

---

# PARTE III — IDENTIFICAÇÃO POR FASE DO JOGO

## 21. Organização ofensiva adversária

A análise deve identificar:

- Estrutura de construção.
- Ocupação dos corredores.
- Relação entre médios.
- Profundidade.
- Movimentos de apoio.
- Projeção de laterais ou alas.
- Equilíbrio preventivo.

### Vulnerabilidades possíveis

- Espaço após subida dos laterais.
- Pivô isolado.
- Centrais afastados.
- Falta de cobertura.
- Previsibilidade na circulação.

---

## 22. Primeira fase de construção

### Observar

- GR.
- Centrais.
- Laterais.
- Pivôs.
- Linhas de passe.
- Orientação corporal.
- Apoios.

### Vulnerabilidades possíveis

- Central sem linha interior.
- Pivô marcado.
- Lateral isolado.
- GR com poucas soluções.
- Construção previsível.

### Soluções possíveis

- Condicionar passe.
- Pressionar após gatilho.
- Fechar apoio interior.
- Orientar circulação.

### Regra

Pressão alta só deve ser recomendada se a própria equipa conseguir coordenar pressão e cobertura.

---

## 23. Segunda fase de construção

### Observar

- Progressão dos centrais.
- Posicionamento dos médios.
- Relação com avançados.
- Ocupação entre linhas.
- Apoios interiores.

### Vulnerabilidades possíveis

- Médio isolado.
- Espaço após condução.
- Passe vertical previsível.
- Falta de apoio ao portador.

---

## 24. Organização ofensiva no último terço

### Observar

- Ocupação da área.
- Extremos.
- Laterais ou alas.
- Médios de chegada.
- Movimentos de rutura.
- Equilíbrio defensivo.

### Vulnerabilidades possíveis

- Poucos jogadores na cobertura.
- Corredor contrário desprotegido.
- Espaço atrás dos laterais.
- Dependência de um único criador.

---

## 25. Organização defensiva adversária

A IA deve identificar:

- Altura do bloco.
- Estrutura real.
- Compactação.
- Referências de marcação.
- Gatilhos de pressão.
- Coberturas.
- Proteção central.
- Controlo da profundidade.

### Regra

O sistema nominal não determina automaticamente o comportamento defensivo.

---

## 26. Pressão alta adversária

### Vulnerabilidades possíveis

- Espaço nas costas da primeira linha.
- Central exterior livre.
- Médio entre linhas.
- Profundidade nas costas.
- Pressão sem cobertura.
- Descoordenação após mudança de corredor.

### Soluções possíveis

- Terceiro homem.
- Atrair e ultrapassar.
- Mudança de corredor.
- Passe direto condicionado.
- Movimento de apoio e rutura.

---

## 27. Bloco médio adversário

### Vulnerabilidades possíveis

- Espaço entre linhas.
- Corredor contrário.
- Espaço após saída do médio.
- Central livre para conduzir.
- Armadilha lateral ultrapassável.

### Soluções possíveis

- Circulação.
- Condução.
- Fixar e libertar.
- Terceiro homem.
- Mudança de corredor.
- Combinação exterior.

---

## 28. Bloco baixo adversário

### Vulnerabilidades possíveis

- Entrada da área.
- Segundo poste.
- Espaço após deslocamento.
- Passe atrasado.
- Intervalos entre defensores.
- Dificuldade em sair após recuperação.

### Soluções possíveis

- Mobilidade.
- Largura.
- Mudança de corredor.
- Combinações curtas.
- Passe atrasado.
- Cruzamento condicionado.
- Remate exterior condicionado.
- Segunda bola.

---

## 29. Transição ofensiva adversária

### Observar

- Primeiro passe após recuperação.
- Jogadores preparados para sair.
- Direção preferencial.
- Movimentos de profundidade.
- Apoios.
- Velocidade de decisão.

### Vulnerabilidades possíveis

- Falta de apoio ao primeiro recetor.
- Dependência de um corredor.
- Passe previsível.
- Jogador isolado.
- Pouca continuidade.

### Soluções defensivas possíveis

- Condicionar primeira ligação.
- Proteger centro.
- Temporizar.
- Controlar profundidade.
- Recuperar organização.

---

## 30. Transição defensiva adversária

### Observar

- Reação após perda.
- Contra-pressão.
- Cobertura.
- Distâncias.
- Jogadores projetados.
- Proteção central.

### Vulnerabilidades possíveis

- Falta de cobertura.
- Laterais ou alas altos.
- Pivô ultrapassado.
- Centrais isolados.
- Espaço para contra-ataque.

### Soluções possíveis

- Primeiro passe seguro.
- Ataque à profundidade.
- Mudança de corredor.
- Explorar superioridade.
- Temporizar se não existir vantagem.

---

# PARTE IV — VULNERABILIDADES ESPACIAIS

## 31. Espaço entre linhas

### Identificação

Existe distância entre médios e defesas que permite potencial receção.

### Verificar

- Linha de passe.
- Pressão sobre portador.
- Orientação do recetor.
- Cobertura.
- Continuidade.

### Exploração possível

- MO.
- Interior.
- PL que baixa.
- Extremo interior.
- Terceiro homem.

---

## 32. Intervalo entre central e lateral

### Identificação

Existe espaço entre dois defensores da última linha.

### Causas possíveis

- Lateral sobe.
- Central desloca.
- Falha de compactação.
- Movimento de arrastamento.

### Exploração possível

- Rutura diagonal.
- Movimento do PL.
- Entrada do extremo.
- Passe vertical.

### Riscos

- Cobertura do central.
- Fora de jogo.
- GR controlar profundidade.

---

## 33. Espaço nas costas do lateral

### Identificação

Lateral projeta-se ou abandona posição.

### Verificar

- Médio cobre?
- Central exterior ajusta?
- Extremo recupera?
- Existe linha de passe?
- Existe jogador para atacar?

### Exploração possível

- Passe em profundidade.
- Diagonal.
- Contra-ataque.
- Mudança de corredor.

---

## 34. Espaço nas costas do ala

### Identificação

Ala encontra-se alto e existe espaço no corredor exterior.

### Exploração possível

- Extremo em profundidade.
- PL a deslocar-se.
- Passe diagonal.
- Transição rápida.

### Riscos

- Central exterior cobrir.
- Médio recuperar.
- Ala regressar.
- Passe intercetado.

---

## 35. Espaço nas costas da última linha

### Identificação

A linha defensiva encontra-se suficientemente avançada para existir profundidade explorável.

### Condições

- Portador com tempo.
- Linha de passe.
- Movimento de rutura.
- Velocidade relativa.
- Controlo do fora de jogo.

### Regra

Não recomendar automaticamente passe longo.

---

## 36. Espaço frontal à área

### Identificação

Existe espaço para receber ou rematar à entrada da área.

### Verificar

- Linha de remate.
- Pressão.
- Distância.
- Orientação.
- Capacidade individual.
- Ressaltos.

### Exploração possível

- Remate exterior.
- Passe para área.
- Combinação.
- Terceiro homem.

---

## 37. Segundo poste

### Identificação

O lado contrário à bola apresenta possível inferioridade defensiva.

### Verificar

- Lateral contrário.
- Central.
- GR.
- Movimento do atacante.
- Qualidade do cruzamento.

### Regra

Não assumir que o segundo poste está livre apenas porque o bloco se deslocou.

---

## 38. Corredor contrário

### Identificação

A organização defensiva concentra-se no lado da bola.

### Exploração possível

- Mudança de corredor.
- Passe diagonal.
- Circulação rápida.
- Receção orientada.

### Riscos

- Adversário deslocar.
- Passe lento.
- Recetor pressionado.
- Falta de continuidade.

---

# PARTE V — VULNERABILIDADES ESTRUTURAIS

## 39. Inferioridade numérica central

### Exemplo

Dois médios adversários enfrentam três referências interiores.

### Verificar

- Posicionamento real.
- Pressão dos avançados.
- Coberturas.
- Capacidade de acesso.
- Superioridade funcional.

### Regra

Três contra dois não garante jogador livre.

---

## 40. Inferioridade numérica exterior

### Exemplo

Um lateral enfrenta extremo e lateral projetado.

### Verificar

- Médio exterior recupera?
- Central cobre?
- Existe espaço?
- Existe linha de passe?

### Exploração possível

- Sobreposição.
- Desmarcação interior.
- Triângulo.
- Terceiro homem.

---

## 41. Central exterior exposto

### Situação

Equipa adversária utiliza três centrais e um central exterior fica isolado.

### Exploração possível

- Movimento diagonal.
- Ataque ao intervalo.
- PL a arrastar.
- Extremo em profundidade.

### Riscos

- Central central cobrir.
- Ala recuperar.
- Médio compensar.

---

## 42. Pivô isolado

### Situação

O médio defensivo tem muitas zonas ou referências para controlar.

### Exploração possível

- Movimentos alternados.
- MO entre linhas.
- PL a baixar.
- Terceiro homem.
- Rotação dos médios.

### Regra

Não assumir incapacidade do pivô sem observar as suas coberturas.

---

## 43. Primeira linha ultrapassável

### Situação

A primeira linha de pressão deixa espaço ou linhas disponíveis.

### Exploração possível

- Condução.
- Passe interior.
- Terceiro homem.
- Mudança de corredor.

### Riscos

- Armadilha.
- Pressão sobre receção.
- Passe intercetado.

---

## 44. Última linha sem cobertura

### Situação

Um defensor sai e os restantes não compensam.

### Exploração possível

- Movimento de rutura.
- Passe no intervalo.
- Ataque à profundidade.

### Regra

Confirmar se existe cobertura do GR ou de outro defensor.

---

## 45. Assimetria adversária

### Situação

O adversário ocupa os dois lados de forma diferente.

### Exemplos

- Um lateral sobe mais.
- Um extremo recupera menos.
- Um médio desloca-se preferencialmente.
- Um ala mantém maior altura.

### Exploração possível

- Atacar lado exposto.
- Atrair e mudar.
- Criar superioridade.

### Regra

Assimetria não é automaticamente um defeito.

---

# PARTE VI — VULNERABILIDADES COMPORTAMENTAIS

## 46. Pressão descoordenada

### Sinais

- Primeiro jogador pressiona.
- Restantes mantêm posição.
- Linha de passe permanece aberta.
- Cobertura chega tarde.

### Exploração possível

- Passe para jogador livre.
- Terceiro homem.
- Condução após ultrapassar pressão.

---

## 47. Basculação lenta

### Sinais

- Bloco desloca-se tarde.
- Jogador contrário recebe livre.
- Distâncias aumentam.
- Cobertura demora.

### Exploração possível

- Mudança de corredor.
- Passe diagonal.
- Circulação rápida.

---

## 48. Central que abandona a linha

### Sinais

- Sai frequentemente à marcação.
- Deixa espaço.
- Cobertura insuficiente.

### Exploração possível

- PL em apoio.
- Segundo PL em rutura.
- Movimento diagonal.
- Terceiro homem.

---

## 49. Lateral agressivo sem cobertura

### Sinais

- Salta à pressão.
- Central não aproxima.
- Médio não recupera.
- Espaço fica disponível.

### Exploração possível

- Passe nas costas.
- Um-dois.
- Movimento diagonal.
- Sobreposição.

---

## 50. Médio que não acompanha

### Sinais

- Perde referência.
- Reage tarde.
- Permite receção.
- Não cobre saída de colega.

### Exploração possível

- Movimento entre linhas.
- Terceiro homem.
- Rotação.
- Entrada na área.

### Regra

Confirmar se a responsabilidade pertence realmente ao médio.

---

## 51. Dificuldade na defesa de cruzamentos

### Sinais

- Jogador livre na área.
- Mau controlo do primeiro poste.
- Segundo poste desprotegido.
- Falha de comunicação.
- Ressaltos concedidos.

### Exploração possível

- Cruzamento direcionado.
- Movimento sincronizado.
- Passe atrasado.
- Ataque à segunda bola.

---

## 52. Dificuldade na defesa de passes atrasados

### Sinais

- Médios recuam demasiado.
- Entrada da área fica livre.
- Defesas concentram-se junto à baliza.
- Jogador chega sem marcação.

### Exploração possível

- Linha de fundo.
- Passe atrasado.
- Entrada de médio.
- Remate.

---

## 53. Dificuldade na reação à perda

### Sinais

- Jogadores afastados.
- Sem pressão imediata.
- Cobertura insuficiente.
- Corredor central aberto.

### Exploração possível

- Primeiro passe vertical.
- Ataque à profundidade.
- Mudança de corredor.
- Contra-ataque.

---

## 54. Dificuldade na reação à recuperação

### Sinais

- Primeiro passe previsível.
- Apoios afastados.
- PL isolado.
- Perda imediata.

### Exploração defensiva possível

- Condicionar primeira ligação.
- Fechar linha principal.
- Pressionar com cobertura.
- Recuperar segunda bola.

---

# PARTE VII — AVALIAÇÃO DA EXPLORABILIDADE

## 55. Vulnerabilidade e capacidade da própria equipa

Uma fragilidade adversária só deve originar uma recomendação operacional quando existe uma forma plausível de a explorar.

### Exemplo

O adversário deixa espaço nas costas da defesa.

A equipa pode não conseguir explorá-lo se:

- O portador está pressionado.
- Não existe movimento de rutura.
- O passe não está disponível.
- O recetor não possui vantagem.
- O risco de perda é elevado.

### Regra

A IA deve relacionar vulnerabilidades adversárias com recursos e capacidades demonstrados da própria equipa.

---

## 56. Superioridade numérica

Existe quando uma equipa possui mais jogadores numa determinada relação espacial.

### Regra

É necessário verificar se essa vantagem pode ser utilizada.

---

## 57. Superioridade posicional

Existe quando a ocupação do espaço cria uma vantagem de acesso ou relação sobre o adversário.

### Exemplo

Jogador entre linhas com linha de passe e continuidade.

---

## 58. Superioridade qualitativa

Existe quando uma característica relevante de um jogador oferece vantagem numa situação específica.

### Exemplos

- Velocidade em profundidade.
- Capacidade de drible.
- Qualidade de passe.
- Jogo aéreo.
- Remate exterior.

### Regra

A superioridade qualitativa deve ser baseada em evidência, não em pressupostos.

---

## 59. Superioridade dinâmica

Existe quando movimentos, tempos e trajetórias criam vantagem durante a ação.

### Exemplos

- Rutura sincronizada.
- Terceiro homem.
- Mudança de direção.
- Ataque ao espaço após saída defensiva.

---

## 60. Acessibilidade da vulnerabilidade

A IA deve avaliar:

1. Existe espaço?
2. Existe linha de passe?
3. O portador tem tempo?
4. O recetor consegue chegar?
5. Existe cobertura adversária?
6. Existe continuidade?
7. Existe equilíbrio após eventual perda?

### Regra

Uma vulnerabilidade inacessível não deve ser apresentada como oportunidade imediata.

---

## 61. Persistência

A vulnerabilidade pode ser:

- Pontual.
- Recorrente.
- Dependente de gatilho.
- Dependente do resultado.
- Dependente de determinado jogador.
- Dependente da fase do jogo.

### Regra

A persistência influencia a prioridade, mas não substitui a avaliação da gravidade.

---

## 62. Impacto potencial

A IA deve avaliar a consequência provável da exploração.

### Níveis qualitativos

**Baixo:** permite circulação ou ganho limitado de metros.

**Moderado:** permite progressão relevante ou entrada em zona ofensiva.

**Elevado:** pode gerar entrada na área ou oportunidade de finalização.

**Muito elevado:** pode gerar oportunidade clara de finalização ou impedir situação defensiva crítica.

### Regra

Estes níveis são classificações qualitativas, não probabilidades estatísticas.

---

## 63. Risco de exploração

A solução pode envolver:

- Perda central.
- Passe intercetado.
- Falta de cobertura.
- Contra-ataque.
- Exposição dos centrais.
- Inferioridade após perda.

### Classificação

- Baixo.
- Moderado.
- Elevado.
- Crítico.

### Regra

O risco deve ser avaliado separadamente do benefício potencial.

---

## 64. Custo tático

Uma solução pode exigir:

- Mudança de sistema.
- Alteração de funções.
- Maior projeção.
- Maior desgaste.
- Abandono de zonas.
- Coordenação complexa.

### Regra

A IA deve preferir, em condições semelhantes, soluções que respeitem as capacidades e os princípios da equipa.

---

# PARTE VIII — PRIORIZAÇÃO DAS VULNERABILIDADES

## 65. Critérios de prioridade

A IA deve considerar:

1. Evidência.
2. Repetição.
3. Persistência.
4. Acessibilidade.
5. Impacto potencial.
6. Capacidade da equipa.
7. Risco.
8. Custo tático.
9. Contexto do jogo.
10. Resposta provável do adversário.

---

## 66. Prioridade alta

Pode ser atribuída quando:

- Existe evidência consistente.
- A vulnerabilidade é acessível.
- A equipa possui recursos para explorar.
- O impacto é relevante.
- O risco é aceitável.

### Regra

Uma vulnerabilidade grave mas inacessível não deve receber automaticamente prioridade alta.

---

## 67. Prioridade média

Pode ser atribuída quando:

- Existe alguma evidência.
- A exploração depende de condições.
- O impacto é moderado ou elevado.
- Existem riscos controláveis.

---

## 68. Prioridade baixa

Pode ser atribuída quando:

- Existe pouca evidência.
- A exploração é difícil.
- O impacto é reduzido.
- O custo tático é elevado.
- O risco é desproporcionado.

---

## 69. Não recomendável

Uma solução deve ser rejeitada quando:

- Exige condições contraditórias.
- Não existe linha de passe.
- A vulnerabilidade não é acessível.
- O risco é inaceitável.
- Depende de capacidades não demonstradas.
- Elimina proteção defensiva essencial sem compensação.

---

## 70. Regra de priorização

A IA não deve utilizar uma fórmula numérica arbitrária como se representasse uma probabilidade real.

Pode usar uma matriz qualitativa para ordenar hipóteses, desde que:

- Os critérios sejam explícitos.
- A evidência seja identificada.
- A incerteza seja comunicada.
- O risco seja apresentado.
- A prioridade possa ser revista.

---

# PARTE IX — CONSTRUÇÃO DE RECOMENDAÇÕES

## 71. Estrutura de uma recomendação

Cada recomendação deve conter:

1. Vulnerabilidade identificada.
2. Evidência observada.
3. Condições de aparecimento.
4. Mecanismo de exploração.
5. Jogadores ou funções envolvidos.
6. Espaço pretendido.
7. Ação do portador.
8. Movimento sem bola.
9. Cobertura preventiva.
10. Resposta provável adversária.
11. Alternativa.
12. Risco.
13. Confiança.

---

## 72. Recomendações condicionais

A IA deve utilizar lógica condicional.

### Exemplo

**Se** o central adversário sair para acompanhar o PL que baixa,

**e se** não existir cobertura adequada,

**então** procurar rutura de outro jogador no espaço libertado.

**Caso contrário**, manter circulação e procurar outra forma de progressão.

---

## 73. Recomendações alternativas

Uma vulnerabilidade pode ser explorada por diferentes mecanismos.

### Exemplo

Espaço nas costas do lateral.

**Opção A:** passe direto em profundidade.

**Opção B:** combinação exterior e rutura.

**Opção C:** mudança de corredor.

### Regra

A escolha depende da pressão sobre a bola e das capacidades disponíveis.

---

## 74. Recomendações de baixo risco

Podem incluir:

- Circulação para deslocar.
- Apoio próximo.
- Mudança de corredor controlada.
- Condução com cobertura.
- Preparação da segunda bola.

### Regra

Baixo risco não significa ausência de risco.

---

## 75. Recomendações de risco elevado

Podem incluir:

- Passe vertical sob pressão.
- Projeção simultânea de vários jogadores.
- Ataque direto sem apoio.
- Condução central sem cobertura.

### Regra

Estas soluções exigem justificação contextual e avaliação do equilíbrio preventivo.

---

## 76. Recomendações durante o jogo

Devem ser:

- Curtas.
- Claras.
- Executáveis.
- Ligadas ao comportamento observado.
- Compatíveis com o modelo da equipa.

### Exemplo

"Quando o lateral deles saltar à pressão sem cobertura, procura a diagonal nas costas. Mantém um médio preparado para proteger a perda."

---

## 77. Recomendações para preparação do jogo

Podem incluir:

- Padrões de construção.
- Zonas de pressão.
- Movimentos de rutura.
- Combinações.
- Alterações posicionais.
- Exercícios específicos.

### Regra

A preparação deve distinguir hipóteses de padrões confirmados.

---

# PARTE X — ANÁLISE POR SISTEMA ADVERSÁRIO

## 78. Vulnerabilidades possíveis do 4-4-2

### Situações a observar

- Dois médios perante três referências interiores.
- Espaço entre linhas.
- Extremos a fechar por dentro.
- Lateral isolado.
- Dois PL afastados dos médios.

### Exploração possível

- Terceiro homem.
- Médio adicional.
- Mudança de corredor.
- Combinação exterior.
- Receção entre linhas.

### Regra

Nenhuma destas fragilidades é inerente a todos os 4-4-2.

---

## 79. Vulnerabilidades possíveis do 4-3-3

### Situações a observar

- Espaço nas costas dos laterais.
- Pivô isolado.
- Distância entre interiores.
- Extremos altos.
- Pressão sem cobertura.

### Exploração possível

- Transição exterior.
- Movimento entre linhas.
- Passe nas costas.
- Mudança de corredor.
- Terceiro homem.

---

## 80. Vulnerabilidades possíveis do 4-2-3-1

### Situações a observar

- Espaço entre duplo pivô e MO.
- Extremos sem recuperação.
- Laterais projetados.
- PL isolado.
- MO a abandonar cobertura central.

### Exploração possível

- Superioridade central.
- Passe vertical.
- Mudança de corredor.
- Ataque nas costas do lateral.
- Pressão sobre construção.

---

## 81. Vulnerabilidades possíveis do 3-5-2

### Situações a observar

- Espaço nas costas dos alas.
- Central exterior exposto.
- Distância entre alas e médios.
- Pivô sobrecarregado.
- Dificuldade em controlar largura.

### Exploração possível

- Mudança de corredor.
- Ataque exterior.
- Movimento diagonal.
- Transição nas costas do ala.
- Combinação interior-exterior.

---

## 82. Vulnerabilidades possíveis do 3-4-3

### Situações a observar

- Dois médios perante três referências.
- Espaço nas costas dos alas.
- Centrais exteriores expostos.
- Distância entre primeira linha e pivôs.
- Falta de cobertura após perda.

### Exploração possível

- Superioridade central.
- Terceiro homem.
- Ataque nas costas do ala.
- Mudança de corredor.
- Movimento entre linhas.

---

## 83. Vulnerabilidades possíveis de linhas de cinco

### Situações a observar

- Espaço exterior intermédio.
- Ala obrigado a sair.
- Central exterior deslocado.
- Espaço frontal.
- Dificuldade em pressionar construção.

### Exploração possível

- Fixar ala.
- Combinação exterior.
- Mudança de corredor.
- Passe atrasado.
- Remate exterior condicionado.

---

# PARTE XI — CASOS PRÁTICOS

## 84. Caso A — Lateral adversário sem cobertura

**Observação:** lateral sobe repetidamente e deixa espaço.

**Verificação:**

- Médio cobre?
- Central ajusta?
- Existe jogador para atacar?
- Existe passe disponível?

**Recomendação condicionada:**

Explorar profundidade no corredor quando a cobertura estiver ausente.

**Risco:** perda e transição adversária.

---

## 85. Caso B — Central sai da linha

**Observação:** central acompanha PL em apoio.

**Verificação:**

- Outro central cobre?
- Existe espaço?
- Existe rutura?
- Portador pode passar?

**Recomendação condicionada:**

Utilizar apoio do PL para atrair e rutura de segundo jogador.

**Risco:** fora de jogo ou passe intercetado.

---

## 86. Caso C — Dois médios perante três

**Observação:** adversário defende com dois médios centrais.

**Verificação:**

- Existe terceiro jogador livre?
- Avançados fecham linhas?
- Existe acesso?
- Médios adversários recebem cobertura?

**Recomendação condicionada:**

Criar superioridade funcional através de posicionamento e terceiro homem.

**Risco:** perda central.

---

## 87. Caso D — Pressão alta sem cobertura

**Observação:** PL pressiona central e médios não acompanham.

**Verificação:**

- Existe espaço atrás da pressão?
- Central tem tempo?
- Existe recetor?
- Há cobertura adversária?

**Recomendação condicionada:**

Ultrapassar primeira linha por passe ou condução.

**Risco:** armadilha ou interceção.

---

## 88. Caso E — Bloco médio desloca lentamente

**Observação:** adversário demora a ajustar após mudança de corredor.

**Verificação:**

- O comportamento é repetido?
- Existe recetor livre?
- O passe chega a tempo?
- Há continuidade?

**Recomendação condicionada:**

Atrair de um lado e mudar rapidamente para o outro.

**Risco:** mudança intercetada.

---

## 89. Caso F — Bloco baixo deixa entrada da área

**Observação:** médios recuam para dentro da área.

**Verificação:**

- Existe espaço frontal?
- Há linha de remate?
- Existe jogador com capacidade?
- Há cobertura para ressalto?

**Recomendação condicionada:**

Procurar passe atrasado ou remate exterior em condições favoráveis.

**Risco:** remate bloqueado e contra-ataque.

---

## 90. Caso G — Ala alto no 3-5-2

**Observação:** ala projeta-se e deixa espaço.

**Verificação:**

- Central exterior cobre?
- Médio recupera?
- Existe linha?
- Existe atacante disponível?

**Recomendação condicionada:**

Explorar espaço nas costas durante transição.

**Risco:** central exterior antecipar.

---

## 91. Caso H — Pivô isolado

**Observação:** pivô tem várias referências interiores.

**Verificação:**

- Existem apoios?
- Existe cobertura?
- O pivô mantém posição?
- Há acesso entre linhas?

**Recomendação condicionada:**

Criar movimentos alternados para gerar dilema.

**Risco:** congestionamento e perda central.

---

## 92. Caso I — Cruzamentos mal defendidos

**Observação:** adversário permite receções livres na área.

**Verificação:**

- Em que zona?
- Ocorre repetidamente?
- Qual é a origem?
- Existe vantagem de finalização?

**Recomendação condicionada:**

Atacar zona identificada com movimentos sincronizados.

**Risco:** cruzamento intercetado.

---

## 93. Caso J — Transição defensiva lenta

**Observação:** adversário demora a reorganizar após perda.

**Verificação:**

- Existe espaço?
- Existe portador orientado?
- Há apoio?
- Há profundidade?

**Recomendação condicionada:**

Acelerar primeira ligação e atacar espaço antes da reorganização.

**Risco:** perda imediata.

---

## 94. Caso K — Construção previsível

**Observação:** adversário utiliza repetidamente a mesma saída.

**Verificação:**

- É uma preferência ou imposição?
- Existem alternativas?
- Há cobertura?
- Qual é o gatilho?

**Recomendação condicionada:**

Preparar pressão orientada para a saída mais frequente.

**Risco:** adversário alterar construção e ultrapassar pressão.

---

## 95. Caso L — Segundo poste desprotegido

**Observação:** lateral contrário fecha demasiado ou perde referência.

**Verificação:**

- Central cobre?
- GR controla?
- Existe atacante?
- Cruzamento é possível?

**Recomendação condicionada:**

Atacar segundo poste quando existir vantagem real.

**Risco:** cruzamento bloqueado ou controlado.

---

# PARTE XII — REGRAS DE INTERPRETAÇÃO PARA A IA

## 96. Processo obrigatório de análise

A IA deve seguir a sequência:

**Observação → Contexto → Hipótese → Verificação → Vulnerabilidade → Explorabilidade → Risco → Recomendação → Confiança.**

### Passo 1 — Observação

Descrever o que aconteceu sem interpretar excessivamente.

### Passo 2 — Contexto

Identificar fase, zona, estrutura, resultado e circunstâncias relevantes.

### Passo 3 — Hipótese

Formular uma possível fragilidade.

### Passo 4 — Verificação

Procurar repetições, contraexemplos e coberturas.

### Passo 5 — Vulnerabilidade

Determinar se existe uma condição defensiva problemática.

### Passo 6 — Explorabilidade

Avaliar se a própria equipa pode aproveitá-la.

### Passo 7 — Risco

Identificar consequências da tentativa.

### Passo 8 — Recomendação

Propor ação concreta e alternativa.

### Passo 9 — Confiança

Comunicar qualidade e limites da evidência.

---

## 97. Perguntas obrigatórias

Antes de apresentar uma vulnerabilidade como explorável, a IA deve verificar:

1. Qual é a observação?
2. Qual é a fonte?
3. Qual é a fase do jogo?
4. Qual é a zona?
5. Qual é o sistema nominal?
6. Qual é a estrutura real?
7. O comportamento repetiu-se?
8. Quantas oportunidades existiram?
9. Existem contraexemplos?
10. Existe cobertura adversária?
11. Existe espaço?
12. Existe acesso?
13. Existe tempo?
14. Existe jogador capaz de explorar?
15. Existe continuidade?
16. Existe superioridade?
17. Qual é o impacto potencial?
18. Qual é o risco?
19. Qual é o custo tático?
20. Qual é a resposta provável adversária?
21. Existe alternativa?
22. Qual é o grau de confiança?
23. Que informação falta?

---

## 98. Classificação da evidência

### Evidência forte

- Observações repetidas e comparáveis.
- Contexto conhecido.
- Coberturas analisadas.
- Contraexemplos considerados.
- Comportamento consistente.

### Evidência moderada

- Algumas observações relevantes.
- Contexto parcialmente conhecido.
- Repetição limitada.
- Algumas incertezas.

### Evidência fraca

- Observação isolada.
- Contexto incompleto.
- Coberturas desconhecidas.
- Pouca informação.

### Informação insuficiente

- Não é possível formular conclusão defensável.

### Regra

Estas classificações não correspondem a percentagens estatísticas de confiança.

---

## 99. Classificação da vulnerabilidade

A IA deve distinguir:

**Hipótese:** possível fragilidade ainda não confirmada.

**Potencial:** condição identificada, mas exploração não demonstrada.

**Observada:** fragilidade reconhecida numa sequência.

**Recorrente:** fragilidade identificada em situações comparáveis.

**Explorável:** existe mecanismo plausível para a própria equipa.

**Explorada:** a equipa conseguiu aproveitar a condição numa situação concreta.

### Regra

Uma vulnerabilidade pode ser recorrente sem ser explorável pela equipa.

---

## 100. Classificação das recomendações

### Fundamentada

A solução possui evidência, acesso, capacidade e risco aceitável.

### Condicionada

Depende de circunstâncias que ainda devem ser verificadas.

### Contraditória

Exige condições incompatíveis com o contexto observado.

### Informação insuficiente

Não existem dados para recomendar com segurança.

---

## 101. Tratamento de informação contraditória

Quando existirem observações divergentes, a IA deve:

1. Identificar a contradição.
2. Comparar contextos.
3. Verificar alterações de sistema.
4. Considerar jogadores envolvidos.
5. Avaliar se houve adaptação adversária.
6. Reduzir a confiança quando necessário.
7. Evitar conclusões absolutas.

---

## 102. Atualização durante o jogo

As vulnerabilidades devem ser reavaliadas quando:

- O adversário altera sistema.
- Existe substituição.
- A altura do bloco muda.
- O adversário ajusta coberturas.
- O resultado altera comportamento.
- A equipa deixa de conseguir explorar a zona.
- Surgem novos padrões.

### Regra

Uma recomendação correta no início do jogo pode deixar de ser adequada mais tarde.

---

# PARTE XIII — MODELO DE RELATÓRIO

## 103. Ficha de vulnerabilidade

### Identificação

- Código da vulnerabilidade:
- Adversário:
- Jogo:
- Minuto ou intervalo:
- Fase do jogo:
- Zona:
- Sistema nominal:
- Estrutura real:

### Observação

- Comportamento observado:
- Fonte:
- Número de ocorrências:
- Número de oportunidades:
- Contraexemplos:
- Contexto:

### Diagnóstico

- Tipo de vulnerabilidade:
- Mecanismo causal provável:
- Cobertura adversária:
- Persistência:
- Classificação:
- Evidência:

### Explorabilidade

- Espaço:
- Linha de passe:
- Tempo disponível:
- Jogadores envolvidos:
- Capacidades necessárias:
- Impacto potencial:
- Risco:
- Custo tático:

### Recomendação

- Mecanismo:
- Movimentos:
- Ação do portador:
- Cobertura preventiva:
- Alternativa:
- Resposta provável adversária:

### Avaliação

- Prioridade:
- Confiança:
- Informação em falta:
- Necessidade de nova observação:

---

## 104. Relatório resumido para equipa técnica

O relatório deve apresentar, preferencialmente, as três vulnerabilidades mais relevantes quando existir evidência suficiente.

Para cada uma:

1. O que foi observado.
2. Porque pode ser uma vulnerabilidade.
3. Quando aparece.
4. Como explorar.
5. Quem deve intervir.
6. Qual é o risco.
7. Qual é a confiança.

### Regra

Não preencher artificialmente três vulnerabilidades se apenas uma estiver fundamentada.

---

## 105. Relatório durante o jogo

### Formato recomendado

**Observação:** o lateral direito adversário sobe e o médio não cobre.

**Hipótese:** espaço nas costas do lateral.

**Condição:** central exterior não compensa.

**Solução:** procurar diagonal do atacante nesse corredor quando o portador tiver tempo.

**Risco:** passe intercetado e perda da posse.

**Confiança:** moderada, após observações repetidas.

---

## 106. Relatório pós-jogo

Deve distinguir:

- Vulnerabilidades previstas.
- Vulnerabilidades confirmadas.
- Vulnerabilidades não confirmadas.
- Vulnerabilidades exploradas.
- Recomendações eficazes.
- Recomendações ineficazes.
- Ajustamentos necessários.

### Regra

O resultado final do jogo não prova, por si só, que uma recomendação foi correta ou incorreta.

---

# PARTE XIV — RELAÇÃO COM OUTROS DOCUMENTOS

## 107. Fundamentos

- `conhecimento/fundamentos/fases_jogo.md`
- `conhecimento/fundamentos/principios_ofensivos.md`
- `conhecimento/fundamentos/principios_defensivos.md`
- `conhecimento/fundamentos/superioridades.md`
- `conhecimento/fundamentos/modelos_jogo.md`

## 108. Sistemas táticos

- `conhecimento/sistemas/352/organizacao.md`
- `conhecimento/sistemas/352/ataque.md`
- `conhecimento/sistemas/352/defesa.md`
- `conhecimento/sistemas/352/transicoes.md`
- `conhecimento/sistemas/433/organizacao.md`
- `conhecimento/sistemas/433/ataque.md`
- `conhecimento/sistemas/433/defesa.md`
- `conhecimento/sistemas/433/transicoes.md`
- `conhecimento/sistemas/4231/organizacao.md`
- `conhecimento/sistemas/4231/ataque.md`
- `conhecimento/sistemas/4231/defesa.md`
- `conhecimento/sistemas/4231/transicoes.md`
- `conhecimento/sistemas/343/organizacao.md`
- `conhecimento/sistemas/343/ataque.md`
- `conhecimento/sistemas/343/defesa.md`
- `conhecimento/sistemas/343/transicoes.md`

## 109. Análise dos adversários

- `conhecimento/adversarios/estruturas_taticas.md`
- `conhecimento/adversarios/pressao_alta.md`
- `conhecimento/adversarios/bloco_medio.md`
- `conhecimento/adversarios/bloco_baixo.md`

## 110. Modelo da equipa

- `conhecimento/equipa/modelo_jogo.md`
- `conhecimento/equipa/principios_ofensivos.md`
- `conhecimento/equipa/principios_defensivos.md`
- `conhecimento/equipa/principios_equipa.md`
- `conhecimento/equipa/caracteristicas_jogadores.md`

---

# PARTE XV — PRINCÍPIO FINAL

## 111. Princípio central

A análise de vulnerabilidades adversárias deve partir de observações verificáveis e evoluir através de hipóteses, comparação de situações, avaliação de coberturas e análise da capacidade de exploração.

A IA deve compreender que:

- Uma estrutura não determina automaticamente uma fragilidade.
- Um espaço livre não garante uma oportunidade.
- Uma inferioridade numérica pode ser compensada.
- Uma falha isolada não constitui necessariamente um padrão.
- Uma vulnerabilidade recorrente pode não ser explorável.
- Uma recomendação ofensiva pode criar vulnerabilidades defensivas.
- Uma solução eficaz pode deixar de funcionar após adaptação adversária.
- A confiança depende da evidência e não da convicção da resposta.

A sequência obrigatória é:

**Observar → Contextualizar → Formular hipótese → Verificar → Avaliar explorabilidade → Avaliar risco → Recomendar → Reavaliar.**

O objetivo final é permitir que o assistente de IA identifique as vulnerabilidades adversárias mais relevantes e apresente recomendações claras, condicionadas, fundamentadas e compatíveis com as capacidades e o modelo de jogo da própria equipa.