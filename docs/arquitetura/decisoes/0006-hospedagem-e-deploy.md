# ADR 0006 — Hospedagem do protótipo: Render (Docker) e Neon (PostgreSQL)

**Estado:** Consolidado.
**Data:** 26/10/2026

## Contexto

O protótipo precisa de uma URL pública para a avaliação do TCC, sem custo e com pouca manutenção. O tráfego esperado é baixo. A [ADR 0001](0001-stack.md) deixou a hospedagem em aberto, e a stack exige Python 3.15, que as plataformas de runtime Python gerenciado ainda não oferecem de forma confiável; por isso a aplicação precisa ser entregue como contêiner.

Planos gratuitos mudam com frequência. Os limites abaixo não foram reverificados na documentação oficial na data desta decisão e devem ser conferidos antes de qualquer mudança de plano.

## Decisão

1. **Aplicação no Render**, como Web Service com runtime Docker, construído a partir do `Dockerfile` do repositório.
2. **Banco no Neon**, em um projeto separado do desenvolvimento e do teste. Os três bancos são distintos: `oqf_dev` (local), `oqf_test` (criado e destruído pelo pytest-django) e o banco de produção no Neon. Seed, migrate e carga de conteúdo só atingem produção por comando explícito com `--env-file .env.production`.
3. **Imagem** em dois estágios (`python:3.15-slim`; uv 0.13.0 copiado da imagem oficial). As dependências são instaladas antes do código para aproveitar o cache, a execução é com usuário não-root e o `.python-version` fica fora da imagem (ele fixa `3.15.0` e a imagem traz `3.15.x`).
4. **Servidor:** gunicorn. Arquivos estáticos servidos pelo WhiteNoise, coletados no build da imagem (`collectstatic`).
5. **Configuração só por variáveis de ambiente**, sem `DATABASE_URL` nem dependência de leitura de `.env` em produção:
   - `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` (domínio exato, sem esquema nem barra) e `DJANGO_DEBUG` ausente;
   - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_SSLMODE=require`, usando o host direto do Neon (sem `-pooler`);
   - `DJANGO_BEHIND_PROXY=1`, que ativa `SECURE_PROXY_SSL_HEADER`. Sem ele, o CSRF rejeita os POSTs atrás do proxy TLS do Render.
     - Revisto em 26/10/2026: a mesma variável liga também `SECURE_SSL_REDIRECT`, cookies de sessão e CSRF com `Secure` e HSTS de 1 hora com `includeSubDomains`. O valor curto e a ausência de preload existem porque o HSTS é difícil de reverter no navegador. O preload também exige domínio próprio, e o aviso `security.W021` fica silenciado por isso. O Render já redireciona para HTTPS e aceita resposta 3xx no health check.
6. **Migrations** rodam no início de cada instância (`CMD`: `migrate --noinput` e depois gunicorn).
7. **Conteúdo** é carregado manualmente, da máquina do mantenedor, contra o banco de produção, na ordem `load_sources content/sources.toml` → `fetch_sources` → `load_content content`. A ordem importa porque `load_content` verifica cada trecho citado contra o snapshot coletado.

## Alternativas descartadas

- **Código sugerido pelo Neon** (`python-dotenv` e `DATABASE_URL` com `urlparse`): exigiria dependência nova, quebraria os bancos de dev e de teste que usam variáveis `POSTGRES_*` separadas, não decodifica a senha da URL e falha de forma obscura quando a variável falta. O `settings.py` existente cobre o caso com `POSTGRES_SSLMODE`.
- **`dj-database-url`:** dependência a mais para o que o `settings.py` já resolve.
- **PythonAnywhere:** PostgreSQL só em plano pago e versão do Python limitada.
- **Fly.io e Railway:** sem plano gratuito contínuo.
- **Cloud Run e Oracle Cloud:** viáveis, mas exigem conta e cartão em nuvem pública ou administração do servidor, sem ganho que o protótipo precise.

## Consequências

- **Cold start.** O plano gratuito do Render dorme após cerca de 15 minutos sem acesso; o primeiro acesso seguinte leva cerca de 1 minuto e roda `migrate` de novo. Isso deve ser avisado a quem avalia o protótipo.
- **Atalho (`shortcut:`).** `migrate` no start é seguro com uma única instância. Com mais de uma réplica, deve virar um comando de release.
- **Conteúdo fora do deploy.** Publicar o código não atualiza o catálogo; mudanças em `content/` exigem repetir `load_content` (e `fetch_sources`, se houver fonte nova) contra produção. O plano exibe a data de coleta desta carga, distinta da data de vigência (RN12).
- **Região (revisto em 26/10/2026).** Aplicação e banco ficam na mesma região, Virginia nos dois. Com o Render em Oregon e o Neon em São Paulo, cada resposta somava cerca de 50 idas e voltas entre continentes, o que dava segundos de espera. O Django reusa a conexão entre requests (`CONN_MAX_AGE=60`, com `CONN_HEALTH_CHECKS` para quando o Neon escala para zero). Nenhum dos dois provedores muda a região de um serviço existente; mudar exige criar outro e recarregar o conteúdo.
- **Segredos.** `.env.production` está no `.gitignore` e no `.dockerignore`; as variáveis do Render são configuradas no painel.
- **Sem backup nem monitoramento** definidos para o banco de produção. Seguem pendentes, assim como domínio próprio.
- **Validação.** Contêiner testado localmente (estáticos servidos com 200; `migrate` falha de forma explícita sem banco). Em produção, a página inicial respondeu após a correção de `DJANGO_ALLOWED_HOSTS`. A jornada completa até o plano, que valida o CSRF atrás do proxy, ainda deve ser percorrida e registrada.
