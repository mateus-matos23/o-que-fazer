# ADR 0003 — Regras e dependências como dados citados, carregados de arquivos versionados

**Estado:** Aceito. Abordagem aprovada pelo autor em 24/10/2026. Implementada nas fatias 2a a 2c.
**Data:** 24/10/2026

## Contexto

O [ADR 0002](0002-motor-baseado-em-regras.md) adotou um motor baseado em conhecimento explícito, mas deixou em aberto como representar regras e dependências (pendência 8). A representação precisa:

- fazer cada regra apontar para a sua fonte (RN01, RF15);
- explicar a etapa ao cidadão (RF19);
- tratar "não sei" sem convertê-lo em negativa (RN03, RN04);
- permitir derivar a próxima pergunta das próprias regras;
- ser revisável por quem não programa e reproduzível no banco de teste.

## Decisão

1. **Regras são dados, não código.**
   - Uma `Rule` é a conjunção (E) de `Condition`s.
   - Cada condição referencia uma `Question`, usa um operador (`ANY_OF` ou `NONE_OF`) e lista `AnswerOption`s dessa pergunta.
   - Um procedimento é aplicável se alguma das suas regras for aplicável (OU).
   - Os conectivos E e OU seguem a lógica de três valores de Kleene.
   - Uma condição sobre um fato ausente ou respondido com "não sei" resulta em `UNDETERMINED`.
   - Um candidato sem regras é aplicável.
2. **"Não sei" não é opção de resposta.** É indicado por `Question.allows_unknown` e mantém o fato desconhecido. Os slugs `nao-sei` e `unknown` são reservados e recusados na carga.
3. **Esclarecimento intermediário** é um `Procedure` com `clarifies` apontando para uma pergunta que aceita "não sei".
   - Ele não é candidato da situação.
   - Entra no plano quando aquela pergunta foi respondida com "não sei".
   - Motivo: se fosse candidato sem regra, apareceria sempre, inclusive para quem já sabe a resposta.
4. **Dependências** são arestas `before → after`, com tipo `MANDATORY`, `CONDITIONAL` (exige uma `Rule` sem procedimento) ou `RECOMMENDED`.
   - A ordenação usa Kahn em camadas, desempatada por slug (`guidance/engine/ordering.py`).
   - Na carga, o ciclo é recusado sobre todas as arestas, inclusive as recomendadas. O erro lista só os procedimentos que formam o ciclo (invariante 5).
5. **Toda afirmação cita `snapshot` e `excerpt` literal.**
   - A carga procura o trecho no texto normalizado da versão coletada com sucesso mais recente.
   - Se não encontrar, falha.
6. **O conteúdo fica em TOML versionado** em `content/`, lido com `tomllib`. A carga é feita por comandos:
   - `load_sources` faz upsert de órgãos e fontes;
   - `fetch_sources` faz a coleta;
   - `load_content` valida tudo e só então substitui o `catalog` inteiro em uma transação.
   - O Django Admin é somente leitura.

## Alternativas consideradas

| Alternativa | Motivo da rejeição |
| --- | --- |
| Regras como funções Python por procedimento | Não citam fonte, não são revisáveis por quem não programa e impedem derivar a próxima pergunta das condições. |
| Expressões em texto (mini-linguagem ou `eval`) | Exige parser próprio e validação semântica, e abre risco de injeção. Não ganha nada sobre condições estruturadas no recorte atual. |
| Motor de regras externo (biblioteca) | Dependência nova para um problema pequeno; a lógica de Kleene, com poucas dezenas de regras, cabe em poucas linhas. |
| Edição pelo Django Admin | A mudança de conteúdo deixaria de ser revisável por `git diff` e reproduzível no banco de teste. |
| "Não sei" como opção comum | Permitiria regras que tratam desconhecido como resposta (por exemplo, `NONE_OF` aplicável), o que viola RN03. |
| Upsert incremental do catálogo | A sessão guarda slugs. Um item removido dos arquivos ficaria órfão no banco. A substituição total é simples e atômica. |

## Consequências

- **A verificação do trecho funciona em fontes reais.** Na primeira carga contra as páginas do gov.br, ela encontrou trechos que não batiam. A causa era a extração de HTML, que separava a pontuação ("gratuita ,"); a normalização foi corrigida. Quando uma página mudar e o trecho sumir, a carga falha e obriga uma nova revisão.
- **A autoria passa a ser mais trabalhosa.** Uma afirmação sem trecho literal documentado fica fora do conteúdo e vira pendência. Exemplo: o prazo de 48 h por e-mail na jornada CPF irregular.
- **O ciclo é detectado na carga.** O motor (Fase 3) reutiliza a mesma ordenação.
- **Ponto em aberto para a Fase 3:** um pré-requisito `MANDATORY` de um procedimento aplicável que não está entre os candidatos entra no plano? Proposta: entra se não for `NOT_APPLICABLE`, com a indicação "necessário para X".
- **Limitações:**
  - Divergências entre fontes (RN13) ficam como comentário no TOML, sem tabela própria.
  - Não se registra quem revisou o conteúdo nem quando.
