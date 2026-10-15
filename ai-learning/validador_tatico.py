
def normalizar_passe(passe):
    """Converte um passe para o formato (origem, destino)."""

    # Aceita dicionários devolvidos pelo modelo.
    if isinstance(passe, dict):
        if set(passe) != {"origem", "destino"}:
            return None

        valores = (passe["origem"], passe["destino"])

    # Aceita listas ou tuplos com dois jogadores.
    elif isinstance(passe, (list, tuple)) and len(passe) == 2:
        valores = passe

    else:
        return None

    # Ambos os jogadores devem ter nomes válidos.
    if not all(
        isinstance(jogador, str) and jogador.strip()
        for jogador in valores
    ):
        return None

    return tuple(jogador.strip() for jogador in valores)


def normalizar_sequencia(sequencia):
    """Normaliza todos os passes de uma sequência."""

    if not isinstance(sequencia, list):
        return None

    return [
        normalizar_passe(passe)
        for passe in sequencia
    ]


def validar_sequencia(sequencia, numero_esperado=5):
    """
    Verifica quantidade, formato, autopasses e continuidade.

    Esta função valida a estrutura, não a qualidade tática.
    """

    if not isinstance(sequencia, list):
        return ["A sequência de passes não é uma lista."]

    erros = []

    # Verificar o número de passes.
    if len(sequencia) != numero_esperado:
        erros.append(
            f"Esperados {numero_esperado} passes, "
            f"mas foram encontrados {len(sequencia)}."
        )

    passes = normalizar_sequencia(sequencia)

    # Verificar cada passe individualmente.
    for i, passe in enumerate(passes, start=1):

        if passe is None:
            erros.append(f"Passe {i}: formato inválido.")
            continue

        origem, destino = passe

        if origem.casefold() == destino.casefold():
            erros.append(
                f"Passe {i}: {origem} passa a bola a si próprio."
            )

    # O destinatário de um passe inicia o seguinte.
    for i in range(len(passes) - 1):

        atual = passes[i]
        seguinte = passes[i + 1]

        if atual is None or seguinte is None:
            continue

        if atual[1].casefold() != seguinte[0].casefold():
            erros.append(
                f"Falta de continuidade entre os passes "
                f"{i + 1} e {i + 2}."
            )

    return erros


if __name__ == "__main__":

    # Teste com dicionários.
    exemplo_dicionarios = [
        {"origem": "DC", "destino": "DCE"},
        {"origem": "DCE", "destino": "DC"},
        {"origem": "DC", "destino": "DCD"},
        {"origem": "DCD", "destino": "AD"},
        {"origem": "AD", "destino": "MDC-D"},
    ]

    # Teste com listas.
    exemplo_listas = [
        ["DC", "DCE"],
        ["DCE", "DC"],
        ["DC", "DCD"],
        ["DCD", "AD"],
        ["AD", "MDC-D"],
    ]

    # Teste que deve reprovar por falta de continuidade.
    exemplo_invalido = [
        ["DC", "DCE"],
        ["DCD", "DC"],
        ["DC", "DCD"],
        ["DCD", "AD"],
        ["AD", "MDC-D"],
    ]

    exemplos = [
        ("Dicionários", exemplo_dicionarios),
        ("Listas", exemplo_listas),
        ("Sequência inválida", exemplo_invalido),
    ]

    for nome, exemplo in exemplos:
        erros = validar_sequencia(exemplo)

        print(f"\nTeste: {nome}")

        if erros:
            for erro in erros:
                print(f"- {erro}")
        else:
            print("APROVADO")
