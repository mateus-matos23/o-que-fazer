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
