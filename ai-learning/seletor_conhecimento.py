
import re
import unicodedata
from pathlib import Path


# ============================================================
# CONFIGURAÇÃO
# ============================================================

PASTA_CONHECIMENTO = (
    Path(__file__).resolve().parent / "conhecimento"
)

SISTEMA_PRINCIPAL = "352"

SISTEMAS_EQUIPA = {
    "352", "433", "4231", "343"
}

FORMACOES = {
    "352": "3-5-2",
    "433": "4-3-3",
    "4231": "4-2-3-1",
    "343": "3-4-3",
    "442": "4-4-2",
    "4141": "4-1-4-1",
    "532": "5-3-2",
    "541": "5-4-1",
    "4321": "4-3-2-1",
    "4312": "4-3-1-2",
    "4222": "4-2-2-2",
    "3421": "3-4-2-1",
}

TEMAS = {
    "defesa": [
        "defender", "defesa", "defensiva", "defensivo",
        "sem bola", "bloco medio", "bloco baixo",
        "marcacao", "cobertura", "pressionar",
        "pressao defensiva", "organizar defensivamente",
    ],
    "saida_bola": [
        "saida de bola", "sair a jogar", "sair da pressao",
        "construcao", "construir", "primeira fase",
        "primeira linha de pressao",
    ],
    "ataque": [
        "atacar", "ataque", "ofensivo", "ofensiva",
        "finalizacao", "criar oportunidades",
        "profundidade", "ultimo terco",
        "passe de rutura",
    ],
    "transicoes": [
        "transicao", "transicoes", "contra-ataque",
        "reacao a perda", "recuperacao da bola",
        "transicao ofensiva", "transicao defensiva",
    ],
}

TERMOS_EQUIPA = [
    "nossa equipa",
    "minha equipa",
    "nosso modelo",
    "nossos jogadores",
    "nossos sub-19",
    "sub-19",
    "ccdr",
    "nosso 3-5-2",
    "nosso 4-3-3",
    "nosso 4-2-3-1",
    "nosso 3-4-3",
    "minha 3-5-2",
    "minha 4-3-3",
    "minha 4-2-3-1",
    "minha 3-4-3",
]

# Documentos gerais úteis em diferentes perguntas.
FUNDAMENTOS_GERAIS = {
    "fases_jogo",
    "modelos_jogo",
    "superioridades",
}

# Documentos de fundamentos por tema.
FUNDAMENTOS_POR_TEMA = {
    "defesa": {"principios_defensivos"},
    "saida_bola": {"principios_ofensivos"},
    "ataque": {"principios_ofensivos"},
    "transicoes": {
        "principios_ofensivos",
        "principios_defensivos",
    },
    "geral": {
        "principios_ofensivos",
        "principios_defensivos",
    },
}

# Documentos da equipa relevantes para cada tema.
EQUIPA_POR_TEMA = {
    "defesa": {
        "principios_defensivos",
        "principios_equipa",
    },
    "saida_bola": {
        "principios_ofensivos",
        "principios_equipa",
    },
    "ataque": {
        "principios_ofensivos",
        "principios_equipa",
    },
    "transicoes": {
        "principios_ofensivos",
        "principios_defensivos",
        "principios_equipa",
    },
    "geral": {
        "principios_equipa",
    },
}

# Documentos de análise adversária por tema.
ADVERSARIOS_POR_TEMA = {
    "defesa": {
        "estruturas_taticas",
        "analise_vulnerabilidades",
    },
    "saida_bola": {
        "estruturas_taticas",
        "pressao_alta",
        "analise_vulnerabilidades",
    },
    "ataque": {
        "estruturas_taticas",
        "analise_vulnerabilidades",
    },
    "transicoes": {
        "estruturas_taticas",
        "analise_vulnerabilidades",
    },
    "geral": {
        "estruturas_taticas",
    },
}


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalizar_texto(texto):
    """Converte para minúsculas e remove acentos."""

    texto = unicodedata.normalize(
        "NFD",
        str(texto).casefold(),
    )

    return "".join(
        letra
        for letra in texto
        if unicodedata.category(letra) != "Mn"
    )


def contem_expressao(texto, expressao):
    """Procura uma expressão sem confundir partes de palavras."""

    padrao = (
        r"(?<!\w)"
        + re.escape(normalizar_texto(expressao))
        + r"(?!\w)"
    )

    return bool(re.search(padrao, texto))


# ============================================================
# IDENTIFICAÇÃO DE FORMAÇÕES
# ============================================================

def identificar_formacoes(pergunta):
    """Identifica formações mencionadas no texto."""

    texto = normalizar_texto(pergunta)
    encontradas = []

    for codigo in FORMACOES:
        padrao = (
            r"(?<!\d)"
            + r"[-\s]*".join(codigo)
            + r"(?!\d)"
        )

        if re.search(padrao, texto):
            encontradas.append(codigo)

    return encontradas


def identificar_temas(pergunta):
    """Identifica os temas da pergunta."""

    texto = normalizar_texto(pergunta)
    encontrados = set()

    for tema, palavras in TEMAS.items():
        if any(
            contem_expressao(texto, palavra)
            for palavra in palavras
        ):
            encontrados.add(tema)

    return encontrados or {"geral"}


def identificar_formacao_adversaria(texto, formacoes):
    """
    Identifica formações associadas ao adversário.

    Procura expressões como:
    - contra um 4-4-2
    - adversário em 4-3-3
    - enfrentar uma equipa em 5-3-2
    """

    padrao_adversario = (
        r"(?:contra|adversari[oa]|enfrentar|defrontar)"
        r"[\w\s-]{0,60}?"
        r"(?:em|num|no|com|um|uma|sistema|formacao)?"
        r"\s*"
        r"(?<!\d)(\d(?:[-\s]*\d){2,3})(?!\d)"
    )

    for correspondencia in re.finditer(
        padrao_adversario,
        texto,
    ):
        codigo = re.sub(
            r"\D",
            "",
            correspondencia.group(1),
        )

        if codigo in formacoes:
            return codigo

    return None


def identificar_contexto(pergunta):
    """Distingue o contexto da equipa e do adversário."""

    texto = normalizar_texto(pergunta)

    formacoes = identificar_formacoes(texto)
    temas = identificar_temas(texto)

    menciona_equipa = any(
        contem_expressao(texto, termo)
        for termo in TERMOS_EQUIPA
    )

    adversaria = identificar_formacao_adversaria(
        texto,
        formacoes,
    )

    # O sistema habitual é 3-5-2.
    propria = (
        SISTEMA_PRINCIPAL
        if menciona_equipa
        else None
    )

    # Uma formação explicitamente associada à nossa equipa
    # substitui o sistema habitual.
    for codigo in formacoes:

        if codigo not in SISTEMAS_EQUIPA:
            continue

        nome = FORMACOES[codigo]

        if (
            contem_expressao(texto, f"nosso {nome}")
            or contem_expressao(texto, f"minha {nome}")
        ):
            propria = codigo
            menciona_equipa = True
            break

    # Pergunta sobre uma formação isolada, sem adversário.
    if (
        adversaria is None
        and len(formacoes) == 1
        and not menciona_equipa
    ):
        codigo = formacoes[0]

        if codigo in SISTEMAS_EQUIPA:
            propria = codigo

    return {
        "formacao_propria": propria,
        "formacao_adversaria": adversaria,
        "temas": temas,
        "contexto_equipa": menciona_equipa,
    }


# ============================================================
# SELEÇÃO DOS DOCUMENTOS
# ============================================================

def documento_relevante(relativo, contexto, pergunta):
    """Decide se um documento pertence ao contexto."""

    caminho = normalizar_texto(relativo)
    nome = normalizar_texto(
        Path(relativo).stem
    )

    temas = contexto["temas"]

    # 1. Fundamentos universais.
    if caminho.startswith("fundamentos/"):

        relevantes = set(FUNDAMENTOS_GERAIS)

        for tema in temas:
            relevantes.update(
                FUNDAMENTOS_POR_TEMA.get(tema, set())
            )

        return nome in relevantes

    # 2. Conhecimento dos sistemas táticos.
    if caminho.startswith("sistemas/"):

        sistema = contexto["formacao_propria"]

        if sistema is None:
            return False

        if not caminho.startswith(
            f"sistemas/{sistema}/"
        ):
            return False

        # Nesta fase, carregar os documentos existentes
        # do sistema selecionado.
        return True

    # 3. Conhecimento específico da equipa.
    if caminho.startswith("equipa/"):

        if not contexto["contexto_equipa"]:
            return False

        # Modelo e características são transversais.
        if nome in {
            "modelo_jogo",
            "caracteristicas_jogadores",
        }:
            return True

        relevantes = set()

        for tema in temas:
            relevantes.update(
                EQUIPA_POR_TEMA.get(tema, set())
            )

        return nome in relevantes

    # 4. Conhecimento sobre adversários.
    if caminho.startswith("adversarios/"):

        if contexto["formacao_adversaria"] is None:
            return False

        relevantes = set()

        for tema in temas:
            relevantes.update(
                ADVERSARIOS_POR_TEMA.get(tema, set())
            )

        texto = normalizar_texto(pergunta)

        # Incluir documentos de blocos apenas quando
        # são mencionados na pergunta.
        if contem_expressao(texto, "bloco medio"):
            relevantes.add("bloco_medio")

        if contem_expressao(texto, "bloco baixo"):
            relevantes.add("bloco_baixo")

        if (
            contem_expressao(texto, "pressao alta")
            or contem_expressao(texto, "bloco alto")
        ):
            relevantes.add("pressao_alta")

        return nome in relevantes

    # 5. Casos práticos de confronto entre sistemas.
    if caminho.startswith("casos_praticos/"):

        propria = contexto["formacao_propria"]
        adversaria = contexto["formacao_adversaria"]

        if not propria or not adversaria:
            return False

        # Evita correspondências acidentais de números.
        padrao = (
            rf"(?<!\d){propria}"
            rf"[_-]+vs[_-]+"
            rf"{adversaria}(?!\d)"
        )

        return bool(re.search(padrao, nome))

    # 6. Documento antigo da saída de bola 3-5-2.
    if caminho == "saida_bola_352_duplo_pivo.md":

        return (
            contexto["formacao_propria"] == "352"
            and "saida_bola" in temas
        )

    return False


def selecionar_documentos(pergunta):
    """Seleciona documentos relevantes para a pergunta."""

    contexto = identificar_contexto(pergunta)
    documentos = []

    if not PASTA_CONHECIMENTO.is_dir():
        return contexto, documentos

    for ficheiro in sorted(
        PASTA_CONHECIMENTO.rglob("*.md")
    ):

        relativo = ficheiro.relative_to(
            PASTA_CONHECIMENTO
        ).as_posix()

        if documento_relevante(
            relativo,
            contexto,
            pergunta,
        ):
            documentos.append(ficheiro)

    return contexto, documentos


# ============================================================
# CARREGAMENTO DOS DOCUMENTOS
# ============================================================

def carregar_documentos(documentos):
    """
    Carrega os documentos selecionados.

    Devolve:
    - Texto para enviar ao modelo.
    - Conjunto dos caminhos reais dos documentos.
    """

    partes = []
    nomes = set()

    for ficheiro in documentos:

        relativo = ficheiro.relative_to(
            PASTA_CONHECIMENTO
        ).as_posix()

        conteudo = ficheiro.read_text(
            encoding="utf-8"
        ).strip()

        # Não enviar documentos vazios ao Qwen3.
        if not conteudo:
            continue

        nomes.add(relativo)

        partes.append(
            f"DOCUMENTO: {relativo}\n\n"
            f"{conteudo}"
        )

    conhecimento = "\n\n---\n\n".join(partes)

    return conhecimento, nomes


# ============================================================
# TESTES MANUAIS
# ============================================================

if __name__ == "__main__":

    perguntas = [
        "Como defender contra um 4-4-2 com a nossa equipa?",
        "Como sair a jogar no nosso 3-5-2?",
        "Explica os princípios do 4-3-3.",
        "Como atacar em 3-4-3?",
        "Como enfrentar um 4-3-3 em bloco médio?",
        "Como sair da pressão alta num 4-2-3-1?",
    ]

    for pergunta in perguntas:

        contexto, documentos = selecionar_documentos(
            pergunta
        )

        print("\n" + "=" * 60)
        print("PERGUNTA:", pergunta)
        print("CONTEXTO:", contexto)

        print("\nDOCUMENTOS SELECIONADOS:")

        conhecimento, nomes = carregar_documentos(
            documentos
        )

        if not nomes:
            print("- Nenhum documento com conteúdo.")

        for nome in sorted(nomes):
            print("-", nome)

        print(
            "\nTotal de documentos com conteúdo:",
            len(nomes),
        )

        print(
            "Caracteres de conhecimento:",
            len(conhecimento),
        )
