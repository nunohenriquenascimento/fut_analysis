# Importar fragmentos reais de jornadas FPF

A fixture `backend/tests/fixtures/fpf/fixture_677921.html` é a resposta original,
sem `og:url`, fornecida pelo operador para a jornada 1. Não deve ser alterada
para acrescentar identidade. SHA-256 dos bytes originais:
`e20e3e71962613bac8ad3015f6b2b4883c05394eb5b941fb176b57373b819bf4`.

## Fluxo no frontend

1. Selecionar o HTML da competição e o fragmento, ou usar uma competição FPF
   previamente importada.
2. No campo do fragmento, indicar o URL completo do pedido original:
   `https://resultados.fpf.pt/Competition/GetClassificationAndMatchesByFixture?fixtureId=677921`.
3. Validar os documentos e mapear as equipas existentes.
4. Rever o preview e confirmar com `SINCRONIZAR FPF`.

O URL é uma declaração explícita de proveniência do ADMIN. Um fragmento sem
identidade própria não permite comprovar criptograficamente de que pedido veio.
O sistema valida a origem HTTPS exata, a rota, um único `fixtureId`, a associação
no HTML da competição à época/série/jornada e a presença de todas as equipas da
série exatamente uma vez. Não usa o nome do ficheiro nem aceita um número de
jornada arbitrário. Se existir `og:url`, este tem de concordar com o URL declarado.

## Contrato de importação

`fixture_htmls` mantém compatibilidade com HTML completo e aceita objetos:

```json
{
  "html": "<corpo original da resposta>",
  "source_url": "https://resultados.fpf.pt/Competition/GetClassificationAndMatchesByFixture?fixtureId=677921",
  "competition_id": 30369,
  "season_id": 106,
  "series_id": 99718
}
```

O backend revalida o contexto no preview e na confirmação. A jornada é derivada
dos links da série confirmada. A origem e o contexto ficam na captura da jornada.

A resposta real contém 4–0 (#2682543), 5–0 (#2682545), 0–1 (#2682544) e um encontro
agendado sem ID. Datas como `3 out` e `1 nov 16:00` são preservadas como texto
parcial e mostradas no calendário/resultados/detalhes; não originam um ano ou
instante inventado. Os estádios são extraídos também dentro dos links de fichas.

Jogos sem `matchId` usam a identidade estável da competição/época/série/fixtureId
e dos IDs internos das equipas. Quando surgir o ID FPF, mantém-se a chave e o ID
local. Capturas simultâneas com resultados contraditórios são rejeitadas com
HTTP 409 antes de qualquer escrita. Resultados ligados a jogos internos continuam
a ser derivados dos eventos, sem alterações a jogos, jogadores ou convocatórias.

Não é necessária migração: continua a ser exigido Alembic `0008`. Nenhuma
consulta automática à FPF é feita ao importar um ficheiro.
