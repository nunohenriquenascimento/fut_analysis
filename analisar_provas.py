"""Análise dos testes Sub-19 num único ficheiro. Python 3.10+.

INSTALAÇÃO (uma vez):
    py -m pip install openpyxl

EXECUÇÃO:
    py analisar_provas.py "Provas_Fisicas_Sub19(1).xlsx"

OPÇÕES:
    --saida powerbi          Pasta dos CSV e histórico (por defeito: powerbi)
    --data 2026-09-19        Data efetiva; se omitida, tenta ler E3 do Excel
    --sessao avaliacao-01    Identificador da avaliação
    --yoyo-apos-rsa sim      sim, nao ou desconhecido (preencher conforme realizado)

POWER BI:
    Importar atletas.csv, resultados.csv, tentativas.csv e avisos.csv.
    UTF-8; delimitador ponto e vírgula; números com vírgula decimal (pt-PT).
    atleta_id é TEXTO. valor e percentil_plantel são números decimais.
    Relacionar atletas[registo_id] 1:* com as outras tabelas, filtro unidirecional.
    Para gráficos de resultados: eixo atleta_nome, valor = valor e filtro metrica.
    Filtrar UMA métrica de cada vez, pois as unidades são diferentes.
    Percentis internos: maior = melhor; não representam normas externas.
    Campos *_pct e percentil_plantel usam escala 0–100, NÃO a formatação % do BI.
    Para curvas RSA: tentativas, prova=RSA, eixo tentativa, valor=valor,
    legenda atleta_nome, filtro valido=1.
    Reexecutar o comando após preencher o Excel; depois Atualizar no Power BI.

VERSÃO 2: histórico automático SQLite e CSV agregados, incluindo evolucao.csv.
Usar sempre a mesma pasta --saida e IDs estáveis. --guia explica o contexto,
as colunas opcionais e as regras de interpretação. Sessões repetidas são recusadas
salvo --substituir-sessao (preserva revisão anterior). Não modifica o Excel nem
cria gráficos. Sem qualquer referência normativa externa Sub-19.
"""
import argparse
import csv
import math
import os
import json
import sqlite3
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from statistics import mean
from zipfile import BadZipFile

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException


# Cada chave representa uma coluna de entrada; resultados Excel são ignorados.
COLUNAS = {
    'id': (0, 'ID'), 'nome': (1, 'Atleta'), 'dorsal': (2, 'Dorsal'),
    'posicao': (3, 'Posição atual'), 'pe': (4, 'Pé dominante'),
    'estado': (5, 'Estado'), 'altura': (6, 'Altura (cm)'), 'peso': (7, 'Peso (kg)'),
    'salto1': (9, 'Salto 1'), 'salto2': (10, 'Salto 2'), 'salto3': (11, 'Salto 3'),
    's5_1': (13, '5 m'), 's10_1': (14, '10 m'), 's30_1': (15, '30 m'),
    's5_2': (16, '5 m'), 's10_2': (17, '10 m'), 's30_2': (18, '30 m'),
    'dir1': (23, 'Dir. 1'), 'dir2': (24, 'Dir. 2'),
    'esq1': (26, 'Esq. 1'), 'esq2': (27, 'Esq. 2'),
    **{f'rsa{i}': (29+i, f'RSA {i}') for i in range(1, 7)},
    'yoyo': (39, 'Yo-Yo IR1 (m)'), 'nivel': (40, 'Nível final'),
    'flexoes': (41, 'Flexões'), 'prancha': (42, 'Prancha (s)'),
    'rpe': (43, 'RPE (0–10)'), 'encaixe': (44, 'Encaixe a testar'),
    'notas': (45, 'Observações'),
}

# Código, nome, unidade, orientação. None = não classificar automaticamente.
METRICAS = {
    'salto_cm': ('Salto horizontal — melhor', 'cm', 'maior'),
    'sprint_5_s': ('Sprint 5 m — melhor', 's', 'menor'),
    'sprint_10_s': ('Sprint 10 m — melhor', 's', 'menor'),
    'sprint_30_s': ('Sprint 30 m — melhor', 's', 'menor'),
    'parcial_10_30_s': ('Parcial 10–30 m — melhor', 's', 'menor'),
    'velocidade_media_10_30_kmh': ('Velocidade média 10–30 m', 'km/h', 'maior'),
    '505_direito_s': ('505 apoio direito — melhor', 's', 'menor'),
    '505_esquerdo_s': ('505 apoio esquerdo — melhor', 's', 'menor'),
    '505_assimetria_pct': ('505 assimetria relativa', '%', None),
    'rsa_melhor_s': ('RSA — melhor sprint', 's', 'menor'),
    'rsa_media_s': ('RSA — média dos seis sprints', 's', 'menor'),
    'rsa_total_s': ('RSA — soma dos seis sprints', 's', 'menor'),
    'rsa_quebra_pct': ('RSA — quebra percentual', '%', None),
    'yoyo_m': ('Yo-Yo IR1 — distância', 'm', 'maior'),
    'flexoes_rep': ('Flexões — repetições', 'rep', 'maior'),
    'prancha_s': ('Prancha — duração', 's', 'maior'),
    'rpe': ('Perceção de esforço', '0–10', None),
}

# Colunas opcionais, acrescentadas DEPOIS de AT na linha 6 de Registo.
# Só são analisadas quando existe pelo menos um valor para o atleta.
EXTRAS = {
    'cmj_cm': ('CMJ', 'cm', 'maior', ['CMJ 1 (cm)', 'CMJ 2 (cm)', 'CMJ 3 (cm)']),
    'unilateral_direito_cm': ('Salto unilateral direito', 'cm', 'maior',
        ['Unilateral D1 (cm)', 'Unilateral D2 (cm)', 'Unilateral D3 (cm)']),
    'unilateral_esquerdo_cm': ('Salto unilateral esquerdo', 'cm', 'maior',
        ['Unilateral E1 (cm)', 'Unilateral E2 (cm)', 'Unilateral E3 (cm)']),
    'tornozelo_direito_cm': ('Joelho à parede direito', 'cm', None, ['Tornozelo D (cm)']),
    'tornozelo_esquerdo_cm': ('Joelho à parede esquerdo', 'cm', None, ['Tornozelo E (cm)']),
    'forca_isometrica_n': ('Força isométrica', 'N', 'maior',
        ['Força 1 (N)', 'Força 2 (N)', 'Força 3 (N)']),
    'agilidade_reativa_s': ('Agilidade reativa', 's', 'menor',
        ['Reativa 1 (s)', 'Reativa 2 (s)', 'Reativa 3 (s)']),
}
for _codigo, (_nome, _unidade, _sentido, _) in EXTRAS.items():
    METRICAS[_codigo] = (_nome, _unidade, _sentido)

CONTEXTO_PADRAO = {
    'cronometragem': 'desconhecido', 'piso': 'desconhecido',
    'avaliador': 'desconhecido', 'periodo': 'desconhecido',
    'condicoes': 'desconhecido', 'protocolo': 'desconhecido',
    'treino_previo': 'desconhecido', 'protocolo_extras': 'desconhecido',
}

GUIA = '''VERSÃO 2 — GUIA
Excel original: manter colunas A:AT e cabeçalhos na linha 6.
Opcionais: acrescentar colunas depois de AT, sem deslocar as originais.
Cabeçalhos aceites:
{colunas}
Também: Descanso RSA-YoYo (min), por atleta; vazio = desconhecido.
Não preencher zero para um teste não realizado. Não criar colunas de resultados.
Yo-Yo IR1: distância de percursos completos de 20 m; ida e volta = 40 m.
Não incluir a recuperação nem percursos incompletos. Usar este critério em todas
as avaliações comparadas e documentá-lo no protocolo.
Os três ensaios opcionais devem seguir o mesmo protocolo; ensaios ausentes
tornam o resultado parcial. Mobilidade usa um registo por lado, admite zero.
Força é expressa em NEWTONS, não kg. O salto CMJ não mede força máxima.
--protocolo-extras deve identificar métodos, equipamento, posição, estímulo e
critérios de validade dos testes opcionais realizados. Sem isso não se classificam.

CONTEXTO
Usar --cronometragem manual|eletronica|video, --piso, --avaliador,
--periodo manha|tarde|noite, --condicoes e --treino-previo sim|nao.
--protocolo é uma identificação estável de um protocolo documentado: incluir
partida, aquecimento, descansos, ordem, distâncias, unidades e critérios de validade.
Alterar essa identificação sempre que o procedimento mudar. Desconhecido não
é confirmação de igualdade. Os textos são comparados literalmente.
--yoyo-apos-rsa sim|nao; se sim, registar descanso individual na coluna opcional.
Não existe correção matemática automática da fadiga ou do erro de cronometragem.

HISTÓRICO
--data AAAA-MM-DD (ou E3) e --sessao identificam cada avaliação.
--equipa-id identifica permanentemente a equipa; usar sempre os mesmos IDs de
atleta, não números de linha/dorsais que possam mudar entre avaliações.
O histórico fica em --saida/historico.sqlite3; conservar/copiar essa base de dados.
Sessão repetida: recusada por segurança. Para corrigir usar --substituir-sessao;
a versão anterior fica preservada na tabela revisoes da base de dados.
Os CSV são reconstruídos com TODAS as sessões guardadas. Não importar CSV antigos
automaticamente: para os migrar, voltar a executar os Excel originais, um por sessão.
Uma identidade com nome diferente é bloqueada para evitar misturar jogadores.

POWER BI
Importar atletas.csv, resultados.csv, tentativas.csv, avisos.csv e evolucao.csv.
Usar atletas[registo_id] 1:* nas restantes tabelas, filtro unidirecional.
registo_id identifica atleta+sessão+equipa. atleta_chave permite seguir o atleta.
Filtrar equipa_id e sessao_id para comparar o plantel numa avaliação.
Evolução: filtrar atleta_chave e metrica; eixo data; valores em resultados[valor].
Conclusões e classificações ficam em resultados; diferenças em evolucao.
UTF-8, separador ;, números com vírgula decimal, IDs como texto.
Percentagens e percentis usam escala 0–100 (não formatar novamente como %).

INTERPRETAÇÃO
Percentis de resultados completos, por métrica e contexto registado equivalente.
Classificação interna: <25 inferior; 25 a <75 intermédia; >=75 superior.
Exige pelo menos 5 atletas: convenção operacional, NÃO norma científica.
Com 2–4 atletas mostra percentil sem faixa; com 1 não calcula percentil.
Contexto desconhecido permite descrição interna com ressalva, não certifica
comparabilidade. Assimetria, quebra RSA, RPE e mobilidade não recebem faixa.
Variações históricas são valores observados, não melhoria física comprovada.
Comparação automática usa a avaliação anterior completa em data estritamente
anterior. Mesmo dia não é ordenado. Contexto diferente/desconhecido bloqueia
a interpretação favorável/desfavorável, mas conserva as diferenças numéricas.
Não há normas externas Sub-19, diagnóstico de lesão ou posição ideal.
'''

def texto(v):
    return '' if v is None else str(v).strip()


def ler_excel(caminho):
    wb = load_workbook(caminho, read_only=True, data_only=False)
    try:
        if 'Registo' not in wb.sheetnames:
            raise ValueError("Não existe a folha 'Registo'.")
        ws = wb['Registo']
        header = next(ws.iter_rows(min_row=6, max_row=6, max_col=46, values_only=True))
        for _, (i, nome) in COLUNAS.items():
            if texto(header[i]) != nome:
                raise ValueError(f'Cabeçalho inesperado na coluna {i+1}: esperado {nome!r}, recebido {header[i]!r}.')
        extra_header = next(ws.iter_rows(min_row=6, max_row=6, values_only=True))
        aceites = {h for _, _, _, nomes in EXTRAS.values() for h in nomes}
        aceites.add('Descanso RSA-YoYo (min)')
        extras = {}
        for i, h in enumerate(extra_header[46:], 46):
            if texto(h) in aceites:
                if texto(h) in extras:
                    raise ValueError('Cabeçalho opcional repetido: ' + texto(h))
                extras[texto(h)] = i
        registos = []
        for linha, row in enumerate(ws.iter_rows(min_row=7, max_col=max(46, len(extra_header)), values_only=True), 7):
            r = {chave: row[i] for chave, (i, _) in COLUNAS.items()}
            r.update({h: row[i] for h, i in extras.items()})
            # Os IDs 1–21 estão pré-preenchidos mesmo quando não há atletas.
            if not any(texto(v) for k, v in r.items() if k != 'id'):
                continue
            r['linha_excel'] = linha
            registos.append(r)
        return registos, {'data': ws['E3'].value, 'equipa': texto(ws['B3'].value)}
    finally:
        wb.close()


def analisar(registos, sessao, data_avaliacao, equipa='', yoyo_apos_rsa='desconhecido'):
    """Função reutilizável numa futura API: devolve quatro listas de dicionários."""
    ids = [texto(r['id']) for r in registos]
    if any(not i for i in ids):
        raise ValueError('Há atletas sem ID. Preenche a coluna ID antes de analisar.')
    duplicados = [i for i,n in Counter(ids).items() if n > 1]
    if duplicados:
        raise ValueError('IDs repetidos: ' + ', '.join(duplicados))
    atletas, resultados, tentativas, avisos = [], [], [], []
    for r in registos:
        base = {'sessao_id': sessao, 'data': data_avaliacao, 'atleta_id': texto(r['id']), 'atleta_nome': texto(r['nome'])}
        def aviso(campo, mensagem):
            avisos.append({**base, 'linha_excel': r['linha_excel'], 'campo': campo, 'mensagem': mensagem})
        def numero(chave, zero=False, inteiro=False):
            raw = r.get(chave)
            if not texto(raw):
                return None
            try:
                if isinstance(raw, bool):
                    raise ValueError
                n = float(texto(raw).replace(',', '.'))
                if not math.isfinite(n) or n < 0 or (n == 0 and not zero) or (inteiro and not n.is_integer()):
                    raise ValueError
                return n
            except (ValueError, TypeError, OverflowError):
                aviso(chave, 'Valor excluído: usar número ' + ('inteiro ' if inteiro else '') + ('>= 0.' if zero else '> 0.') + ' Não colocar zero para teste não realizado.')
                return None
        def tentativa(chave, prova, ordem, unidade, valor, lado=''):
            if texto(r.get(chave)):
                tentativas.append({**base, 'prova': prova, 'lado': lado, 'tentativa': ordem, 'valor_original': texto(r[chave]), 'valor': valor, 'unidade': unidade, 'valido': int(valor is not None)})
        calculos = {}
        def resultado(chave, valor, n, esperado, estado=None):
            calculos[chave] = valor
            nome, unidade, orientacao = METRICAS[chave]
            resultados.append({**base, 'metrica': chave, 'prova': nome, 'valor': valor, 'unidade': unidade,
                'orientacao': orientacao or '', 'tentativas_validas': n, 'tentativas_previstas': esperado,
                'estado_resultado': estado or ('sem_resultado' if valor is None else 'completo' if n == esperado else 'parcial'),
                'percentil_plantel': None, 'n_comparacao': 0, 'yoyo_apos_rsa': yoyo_apos_rsa})
        def serie(chaves, prova, unidade, maior=False, lado=''):
            valores = [numero(k) for k in chaves]
            for i,(k,v) in enumerate(zip(chaves,valores),1):
                tentativa(k,prova,i,unidade,v,lado)
            validos = [v for v in valores if v is not None]
            melhor = (max(validos) if maior else min(validos)) if validos else None
            return melhor, len(validos), valores
        if not base['atleta_nome']:
            aviso('nome', 'Nome em falta; o atleta é identificado pelo ID.')
        altura, peso = numero('altura'), numero('peso')
        if altura is not None and altura < 100:
            aviso('altura', 'Confirmar unidade da altura: centímetros, não metros.')
        atletas.append({**base, 'equipa': equipa, 'dorsal': texto(r['dorsal']), 'posicao': texto(r['posicao']),
            'pe_dominante': texto(r['pe']), 'estado': texto(r['estado']), 'altura_cm': altura, 'peso_kg': peso,
            'nivel_yoyo': texto(r['nivel']), 'encaixe_a_testar': texto(r['encaixe']), 'observacoes': texto(r['notas'])})
        v,n,_ = serie(['salto1','salto2','salto3'],'Salto horizontal','cm',maior=True)
        resultado('salto_cm',v,n,3)
        sprints = []
        for i in (1,2):
            chaves = [f's{dist}_{i}' for dist in (5,10,30)]
            tempos = [numero(k) for k in chaves]
            conhecidos = [v for v in tempos if v is not None]
            if any(b <= a for a,b in zip(conhecidos,conhecidos[1:])):
                aviso(f'sprint_{i}', 'Tentativa excluída: tempos acumulados devem aumentar de 5 para 10 e para 30 m.')
                tempos = [None,None,None]
            for k,dist,v in zip(chaves,(5,10,30),tempos):
                tentativa(k,f'Sprint {dist} m',i,'s',v)
            sprints.append(tempos)
        for j,dist in enumerate((5,10,30)):
            validos = [t[j] for t in sprints if t[j] is not None]
            resultado(f'sprint_{dist}_s',min(validos) if validos else None,len(validos),2)
        parciais = [t[2]-t[1] for t in sprints if t[1] is not None and t[2] is not None]
        parcial = min(parciais) if parciais else None
        resultado('parcial_10_30_s',parcial,len(parciais),2)
        resultado('velocidade_media_10_30_kmh',72/parcial if parcial else None,len(parciais),2)
        dr,nd,_ = serie(['dir1','dir2'],'505','s',lado='direito')
        es,ne,_ = serie(['esq1','esq2'],'505','s',lado='esquerdo')
        resultado('505_direito_s',dr,nd,2)
        resultado('505_esquerdo_s',es,ne,2)
        assimetria = abs(dr-es)/min(dr,es)*100 if dr is not None and es is not None else None
        resultado('505_assimetria_pct',assimetria,nd+ne,4)
        _,n,rsa = serie([f'rsa{i}' for i in range(1,7)],'RSA','s')
        completo = n == 6
        if 0 < n < 6:
            aviso('RSA', 'Série incompleta: necessários seis tempos válidos para calcular o resumo RSA.')
        for chave,valor in [
            ('rsa_melhor_s',min(rsa) if completo else None),
            ('rsa_media_s',mean(rsa) if completo else None),
            ('rsa_total_s',sum(rsa) if completo else None),
            ('rsa_quebra_pct',(sum(rsa)/(6*min(rsa))-1)*100 if completo else None),
        ]:
            resultado(chave,valor,n,6,'completo' if completo else 'incompleto' if n else 'sem_resultado')
        yoyo = numero('yoyo',zero=True,inteiro=True)
        if yoyo is not None and yoyo % 20:
            aviso('yoyo', 'Distância excluída: usar múltiplos de 20 m (percursos completos; ida e volta = 40 m), sem metros de recuperação.')
            yoyo = None
        tentativa('yoyo','Yo-Yo IR1',1,'m',yoyo)
        resultado('yoyo_m',yoyo,int(yoyo is not None),1)
        for campo,chave,prova,unidade,inteiro in [('flexoes','flexoes_rep','Flexões','rep',True),('prancha','prancha_s','Prancha','s',False),('rpe','rpe','RPE','0–10',False)]:
            v = numero(campo,zero=True,inteiro=inteiro)
            if campo == 'rpe' and v is not None and v > 10:
                aviso('rpe','Valor excluído: a escala utilizada vai de 0 a 10.')
                v = None
            tentativa(campo,prova,1,unidade,v)
            resultado(chave,v,int(v is not None),1)
        for chave, (prova, unidade, sentido, nomes) in EXTRAS.items():
            if not any(texto(r.get(k)) for k in nomes):
                continue
            valores = [numero(k, zero=chave.startswith('tornozelo')) for k in nomes]
            for i, (k, v) in enumerate(zip(nomes, valores), 1):
                tentativa(k, prova, i, unidade, v)
            validos = [v for v in valores if v is not None]
            melhor = (min(validos) if sentido == 'menor' else max(validos)) if validos else None
            resultado(chave, melhor, len(validos), len(nomes))
    for chave,(_,_,orientacao) in METRICAS.items():
        # Comparação apenas com protocolo completo, nunca com tentativas parciais.
        grupo = [r for r in resultados if r['metrica']==chave and r['estado_resultado']=='completo' and r['valor'] is not None]
        if not orientacao:
            continue
        for r in grupo:
            r['n_comparacao'] = len(grupo)
            if len(grupo) < 2:
                continue
            v = r['valor']
            piores = sum(x['valor'] < v if orientacao=='maior' else x['valor'] > v for x in grupo)
            iguais = sum(x['valor']==v for x in grupo)
            r['percentil_plantel'] = 100*(piores+(iguais-1)/2)/(len(grupo)-1)
    return {'atletas':atletas,'resultados':resultados,'tentativas':tentativas,'avisos':avisos}


def enriquecer(tabelas, registos, equipa_id, contexto):
    """Acrescenta contexto, chaves estáveis e interpretação sem normas externas."""
    contexto = {**CONTEXTO_PADRAO, **contexto}
    por_id = {texto(r['id']): r for r in registos}
    descansos = {}
    for aid, reg in por_id.items():
        raw = reg.get('Descanso RSA-YoYo (min)')
        if not texto(raw):
            descansos[aid] = None
            continue
        try:
            n = float(texto(raw).replace(',', '.'))
            if isinstance(raw, bool) or not math.isfinite(n) or n < 0:
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError(f'Descanso RSA-YoYo inválido para atleta {aid}.')
        descansos[aid] = n
    for linhas in tabelas.values():
        for r in linhas:
            r['equipa_id'] = equipa_id
            r['atleta_chave'] = json.dumps([equipa_id, r['atleta_id']], ensure_ascii=False)
            r['registo_id'] = json.dumps([equipa_id, r['sessao_id'], r['atleta_id']], ensure_ascii=False)
    grupos = {}
    for r in tabelas['resultados']:
        r.update(contexto)
        r['descanso_rsa_yoyo_min'] = descansos[r['atleta_id']]
        campos = list(CONTEXTO_PADRAO)
        if r['metrica'] not in EXTRAS:
            campos.remove('protocolo_extras')
        if r['metrica'] == 'yoyo_m':
            campos.append('yoyo_apos_rsa')
            if r['yoyo_apos_rsa'] != 'nao':
                campos.append('descanso_rsa_yoyo_min')
        r['contexto_completo'] = int(all(r.get(k) is not None and texto(r[k]).lower() not in ('', 'desconhecido') for k in campos))
        r['contexto_chave'] = json.dumps({k: r.get(k) for k in campos}, sort_keys=True, ensure_ascii=False)
        r['classificacao_externa'] = 'sem_referencia_sub19_validada'
        r['percentil_plantel'] = None
        r['n_comparacao'] = 0
        r['classificacao_interna'] = 'nao_aplicavel'
        r['conclusao'] = ''
        if r['orientacao'] and r['estado_resultado'] == 'completo':
            grupos.setdefault((r['metrica'], r['contexto_chave']), []).append(r)
    for grupo in grupos.values():
        for r in grupo:
            r['n_comparacao'] = len(grupo)
            if len(grupo) > 1:
                piores = sum(x['valor'] < r['valor'] if r['orientacao'] == 'maior' else x['valor'] > r['valor'] for x in grupo)
                iguais = sum(x['valor'] == r['valor'] for x in grupo)
                r['percentil_plantel'] = 100 * (piores + (iguais - 1) / 2) / (len(grupo) - 1)
            if r['metrica'] in EXTRAS and contexto['protocolo_extras'] == 'desconhecido':
                r['classificacao_interna'] = 'protocolo_opcional_nao_documentado'
            elif len(grupo) < 5:
                r['classificacao_interna'] = 'amostra_insuficiente_para_faixa'
            else:
                p = r['percentil_plantel']
                r['classificacao_interna'] = 'inferior' if p < 25 else 'intermedia' if p < 75 else 'superior'
    for r in tabelas['resultados']:
        if r['valor'] is None:
            r['conclusao'] = 'Sem resultado válido; não equivale a desempenho baixo.'
            continue
        frase = f"{r['prova']}: {r['valor']:.3f} {r['unidade']}. "
        if r['estado_resultado'] != 'completo':
            frase += 'Resultado incompleto/parcial; excluído da classificação interna. '
        elif r['classificacao_interna'] in ('inferior', 'intermedia', 'superior'):
            frase += f"Faixa {r['classificacao_interna']} entre {r['n_comparacao']} atletas com o mesmo contexto registado. Não é uma norma Sub-19. "
        elif r['orientacao']:
            frase += 'Sem classificação por faixa: amostra insuficiente ou protocolo opcional não documentado. '
        if r['metrica'] == 'rsa_quebra_pct':
            frase += 'Interpretar juntamente com tempo médio e melhor sprint; pouca quebra não implica bom desempenho. '
        if r['metrica'] == '505_assimetria_pct':
            frase += 'Diferença descritiva entre lados; não prevê lesão nem identifica a sua causa. '
        if r['metrica'] == 'yoyo_m' and r['yoyo_apos_rsa'] != 'nao':
            frase += 'RSA prévio ou ordem desconhecida: possível influência da fadiga; não foi aplicada correção. '
        if not r['contexto_completo']:
            frase += 'Contexto incompleto: comparabilidade não confirmada. '
        if r['cronometragem'] == 'manual' and r['unidade'] in ('s', 'km/h', '%'):
            frase += 'Cronometragem manual: pequenas diferenças podem refletir erro de medição. '
        r['conclusao'] = frase.strip()
    return tabelas


def calcular_evolucao(resultados):
    linhas, anteriores = [], {}
    for r in sorted(resultados, key=lambda x: (x['data'], x['sessao_id'], x['atleta_chave'], x['metrica'])):
        chave = (r['atleta_chave'], r['metrica'])
        candidatos = [p for p in anteriores.get(chave, []) if p['data'] < r['data']]
        if r['estado_resultado'] == 'completo' and r['valor'] is not None:
            if candidatos:
                ultima_data = max(p['data'] for p in candidatos)
                ultimos = [p for p in candidatos if p['data'] == ultima_data]
                # Mais de uma avaliação na mesma data: sem escolha arbitrária.
                p = ultimos[0]
                ambiguo = len(ultimos) > 1
                comp = not ambiguo and r['contexto_completo'] and p['contexto_completo'] and r['contexto_chave'] == p['contexto_chave']
                delta = None if ambiguo else r['valor'] - p['valor']
                pct = None if ambiguo or p['valor'] == 0 else delta / abs(p['valor']) * 100
                direcao = 'nao_interpretada'
                if comp and r['orientacao']:
                    favoravel = delta > 0 if r['orientacao'] == 'maior' else delta < 0
                    direcao = 'sem_alteracao' if delta == 0 else 'variacao_favoravel' if favoravel else 'variacao_desfavoravel'
                linhas.append({k: r[k] for k in ('equipa_id', 'sessao_id', 'data', 'atleta_id', 'atleta_nome', 'atleta_chave', 'registo_id', 'metrica', 'unidade')} | {
                    'sessao_anterior': '' if ambiguo else p['sessao_id'], 'data_anterior': ultima_data,
                    'valor_anterior': None if ambiguo else p['valor'], 'valor_atual': r['valor'],
                    'diferenca': delta, 'variacao_pct': pct, 'contexto_compativel': int(bool(comp)),
                    'interpretacao': direcao,
                    'ressalva': 'Várias sessões anteriores na mesma data: comparação ambígua.' if ambiguo else
                    'Variação observada; não prova adaptação física nem mudança superior ao erro de medição.' if comp else
                    'Contexto diferente ou incompleto: diferenças numéricas não interpretadas como evolução física.'})
            anteriores.setdefault(chave, []).append(r)
    return linhas


def guardar_historico(tabelas, caminho, substituir=False):
    """Transação SQLite; revisões preservadas; CSV regenerável a partir desta base."""
    primeiro = tabelas['atletas'][0]
    equipa, sessao, data_sessao = (primeiro[k] for k in ('equipa_id', 'sessao_id', 'data'))
    if not data_sessao or not sessao or not equipa:
        raise ValueError('Histórico requer equipa, sessão e data.')
    payload = json.dumps(tabelas, ensure_ascii=False, allow_nan=False)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(caminho) as db:
        db.execute('CREATE TABLE IF NOT EXISTS sessoes (equipa TEXT, sessao TEXT, data TEXT, payload TEXT, PRIMARY KEY(equipa,sessao))')
        db.execute('CREATE TABLE IF NOT EXISTS revisoes (equipa TEXT, sessao TEXT, arquivada_em TEXT, payload TEXT)')
        db.execute('BEGIN IMMEDIATE')
        existente = db.execute('SELECT payload FROM sessoes WHERE equipa=? AND sessao=?', (equipa, sessao)).fetchone()
        if existente and not substituir:
            raise ValueError('Sessão já existe. Para corrigir explicitamente usar --substituir-sessao; a versão anterior será preservada.')
        identidade = {a['atleta_chave']: a['atleta_nome'].strip().casefold() for a in tabelas['atletas']}
        for (salvo,) in db.execute('SELECT payload FROM sessoes'):
            for a in json.loads(salvo)['atletas']:
                if a['atleta_chave'] in identidade and a['atleta_nome'].strip().casefold() != identidade[a['atleta_chave']]:
                    raise ValueError(f"ID {a['atleta_id']} já associado a outro nome. Confirmar identidade antes de importar.")
        if existente:
            db.execute('INSERT INTO revisoes VALUES (?,?,?,?)', (equipa, sessao, datetime.now().isoformat(), existente[0]))
        db.execute('INSERT OR REPLACE INTO sessoes VALUES (?,?,?,?)', (equipa, sessao, data_sessao, payload))
        agregado = {k: [] for k in tabelas}
        for (salvo,) in db.execute('SELECT payload FROM sessoes ORDER BY data,equipa,sessao'):
            for k, rows in json.loads(salvo).items():
                agregado[k].extend(rows)
    agregado['evolucao'] = calcular_evolucao(agregado['resultados'])
    return agregado


def exportar(tabelas,pasta):
    pasta.mkdir(parents=True,exist_ok=True)
    vazios = {
        'tentativas':['sessao_id','data','atleta_id','atleta_nome','prova','lado','tentativa','valor_original','valor','unidade','valido'],
        'avisos':['sessao_id','data','atleta_id','atleta_nome','linha_excel','campo','mensagem'],
        'evolucao':['equipa_id','sessao_id','data','atleta_id','atleta_nome','atleta_chave','registo_id','metrica','unidade','sessao_anterior','data_anterior','valor_anterior','valor_atual','diferenca','variacao_pct','contexto_compativel','interpretacao','ressalva'],
    }
    for k in ('tentativas', 'avisos'):
        vazios[k] += ['equipa_id', 'atleta_chave', 'registo_id']
    def serializar(v):
        if v is None:
            return ''
        if isinstance(v,float):
            return format(v,'.12g').replace('.',',')
        return v
    # Preparar todos os ficheiros antes de substituir os quatro CSV conhecidos.
    temporarios = []
    try:
        for nome,linhas in tabelas.items():
            campos = list(dict.fromkeys(k for row in linhas for k in row)) if linhas else vazios[nome]
            tmp = pasta/f'.{nome}.tmp'
            temporarios.append((tmp,pasta/f'{nome}.csv'))
            with tmp.open('w',encoding='utf-8-sig',newline='') as f:
                w=csv.DictWriter(f,fieldnames=campos,delimiter=';')
                w.writeheader()
                w.writerows({k:serializar(v) for k,v in row.items()} for row in linhas)
        for tmp,dest in temporarios:
            os.replace(tmp,dest)
    finally:
        for tmp,_ in temporarios:
            tmp.unlink(missing_ok=True)


def normalizar_data(v):
    if not texto(v):
        return ''
    if isinstance(v,(datetime,date)):
        return v.date().isoformat() if isinstance(v,datetime) else v.isoformat()
    for formato in ('%Y-%m-%d','%d/%m/%Y','%d-%m-%Y'):
        try:
            return datetime.strptime(texto(v),formato).date().isoformat()
        except ValueError:
            pass
    raise ValueError('Data inválida. Usa --data AAAA-MM-DD ou preenche E3 como data no Excel.')


def main():
    parser=argparse.ArgumentParser(description='Ler provas físicas do Excel e exportar tabelas para Power BI.')
    parser.add_argument('excel',type=Path,nargs='?')
    parser.add_argument('--guia', action='store_true', help='Mostrar instruções, colunas opcionais e configuração Power BI.')
    parser.add_argument('--saida',type=Path,default=Path('powerbi'))
    parser.add_argument('--data')
    parser.add_argument('--sessao')
    parser.add_argument('--equipa-id', help='Identificador estável da equipa; por defeito B3 do Excel.')
    parser.add_argument('--substituir-sessao', action='store_true')
    parser.add_argument('--cronometragem', choices=['manual','eletronica','video','desconhecido'], default='desconhecido')
    parser.add_argument('--periodo', choices=['manha','tarde','noite','desconhecido'], default='desconhecido')
    parser.add_argument('--treino-previo', choices=['sim','nao','desconhecido'], default='desconhecido')
    for campo in ('piso','avaliador','condicoes','protocolo','protocolo-extras'):
        parser.add_argument('--'+campo, default='desconhecido')
    parser.add_argument('--yoyo-apos-rsa',choices=['sim','nao','desconhecido'],default='desconhecido')
    args=parser.parse_args()
    if args.guia:
        print(GUIA.format(colunas='\n'.join(', '.join(v[3]) for v in EXTRAS.values())))
        return
    if args.excel is None:
        parser.error('Indica o Excel: py analisar_provas.py "Provas_Fisicas_Sub19(1).xlsx". Ajuda: --guia')
    try:
        registos,meta=ler_excel(args.excel)
        if not registos:
            raise ValueError('A folha está vazia. Preenche os atletas e as tentativas em Registo; não foram alterados resultados anteriores.')
        data_avaliacao=normalizar_data(args.data if args.data is not None else meta['data'])
        if not data_avaliacao:
            raise ValueError('Preenche a data em E3 ou usa --data AAAA-MM-DD para guardar histórico.')
        sessao=args.sessao or data_avaliacao or args.excel.stem
        tabelas=analisar(registos,sessao,data_avaliacao,meta['equipa'],args.yoyo_apos_rsa)
        equipa_id = texto(args.equipa_id or meta['equipa'])
        if not equipa_id:
            raise ValueError('Indica --equipa-id ou preenche B3 do Excel.')
        contexto = {k: texto(getattr(args, k)) or 'desconhecido' for k in CONTEXTO_PADRAO}
        enriquecer(tabelas, registos, equipa_id, contexto)
        agregado = guardar_historico(tabelas, args.saida/'historico.sqlite3', args.substituir_sessao)
        try:
            exportar(agregado,args.saida)
        except OSError as exc:
            raise OSError('Histórico guardado, mas falhou a exportação CSV (fechar Excel/Power BI se estiver a bloquear ficheiros). Repetir com --substituir-sessao. ' + str(exc)) from exc
        print(f"Concluído: {len(tabelas['atletas'])} atletas, {len(tabelas['avisos'])} avisos.")
        print(f'CSV para Power BI: {args.saida.resolve()}')
        print('Histórico preservado em historico.sqlite3; CSV incluem todas as sessões.')
        print('Consultar avisos.csv e conclusao em resultados.csv. Evolução em evolucao.csv.')
        print('Power BI: relacionar por registo_id, não apenas atleta_id. Instruções: --guia.')
        if not data_avaliacao:
            print('Data não preenchida: definir --data para identificar a avaliação.')
        if args.yoyo_apos_rsa=='desconhecido':
            print('Confirmar contexto do Yo-Yo com --yoyo-apos-rsa sim ou nao.')
    except (ValueError,OSError,BadZipFile,InvalidFileException,sqlite3.Error) as exc:
        parser.exit(2,f'Erro: {exc}\n')


if __name__=='__main__':
    main()
