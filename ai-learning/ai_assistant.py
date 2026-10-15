
import json
import re
from pathlib import Path

import requests

from validador_tatico import (
    normalizar_sequencia,
    validar_sequencia,
)


# Configuração do Ollama e do projeto.
OLLAMA_URL = "http://localhost:11434/api/chat"
MODELO = "qwen3:8b"

PASTA_CONHECIMENTO = (
    Path(__file__).resolve().parent / "conhecimento"
)

TIMEOUT_SEGUNDOS = 180
MAX_HISTORICO = 12
MAX_CORRECOES = 1


# Campos obrigatórios da resposta.
CAMPOS_TEXTO = (
    "fase_jogo",
    "sistema_tatico",
    "organizacao",
)

CAMPOS_LISTA = (
    "passes",
    "riscos",
    "documentos_consultados",
)


# Estrutura JSON solicitada diretamente ao Ollama.
ESQUEMA_RESPOSTA = {
    "type": "object",
    "properties": {
        "fase_jogo": {
            "type": "string"
        },
        "sistema_tatico": {
            "type": "string"
        },
        "organizacao": {
            "type": "string"
        },
        "passes": {
            "type": "array",
            "items": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 2,
                "maxItems": 2,
            },
        },
        "riscos": {
            "type": "array",
            "items": {"type": "string"},
        },
        "documentos_consultados": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "fase_jogo",
        "sistema_tatico",
        "organizacao",
        "passes",
        "riscos",
        "documentos_consultados",
    ],
    "additionalProperties": False,
}


def carregar_conhecimento():
    """Carrega os documentos Markdown da pasta conhecimento."""

    if not PASTA_CONHECIMENTO.exists():
        print("Aviso: pasta de conhecimento não encontrada.")
        return "", set()

    documentos = []
    nomes = set()

    for ficheiro in sorted(PASTA_CONHECIMENTO.glob("*.md")):

        conteudo = ficheiro.read_text(
            encoding="utf-8"
        ).strip()

        if not conteudo:
            continue

        nomes.add(ficheiro.name)

        documentos.append(
            f"Documento: {ficheiro.name}\n{conteudo}"
        )

    if documentos:
        print("Conhecimento tático carregado com sucesso.")
        print("Documentos:", ", ".join(sorted(nomes)))
    else:
        print("Aviso: não existem documentos táticos.")

    return "\n\n".join(documentos), nomes


def criar_sistema(conhecimento, nomes):
    """Constrói as instruções do assistente tático."""

    nomes_texto = ", ".join(sorted(nomes)) or "Nenhum"

    return f"""
És um assistente especializado em análise tática de futebol.

Responde sempre em português europeu.
Utiliza terminologia futebolística de Portugal.

Terminologia:
- Guarda-redes, nunca goleiro.
- Médio defensivo, nunca volante.
- Médio ofensivo, nunca volante.
- DCE e DCD são defesas centrais exteriores, não laterais.
- DC é o defesa central do meio.
- MDC-E e MDC-D formam o duplo pivô.
- MO10 é o médio ofensivo, ou número 10.

Utiliza a documentação tática como referência principal.
Se a informação for insuficiente, identifica as limitações.

Regras:
- Respeita a formação solicitada pelo treinador.
- Mantém as posições definidas na documentação.
- Não substituas os dois MDC por MIE e MID.
- Distingue receção de bola de passe.
- Quando forem pedidos cinco passes, apresenta cinco passes.
- Cada passe começa no jogador que recebeu o anterior.
- Não cries autopasses.
- Explica como se abrem linhas de passe inicialmente fechadas.
- Não assumes que um passe interior está disponível.
- Identifica os riscos e as alternativas.
- Distingue conservação, atração e progressão.
- Preenche todos os campos obrigatórios.
- Usa apenas nomes de documentos realmente fornecidos.

Documentos disponíveis: {nomes_texto}

Devolve APENAS um objeto JSON válido.

O objeto deve conter exatamente estas propriedades:
- fase_jogo: texto
- sistema_tatico: texto
- organizacao: texto
- passes: lista de pares [origem, destino]
- riscos: lista de textos
- documentos_consultados: lista de nomes de ficheiros

Exemplo de formato:

{{
  "fase_jogo": "Saída de bola",
  "sistema_tatico": "3-5-2",
  "organizacao": "Explicação tática da solução.",
  "passes": [
    ["DC", "DCE"],
    ["DCE", "DC"]
  ],
  "riscos": [
    "Risco identificado."
  ],
  "documentos_consultados": [
    "nome_real_do_documento.md"
  ]
}}

O exemplo serve apenas para demonstrar o formato.
Não o copies automaticamente como solução.

Quando não forem pedidos passes, utiliza [].

Documentação tática:
{conhecimento}
""".strip()


def extrair_json(texto):
    """Converte a resposta do modelo num dicionário Python."""

    # Remove eventuais blocos de raciocínio presentes no texto.
    texto = re.sub(
        r"<think>.*?</think>",
        "",
        texto,
        flags=re.DOTALL,
    ).strip()

    # Remove blocos Markdown, caso sejam devolvidos.
    if texto.startswith("```"):
        texto = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            texto,
            flags=re.IGNORECASE,
        ).strip()

    dados = json.loads(texto)

    if not isinstance(dados, dict):
        raise ValueError(
            "A resposta não é um objeto JSON."
        )

    return dados


def pedir_resposta(mensagens):
    """Envia as mensagens ao Ollama e obtém a resposta."""

    resposta = requests.post(
        OLLAMA_URL,
        json={
            "model": MODELO,
            "messages": mensagens,
            "stream": False,
            "think": True,
            "format": ESQUEMA_RESPOSTA,
            "options": {
                "temperature": 0.3,
            },
        },
        timeout=TIMEOUT_SEGUNDOS,
    )

    resposta.raise_for_status()

    dados = resposta.json()

    modelo = dados.get("model", "desconhecido")
    mensagem = dados.get("message") or {}
    conteudo = mensagem.get("content", "")
    motivo = dados.get("done_reason")

    if not isinstance(conteudo, str) or not conteudo.strip():
        raise ValueError(
            "O modelo devolveu uma resposta vazia. "
            f"Motivo: {motivo or 'desconhecido'}."
        )

    if motivo not in (None, "stop"):
        raise ValueError(
            f"A geração foi interrompida: {motivo}."
        )

    return modelo, conteudo


def pergunta_pede_cinco_passes(pergunta):
    """Deteta pedidos explícitos de cinco passes."""

    pergunta = pergunta.casefold()

    return bool(
        re.search(
            r"\b(cinco|5)\s+passes\b",
            pergunta,
        )
        or re.search(
            r"\b(cinco|5)\s+transmissões\b",
            pergunta,
        )
    )


def validar_resposta(dados, validar_passes, nomes_documentos):
    """Verifica os campos obrigatórios e a sequência."""

    erros = []

    # Verificar os campos de texto.
    for campo in CAMPOS_TEXTO:

        valor = dados.get(campo)

        if not isinstance(valor, str) or not valor.strip():
            erros.append(
                f"Campo obrigatório inválido: {campo}."
            )

    # Verificar os campos que devem conter listas.
    for campo in CAMPOS_LISTA:

        if not isinstance(dados.get(campo), list):
            erros.append(
                f"Campo obrigatório inválido: {campo}."
            )

    # Verificar os riscos.
    riscos = dados.get("riscos")

    if isinstance(riscos, list):
        if not all(
            isinstance(risco, str) and risco.strip()
            for risco in riscos
        ):
            erros.append(
                "A lista de riscos contém valores inválidos."
            )

    # Confirmar que os documentos indicados existem.
    documentos = dados.get("documentos_consultados")

    if isinstance(documentos, list):

        if not all(
            isinstance(documento, str)
            for documento in documentos
        ):
            erros.append(
                "A lista de documentos contém valores inválidos."
            )

        else:
            desconhecidos = [
                documento
                for documento in documentos
                if documento not in nomes_documentos
            ]

            if desconhecidos:
                erros.append(
                    "O modelo indicou documentos não carregados."
                )

    # Validar os cinco passes quando foram pedidos.
    if validar_passes:
        erros.extend(
            validar_sequencia(
                dados.get("passes", [])
            )
        )

    return erros



def gerar_resposta_com_correcao(
    mensagens,
    validar_passes,
    nomes,
):
    """Gera, valida e tenta corrigir a resposta do modelo."""

    # 1. Gerar a primeira resposta.
    modelo, conteudo = pedir_resposta(mensagens)
    dados = extrair_json(conteudo)

    erros = validar_resposta(
        dados,
        validar_passes,
        nomes,
    )

    houve_correcao = False

    # Diagnóstico dos campos que têm apresentado problemas.
    print("\n[DIAGNÓSTICO] Primeira resposta:")
    print("Documentos:", dados.get("documentos_consultados"))
    print("Passes:", dados.get("passes"))
    print("Erros:", erros)

    # 2. Tentar corrigir os erros, se existirem.
    for _ in range(MAX_CORRECOES):

        if not erros:
            break

        print("\nForam encontrados erros na resposta:")

        for erro in erros:
            print(f"- {erro}")

        print("\nA solicitar uma correção ao modelo...")

        # Mostrar os nomes exatos permitidos.
        documentos_validos = sorted(nomes)

        instrucao = (
            "A tua resposta JSON contém os seguintes erros:\n"
            + "\n".join(f"- {erro}" for erro in erros)
            + "\n\nCorrige APENAS os campos inválidos."
            + "\nPreserva os campos que já estão corretos."
            + "\nNão elimines passes válidos."
            + "\nNão alteres a formação tática."
            + "\nNão alteres a organização sem necessidade."
            + "\nMantém português europeu."
            + "\nCada passe deve ter o formato [origem, destino]."
            + "\nO destinatário de um passe inicia o seguinte."
            + "\nSe foram pedidos cinco passes, mantém cinco."
            + "\nDocumentos permitidos: "
            + json.dumps(documentos_validos, ensure_ascii=False)
            + "\nUsa apenas nomes exatos de documentos permitidos."
            + "\nSe nenhum documento foi utilizado, indica []."
            + "\nDevolve o objeto JSON completo, "
            "com todos os campos obrigatórios."
        )

        # 3. Enviar a resposta anterior para correção.
        mensagens_correcao = [
            *mensagens,
            {
                "role": "assistant",
                "content": conteudo,
            },
            {
                "role": "user",
                "content": instrucao,
            },
        ]

        try:
            novo_modelo, novo_conteudo = pedir_resposta(
                mensagens_correcao
            )

            novos_dados = extrair_json(
                novo_conteudo
            )

            # Validar antes de aceitar a nova resposta.
            novos_erros = validar_resposta(
                novos_dados,
                validar_passes,
                nomes,
            )

        except (requests.RequestException, ValueError) as erro:
            print(
                "Não foi possível concluir a correção: "
                f"{type(erro).__name__}"
            )
            break

        houve_correcao = True

        print("\n[DIAGNÓSTICO] Resposta corrigida:")
        print(
            "Documentos:",
            novos_dados.get("documentos_consultados")
        )
        print(
            "Passes:",
            novos_dados.get("passes")
        )
        print("Erros:", novos_erros)

        # 4. Comparar a qualidade estrutural das respostas.
        # Uma correção só é aceite se reduzir os erros.
        if len(novos_erros) < len(erros):

            modelo = novo_modelo
            conteudo = novo_conteudo
            dados = novos_dados
            erros = novos_erros

            print(
                "\nA correção melhorou a resposta "
                "e foi aceite."
            )

        else:
            print(
                "\nA correção não melhorou a resposta. "
                "Foi mantida a versão anterior."
            )

    return (
        modelo,
        conteudo,
        dados,
        erros,
        houve_correcao,
    )



def mostrar_resposta(
    dados,
    validar_passes,
    erros,
    houve_correcao,
):
    """Apresenta a resposta final e o resultado da validação."""

    print("\nAI Assistant:")

    print(
        "\nFase do jogo:",
        dados.get("fase_jogo") or "Não indicada",
    )

    print(
        "Sistema tático:",
        dados.get("sistema_tatico") or "Não indicado",
    )

    print("\nOrganização:")
    print(
        dados.get("organizacao") or "Não indicada"
    )

    if validar_passes:

        print("\nSequência de passes:")

        passes = normalizar_sequencia(
            dados.get("passes")
        )

        if passes is None:
            print("Formato de sequência inválido.")

        else:
            for i, passe in enumerate(passes, start=1):

                if passe is None:
                    print(f"{i}. Formato inválido.")

                else:
                    print(
                        f"{i}. {passe[0]} → {passe[1]}"
                    )

    # Mostrar a validação mesmo quando não foram pedidos passes.
    if erros:

        print("\nValidação da resposta: REPROVADA")

        for erro in erros:
            print(f"- {erro}")

    else:
        print("\nValidação da resposta: APROVADA")

        if validar_passes:
            print(
                "A sequência passou a validação estrutural."
            )

    if houve_correcao:
        print("Foi realizada uma tentativa de correção.")

    if validar_passes:
        print("A coerência tática requer avaliação humana.")

    print("\nRiscos:")

    riscos = dados.get("riscos", [])

    if isinstance(riscos, list):
        for risco in riscos:
            print(f"- {risco}")

    print(
        "\nDocumentos indicados pelo modelo:",
        dados.get("documentos_consultados", []),
    )


def main():
    """Inicia o assistente e mantém a conversa no terminal."""

    conhecimento, nomes = carregar_conhecimento()

    sistema = criar_sistema(
        conhecimento,
        nomes,
    )

    historico = []

    print(f"\nAssistente iniciado com {MODELO}.")
    print("Escreve 'sair' para terminar.\n")

    while True:

        try:
            pergunta = input("Tu: ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nConversa terminada.")
            break

        if pergunta.casefold() in {
            "sair",
            "exit",
            "quit",
        }:
            break

        if not pergunta:
            continue

        mensagens = [
            {
                "role": "system",
                "content": sistema,
            },
            *historico,
            {
                "role": "user",
                "content": pergunta,
            },
        ]

        validar_passes = pergunta_pede_cinco_passes(
            pergunta
        )

        print("\nA analisar...")

        try:
            (
                modelo,
                conteudo,
                dados,
                erros,
                houve_correcao,
            ) = gerar_resposta_com_correcao(
                mensagens,
                validar_passes,
                nomes,
            )

            print(f"Modelo utilizado: {modelo}")

            mostrar_resposta(
                dados,
                validar_passes,
                erros,
                houve_correcao,
            )

            # Guardar apenas respostas aprovadas.
            if not erros:

                historico.extend([
                    {
                        "role": "user",
                        "content": pergunta,
                    },
                    {
                        "role": "assistant",
                        "content": conteudo,
                    },
                ])

                historico = historico[-MAX_HISTORICO:]

        except requests.Timeout:
            print(
                "O Ollama demorou demasiado a responder."
            )

        except requests.RequestException as erro:
            print(
                "Erro de comunicação com o Ollama: "
                f"{type(erro).__name__}"
            )

        except (ValueError, TypeError, KeyError) as erro:
            print(
                f"Erro ao interpretar a resposta: {erro}"
            )

        print()


if __name__ == "__main__":
    main()
