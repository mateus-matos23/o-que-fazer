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
| 4 | Fluxo mínimo HTTP com templates Django sem estilo e sessão Django | Consolidado (commits `ad23d39`, `c14f994`) |
| 5 | Jornadas desligamento do trabalho e perda de documentos | Consolidado |
| 6 | UI/UX, acessibilidade, frontend e RF18 (RF02 segue pendente) | Consolidado |
| 7 | Conversa guiada: funil de triagem, efeito da resposta, preferência de atendimento e plano com ponto de partida (RF21 a RF26) | Consolidado (25/10/2026) |
| 8 | Hospedagem: Dockerfile, gunicorn, WhiteNoise e deploy no Render com Neon (ADR 0006) | Consolidado (26/10/2026, commits `de7d221`, `94f9ec7`) |
| 9 | Redesenho visual "azulejo": paleta, triagem ilustrada, etapas da conversa e plano como linha do tempo | Em andamento (26/10/2026) |

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

## Fase 4 — Fluxo mínimo HTTP

Templates Django sem CSS nem JavaScript, com HTML semântico (`fieldset` e `legend`, resumo em `ol`). O visual fica para a Fase 6.

| Fatia | Escopo | Estado |
| --- | --- | --- |
| 4a | Lista de situações, pergunta e sessão | Consolidado (`ad23d39`) |
| 4b | Plano, revisão e edição de respostas, recomeçar e erro de ciclo | Consolidado (`c14f994`) |

**Rotas**

| Rota | Função |
| --- | --- |
| `/` | Situações (RF01). |
| `/s/<slug>/` | Próxima pergunta; o POST segue o padrão POST/redirect/GET com 303. |
| `/s/<slug>/plano/` | Plano, exibido só quando não resta pergunta relevante. |
| `/s/<slug>/respostas/` | Revisão das respostas (RF16). |
| `/s/<slug>/respostas/<pergunta>/` | Edição de uma resposta; o plano é recalculado (invariante 8). |
| `/s/<slug>/recomecar/` | Recomeçar; aceita só POST. |

**Sessão** (`guidance/session.py`)
- Formato: `{"facts": {situação: {pergunta: [opções] | "unknown"}}}`, guardado na sessão do Django, sem conta e sem tabela.
- Uma resposta que não cabe mais no catálogo carregado (pergunta ou opção removida) é descartada com `warning` no log, e a pergunta volta a ser feita.
- Motivo: `load_content` substitui o catálogo, e as sessões antigas guardam slugs.

**Formulário** (`guidance/forms.py`)
- Pergunta de escolha única vira botões de opção; de escolha múltipla, caixas de seleção, e a escolha múltipla aceita "nenhuma destas".
- "Não sei" só aparece quando a pergunta aceita. Na escolha única, usa o valor reservado `__unknown__`; na múltipla, um campo próprio, que não pode vir junto com outras opções.
- Toda validação é feita no servidor.

**Plano**
- Começa por um aviso de que o sistema é orientativo, seguido de um resumo e depois dos detalhes de cada etapa.
- Cada etapa mostra:
  - motivo (RF19);
  - "necessária antes de" e "faça depois de", com "(sugestão)" nas dependências recomendadas (RN08);
  - órgão, requisitos e canais;
  - custo e prazo, ou "Não informado" (RN11);
  - fonte, com a data de coleta e a data declarada pelo órgão (RN12), no fuso America/Fortaleza.
- Um ciclo registra os slugs no log e mostra uma página de erro genérica (500), nunca um plano parcial.

**Verificação**
- Testes com o client do Django cobrem a jornada inteira, "não sei", edição, recomeçar, CSRF, 404, 400 e 405, fuso e ciclo.
- Em 24/10/2026, a jornada foi percorrida por HTTP com `runserver` sobre o `oqf_dev`: lista, pergunta com 6 opções ("Não sei" incluída), POST 303 e plano com fonte e data de coleta.
- Não houve verificação no navegador com o `verificador-ui`. Motivo: as telas não têm estilo e serão refeitas na Fase 6, onde a verificação visual e de acessibilidade acontece.

## Fase 5 — Demais jornadas

| Fatia | Escopo | Estado |
| --- | --- | --- |
| 5a-1 | Opção de resposta fora da cobertura (`AnswerOption.out_of_coverage`) e aviso no plano | Consolidado (`b62e309`) |
| 5a-2 | Jornada "desligamento do trabalho" | Consolidado (`96870db`) |
| 5b | Jornada "perda de documentos" | Consolidado (`28c9b32`) |
| 5c | Perda de documentos: 2ª via da CIN e da CNH, com a primeira dependência obrigatória | Consolidado |

**Opção fora da cobertura** (decisão do autor em 24/10/2026)
- Algumas respostas reais não têm orientação oficial lida nesta versão. Exemplos: término por acordo, culpa recíproca ou fim de contrato; perda de CIN, CNH ou título de eleitor.
- Essas opções continuam disponíveis para o cidadão, que não fica sem a sua resposta. Elas recebem `out_of_coverage = true` no TOML.
- O plano mostra a seção "Limite de cobertura" com as respostas afetadas. As demais etapas aplicáveis continuam no plano.
- A avaliação das regras não muda. O aviso não cita órgão nem canal, porque não há fonte para isso.
- Alternativas rejeitadas:
  - tornar o procedimento indeterminado, o que mudaria a lógica de Kleene do motor;
  - omitir as opções, o que empurraria o cidadão para o "não sei".

**Desligamento do trabalho** (`content/desligamento-do-trabalho.toml`)
- Perguntas: forma de término e tipo de vínculo (empregado ou doméstico). O vínculo existe porque separa o seguro 1045 do 9815 (RN02).
- Procedimentos:
  - seguro-desemprego e seguro-desemprego do doméstico, quando a dispensa é sem justa causa e o vínculo corresponde;
  - saque do FGTS por dispensa sem justa causa;
  - CTPS Digital e extrato do CAGED, sem regra, aplicáveis a qualquer forma de término.
- Pedido de demissão e justa causa deixam os seguros e o FGTS não aplicáveis. As fontes só tratam da dispensa sem justa causa (decisão do autor).
- "Não sei" na forma de término deixa os seguros e o FGTS indeterminados, nunca não aplicáveis.

**Perda de documentos** (`content/perda-de-documentos.toml`)
- Pergunta de escolha múltipla: CPF; CIN, CNH e título de eleitor fora da cobertura.
- Procedimentos:
  - segunda via do CPF, quando o CPF foi perdido;
  - registro de extravio na Delegacia Online da Polícia Civil do Maranhão, sem regra, porque a página trata de "extravio de documentos" em geral.
- Não há dependência entre o B.O. e a segunda via, porque nenhum trecho a sustenta.
- A amostra da Delegacia Online terminava no menu do site. Recebeu o parágrafo do snapshot coletado em 24/10/2026, que o procedimento cita.
- A condição do canal "sem gov.br" (não ter declarado IR nos últimos dois anos) está no texto da página e entrou. Isso resolve a observação 6 da evidência.

**5c — CIN e CNH na perda de documentos** (25/10/2026)
- Por quê: a coleta de 24/10/2026 achou trechos literais para as duas segundas vias e, na página do DETRAN-MA, o primeiro trecho que sustenta uma precedência ("Boletim de Ocorrência;" entre os documentos da 2ª via da CNH). Isso põe a ordenação topológica em uso com conteúdo real.
- CIN e CNH deixaram de ser `out_of_coverage`; o título de eleitor continua fora (fonte do TSE não localizada).
- Segunda via da CNH (DETRAN-MA): requisitos B.O., RG e taxa; vale só para CNH do Maranhão (outro estado é "alteração de dados"); atendimento presencial; custo R$ 90,00 pela tabela de taxas.
- Segunda via da CIN (Ident-MA): certidão de nascimento ou casamento atualizada e RG atual, se houver; postos na Grande Ilha, nos demais municípios e em qualquer UF. Custo "não informado" (RN11).
- Dependência MANDATORY `registrar-ocorrencia-extravio` → `segunda-via-cnh`. A CIN não depende do B.O.: nenhuma fonte lida exige.
- Adiado: certidão como etapa antes da CIN. A única fonte é um serviço da SEMCAS com requisitos vagos e a via normal (cartório) não tem fonte. A certidão fica como requisito.
- Amostras novas: `html-govbr-cin-faq.md` (unificada; a `html-govbr-cin-faq-emissao.md` saiu), `html-ssp-cin-ma.md`, `html-detran-2via-cnh.md`, `html-detran-taxas.md`.
- Carga real em 25/10/2026 no `oqf_dev`: `fetch_sources` coletou as 4 fontes novas e `load_content` encontrou todos os trechos nas páginas ao vivo (13 procedimentos, 1 dependência).
- Navegador (Chromium headless via CDP, 320 px e 1280 px): com CPF, CIN, CNH e título, o plano traz o B.O. antes da CNH, mostra "Faça depois de" na CNH, o custo de R$ 90,00 e o aviso de limite de cobertura; sem rolagem horizontal, um `h1` e nenhum erro no console. Só a CNH: dois passos, sem aviso de cobertura.

**Verificação**
- 253 testes:
  - estruturais por jornada;
  - tabelas de casos fatos → plano sobre o conteúdo real;
  - percursos com o client do Django até o plano;
  - contagens globais em `catalog/tests/test_content_counts.py`.
- Em 24/10/2026, a carga real no `oqf_dev` (`load_sources`, `fetch_sources` e `load_content`) encontrou todos os trechos nas páginas e APIs oficiais. Resultado: 18 fontes, 3 situações e 11 procedimentos.
- O que ficou de fora por falta de trecho literal está listado no cabeçalho de cada TOML.

## Fase 6 — Interface, acessibilidade e busca direta

Decisões no [ADR 0004](../arquitetura/decisoes/0004-frontend-e-acessibilidade.md): templates Django, um CSS próprio sem JavaScript nem dependência, meta WCAG 2.2 AA com verificação própria e RF18 em versão simples.

| Fatia | Escopo | Estado |
| --- | --- | --- |
| 6a | ADR 0004 e fonte local Atkinson Hyperlegible Next (OFL) | Consolidado (`3ef7ec8`) |
| 6b | CSS próprio e reescrita dos sete templates do fluxo | Consolidado (`3b468bb`) |
| 6c | Busca "Onde resolvo?" (RF18) e página de detalhe do serviço | Consolidado (`00076a0`) |
| 6d | Verificação final de acessibilidade | Consolidado (`f50d663`) |
| 6e | Simplificação do diff da fase e documentação | Consolidado |

**6b — Fluxo do cidadão**
- O link "Pular para o conteúdo" leva ao `main`. Cada tela tem um único `h1`; na pergunta, o `h1` fica dentro do `legend` para o leitor de tela anunciar a pergunta junto com as opções.
- O progresso conta as respostas dadas ("Você já respondeu N"), sem total fixo, porque o número de perguntas depende das respostas (ADR 0002).
- Erro de formulário: o bloco de erro fica ligado ao `fieldset` por `aria-describedby`, recebe o foco ao carregar (`autofocus` com `tabindex="-1"`, sem JavaScript) e o título da página ganha o prefixo "Erro:".
- O resumo do plano é um roteiro numerado pelas camadas da ordenação. Etapas da mesma camada levam a nota "Podem ser feitas em qualquer ordem", que reflete o Kahn em camadas sem inventar precedência (RN08).
- Verificação no Chromium headless, via CDP (o `verificador-ui` não tinha as ferramentas de navegador nesta sessão): só teclado, foco visível, reflow em 320 e 360 px, zoom de 200%, alvos de 24 px ou mais e contraste calculado das cores do tema. A primeira rodada achou o link de contexto com 22 px e o erro sem foco nem anúncio; os dois foram corrigidos e verificados de novo.

**6c — Onde resolvo? (RF18)**
- `GET /onde-resolvo/?q=` busca no título e na descrição dos procedimentos, sem diferenciar maiúsculas. O termo é validado no servidor (2 a 100 caracteres).
- `GET /onde-resolvo/<slug>/` mostra órgão, requisitos, canais, custo, prazo e fonte, com o mesmo bloco do plano (`_procedure_facts.html`). A página não avalia aplicabilidade, porque não há fatos; um aviso encaminha ao modo por situação.
- O repositório passou a montar um procedimento isolado (`load_procedure`) com a mesma consulta e a mesma conversão usadas pelo `load_catalog`.

**6d — Verificação final (24/10/2026)**
- Varredura automatizada própria (script CDP no Chromium headless) em 10 telas: home, busca vazia, com resultado e com erro, detalhe do serviço, duas perguntas e os planos das três jornadas ("não sei" no CPF; sem justa causa e doméstico; perda do CPF).
- Cada tela foi vista em 320 px, 1280 px e 640 px (equivalente a 1280 px com zoom de 200%).
- Critérios: um `h1` e títulos sem salto; `header`, `main` e `footer`; nenhuma rolagem horizontal; alvos não inline com 24 px ou mais (WCAG 2.5.8); contraste de 4,5:1 ou mais nas amostras de texto, link, botão, aviso e rodapé; nenhum erro no console.
- Resultado: as 30 combinações passaram.
- Não verificado: leitor de tela real (NVDA, TalkBack, VoiceOver), Firefox e Safari, impressão. A verificação não substitui uma ferramenta como o axe-core nem um teste com pessoas usuárias.

**6e — Simplificação**
- Uma revisão de reuso, simplificação, eficiência e altitude sobre o diff da fase. Foram aplicadas: a remoção de uma regra CSS que nunca valia (`dd ul`), a fusão das regras repetidas de `.errors` e `.notice` e dos links de 24 px, e o uso de `.first()` em `load_procedure`. O visual não mudou; a varredura da 6d foi refeita e passou.
- Não aplicadas, para debate:
  - limitar o número de resultados da busca, que muda o comportamento visível;
  - a página de detalhe pré-busca as regras sem usá-las (cerca de 4 consultas a mais), porque reaproveita a conversão do `load_catalog`;
  - o bloco de erro repetido entre busca e pergunta (dois usos);
  - o contexto repetido entre `question` e `edit_answer`, que é anterior à fase.

## Fase 7 — Conversa guiada

Proposta aprovada pelo autor em 25/10/2026. Estado: Consolidado; as fatias 0 a 9 foram entregues (a 9 só como pesquisa; a pergunta perda × furto/roubo não entrou).

**Motivação.** Hoje o cidadão escolhe a situação numa lista e responde uma ou duas perguntas antes do plano. O autor quer uma experiência de "conversa guiada", inspirada no Akinator, para um público com idade, escolaridade e familiaridade com tecnologia variadas. A conversa leva à situação por um funil de triagem, mostra o efeito de cada resposta no plano e termina num plano com ponto de partida. Requisitos RF21 a RF26 e regras RN02, RN14 e RN16 em [requisitos](../produto/requisitos.md).

**Decisões de 25/10/2026 (aprovadas pelo autor)**

1. **RN02 mantida.** Cada pergunta continua existindo só se a resposta puder alterar aplicabilidade, ordem ou encaminhamento. O funil de triagem entra como encaminhamento.
2. **RF02 (texto livre) segue fora.** A direção registrada, para quando entrar, são palavras-chave determinísticas com confirmação do cidadão, sem LLM ([pendências](../pendencias.md), item 6).
3. **Preferência de atendimento só ordena canais.** Ela nunca esconde canal nem altera aplicabilidade (RN14).
4. **Efeito da resposta como aviso de uso único na sessão.** Os fatos continuam sendo a única verdade; o aviso guarda só slugs e um inteiro, e some depois de mostrado. (Revisada na fatia 3: a proposta inicial era um parâmetro de URL.)
5. **Lista de situações mantida** como link secundário, ao lado do funil.

**Fatias.** Cada fatia depende da anterior estar funcional e validada.

| Fatia | Escopo | Estado |
| --- | --- | --- |
| 0 | Documentação base (produto, glossário, pendências e este registro) | Consolidado |
| 1 | Linguagem simples e dica por pergunta | Consolidado |
| 2 | Funil de triagem, com limite de cobertura nos ramos sem jornada | Consolidado |
| 3 | Efeito da resposta no plano | Consolidado |
| 4 | Preferência de atendimento e ordenação dos canais | Consolidado |
| 5 | Plano com "Comece por aqui", "O que separar antes" e versão para impressão | Consolidado |
| 6 | Requisitos e canais condicionais no motor | Consolidado |
| 7 | Perguntas novas com fonte: primeira solicitação do seguro-desemprego; declaração de IR nos últimos dois anos para o canal "sem gov.br" do CPF | Consolidado |
| 8 | "Não sei" com como descobrir (pesquisa) | Consolidado (esclarecimento só para a declaração de IR; as outras 3 perguntas ficam na pendência 15) |
| 9 | Pesquisa perda × furto/roubo | Consolidado (pesquisa; a pergunta não entra) |

**Fatia 1 — linguagem simples e dica.**

- `Question.help_text` (migration 0003) e chave TOML opcional `help` por pergunta. A dica é ligada ao `fieldset` por `aria-describedby`, junto de `form-errors` quando há erro.
- Perguntas reescritas: "Qual é a situação do seu CPF na consulta da Receita Federal?", "Como você saiu do emprego?" e "Que tipo de trabalho era?"; a pergunta de documentos perdidos manteve o texto e ganhou dica. Os rótulos do desligamento passaram a frases simples, com o termo oficial entre parênteses.
- Motivo: público variado (RF24). As dicas não afirmam nada sem fonte (RN16). "Culpa recíproca" foi mantida porque não há fonte para explicar o termo.
- Gates: ruff, mypy e pytest verdes (281 passed).
- Verificação no Chromium headless via CDP em 25/10/2026, após migrate e load_content no `oqf_dev` (autorizados pelo autor para a Fase 7): textos, dicas e `aria-describedby` conferidos; contraste da dica 6,69:1; sem rolagem horizontal em 320 px; sem erros de console.
- Limite observado: o envio vazio é barrado pela validação nativa do navegador (`required` nos radios, anterior à fatia), então o bloco `#form-errors` só aparece quando o navegador não valida. O caminho do servidor segue coberto por testes.

**Fatia 2 — funil de triagem.**

- `TriageNode` e `TriageChoice` (migration 0004), tabela TOML `triage` e `content/triage.toml` com 3 nós e 12 opções. A raiz `/` mostra o nó `inicio`; `/comecar/<slug>/` mostra os demais; `/fora-da-cobertura/` é o limite de cobertura; a lista de situações passou a `/situacoes/`. Sem nó `inicio` no conteúdo, a raiz mostra a lista.
- Validação na carga: nó `inicio` ausente, slug duplicado, opção sem exatamente um destino, `next` ou `situation` inexistente, ciclo, nó inalcançável, situação não alcançável pelo funil e nó sem opções.
- Motivo: o público variado (RF21, RF24) não deve precisar reconhecer o nome da situação. O funil é encaminhamento (RN02), por isso não tem fonte. Decisão em [ADR 0005](../arquitetura/decisoes/0005-funil-de-triagem.md).
- Gates: ruff, mypy e pytest verdes (311 passed).
- Verificação no navegador (25/10/2026, Chromium headless via CDP, `oqf_dev` com a migration 0004 e o conteúdo carregado): 41 de 41 verificações passaram — textos, ordem e destino das opções, navegação por teclado com foco visível, redirecionamento de `/comecar/inicio/`, 404 em nó inexistente, sem rolagem horizontal em 360 e 1280 px, alvos ≥ 24×24 px, contraste da dica 6,69:1 e das opções 5,95:1.

**Fatia 3 — efeito da resposta.**

- `answer_effect(catalog, before, after)` em `guidance/engine/effect.py` (motor puro) compara o plano de antes com o de depois, sendo "no plano" as etapas de `build_plan`: `entered` = etapas novas (na ordem do plano de depois), `left` = etapas que existiam e saíram (na ordem do catálogo), `in_play` = `len(plan.undetermined)`. Ciclo entre dependências propaga `DependencyCycleError`.
- As views `question` e `edit_answer`, no POST válido, calculam o efeito com os fatos lidos antes e depois de gravar a resposta e o guardam na sessão (`write_effect`, `pop_effect` em `guidance/session.py`) como aviso de uso único por situação. O GET de `question` consome o aviso só ao renderizar a pergunta; o plano consome e mostra. Se o cálculo esbarrar em ciclo, nada é guardado: a view do plano já registra e mostra o erro. O bloco `_answer_effect.html` é omitido sem mudanças e sem providências em análise. Quando há `left`, ele lembra que sair do plano não significa falta de direito.
- Leitura defensiva: formato corrompido, tipos errados ou slug fora do catálogo viram "sem aviso", sem exceção.
- Motivo: a primeira versão comparava a avaliação "com e sem a resposta" e media aplicabilidade, não o plano. Isso mostrava "saiu" para o que nunca esteve nas etapas (indeterminado que virou não aplicável), ignorava o esclarecimento de "não sei", divergia de `plan.undetermined` (por causa dos pré-requisitos puxados) e, ao editar, comparava com "sem resposta" em vez do plano que a pessoa via. Comparar planos corrige os quatro. O aviso na sessão em vez de parâmetro de URL evita um efeito que dependa de link ou recarga: ele só vale logo após a resposta.
- Gates: ruff, mypy e pytest verdes (341 passed).
- Verificação no navegador (25/10/2026, Chromium headless via CDP): desligamento sem justa causa → doméstico → edição para empregado → mesma resposta regravada, e CPF com "Não sei". Os itens de "entrou" estão nas etapas, os de "saiu" estavam no plano anterior e não estão no atual, e a resposta regravada não mostra bloco. O bloco some ao recarregar. Fica dentro de `main` antes do `h1`, com contraste de 14,7:1 e 7,19:1 e sem rolagem horizontal em 360 px.

**Fatia 4 — preferência de atendimento.**

- Depois da última pergunta e antes do primeiro plano, `s/<slug>/atendimento/` pergunta "Como você prefere ser atendido?" (internet ou aplicativo, telefone, pessoalmente, tanto faz). A resposta fica na sessão (`channel_preference`), vale para todas as situações e valor desconhecido ou corrompido vira "sem preferência". O plano aberto direto, sem preferência, aparece normalmente na ordem original.
- `guidance/engine/channels.py` (motor puro) define as quatro opções fixas, com slugs em português como os demais valores de URL e sessão, e `order_channels`: canais dos tipos preferidos primeiro, ordem estável, nenhum removido. EMAIL não entra em nenhum grupo. A etapa sem canal do tipo preferido mostra "… não informado na fonte para esta etapa" (RN11). O topo do plano diz qual preferência ordenou os canais e oferece "Mudar".
- Motivo: RN14 e RF23. A preferência não é Fato nem `Question`: não passa por regras, não altera aplicabilidade nem a ordem das etapas (RN08). A busca "Onde resolvo?" não muda. O aviso de efeito da fatia 3 continua sendo consumido só por `plan` ou pela pergunta, não pela página de preferência.
- Gates: ruff, mypy e pytest verdes (364 passed).
- Verificação no navegador (25/10/2026, Chromium headless via CDP): a última pergunta leva à página de preferência e depois ao plano, com o efeito da resposta preservado. Por telefone e pessoalmente põem os canais do tipo preferido primeiro e mostram o aviso nas etapas sem esse tipo. Tanto faz mantém a ordem de "Onde resolvo?". O número de canais por etapa é o mesmo em toda preferência (10 no total). A preferência vale para outra situação, e a CPF foi direto ao plano. Foco visível, contraste ≥ 5,95:1 e sem rolagem horizontal em 360 px. Etapa sem nenhum canal não apareceu no conteúdo real (coberta por teste).

**Fatia 5 — plano com "comece por aqui".**

- Cartão "Comece por aqui" logo abaixo da preferência de atendimento, com a etapa ou as etapas da camada 1. A seção "O que separar antes" vem depois do Resumo, com um grupo por etapa que tem requisitos, na ordem do plano, sem mesclar nem remover repetidos. Os requisitos seguem dentro de cada etapa (RF12).
- Impressão por `@media print` no fim de `guidance/static/guidance/site.css`: esconde cabeçalho, controles, preferência e links de editar, e imprime a URL dos links externos. A linha "Para guardar este plano, use a opção de imprimir do navegador." fica escondida na impressão. Sem botão e sem JavaScript.
- `_plan_context` em `guidance/views.py` reúne o contexto do plano (etapas, camada 1, requisitos, limite de cobertura e indeterminados); a view e os testes usam a mesma função. O motor não mudou.
- Motivo: RF26. O cidadão precisa saber por onde começar e o que reunir antes de sair. Agrupar por etapa preserva a origem de cada requisito: requisitos parecidos de procedimentos diferentes não são unificados (glossário).
- Gates: ruff format, ruff check, mypy e pytest verdes (376 passed; eram 364 na fatia 4). `git diff --check` limpo.
- Verificação no navegador (25/10/2026, Chromium headless via CDP): "Comece por aqui" com três etapas em perda de documentos (CPF, CIN e CNH; a CNH fica fora do cartão porque depende do B.O.) e com uma etapa em CPF suspenso; "O que separar antes" com 4 grupos na ordem do plano e sem mesclar; na impressão emulada, cabeçalho, rodapé, formulários, preferência e dica de impressão escondidos, URL dos 7 links externos impressa, texto preto sobre branco; sem rolagem horizontal em 360 px; contraste mínimo de 6,41:1; foco visível nos links do cartão. O aviso de efeito e o link "Alterar essa resposta" não estavam na página verificada; a regra de impressão deles é coberta pelo teste da folha de estilo.

**Fatia 6 — requisitos e canais condicionais.**

- `Requirement.rule` e `ServiceChannel.rule` (FK opcional para `Rule`, `PROTECT`, como em `Dependency.rule`; migration `catalog/0005`). No TOML, `rule = "<slug>"` é opcional em `requirements` e `channels`. O carregador exige que a regra exista e não tenha `procedure`, e uma regra usada só por requisito ou canal deixa de ser órfã. Como as regras agora são protegidas, `_replace` apaga requisitos e canais antes das regras e os recria depois delas. O carregador também passou a exigir que toda pergunta citada por regra de um procedimento relevante de uma situação esteja ligada a ela (evita KeyError em `next_question`).
- Motor: `RequirementDef.rule` e `ChannelDef.rule` (padrão `None`), `visible_items` em `guidance/engine/evaluation.py` e `PlanStep.requirements`/`channels` já filtrados. `next_question` ganhou um laço: regras de item indeterminadas de procedimentos aplicáveis pontuam suas perguntas ainda não respondidas, então "não sei" não repete a pergunta. `answer_effect` não mudou.
- Repositório: regra, condições e citação dos itens vêm no prefetch (constante, até 6 consultas a mais, só quando há item com regra). Telas: o plano usa os itens visíveis (inclusive em "O que separar antes" e na ordenação por preferência); item indeterminado traz "Pode valer para você:" em texto, estilo `.maybe`; se todos os itens somem, aparece "Nenhum dos itens da fonte vale para o que você informou." em vez de "Não informado". Em "Onde resolvo?" os itens com regra aparecem marcados.
- Motivo: RF25 e RN03/RN11. Um requisito ou canal que só vale para parte dos casos não deve aparecer para quem já sabe que não é o seu, nem sumir para quem ainda não sabe. Esta fatia não altera `content/*.toml`; as perguntas que usam o recurso vêm na fatia 7.
- Gates: ruff format, ruff check, mypy e pytest verdes (404 passed; eram 376 na fatia 5). `git diff --check` limpo.
- Verificação no navegador: feita junto da fatia 7, que traz o primeiro conteúdo condicional (ver abaixo).

**Fatia 7 — perguntas novas com fonte já coletada.**

- Desligamento: pergunta `vezes-seguro-desemprego` (primeira, segunda, terceira ou mais; "Não sei" permitido; `order = 1`) e três regras sem `procedure` (`regra-carencia-primeira`, `-segunda`, `-demais`), uma por requisito de carência do `seguro-desemprego`, citando o mesmo trecho do requisito. Perda: pergunta `declarou-imposto-de-renda` (sim, não; "Não sei" permitido; `order = 1`), ligada à situação que carrega `segunda-via-cpf`, e a regra `regra-cpf-sem-declaracao-ir` no canal "sem gov.br" do CPF. Comentário do topo do TOML da perda atualizado.
- Motivo: primeiro conteúdo real a usar requisitos e canais condicionais (RF25). Quem já sabe a quantas vezes pediu o seguro, ou se declarou IR, deixa de ver itens que não são seus; quem não sabe vê todos, marcados (RN03). A pergunta só é feita quando o procedimento é aplicável (RN02). A ajuda das perguntas não afirma regra nem prazo (RN16). Nenhuma alteração em motor, carregador, models ou views.
- Testes: contagens globais (Question 6, AnswerOption 22, Rule 13, Condition 15), um ramo por opção mais "não sei", pergunta só com procedimento aplicável, ordem determinística e recálculo ao mudar a resposta. Testes de fluxo HTTP que iam direto ao plano da perda passaram a responder a pergunta de IR.
- Gates: ruff format, ruff check, mypy e pytest verdes (417 passed; eram 404). `git diff --check` limpo.
- Verificação no navegador (25/10/2026, Chromium headless via CDP, conteúdo carregado no `oqf_dev`): no desligamento, a pergunta das vezes aparece só com o seguro aplicável (nunca com pedido de demissão); "primeira" e "segunda" mostram só a carência correspondente, sem marca; "Não sei" mostra as 3 com "Pode valer para você:" (contraste 9,89:1, visível na impressão); alterar a resposta recalcula o plano. Na perda, a pergunta de IR só aparece com CPF; "Sim" esconde o canal "sem gov.br", "Não" o mostra sem marca e "Não sei" o mostra marcado. Em "Onde resolvo?", os itens condicionais aparecem marcados. Sem rolagem horizontal em 360 px; sem erros de console ou de rede.

**Fatia 8 — "não sei" com como descobrir.**

- Fonte nova `govbr-consultar-meu-imposto-de-renda` (amostra `html-consultar-meu-imposto-de-renda.md`, coletada em 25/10/2026) e procedimento de esclarecimento `consultar-declaracoes-ir` (`clarifies = "declarou-imposto-de-renda"`) na perda de documentos: requisitos (conta Prata ou Ouro; contribuinte ou representante), canais (Meu Imposto de Renda e App Receita Federal), custo e prazo, todos com trecho literal da amostra. Comentário do topo do TOML atualizado. Correção no motor após a revisão: `build_plan` só inclui o esclarecimento quando a pergunta ainda importa. A coleta das perguntas citadas por regras indeterminadas saiu de `next_question` para `pending_rule_questions` (`guidance/engine/evaluation.py`), usada também pelo plano; sem isso, uma resposta antiga "não sei" mantinha a etapa depois de o cidadão tirar o CPF dos documentos. Sem alteração em carregador, models ou views.
- Motivo: o "não sei" deve vir com o caminho para descobrir a resposta (RN03), mas só onde há fonte oficial. As outras três perguntas com "não sei" (`forma-de-termino`, `tipo-de-vinculo`, `vezes-seguro-desemprego`) não têm fonte suficiente e ficaram registradas em [pendências](../pendencias.md), item 15.
- Testes: contagens globais (Procedure 14, ProcedureDetail 11, Requirement 35, ServiceChannel 32); etapa presente com `clarifies` preenchido em "não sei", ausente em "sim", "não" e sem a pergunta respondida, e ausente quando o CPF sai dos documentos com IR "não sei"; teste de motor do esclarecimento que some quando o procedimento deixa de se aplicar; único esclarecimento da situação.
- Gates: ruff format, ruff check, mypy e pytest verdes (423 passed; eram 417). `git diff --check` limpo.
- Verificação no navegador (25/10/2026, Chromium headless via CDP): CPF e "Não sei" no IR mostram a etapa de consulta, com canais, requisitos, custo, prazo, fonte e "Alterar essa resposta"; trocar para "Sim", responder "Não" ou tirar o CPF da lista remove a etapa; 360 px sem overflow; console sem erros.

**Fatia 9 — pesquisa perda × furto/roubo (25/10/2026).**

- Só pesquisa e documentação; nenhum código, TOML ou teste foi alterado. Conferidas as páginas atuais da Delegacia Online (Polícia Civil e espelho na SSP-MA), da 2ª via da CNH e da tabela de taxas (DETRAN-MA), das perguntas frequentes da CIN e da notícia da SSP-MA, e do cartão de CPF (gov.br). Trechos literais e conclusão por procedimento em [evidências](../dados/evidencias/perda-de-documentos.md#perda--furtoroubo-fatia-9-25102026).
- Resultado: o DETRAN-MA trata "extravio, furto, roubo ou danificação" como o mesmo serviço (mesmo B.O., RG, canal e taxa; o valor varia entre CNH, R$ 90,00, e PpD, R$ 75,00, não pela causa). CPF e CIN não mencionam a causa. A Delegacia Online lista "extravio de documentos" e "furto simples" e não cita roubo; o indício de que roubo não seria registrável online vem só da frase "não envolvem violência, ameaça" e não está confirmado.
- Estado: a pergunta "foi perda, furto ou roubo?" **não entra** (Pendente em [jornadas](../produto/jornadas.md) e em [pendências](../pendencias.md), item 16). Motivo: nenhuma fonte muda o plano conforme a causa, então a pergunta violaria a RN02. Gatilho para reavaliar: fonte oficial dizendo que roubo não é registrável na Delegacia Online.
- Não abriram: https://delegaciaonline.ssp.ma.gov.br/ e ident.ssp.ma.gov.br (DNS não resolve; o segundo foi endereço tentado, não link encontrado); notícia da Secom sobre a 2ª via da CIN após perda (redireciona para login); https://www.ssp.ma.gov.br/ident/ (404). A Delegacia Online é uma notícia de 2018 e o formulário atual não foi lido.
- Gates não rodados: a fatia não muda código. `git diff --check` limpo.

## Fase 8 — Hospedagem

Decisão e alternativas em [ADR 0006](../arquitetura/decisoes/0006-hospedagem-e-deploy.md). Esta seção registra o que foi feito, na ordem.

- **8a — Dockerfile e conexão segura (`de7d221`).** Imagem em dois estágios com uv, usuário não-root e `.dockerignore`. Dependência nova: `gunicorn`. `settings.py` ganhou `POSTGRES_SSLMODE` (padrão `prefer`; o Neon exige `require`). Motivo: manter as variáveis `POSTGRES_*` que dev e teste já usam, em vez de adotar `DATABASE_URL`.
  - Dois problemas achados ao construir a imagem: o `.python-version` fixa `3.15.0` e a imagem traz `3.15.1` (arquivo fora da imagem pelo `.dockerignore`), e o gunicorn falhava sem diretório home do usuário da imagem (`useradd --create-home`).
- **8b — Estáticos, proxy e migrate (`94f9ec7`).** Dependência nova: `whitenoise`. `collectstatic` no build, `STATIC_ROOT`, e `DJANGO_BEHIND_PROXY=1` para `SECURE_PROXY_SSL_HEADER`. O `CMD` roda `migrate --noinput` antes do gunicorn (atalho `shortcut:` registrado no Dockerfile). Testes para o cabeçalho do proxy e para a ordem do middleware; o aviso do WhiteNoise sobre `staticfiles/` ausente é filtrado no pytest.
- **8c — Carga em produção.** Com `.env.production` (fora do git): `load_sources content/sources.toml` (9 órgãos, 23 fontes), `fetch_sources` (23 de 23 OK) e `load_content content` (3 situações, 6 perguntas, 14 procedimentos, 12 escolhas de triagem). O primeiro comando sugerido omitia o diretório e a ordem de carga; foi corrigido na sessão.
- **8d — Deploy no Render.** O primeiro acesso retornou 400 por `DJANGO_ALLOWED_HOSTS` incorreto no painel; corrigido o valor, o site passou a responder.
- **8e — Latência entre perguntas.** Cada resposta levava segundos porque o Render estava em Oregon e o Neon em São Paulo. Cada resposta (POST, redirecionamento e GET) recarrega o catálogo duas vezes: 16 a 19 consultas por carga, medidas no dev. Somadas à sessão no banco e a uma conexão TLS nova por request, são cerca de 50 idas e voltas entre os continentes.
  - Correção operacional: novos projetos no Render e no Neon, ambos em Virginia, porque nenhum dos dois muda a região de um serviço existente.
  - Correção no código: `CONN_MAX_AGE=60` com `CONN_HEALTH_CHECKS`, para reusar a conexão entre requests.
  - O cache do catálogo em memória ficou de fora: só entra se a medição depois da mudança mostrar uma resposta acima de 500 ms.
  - Pendente: carga do conteúdo no banco novo, jornada completa no Render novo e medição de antes e depois.
- **Gates da 8b:** ruff, mypy, 426 testes e `git diff --check` verdes. A imagem foi validada localmente (estáticos com 200; `migrate` falha de forma explícita sem banco).
- **Não verificado:** jornada completa até o plano em produção (CSRF atrás do proxy), limites atuais dos planos gratuitos, backup e monitoramento do banco.

## Fase 9 — Redesenho visual

Motivo: o autor achou a interface simples demais e pouco convidativa para o cidadão. As restrições da [ADR 0004](../arquitetura/decisoes/0004-frontend-e-acessibilidade.md) continuam: CSS próprio, sem build, sem JS obrigatório e meta WCAG 2.2 AA.

A direção visual vem das fachadas de São Luís: fundo cor de cal, azulejo azul-cobalto com ocre e verde-petróleo nas ações. Só a faixa de azulejo do cabeçalho é ornamento; o resto da interface fica sóbrio. Os cartões usam borda sólida com a base mais grossa, como o vidrado de um ladrilho, no lugar de sombra.

- **9a — Paleta e base.** Novos tokens em `site.css`, com a tabela de contraste recalculada: o menor par de texto é 6,35:1 e o botão primário tem 7,33:1. O cabeçalho ganhou a faixa e a marca (`azulejo.svg`, desenho próprio e decorativo, com `alt=""`). Botões, opções, avisos e etapas receberam raio maior e borda com base mais grossa. A opção marcada usa fundo `--soft` e borda `--ink`.
- **9b — Triagem ilustrada.** As escolhas da triagem viraram cartões com um ladrilho ocre de ícone: uma coluna no celular e duas no desktop. A pergunta inicial ficou maior e funciona como abertura da página.
  - O ícone vem do campo opcional `TriageChoice.icon` (migration `0006`), declarado em `content/triage.toml`.
  - O loader recusa valores fora de `TriageChoice.Icon`.
  - Cada valor tem um SVG em `guidance/templates/guidance/icons/`, incluído no HTML com `aria-hidden="true"`. O rótulo continua sendo o nome acessível do link.
  - Os ícones são do Lucide (licença ISC, em `LICENSE-lucide.txt`), copiados como arquivos, sem dependência nova.
  - Testes: ícone salvo e opcional, ícone inválido recusado, ícone decorativo ou ausente na página e um template para cada valor.
  - Depois do deploy, é preciso repetir `load_content` em produção para preencher os ícones.
- **9c — Etapas da conversa.** Pergunta, preferência de atendimento e plano mostram as etapas Assunto → Perguntas → Atendimento → Plano (`_journey_steps.html`).
  - Não há barra percentual porque o total de perguntas é adaptativo, e um "3 de 7" seria falso.
  - O estado não depende só da cor: a etapa atual tem `aria-current="step"` e negrito, e as concluídas têm ✓ e o texto oculto "(concluída)".
  - No plano, "Atendimento" só aparece como concluída se houver preferência escolhida.
- **9d — Plano.** O topo (aviso orientativo, dica de impressão e preferência) ficou num bloco compacto (`plan-intro`). O resumo virou uma linha do tempo com números em ladrilho cobalto, linha tracejada e cada passo num cartão.
  - "O que separar antes" usa marcador de ladrilho na tela e caixa de conferir só na impressão: na tela, uma caixa vazia pareceria um checkbox que não responde.
  - As etapas mostram "Passo N" como selo e ícones decorativos por seção (órgão, requisitos, canais, custo, prazo e fonte), também na página do serviço. Os ícones entram por máscara CSS a partir de `static/guidance/icons/` (Lucide, ISC), na ordem dos `dt` de `_procedure_facts.html`, sem mudar o HTML.

## Limitações conhecidas

- O banco não garante que o snapshot de uma importação pertence à mesma fonte da importação. Essa garantia hoje é só do código de coleta (`sources/services.py`).
- `load_sources` recusa a troca de URL entre duas fontes já cadastradas (marcado como `shortcut:` no código). Isso será tratado se surgir um caso real.
- A validação de `load_content` roda fora da transação de escrita. Uma coleta concorrente entre as duas etapas pode invalidar a verificação. É um risco baixo para um comando executado manualmente.
- Uma dependência condicional cuja etapa dependente é um pré-requisito puxado (não candidato) não torna a sua pergunta elegível como próxima pergunta. Sem dependências condicionais no conteúdo atual, isso ainda não tem efeito.
- **Fonte mostrada por slug.** O plano mostra a fonte pelo slug, e o link de fontes `GOVBR_API` abre o JSON da API, o que não serve ao cidadão. Na Fase 6, exibir um nome legível e preferir a página HTML do serviço.
- **Etapa sem data de atualização.** As etapas citadas pela ficha da API, como "regularizar CPF suspenso", aparecem com data de atualização "Não informado", porque a API não declara essa data. Revisar o conteúdo para citar a página HTML, que traz "Última Modificação" (RN12).
- **Esquema de URL não validado.** O loader não valida o esquema das URLs de canais e fontes; aceita qualquer texto. O conteúdo é curado e versionado, mas convém restringir a `https://`.
- O conteúdo bruto completo da página HTML é guardado em `TEXT` no banco. As páginas têm até cerca de 150 KB. Não há armazenamento de arquivos brutos fora do banco.
- **Trecho dependente da ordem do JSONB.** O prazo do CAGED cita "30 dias-corridos" da API 7839. Esse texto é formado pela ordem das chaves do JSONB (`max`, depois `unidade`). Se o formato mudar, a carga falha de forma explícita. Melhor citar a página HTML quando a amostra cobrir esse trecho.
- **Amostras HTML truncadas.** As amostras são trechos do texto da página. Afirmações fora do trecho ficam de fora do conteúdo, mesmo existindo na página real (exemplos: conta gov.br, custo dos seguros). Para ampliar a cobertura, é preciso refazer as amostras com o texto completo.
- **Uma só dependência no conteúdo.** Só a perda de documentos tem dependência (B.O. antes da 2ª via da CNH, desde a 5c). Dependências condicionais e recomendadas só são exercidas pelos testes do motor.
- **Esfera da Caixa inferida.** A Caixa (FGTS) foi cadastrada como FEDERAL por inferência; a página não declara a esfera.
- **Busca sensível a acentos.** A busca "Onde resolvo?" usa `icontains`: "demissao" não encontra "demissão". Com o catálogo pequeno o impacto é baixo; a alternativa é a extensão `unaccent` ou a busca textual do Postgres.
