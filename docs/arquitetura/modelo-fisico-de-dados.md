# Modelo físico de dados

> Tabelas do domínio normalizado e do conhecimento (app `catalog`), como cada uma garante as invariantes e por quê. Complementa o [modelo conceitual](modelo-de-dominio.md); a camada de fontes está no [registro de implementação](../implementacao/README.md).

**Estado:** Consolidado em 24/10/2026 (fatias 2a a 2c; decisão no [ADR 0003](decisoes/0003-regras-como-dados.md)).

## Princípio: toda afirmação cita fonte e trecho

Cada linha que afirma algo em nome de um órgão (procedimento, requisito, canal, custo, prazo, regra, dependência) tem:

- `snapshot` — FK obrigatória para `SourceSnapshot` (a versão coletada da fonte, RN01);
- `excerpt` — trecho literal da fonte que fundamenta a afirmação.

Na carga, o trecho é procurado no texto da versão coletada (HTML sem tags ou valores de texto do JSON, com espaços normalizados). Se não for encontrado, a carga falha.

**Por quê:** a FK prova que existe uma fonte, mas não que ela diz aquilo. O trecho torna a afirmação verificável por terceiros e faz a carga falhar quando a página muda e o trecho deixa de existir. Isso obriga uma nova revisão em vez de manter uma orientação desatualizada em silêncio (pipeline, passo 10).

## Tabelas

| Model | Campos principais | Observações |
| --- | --- | --- |
| `Situation` | `slug`, `title`, `candidates` M2M → `Procedure` | Entrada da jornada (RF01). |
| `Question` | `slug`, `text`, `kind` (`SINGLE`/`MULTIPLE`), `allows_unknown`, `order`, `situations` M2M | Reutilizável entre situações. `order` só desempata a próxima pergunta. |
| `AnswerOption` | `question` FK, `slug`, `label`, `out_of_coverage` (padrão falso) | Único por (`question`, `slug`). "Não sei" **não** é opção: é `allows_unknown` e mantém o fato desconhecido (RN03). `out_of_coverage` marca resposta sem orientação oficial nesta versão: continua sendo oferecida e o plano exibe um aviso de limite de cobertura, sem alterar a avaliação das regras. |
| `Procedure` | `slug`, `title`, `description`, `agency` FK, `jurisdiction`, `clarifies` FK → `Question` (nulo), citação | Com `clarifies` preenchido, é um **esclarecimento intermediário**: entra no plano quando aquela pergunta foi respondida com "não sei". |
| `ProcedureDetail` | `procedure` FK, `kind` (`COST`/`DEADLINE`), `text`, citação | Único por (`procedure`, `kind`). Sem linha = "não informado" (RN11). |
| `Requirement` | `procedure` FK, `description`, citação | Requisitos parecidos não são unificados. |
| `ServiceChannel` | `procedure` FK, `kind` (`ONLINE`/`IN_PERSON`/`PHONE`/`APP`/`EMAIL`), `description`, `url`, citação | Alternativa presencial documentada (RN14). |
| `Rule` | `slug`, `procedure` FK (nulo), `explanation`, citação | Conjunção (E) das suas condições. Com `procedure`, define a aplicabilidade. Sem `procedure`, é a condição de uma dependência condicional. |
| `Condition` | `rule` FK, `question` FK, `operator` (`ANY_OF`/`NONE_OF`), `options` M2M → `AnswerOption` | As opções pertencem à pergunta (validado na carga). |
| `Dependency` | `before` FK, `after` FK, `kind` (`MANDATORY`/`CONDITIONAL`/`RECOMMENDED`), `rule` FK (nulo), citação | Check: `rule` preenchida se e somente se `CONDITIONAL`. Único por (`before`, `after`), com `before ≠ after`. |
| `TriageNode` | `slug`, `text`, `help_text` | Pergunta ampla do funil de triagem (RF21). Encaminhamento, sem citação (RN02; [ADR 0005](decisoes/0005-funil-de-triagem.md)). O nó `inicio` é a página inicial. |
| `TriageChoice` | `node` FK, `label`, `order`, `next_node` FK → `TriageNode` (nulo), `situation` FK → `Situation` (nulo) | Único por (`node`, `order`). Check: no máximo um destino; ambos nulos = fora da cobertura. A carga apaga os nós antes das situações. |

`Agency` e `Jurisdiction` vêm da app `sources`.

## Semântica de avaliação (detalhada no [ADR 0003](decisoes/0003-regras-como-dados.md))

- Condição sobre um fato ausente ou "não sei" → `UNDETERMINED`.
- `ANY_OF`: alguma opção escolhida está na lista. `NONE_OF`: nenhuma opção escolhida está na lista.
- Regra = E das condições; procedimento = OU das suas regras (lógica de três valores de Kleene). Um candidato sem regras é aplicável.

## Carga de conteúdo

| Passo | Comando | Arquivo |
| --- | --- | --- |
| 1. Órgãos e fontes | `load_sources` | `content/sources.toml` |
| 2. Coleta | `fetch_sources` | — |
| 3. Situações, perguntas, procedimentos, regras e dependências | `load_content` | `content/<jornada>.toml` |

- `load_sources` faz upsert por `slug`. Fontes não são apagadas, porque importações e snapshots dependem delas.
- `load_content` substitui todo o conteúdo do `catalog` em uma única transação. **Por quê:** a sessão do cidadão guarda slugs, não IDs. A substituição total evita regras ou procedimentos órfãos quando algo sai dos arquivos, e qualquer erro desfaz tudo.
- Cada citação usa a versão mais recente coletada com sucesso da fonte referenciada. Se a fonte nunca foi coletada, a carga falha.
- Validações: referências por slug existentes, opções pertencentes à pergunta da condição, trecho presente na fonte, regra de dependência sem `procedure`, e grafo de dependências sem ciclo (o ciclo é verificado sobre todas as arestas, inclusive as recomendadas).

## Fora desta fase

- **Aviso de "fora da cobertura"** (documento sem fonte oficial no recorte): fica para a Fase 5, junto com a jornada de perda de documentos, que é onde ele aparece.
- **Divergências entre fontes** (RN13, RF20): por ora são registradas como comentário no arquivo TOML e na matriz de evidências. Ainda não há tabela própria.
- **Data de revisão editorial**: a carga não registra quem revisou nem quando. A verificação do trecho cobre a mudança de conteúdo da fonte.
