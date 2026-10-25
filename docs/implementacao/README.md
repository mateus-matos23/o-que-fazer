# Registro de implementação

> O que foi implementado, em que estado está e por que cada decisão foi tomada. Atualizado a cada fatia.

## Propósito

Este registro acompanha a implementação do protótipo. Para cada fase, mostra o estado atual, o que existe no código e as decisões que o justificam, para que quem entrar no projeto consiga entender o código sem acompanhar as conversas que o originaram. A especificação do produto e da arquitetura continua em [docs/](../README.md); aqui fica o que foi efetivamente construído.

## Abordagem

A implementação segue um caminho de núcleo primeiro:

1. fontes oficiais e proveniência;
2. domínio normalizado e conteúdo curado;
3. motor de regras;
4. fluxo mínimo HTTP.

Interface, UI/UX, acessibilidade e frontend ficam para a última fase.

Motivo: o fundamental do produto são as fontes heterogêneas, a modelagem do conhecimento e o motor de orientação. A interface depende de tudo isso; construí-la antes significaria desenhar telas sobre um modelo que ainda pode mudar.

## Fases

| Fase | Escopo | Estado |
| --- | --- | --- |
| 0 | Fundação | Consolidado (commit `e57fcbf`) |
| 1 | Fontes e proveniência (app `sources`) | Consolidado (commits `bc4a2c0`, `8c21ca0`, `8f3c093`) |
| 2 | Domínio normalizado, conhecimento e carregador de conteúdo (app `catalog`, comandos `load_sources`/`load_content`, jornada CPF irregular, ADR 0003) | Consolidado |
| 3 | Motor de orientação (`guidance/engine`, Python puro: avaliação ternária, próxima pergunta, plano em camadas com Kahn; `guidance/repository.py`) | Consolidado (commits `3b957cb`, `90969f6`, `a12eaa1`) |
| 4 | Fluxo mínimo HTTP com templates Django sem estilo e sessão Django | Pendente |
| 5 | Jornadas desligamento do trabalho e perda de documentos | Pendente |
| 6 | UI/UX, acessibilidade, frontend, RF18 e RF02 | Pendente |

## Decisões tomadas em 24/10/2026 (aprovadas pelo autor)

1. **Regras como dados.** Cada regra é um `Rule` composto por `Condition`s, e cada condição pode referenciar uma pergunta, usar o operador `ANY_OF` ou `NONE_OF` e listar opções. A avaliação é ternária e feita em Python puro. Motivo: a regra fica auditável e ligada à fonte, e a próxima pergunta pode ser derivada das condições. Será formalizada no ADR 0003.
2. **Conteúdo curado em arquivos TOML versionados** em `content/`, lidos com `tomllib` (biblioteca padrão, sem dependência nova) e carregados por um comando idempotente que valida tudo antes de gravar. O Django Admin fica só para consulta. Motivo: a mudança de conteúdo é revisável por `git diff` e reproduzível no banco de teste.
3. **Sessão do cidadão na sessão do Django**, sem tabela própria e com expiração curta (`SESSION_COOKIE_AGE` de 2 horas). Motivo: minimização de dados (RN15).
4. **Toda afirmação cita fonte e trecho literal**, verificado na carga contra a versão coletada; carga em três comandos (`load_sources` → `fetch_sources` → `load_content`) e substituição total do conteúdo do `catalog` em uma transação. Motivo e detalhes em [modelo físico de dados](../arquitetura/modelo-fisico-de-dados.md).
5. **Ferramentas:** `psycopg[binary]`, `pytest` com `pytest-django`, `ruff`, `mypy` em modo estrito com `django-stubs`.

## Fase 0 — Fundação

- `requires-python = ">=3.15"` em `pyproject.toml`.
- O boilerplate gerado pelo `uv init` (layout `src/o_que_fazer`, `[project.scripts]` e `[build-system]`) foi removido. O projeto é uma aplicação Django, não uma biblioteca instalável.
- Projeto Django em `config/`.
- Configuração por variáveis de ambiente lidas com `os.environ`, sem `django-environ`. Os comandos são executados com `uv run --env-file .env`.
- PostgreSQL 18 via `docker compose` (`docker-compose.yml`). Não há PostgreSQL instalado na máquina de desenvolvimento.
- Banco de desenvolvimento `oqf_dev` e banco de teste `oqf_test`. O banco de teste é criado e destruído pelo `pytest-django`.
- `LANGUAGE_CODE = "pt-br"` e `TIME_ZONE = "America/Fortaleza"`.
- Gates, executados nesta ordem:

  ```sh
  uv run ruff format --check . && uv run ruff check . && uv run --env-file .env mypy . && uv run --env-file .env pytest
  git diff --check
  ```

- A regra `RUF012` do ruff está desligada, porque `Meta` e as migrations do Django usam listas como atributo de classe.
- O ruff exclui `.agents`, `.claude` e `docs`. O mypy também exclui `docs/` e `.agents/`.

## Fase 1 — Fontes e proveniência

App `sources`, com quatro models:

- **`Agency`** (órgão): `slug`, `name` e `jurisdiction` (`FEDERAL`, `MARANHAO` ou `SAO_LUIS`).
- **`Source`** (fonte): `slug`, `agency`, `url` (única), `format` (`GOVBR_API` ou `HTML`), `jurisdiction` e `access_notes`.
- **`SourceSnapshot`** (versão de fonte): conteúdo bruto de uma coleta, com `content_sha256`, `raw_text`, `raw_json` (opcional) e `declared_updated_at`. A unicidade é por par `(source, content_sha256)`.
- **`SourceImport`** (importação): uma coleta, com `fetched_at`, `http_status`, `outcome` (`OK` ou `FAILED`), `error` e a referência opcional a `snapshot`.

Pontos que a leitura do código não deixa óbvios:

- **Duas datas separadas.** `SourceImport.fetched_at` é a data da coleta. `SourceSnapshot.declared_updated_at` é a data de atualização declarada pelo órgão. Quando o órgão não declara, o campo fica nulo, que significa "não informado" (RN12). Data de coleta não é data de vigência.
- **Reaproveitamento por hash.** Importações com o mesmo SHA-256 apontam para o mesmo snapshot. Por isso `SourceImport` referencia `SourceSnapshot` por chave estrangeira, e não por relação 1:1 como previsto no plano inicial.
- **Restrição no banco.** Uma importação `OK` exige snapshot e erro vazio. Uma importação `FAILED` exige snapshot nulo e registra o erro. Assim não é possível ter sucesso sem conteúdo preservado nem falha sem mensagem.
- **Adaptadores** (`sources/adapters.py`) usam só biblioteca padrão (`urllib`, `html.parser`, `hashlib`) e não gravam no banco. Têm timeout de 60 s e limite de 5 MB por resposta. O `User-Agent` é `Mozilla/5.0`, porque o gov.br responde 403 a requisições sem `User-Agent`.
- **API Gov.br** (`GOVBR_API`, JSON): a ficha de `servicos.gov.br/api/v1/servicos/{id}` é validada (`hasErro` deve ser `false` e `resposta.nome` deve existir). A ficha não traz data de atualização, por isso cada procedimento também precisa da página HTML do serviço.
- **Página HTML** (`HTML`): só é reconhecido o texto `Última Modificação: dd/mm/aaaa`, único formato evidenciado nas amostras. A data "Publicado em", da Polícia Civil do MA, não é data de atualização e fica como "não informado".
- **Falhas explícitas.** Datas divergentes na mesma página, datas impossíveis e conteúdo que não é UTF-8 fazem a coleta falhar. Nada é inferido.
- **Comando** `uv run --env-file .env python manage.py fetch_sources [--source SLUG]`. A opção `--source` pode ser repetida. Slug inexistente é rejeitado. O comando termina com erro se alguma fonte falhar, mas registra todas as importações antes disso.
- **Admin somente leitura** (`ReadOnlyAdmin` em `sources/admin.py`): não permite adicionar, alterar nem excluir. O conteúdo entra pelos comandos `load_sources`, `fetch_sources` e `load_content` (Fase 2).

## Fase 2 — Domínio normalizado e carregador de conteúdo

Estado por fatia:

| Fatia | Escopo | Estado |
| --- | --- | --- |
| 2a | Models do app `catalog` e migration | Consolidado (commit `adf48b9`) |
| 2b | Comandos `load_sources` e `load_content`, verificação de trecho e ordenação de Kahn | Consolidado (commit `3075b63`) |
| 2c | `content/sources.toml` e `content/cpf-irregular.toml` | Consolidado (commits `2fbd178`, `de5d0b0`) |
| 2d | [ADR 0003](../arquitetura/decisoes/0003-regras-como-dados.md) | Consolidado |

**2a — models.** As tabelas e o porquê de cada uma estão no [modelo físico de dados](../arquitetura/modelo-fisico-de-dados.md). O banco impõe as seguintes restrições:

- `Dependency` tem `rule` se e somente se é `CONDITIONAL`;
- `before ≠ after`;
- o par `(before, after)` é único;
- o slug de opção é único por pergunta;
- há no máximo um custo e um prazo por procedimento.

**2b — carga de conteúdo.**

- **`load_sources <arquivo>`** (`sources/loader.py`): upsert de órgãos e fontes por slug, sem apagar nada, porque importações e snapshots dependem das fontes.
- **`load_content <diretório>`** (`catalog/loader.py`): lê todos os `.toml` do diretório, exceto `sources.toml`, e valida tudo antes de gravar. Só depois apaga e recria o conteúdo do `catalog` em uma única transação.
  - A validação acontece em duas etapas. Primeiro o formato: chaves desconhecidas, tipos, valores permitidos, formato de slug e tamanho máximo das colunas, lido do próprio model. Depois as referências cruzadas. Motivo: um erro de formato não gera dezenas de erros de referência falsos.
  - Os erros são acumulados e mostrados juntos, um por linha, no formato `<arquivo>: <slug>: <problema>`.
  - Diretório inexistente, vazio ou só com `sources.toml` também é erro. Motivo: sem essa checagem, um caminho errado apagaria o catálogo inteiro.
- **Verificação do trecho** (`sources/text.py`): o trecho citado precisa aparecer no texto normalizado da versão mais recente coletada com sucesso. Esse texto é o HTML sem tags ou todas as strings do JSON, com espaços normalizados. Em caso de empate de data, vale a importação de maior `id`, para que o resultado seja determinístico.
- **Validações de domínio:**
  - "não sei" não pode ser opção (`nao-sei`/`unknown` são reservados), porque é representado por `allows_unknown` (RN03);
  - `clarifies` só pode apontar para uma pergunta que aceita "não sei";
  - regra de dependência não tem procedimento, e regra sem procedimento precisa ser usada por alguma dependência;
  - condição sem opções e regra sem condições são recusadas.
- **Ciclo** (`guidance/engine/ordering.py`): ordenação de Kahn em camadas, com cada camada ordenada por slug. A carga recusa ciclos sobre todas as arestas, inclusive as recomendadas. O erro lista só os procedimentos que formam o ciclo, sem os que apenas dependem dele (invariante 5). O mesmo módulo será usado pelo motor na Fase 3.
- **Revisão.** O agente `revisor` apontou seis problemas, corrigidos antes do commit. Os principais eram um diretório vazio que apagava o catálogo, limites de coluna que viravam erro do banco sem arquivo nem slug, e empate de data na escolha da versão.

**2c — jornada CPF irregular** (`content/`).

- **Fontes:** 2 órgãos e 7 fontes. São as fichas da API Gov.br 10416 e 10420 e cinco páginas HTML; todas as URLs vêm de [evidências](../dados/evidencias/cpf-irregular.md).
- **Pergunta:** uma única, sobre a situação cadastral. Aceita "não sei" e tem cinco opções: suspenso, pendente de regularização, cancelado, nulo e falecido.
- **Procedimentos com regra:** regularizar CPF suspenso, entregar declarações faltantes e procurar o atendimento da Receita. Este último vale para cancelado, nulo e falecido, que a Receita descreve sem indicar providência (observação 6 da evidência).
- **Esclarecimento:** "consultar a situação do CPF" não é candidato; entra só pelo "não sei" ([ADR 0003](../arquitetura/decisoes/0003-regras-como-dados.md)).
- **Sem dependências:** a única ordem documentada ("o primeiro passo é descobrir o que deu errado") só vale quando a situação é desconhecida. Nesse caso nenhum outro procedimento é aplicável.
- **Validação real, em 24/10/2026, no banco `oqf_dev`:** `load_sources` → `fetch_sources` (7 de 7 fontes OK) → `load_content`.
  - A primeira carga falhou em dois trechos. A extração de HTML separava a pontuação nas fronteiras de tag ("gratuita ,"); a normalização foi corrigida (`2fbd178`) e a carga passou.
  - O teste `catalog/tests/test_content_cpf.py` carrega o `content/` real com as amostras de `docs/dados/amostras/`.
- **Ficou de fora por falta de trecho literal ou de confirmação** (pendências de conteúdo):
  - título de eleitor;
  - prazo de 48 h do atendimento por e-mail;
  - canais `alterar/default.asp` e `cav.receita`;
  - critério de cinco anos da DIRPF.

## Fase 3 — Motor de orientação

O motor fica em `guidance/engine/`, em Python puro, sem Django. Ele recebe um `Catalog` imutável e os fatos da sessão, e devolve avaliações, a próxima pergunta e o plano. Motivo: testes rápidos sem banco e separação entre o que se aplica (`evaluation.py`) e a ordem (`ordering.py`), conforme a invariante 4.

| Fatia | Escopo | Estado |
| --- | --- | --- |
| 3a | Tipos (`model.py`), avaliação ternária (`evaluation.py`), próxima pergunta (`questions.py`) | Consolidado (`3b957cb`) |
| 3b | Montagem do plano (`plan.py`) | Consolidado (`90969f6`) |
| 3c | Repositório do ORM para o `Catalog` (`guidance/repository.py`) e teste de ponta a ponta da jornada CPF | Consolidado (`a12eaa1`) |

**Fatos.**
- A sessão guarda cada resposta como um conjunto de slugs de opções ou `Unknown.UNKNOWN` ("não sei").
- Pergunta ausente significa "não respondida".
- `validate_facts` recusa:
  - pergunta ou opção inexistente;
  - "não sei" em pergunta que não o aceita;
  - pergunta de escolha única sem exatamente uma opção.

**Avaliação.** Usa os conectivos E e OU de Kleene, como descrito no [ADR 0003](../arquitetura/decisoes/0003-regras-como-dados.md). Cada `Evaluation` guarda o resultado de cada regra, que é a base da explicação ao cidadão (RF19).

**Próxima pergunta.**
- A pontuação de uma pergunta conta os candidatos indeterminados que têm uma regra indeterminada citando essa pergunta.
- Também conta as dependências condicionais indeterminadas de etapas aplicáveis.
- Desempate por `order` e depois por `slug`.
- Pergunta sem pontuação nunca é feita (RN02).
- Sem perguntas pontuadas, o motor para (RN10).
- "Não sei" conta como respondida, então a pergunta nunca se repete.
- Motivo: um critério determinístico inspirado em ganho de informação, sem treinamento ([ADR 0002](../arquitetura/decisoes/0002-motor-baseado-em-regras.md)).

**Plano.**
- **O que entra:**
  - os candidatos aplicáveis;
  - os esclarecimentos das perguntas respondidas com "não sei";
  - os pré-requisitos obrigatórios, ou condicionais com regra aplicável. Entram de forma transitiva, a menos que as próprias regras os descartem, e ficam marcados com `required_for`, que corresponde a "necessário para X".
- **Pré-requisito fora dos candidatos:** o autor decidiu em 24/10/2026 que ele entra.
- **Ordem:** camadas de Kahn. Um ciclo levanta erro em vez de gerar um plano parcial.
- **Dependências recomendadas** só reordenam etapas dentro de uma mesma camada; nunca adicionam etapa (RN08).
- **Fora do plano:** os candidatos ainda indeterminados vão para `Plan.undetermined`, para transparência.

**Repositório.**
- Monta o `Catalog` com 16 consultas fixas, qualquer que seja o tamanho do catálogo, comprovado em teste.
- Traz todo pré-requisito alcançável; o motor decide quais arestas valem.
- A data de coleta da citação é o `fetched_at` mais recente entre as importações OK daquele snapshot.

**Verificação.**
- O teste de ponta a ponta cobre a jornada CPF irregular com cada resposta possível, com "não sei" e sem fatos.
- No `oqf_dev`, com as fontes reais, "suspenso" gera a etapa `regularizar-cpf-suspenso` e "não sei" gera `consultar-situacao-cpf`.

## Limitações conhecidas

- O banco não garante que o snapshot de uma importação pertence à mesma fonte da importação. Essa garantia hoje é só do código de coleta (`sources/services.py`).
- Nenhuma coleta real pela rede foi executada ainda. As fontes serão cadastradas pelo `load_sources`, da Fase 2.
- `load_sources` recusa a troca de URL entre duas fontes já cadastradas (marcado como `shortcut:` no código). Isso será tratado se surgir um caso real.
- A validação de `load_content` roda fora da transação de escrita. Uma coleta concorrente entre as duas etapas pode invalidar a verificação. É um risco baixo para um comando executado manualmente.
- Uma dependência condicional cuja etapa dependente é um pré-requisito puxado (não candidato) não torna a sua pergunta elegível como próxima pergunta. Sem dependências no conteúdo atual, isso ainda não tem efeito.
- `fetched_at` é guardado em UTC; a interface (Fase 4) precisa exibi-lo no fuso `America/Fortaleza`.
- O conteúdo bruto completo da página HTML é guardado em `TEXT` no banco. As páginas têm até cerca de 150 KB. Não há armazenamento de arquivos brutos fora do banco.
