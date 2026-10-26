# O que Fazer?

Plataforma web de TCC (Sistemas de Informação — UNDB) que orienta o cidadão no acesso a serviços públicos federais, do Maranhão e de São Luís a partir de situações cotidianas. O cidadão informa o que aconteceu, responde perguntas progressivas e recebe um plano ordenado de providências, com órgão, canais, requisitos e fonte oficial.

O sistema é **orientativo**: não executa serviços, não autentica nos portais oficiais, não consulta dados pessoais restritos e não confirma direitos ou elegibilidade.

## Fase atual

Fases 0 a 7 concluídas (núcleo, três jornadas, interface com meta WCAG 2.2 AA, busca "Onde resolvo?" e conversa guiada: funil de triagem, efeito da resposta, preferência de atendimento e plano com "Comece por aqui"). RF02 (texto livre) segue pendente. Antes de implementar algo, confira a documentação em `docs/` e as decisões em aberto em `docs/pendencias.md`.

## Comandos

- Banco local: `cp .env.example .env` e `docker compose --env-file .env up -d` (Postgres 18).
- Comandos Django e gates sempre com `uv run --env-file .env ...`.
- Gates: `uv run ruff format --check . && uv run ruff check . && uv run --env-file .env mypy . && uv run --env-file .env pytest`.
- Os testes usam o banco `oqf_test`, criado e destruído pelo pytest-django; o banco de desenvolvimento é `oqf_dev`.

## Stack

- Python 3.15, Django 6.1.2, PostgreSQL 18, uv 0.13.0 — ver `docs/arquitetura/decisoes/0001-stack.md`.
- Aplicação monolítica Django; sem microsserviços.
- Dependências sempre via `uv add <pacote>`; comandos via `uv run` (ex.: `uv run python manage.py migrate`).

## Convenções

- **Idioma**: identificadores de código (apps, models, campos, funções) em inglês; textos de interface, documentação e mensagens ao usuário em português.
- **Vocabulário**: use os termos e nomes em inglês definidos no glossário abaixo. Não crie sinônimos.
- **Documentação**: registre decisões de arquitetura como ADR em `docs/arquitetura/decisoes/NNNN-titulo.md`. Mantenha os estados (Consolidado, Proposto, Histórico, Futuro, Pendente) ao editar `docs/`.
- **Não inventar**: não preencha lacunas (URLs, custos, prazos, regras, números de avaliação) por suposição. Registre como pendência.

## Invariantes do domínio

1. Toda orientação publicada tem fonte oficial rastreável, com data de coleta distinta da data de vigência.
2. Aplicabilidade é ternária: aplicável, não aplicável ou indeterminado.
3. "Não sei" mantém o fato desconhecido; nunca vira resposta negativa.
4. Decidir **o que se aplica** (regras sobre fatos) é separado de decidir **a ordem** (ordenação topológica das dependências obrigatórias).
5. Ciclo entre dependências é erro de modelagem: falhe explicitamente, não produza uma ordem.
6. Prioridade de exibição nunca cria exigência administrativa inexistente.
7. Custo, prazo ou canal desconhecido aparece como "não informado".
8. Alterar uma resposta reavalia regras e recalcula o plano.
9. Sem cadastro obrigatório para o cidadão; colete o mínimo de dados pessoais.

Regras completas: RF01–RF20 e RN01–RN15 em `docs/produto/requisitos.md`.

## Mapa da documentação

Leia sob demanda o arquivo relevante para a tarefa:

- `docs/README.md` — resumo do projeto, índice e legenda de estados.
- `docs/produto/` — visão, jornadas e casos de borda, requisitos e regras, interface e acessibilidade.
- `docs/arquitetura/` — visão técnica, modelo de domínio, motor de orientação, ADRs.
- `docs/dados/` — fontes oficiais e pipeline de ingestão e proveniência.
- `docs/academico/` — enquadramento do TCC, referencial teórico, normalização, histórico.
- `docs/pendencias.md` — riscos, entregáveis e decisões em aberto.

## Glossário

@CONTEXT.md
