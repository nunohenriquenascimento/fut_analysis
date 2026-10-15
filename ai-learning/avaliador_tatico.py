
import re

from validador_tatico import (
    normalizar_sequencia,
    validar_sequencia,
)


def contem(texto, termos):
    """Procura termos completos ou expressões no texto."""

    return any(
        re.search(
            rf"(?<!\w){re.escape(termo)}(?!\w)",
            texto,
            flags=re.IGNORECASE,
        )
        for termo in termos
    )


def criar_criterio(nome, estado, explicacao):
    """Representa um resultado de avaliação."""

    return {
        "criterio": nome,
        "estado": estado,
        "explicacao": explicacao,
    }


def avaliar_tatica(pergunta, resposta):
    """
    Analisa indícios táticos na resposta.

    Não confirma automaticamente se os movimentos
    são viáveis dentro de campo.
    """

    resultados = []

    organizacao = resposta.get("organizacao", "")
    riscos = resposta.get("riscos", [])
    passes = resposta.get("passes", [])

    if not isinstance(organizacao, str):
        organizacao = ""

    if not isinstance(riscos, list):
        riscos = []

    texto_riscos = " ".join(
        risco for risco in riscos
        if isinstance(risco, str)
    )

    texto = f"{organizacao} {texto_riscos}"
    pergunta = pergunta.casefold()

    # 1. Formação solicitada.
    sistema = resposta.get("sistema_tatico", "")

    if not isinstance(sistema, str):
        sistema = ""

    formacao_correta = bool(
        re.search(r"(?<!\d)3[\s-]*5[\s-]*2(?!\d)", sistema)
    )

    resultados.append(criar_criterio(
        "Formação 3-5-2",
        "Cumpre" if formacao_correta else "Não cumpre",
        (
            "O sistema indicado é 3-5-2."
            if formacao_correta
            else "O sistema indicado não identifica o 3-5-2."
        ),
    ))

    # 2. Referência aos dois médios defensivos.
    tem_pivos = (
        contem(organizacao, ["MDC-E"])
        and contem(organizacao, ["MDC-D"])
    )

    resultados.append(criar_criterio(
        "Duplo pivô",
        "Cumpre" if tem_pivos else "Por confirmar",
        (
            "Ambos os MDC são identificados."
            if tem_pivos
            else "Falta identificar claramente os dois MDC."
        ),
    ))

    # 3. Presença do número 10.
    tem_mo10 = contem(
        organizacao,
        ["MO10", "número 10", "médio ofensivo"],
    )

    resultados.append(criar_criterio(
        "Número 10",
        "Cumpre" if tem_mo10 else "Por confirmar",
        (
            "O MO10 é considerado na organização."
            if tem_mo10
            else "O papel do MO10 não está suficientemente descrito."
        ),
    ))

    # 4. Resposta à pressão adversária.
    menciona_pressao = contem(
        texto,
        ["pressão", "pressionado", "pressionar", "marcação"],
    )

    explica_mecanismo = contem(
        organizacao,
        [
            "atrair", "fixar", "deslocar", "conduzir",
            "mudar o centro", "devolução", "ângulo",
            "apoio", "terceiro homem",
        ],
    )

    resultados.append(criar_criterio(
        "Resposta à pressão",
        (
            "Indícios presentes"
            if menciona_pressao and explica_mecanismo
            else "Por confirmar"
        ),
        (
            "A resposta menciona pressão e mecanismos de apoio "
            "ou deslocação. Falta confirmar a sua viabilidade."
            if menciona_pressao and explica_mecanismo
            else "Falta justificar melhor como a pressão é ultrapassada."
        ),
    ))

    # 5. Identificar passes interiores potencialmente fechados.
    sequencia = normalizar_sequencia(passes)
    interiores = {"MDC-E", "MDC-D", "MO10"}

    passes_interiores = []

    if sequencia is not None:
        for passe in sequencia:
            if passe is None:
                continue

            origem, destino = passe

            if destino.upper() in interiores:
                passes_interiores.append(
                    f"{origem} → {destino}"
                )

    linhas_fechadas = (
        "fech" in pergunta
        and contem(
            pergunta,
            ["interior", "interiores", "linha", "linhas"],
        )
    )

    justifica_abertura = contem(
        organizacao,
        [
            "sombra de pressão", "sai da sombra",
            "fora da sombra", "desmarcação",
            "deslocar", "arrastar", "libertar",
            "linha aberta", "ângulo de passe",
        ],
    )

    if linhas_fechadas and passes_interiores:
        estado = (
            "Indícios presentes"
            if justifica_abertura
            else "Por confirmar"
        )
        explicacao = (
            "Há passes interiores: "
            + ", ".join(passes_interiores)
            + ". "
            + (
                "A organização menciona mecanismos de abertura, "
                "mas é necessário confirmar cada linha."
                if justifica_abertura
                else "Não está suficientemente explicado como "
                "essas linhas ficaram disponíveis."
            )
        )
    else:
        estado = "Por confirmar"
        explicacao = (
            "Não foi identificado um passe interior condicionado "
            "pela pergunta; avaliar as linhas caso a caso."
        )

    resultados.append(criar_criterio(
        "Linhas de passe",
        estado,
        explicacao,
    ))

    # 6. Distinguir conservação de progressão.
    ha_progressao_explicada = contem(
        organizacao,
        [
            "ultrapassar a primeira linha",
            "superar a primeira linha",
            "ganhar metros",
            "progressão",
            "progredir",
        ],
    )

    resultados.append(criar_criterio(
        "Progressão",
        (
            "Indícios presentes"
            if ha_progressao_explicada
            else "Por confirmar"
        ),
        (
            "A resposta aborda progressão, mas é necessário "
            "confirmar se a sequência a concretiza."
            if ha_progressao_explicada
            else "A sequência pode apenas conservar a posse. "
            "Não está demonstrada progressão."
        ),
    ))

    # 7. Riscos e cobertura defensiva.
    menciona_cobertura = contem(
        texto,
        [
            "cobertura", "equilíbrio", "proteger",
            "proteção", "reação à perda",
        ],
    )

    tem_riscos = bool(texto_riscos.strip())

    resultados.append(criar_criterio(
        "Segurança e cobertura",
        (
            "Indícios presentes"
            if tem_riscos and menciona_cobertura
            else "Por confirmar"
        ),
        (
            "Existem riscos identificados e referências à "
            "proteção defensiva."
            if tem_riscos and menciona_cobertura
            else "Falta explicitar riscos e/ou quem assegura "
            "a cobertura em caso de perda."
        ),
    ))

    # Validação estrutural separada.
    erros_passes = validar_sequencia(passes)

    return {
        "estrutura_aprovada": not erros_passes,
        "erros_estrutura": erros_passes,
        "criterios": resultados,
        "avaliacao_humana_necessaria": True,
    }


def mostrar_avaliacao(relatorio):
    """Apresenta os resultados no terminal."""

    print("\nAVALIAÇÃO TÁTICA")

    for item in relatorio["criterios"]:
        print(
            f"\n{item['criterio']}: {item['estado']}"
        )
        print(f"  {item['explicacao']}")

    print("\nNota: avaliação heurística.")
    print("A viabilidade tática exige análise humana.")


if __name__ == "__main__":

    # Exemplo baseado no cenário B da documentação.
    pergunta = (
        "Os avançados fecham as linhas interiores "
        "e pressionam os centrais exteriores."
    )

    resposta = {
        "fase_jogo": "Saída de bola",
        "sistema_tatico": "3-5-2",
        "organizacao": (
            "DCE, DC e DCD mantêm apoios. "
            "MDC-E aproxima-se da bola e MDC-D "
            "preserva equilíbrio. MO10 oferece ligação. "
            "O ala pode devolver para escapar à pressão."
        ),
        "passes": [
            ["DC", "DCE"],
            ["DCE", "AE"],
            ["AE", "MDC-E"],
            ["MDC-E", "DCE"],
            ["DCE", "DC"],
        ],
        "riscos": [
            "Perda junto à linha",
            "MDC-E na sombra de pressão",
        ],
        "documentos_consultados": [
            "saida_bola_352_duplo_pivo.md"
        ],
    }

    relatorio = avaliar_tatica(pergunta, resposta)
    mostrar_avaliacao(relatorio)
