# Amostras brutas das fontes (coleta de 10/10/2026)

Amostras coletadas por `curl` (sem WebFetch). Os arquivos `api-servicos-*.json` contêm a ficha completa, formatada e sem alteração de conteúdo. Os arquivos `html-*.md` não contêm o HTML bruto: trazem URL, HTTP, data/hora da coleta, a linha de data declarada, o SHA-256 do HTML completo e de 40 linhas de texto literal (tags removidas com `html.parser`).

Fonte de identidade (`https://www.gov.br/identidade`) não foi amostrada: ver Falhas.

| arquivo | fonte | tipo | HTTP | data da coleta | "Última Modificação" declarada | sha256 (só HTML) |
| --- | --- | --- | --- | --- | --- | --- |
| `api-servicos-10416.json` | API `servicos.gov.br/api/v1/servicos/10416` | API (JSON) | 200 | 2026-10-10T20:44:12-03:00 | não há campo na ficha | — |
| `api-servicos-10420.json` | API `servicos.gov.br/api/v1/servicos/10420` | API (JSON) | 200 | 2026-10-10T20:44:14-03:00 | não há campo na ficha | — |
| `api-servicos-10424.json` | API `servicos.gov.br/api/v1/servicos/10424` | API (JSON) | 200 | 2026-10-10T20:52:02-03:00 | não há campo na ficha | — |
| `api-servicos-1045.json` | API `servicos.gov.br/api/v1/servicos/1045` | API (JSON) | 200 | 2026-10-10T20:44:31-03:00 (2ª tentativa; 1ª falhou, ver Falhas) | não há campo na ficha | — |
| `api-servicos-7839.json` | API `servicos.gov.br/api/v1/servicos/7839` | API (JSON) | 200 | 2026-10-10T20:44:22-03:00 | não há campo na ficha | — |
| `api-servicos-9815.json` | API `servicos.gov.br/api/v1/servicos/9815` | API (JSON) | 200 | 2026-10-10T20:44:21-03:00 | não há campo na ficha | — |
| `html-atualizar-cadastro-de-pessoas-fisicas.md` | https://www.gov.br/pt-br/servicos/atualizar-cadastro-de-pessoas-fisicas | HTML (trecho) | 200 | 2026-10-10T20:47:46-03:00 | Última Modificação: 24/09/2026 | `0cc4b87ba34527e3263b067cdb9453b9f5b7557740399c0d28767de6922721ac` |
| `html-declarar-meu-imposto-de-renda.md` | https://www.gov.br/pt-br/servicos/declarar-meu-imposto-de-renda | HTML (trecho) | 200 | 2026-10-10T20:47:47-03:00 | Última Modificação: 12/08/2026 | `6a17e7d611951c17f7a1e0f03c00184e13cb23da771355a91e07070a58209fce` |
| `html-fgts-saque-dispensa.md` | https://www.fgts.gov.br/Paginas/subpaginas/saque-dispensa.aspx | HTML (trecho) | 200 | 2026-10-10T20:47:50-03:00 | não informado | `e56bddefd311a217fbada08063c0fc4524df53fc73403f53419948bf3c0d3c11` |
| `html-inscrever-no-cpf.md` | https://www.gov.br/pt-br/servicos/inscrever-no-cpf | HTML (trecho) | 200 | 2026-10-10T20:47:47-03:00 | Última Modificação: 08/10/2026 | `e1b1649c57dd9b9b90367122391595e2f5d99a0104829d87bb6540a7e1b24da4` |
| `html-obter-a-carteira-de-trabalho.md` | https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho | HTML (trecho) | 200 | 2026-10-10T20:47:49-03:00 | Última Modificação: 15/12/2025 | `dd868ab40ba7a900fc9e6b610a8a63ae007ff6fd31c7236105381dc1a8535661` |
| `html-obter-cartao-de-cpf.md` | https://www.gov.br/pt-br/servicos/obter-cartao-de-cpf | HTML (trecho) | 200 | 2026-10-10T20:47:45-03:00 | Última Modificação: 06/08/2026 | `a6372841b7f5bf54ff857438103ebbccec60d2c2dd00d143c7b964d6b5af0230` |
| `html-policiacivil-delegacia-online.md` | https://www.policiacivil.ma.gov.br/delegacia-online/ | HTML (trecho) | 200 | 2026-10-10T20:49:44-03:00 | Publicado em: quinta-feira, 1 de março de 2018 | `4a658f32c2dafa83cadc0ca719169e9d8033e8df9ce2ee215655696839f927c0` |
| `html-receitafederal-meu-cpf.md` | https://www.gov.br/receitafederal/pt-br/assuntos/meu-cpf | HTML (trecho) | 200 | 2026-10-10T20:47:50-03:00 | não informado | `1ccadf24bdb58df8ed8f0d738a5579c886c1417c840866c6d5245ff40335f316` |
| `html-solicitar-o-seguro-desemprego.md` | https://www.gov.br/pt-br/servicos/solicitar-o-seguro-desemprego | HTML (trecho) | 200 | 2026-10-10T20:47:48-03:00 | Última Modificação: 25/09/2026 | `3ab5f5396ebf4e10ecbc9a93fe35a056b67c483e84523169dfb5f19bd3b4f972` |
| `html-solicitar-seguro-desemprego-empregado-domestico.md` | https://www.gov.br/pt-br/servicos/solicitar-seguro-desemprego-empregado-domestico | HTML (trecho) | 200 | 2026-10-10T20:47:48-03:00 | Última Modificação: 23/09/2026 | `2eb5e1059b250a41f2cabfddfc42be3da0927df56f4cf98df80cf19ed3abd87c` |
| `html-solicitar-vinculos-empregaticios-do-caged.md` | https://www.gov.br/pt-br/servicos/solicitar-vinculos-empregaticios-do-caged | HTML (trecho) | 200 | 2026-10-10T20:47:49-03:00 | Última Modificação: 25/08/2026 | `96d3b10960089545b2559041154ffc67afecd14c23d7dbc2e113d960ec0092b0` |

## Falhas

- **https://www.gov.br/identidade** (página de identidade citada em `perda-de-documentos.md`): falhou. `curl -sSL` resultou em HTTP 404, corpo `{"error_type": "NotFound"}`, após 2 redirecionamentos para `https://www.gov.br/governodigital/pt-br/identificacao-do-cidadao`, que também responde 404. Em 10/10/2026, 20:49:21. Outras tentativas: `curl -I` sem User-Agent retornou `HTTP/1.1 403 Forbidden`; uma execução anterior, com redirecionamento distinto, indicou `HTTP 302` para `https://www.gov.br/gestao/pt-br/identidade`, que também retornou 404 (`governodigital/.../identificacao-do-cidadao`). Nenhuma amostra foi salva. A evidência de `perda-de-documentos.md` (página "confirmada") não se reproduziu.
- **https://www.policiacivil.ma.gov.br/delegacia-online/**: primeira tentativa falhou com `curl: (28) Operation timed out after 90001 milliseconds with 32768 bytes received`. Nova tentativa em 10/10/2026, 20:49:44, retornou HTTP 200 com 144615 bytes; a amostra usa esta segunda coleta.
- **https://servicos.gov.br/api/v1/servicos/1045**: primeira tentativa falhou com `curl: (60) SSL: no alternative certificate subject name matches target host name 'servicos.gov.br'`. Duas novas tentativas, com verificação TLS normal, retornaram HTTP 200 (20:44:29 e 20:44:31). Não foi usado `-k`. A amostra usa a segunda tentativa de 20:44:31.
- **https://www.fgts.gov.br/.../saque-dispensa.aspx**: coletada, mas sem data "Última Modificação" ou "Atualizado em" no HTML. Registrado como "não informado".
- **https://www.gov.br/receitafederal/pt-br/assuntos/meu-cpf**: coletada, sem data no HTML. Registrado como "não informado".

## Identificadores (tarefa 3)

- **Obter Cartão de CPF**: ID **10424**. Confirmado: `servicos/10424` retorna HTTP 200 com `nome` = "Obter Cartão de CPF" (`api-servicos-10424.json`). A página HTML confirma o mesmo ID em `window.histData`, com `nome` = "Obter comprovante de inscrição no CPF". A página `obter-cartao-de-cpf` menciona 10424, não 10416. Divergência de nome dentro do próprio site.
- **Serviço de identidade do Gov.br**: ID **não localizado**. Busca de URLs com WebSearch e varredura por `servicos/N`, `?id=N` e `identificador=N` em 3 páginas gov.br de identidade não encontraram nenhum ID. Uma das URLs (`.../onde-posso-requerer-a-segunda-via`) retornou 404.

## Notas

- Todas as páginas HTML foram baixadas com `User-Agent: Mozilla/5.0`. As fichas da API foram baixadas sem User-Agent.
- O extrato de texto é gerado por `/tmp/oqf-amostras-scripts/extract_text.py` (`python3 -I`, `html.parser`), fora do repositório.
- Os HTML baixados estão somente em `/tmp/oqf-amostras-raw/`. Nenhum HTML bruto foi salvo no repositório.

## Coleta de 24/10/2026

Mesmo método da coleta de 10/10, com duas diferenças: o extrato de texto descarta o conteúdo de `script`, `style` e `noscript`, e o User-Agent é o de um navegador desktop (`Mozilla/5.0 (X11; Linux x86_64) ... Chrome/130`). Script fora do repositório (`/tmp/oqf-scripts/`); HTML bruto só em `/tmp/oqf-coleta/raw/`.

| arquivo | fonte | tipo | HTTP | data da coleta | data declarada | sha256 (só HTML) |
| --- | --- | --- | --- | --- | --- | --- |
| `html-govbr-cin-faq.md` | https://www.gov.br/governodigital/pt-br/identidade/cin/perguntas-frequentes-sobre-a-cin | HTML (trecho: emissão, certidão, segunda via e CPF de menores; 60 linhas) | 200 | 2026-10-24T23:54:06-03:00 | Publicado em 12/04/2023; Atualizado em 16/07/2026 | `c3424804bafd1f054ef0035844a52a0bae62a6e78162e308f97e9bdf5b65f096` |
| `html-ssp-cin-ma.md` | https://www.ssp.ma.gov.br/governo-passa-a-emitir-nova-carteira-de-identidade-nacional-em-todo-o-maranhao/ | HTML (trecho; notícia) | 200 | 2026-10-24T23:51:13-03:00 | Publicado em: sexta-feira, 12 de janeiro de 2024 | `b01123b71f3dd40545a86c579a3d1980ed031124eedff2768bc7116aaf102eb1` |
| `html-detran-2via-cnh.md` | https://www.detran.ma.gov.br/inicio/paginas/Pagina.xhtml?id=19297 | HTML (trecho) | 200 | 2026-10-24T23:51:21-03:00 | não informado | `36ea71abdfef1f9ed6fd5899ecc5a4ce7cda1b5b4f9398f75c748b5ccac57ec7` |
| `html-detran-taxas.md` | https://www.detran.ma.gov.br/inicio/paginas/Taxas.xhtml | HTML (trecho: segunda via CNH) | 200 | 2026-10-24T23:51:23-03:00 | não informado | `c1068152fb36ead0f92c128f91b9de5a447e85074ccb5bf263ea6cceadcfb566` |
| `html-detran-transf-digital.md` | https://www.detran.ma.gov.br/inicio/paginas/Pagina.xhtml?id=23692 | HTML (trecho) | 200 | 2026-10-24T23:51:11-03:00 | não informado | `4b08e2995ce07e85f1870b48810a3642a1eef24fdc2acf13d6c44293d968c9ea` |
| `html-govbr-restricoes-veiculo.md` | https://www.gov.br/pt-br/servicos/consultar-informacoes-sobre-restricoes-e-indicadores-de-veiculos | HTML (trecho) | 200 | 2026-10-24T23:51:13-03:00 | Última Modificação: 15/12/2025 | `ad46bf0e5d676b38554dd4cf30dea7e582e85156d76ecebd72407eb750623379` |
| `html-govbr-sine-emprego.md` | https://www.gov.br/pt-br/servicos/buscar-emprego-no-sistema-nacional-de-emprego-sine | HTML (trecho) | 200 | 2026-10-24T23:51:14-03:00 | Última Modificação: 15/12/2025 | `04e1324417abc7da680003731159f076e1d0e836da5e6bdcbd9e2483abb1e0cb` |
| `html-govbr-cadunico-inscrever.md` | https://www.gov.br/pt-br/servicos/inscrever-se-no-cadastro-unico-para-programas-sociais-do-governo-federal | HTML (trecho) | 200 | 2026-10-24T23:51:14-03:00 | Última Modificação: 15/12/2025 | `5a4c098f1e8b0a5477a719f461177592c4811b2f01e85d3091a856daf659226b` |
| `html-govbr-sus-cadastro.md` | https://www.gov.br/pt-br/servicos/atualizar-informacoes-cadastrais-do-cidadao-no-sus | HTML (trecho) | 200 | 2026-10-24T23:51:15-03:00 | Última Modificação: 21/10/2026 | `8e04ffe76d90f55acb0b711114c2e15524117dc6461f003858cb8f51c3ac7d72` |
| `html-sl-2via-certidao-nascimento.md` | https://www.saoluis.ma.gov.br/portal/carta-servicos/11/ | HTML (trecho) | 200 | 2026-10-24T23:55:23-03:00 | Atualizado em: 05/05/2026 | `29862a69c836a92c15839dc8ae5051a296f727cd21f58f1b1e23c273a3968335` |

### Falhas em 24/10/2026

- **DETRAN-MA, URLs antigas** `.../paginas/detalhe/{id}`: HTTP 404. O conteúdo migrou para `.../inicio/paginas/Pagina.xhtml?id={id}`.
- **DETRAN-MA, ids 19272 (transferência presencial), 19281 (mudança de município), 19279 (mudança de UF) e 19481 (orientações gerais)**: HTTP 200, mas o corpo vem sem o texto do serviço (só o título; conteúdo carregado por JavaScript). Sem amostra; exigem conferência no navegador.
- **TSE e TRE-MA** (`tse.jus.br`, `tre-ma.jus.br`): HTTP 403, como em 10/10.
- **Ident-MA** (`agendamento.ssp.ma.gov.br`): sem resposta (timeout).
- **Catálogo estadual** (`ma.gov.br/todos-os-servicos`): a lista de serviços é carregada por JavaScript; o HTML não traz os serviços.
- **Página federal da CIN** (`gov.br/governodigital/pt-br/identidade/cin`): 200, mas sem data declarada; foi usada a página de perguntas frequentes, que declara data.

### Conferência manual de 25/10/2026 (feita pelo autor no navegador)

- **DETRAN-MA, ids 19272, 19281, 19279 e 19481**: no navegador, em vez do conteúdo, aparece um aviso de **defeso eleitoral**: "Em atendimento à legislação eleitoral, os conteúdos desta sessão de notícias ficarão indisponíveis de 4 de julho de 2026 até o final da eleição estadual no Maranhão" (imagem `https://www.detran.ma.gov.br/inicio/content/imagens/periodo/Capa_de_site-aviso_de_suspensao.png`, SHA-256 `c6ec3a1d11c1a4a4c6e6410bc6d9f49c02a62f0eb7b1f48645d1da7c2c1632ca`, baixada em 2026-10-25T01:00:57-03:00). A indisponibilidade é temporária: recoletar depois da eleição.
- **Ident-MA** (`agendamento.ssp.ma.gov.br`): a página é só um formulário de agendamento (nome, nome da mãe, CPF, cidade, serviço, data). Não traz requisitos, documentos nem taxa da 2ª via da CIN. Não serve como fonte de requisitos.
- **TSE / TRE-MA** (2ª via do título e transferência de domicílio eleitoral): o autor não localizou as páginas.
- **Registro de nascimento em cartório** (TJMA): o autor não localizou uma página de orientação ao cidadão.
