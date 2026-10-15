# Manifesto do pacote mínimo — apenas inventário e hashes locais

## R2: integridade e referências sem aprovação operacional

Aplicam-se as receitas ContentHash/ArtifactHash e TypedRef do
[contrato R2](VALIDADORES_CORRECOES_P1_P10.md) §4. Hashes dos três fontes abaixo
continuam SHA-256 dos bytes brutos, sem normalizar CRLF/LF; não foram recalculados.
Não confundir esse hash com ContentHash de um registo sem assinatura ou com
signed_payload_sha256. Documentos normativos R2 requerem hashes próprios fixados
externamente na futura política; manifesto formato1 e schemas2.0.0 são distintos.
Fixtures completas de forma usam placeholders claramente não verificados, nunca
substituem os hashes reais deste snapshot. Mantém-se NÃO APTO.

## Contrato de validação documental

SC-MANIFESTO 2.0.0 e a composição com os restantes validadores encontram-se em
[VALIDADORES_SCHEMAS.md](VALIDADORES_SCHEMAS.md). Os
[exemplos sintéticos](VALIDADORES_FIXTURES.md) usam hashes/tamanhos fictícios
intencionais e não substituem os três hashes locais abaixo. Não foram recalculados
hashes nem alterados os fontes nesta fase. Manifesto íntegro não prova origem,
configuração aplicada, comportamento real ou autorização operacional.
Referências de autorização/revisão/evidência são agora tipadas pelo
[contrato transversal P1–P10](VALIDADORES_CORRECOES_P1_P10.md). O manifesto de
fontes formato 1 abaixo mantém-se um artefacto distinto e incompleto, não um
bundle 2.0.0 nem uma aprovação. Nenhum hash de fonte foi recalculado nesta etapa.

## Gate de revisão host/guest

O manifesto integra o futuro VAL-MANIFESTO, descrito em
[HYPERV_VALIDADORES.md](HYPERV_VALIDADORES.md), sem implementação nesta fase.
Os três hashes anteriormente calculados não foram recalculados nesta revisão
documental; os fontes não foram alterados. Hashes corretos não aprovam imagem,
quota, canais ou lifecycle. Entradas/controlos e saídas exportáveis são allowlists
distintas; a allowlist do payload nunca autoriza exportar logs ou discos.
Importação por ISO read-only e exportação offline por appliance estão apenas
propostas, com riscos e autorizações próprios, sem qualquer transferência.

Estado: **NÃO APTO / incompleto para execução**. Três ficheiros de código foram
lidos e os seus bytes atuais sujeitos a SHA-256. Não foi criado ISO, arquivo,
imagem, VM ou pacote executável. Não foram importados os testes nesta fase.
Os valores abaixo não são hashes de credenciais; nenhum ficheiro secreto foi lido.

## Conteúdo explícito

Paths relativos à raiz ccdr-match-tracker, preservados exatamente no payload:

| Caminho relativo | Finalidade / justificação | Dependências |
| --- | --- | --- |
| docs/railway/read_only_probe.py | Código sob teste, importado pelo helper; indispensável para diagnóstico | Python stdlib, psycopg 3, SQLAlchemy 2 |
| docs/railway/tests/test_read_only_probe.py | Fornece probe, EXPECTED e environment importados pelo módulo de integração; necessário sem refatorar o harness | Ficheiro anterior, stdlib, psycopg, SQLAlchemy |
| docs/railway/tests/test_probe_postgresql_integration.py | Contém exatamente os oito casos de integração e lifecycle do cluster sintético | Ambos anteriores, Python stdlib, psycopg, SQLAlchemy, binários PostgreSQL na imagem |

```json
{
  "manifest_version": 1,
  "status": "NAO_APTO",
  "scope": "test-source-payload-only",
  "hash_algorithm": "SHA-256",
  "hash_mode": "raw-bytes-no-newline-normalization",
  "exact_file_count": 3,
  "file_type": "regular-file-only",
  "allow_symlinks_hardlinks_reparse_points": false,
  "allow_unlisted_files": false,
  "files": [
    {
      "path": "docs/railway/read_only_probe.py",
      "sha256": "ce1a66d8fb8adb098144553bfb8d8f5b432e7981557c8d3fa827fea14969dada"
    },
    {
      "path": "docs/railway/tests/test_read_only_probe.py",
      "sha256": "32d705dbffbb6c87f4b895584a3d5f79c7f5485a9d0c41c6417f74d2bdf201f7"
    },
    {
      "path": "docs/railway/tests/test_probe_postgresql_integration.py",
      "sha256": "81c40298576fdcc80457c39872fc1776cacdd7d60f5389810a3b4527d0178a68"
    }
  ],
  "image_sha256": null,
  "dependency_lock_sha256": null,
  "payload_iso_sha256": null,
  "approved_preflight_sha256": null,
  "reviewer_approval": null
}
```

O JSON é um bloco documental, não um manifesto já aprovado/importável. O futuro
ficheiro de controlo serializado é mantido fora da árvore payload, com hash
aprovado externamente para evitar autorreferência. O futuro ISO pode conter
`/payload/` (só estes três paths) e `/control/` (lista separada e exata de controlos
aprovados). Não incluir documentos inteiros por conveniência. O hash externo
do ISO cobre ambos; nenhum ficheiro extra em qualquer árvore é tolerado.
Qualquer novo preflight, unit file ou controlo acrescentado exige allowlist e
hash próprios; enquanto não existirem, a composição final está bloqueada.

### Alcance da análise de imports

O helper contém também testes unitários e referências a migrações num método
de teste, mas a importação não executa esse método. O runner futuro deve selecionar
**apenas a classe dos oito testes de integração**, com opt-in e failfast, sem
descoberta recursiva. Não se incluem migrações para satisfazer testes unitários
que não pertencem a este pacote. unittest/ast/importlib fazem parte da stdlib.

O código inclui identificadores, password-sentinela e URL de teste sintéticos;
não são credenciais reais nem endpoints de produção e não são reproduzidos
no manifesto. Os nomes de variáveis Railway nos helpers não implicam herança
do ambiente host: são dados sintéticos fornecidos em memória pelo teste.
O manifesto não atesta a configuração efetiva do futuro processo.

`test_disposable_cluster_safety.py` não é necessário para estes oito casos e
fica excluído. Os 52 testes simulados históricos pertencem à validação local
separada; não serão descobertos no guest como parte desta execução.

## Imagem e dependências — inventário ainda pendente

| Componente | Versão proposta | Hash/proveniência | Condição |
| --- | --- | --- | --- |
| Ubuntu Server amd64 | 24.04 LTS; release exata pendente | Não disponível localmente nesta revisão | Bloqueia execução |
| Python | 3.12; patch/build pendentes | Pendente | Bloqueia execução |
| PostgreSQL/binários cliente e servidor | 18.6 candidato | Artefactos Linux e libs pendentes | Bloqueia execução |
| psycopg e psycopg-binary | 3.3.6 candidatos | Wheels Linux/ABI/hashes pendentes | Bloqueia execução |
| SQLAlchemy | 2.0.54 candidato | Wheel/hash pendentes | Bloqueia execução |
| Transitivas, incluindo greenlet/typing-extensions se requeridas | Conforme resolução Linux exata aprovada | Lista transitiva/markers ainda não resolvidos | Bloqueia execução |
| libpq, OpenSSL, libc, kernel, systemd e restantes pacotes da imagem | Inventário completo exato pendente | SBOM/lock/hashes/proveniência pendentes | Bloqueia execução |
| Preflight, supervisor e unidade cgroup | Ainda não implementados | Código/hash/revisão pendentes | Bloqueia execução |

Não usar requirements-dev.txt/requirements.txt como lock: incluem intervalos e
componentes da aplicação não necessários. Não executar pip/apt nem resolver
dependências nesta fase. Futuramente preparar wheels/pacotes aprovados num
ambiente de build separado, sem segredos, e construir imagem sem instalar nada
durante o ensaio. Nomes/versões instalados têm de corresponder exatamente ao
lock Linux; qualquer dependência direta ou transitiva não aprovada faz recusar.

## Exclusões obrigatórias e política de recusa

Tudo o que não consta da allowlist é proibido, incluindo:

- .env e variantes; credenciais, tokens, chaves privadas, certificados privados,
  password files reais, cookies e perfis pessoais/CLI/cloud.
- URLs/configurações de produção, variáveis e configuração Railway, ficheiros
  de deployment, backend/.env, app/settings e acesso ao host.
- Backups, dumps, PGDATA existente, dados reais, bases SQLite, logs antigos,
  capturas brutas, relatórios com dados de utilizadores ou resíduos de ensaios.
- .git, .venv, __pycache__, .pyc, frontend, backend, migrações, ai-learning e
  ficheiros temporários/editor, thumbnails, metadados de sistema e streams ADS.
- Outros binários/scripts, links simbólicos/hard links, sockets, devices,
  paths absolutos/UNC, componentes `..`, nomes duplicados ou ambíguos por case,
  normalização Unicode ou separadores; rejeitar em vez de corrigir silenciosamente.

Directories estruturais estritamente necessários não contam como ficheiros
extras. O futuro validador deve enumerar todos os ficheiros/streams, não apenas
comparar três hashes conhecidos. Hash ausente/divergente, ficheiro extra, ficheiro
em falta ou falha de enumeração implica recusa. Git checkout/empacotamento pode
mudar CRLF/LF: isso invalida o hash; não normalizar nem aprovar automaticamente.

O manifesto e o código não podem aprovar-se a si próprios: revisor externo fixa
o hash dos controlos e da imagem fora do guest. Uma origem assinada/hash não
prova ausência de segredos nem segurança do conteúdo; exige revisão de conteúdo.
Sem rede/canais e limites comprovados pela especificação VM, hashes corretos
também não autorizam executar.

## Validação efetuada versus pendente

Efetuado nesta fase: leitura dos três fontes, análise estática dos imports e
nomes dos oito métodos, SHA-256 por leitura dos bytes locais. Não houve consulta
de credenciais, exportação de logs ou importação/execução Python dos fontes.

Pendente: validador de allowlist/paths/hashes, assinatura/aprovação independente,
lock Linux, imagem e controlos, ISO e inspeção host/guest. Os três hashes são
um snapshot do working tree, não prova de commit, build ou artefacto remoto.
O estado global mantém-se **NÃO APTO**.
