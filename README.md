# O que Fazer?

Plataforma web de TCC (Sistemas de Informação — UNDB) que orienta o cidadão no acesso a serviços públicos federais, do Maranhão e de São Luís a partir de situações cotidianas. O cidadão escolhe o que aconteceu, responde perguntas e recebe um plano ordenado de providências, com órgão, canais, requisitos e fonte oficial.

O sistema é apenas orientativo: não executa serviços, não autentica nos portais oficiais e não confirma direitos.

Documentação completa em [`docs/`](docs/README.md).

## Requisitos

- [uv](https://docs.astral.sh/uv/) 0.13 (instala o Python 3.15 do projeto)
- Docker com Docker Compose (PostgreSQL 18)
- Acesso à internet para coletar as fontes oficiais

## Como rodar

```sh
# 1. Configuração local e banco de desenvolvimento (oqf_dev)
cp .env.example .env
docker compose --env-file .env up -d

# 2. Dependências e esquema do banco
uv sync
uv run --env-file .env python manage.py migrate

# 3. Conteúdo: órgãos e fontes, coleta das páginas oficiais e catálogo
uv run --env-file .env python manage.py load_sources content/sources.toml
uv run --env-file .env python manage.py fetch_sources
uv run --env-file .env python manage.py load_content content

# 4. Servidor
uv run --env-file .env python manage.py runserver
```

Acesse <http://127.0.0.1:8000/>. Rotas principais:

- `/` — situações ("O que faço agora?");
- `/onde-resolvo/` — busca por serviço ("Onde resolvo?").

A ordem do passo 3 importa:

- `fetch_sources` grava um snapshot de cada fonte oficial. Use `--source <slug>` para coletar só uma.
- `load_content` confere cada trecho citado nos TOML contra esses snapshots. Ele falha se um trecho não estiver na página coletada.

Quando uma página oficial mudar, rode de novo `fetch_sources` e depois `load_content`.

## Testes e gates

```sh
uv run ruff format --check . && uv run ruff check . && uv run --env-file .env mypy . && uv run --env-file .env pytest
git diff --check
```

Os testes usam o banco `oqf_test`, criado e destruído pelo pytest-django. Eles não acessam a internet: os snapshots vêm das amostras em `docs/dados/amostras/`.

A cobertura fica fora dos gates. Para medir, rode `uv run --env-file .env pytest --cov`; a configuração está em `[tool.coverage]` no `pyproject.toml`.

## Estrutura

| Pasta | Conteúdo |
| --- | --- |
| `sources/` | Órgãos, fontes oficiais, coleta e snapshots |
| `catalog/` | Situações, perguntas, procedimentos, regras e dependências carregados de `content/` |
| `guidance/` | Motor de orientação (`guidance/engine/`, Python puro) e telas |
| `content/` | Conteúdo versionado em TOML, uma jornada por arquivo |
| `docs/` | Produto, arquitetura, dados e documentação acadêmica |
