# Evidências — CPF irregular

Registrar, com fontes oficiais acessadas, os serviços e situações cadastrais que orientam o cidadão quando o CPF está irregular; a consulta de situação aparece apenas como esclarecimento intermediário, sem o sistema consultar dados pessoais.

Data da consulta: 2026-10-10. A coluna "Data da consulta" indica quando o conteúdo foi obtido; as datas de atualização declaradas pelas páginas são registradas separadamente (RN12).

## Tabela-resumo

| Serviço | Órgão | Esfera | URL | Formato | Autenticação | Estado da URL | Data da consulta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Consulta da situação cadastral do CPF | Receita Federal do Brasil | Federal | https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp | HTML (formulário) | CPF + data de nascimento; captcha não identificado no conteúdo extraído | confirmada (página carregou) | 2026-10-10 |
| Atualizar CPF / regularização (página do catálogo gov.br) | Receita Federal do Brasil | Federal | https://www.gov.br/pt-br/servicos/atualizar-cadastro-de-pessoas-fisicas | HTML | Não exige login para ler; a solicitação online usa formulário (login gov.br mencionado na ficha da API) | confirmada | 2026-10-10 |
| Regularizar CPF (formulário online, situação suspensa) | Receita Federal do Brasil | Federal | https://servicos.receita.fazenda.gov.br/Servicos/CPF/regularizar/Default.asp | HTML (formulário) | Formulário; exigência de login não informada no conteúdo extraído | confirmada (conteúdo lido) | 2026-10-10 |
| Ficha da API do serviço "Atualizar CPF" (ID 10416) | Órgão do catálogo: Portal de Serviços gov.br (MGI/SGD); órgão competente do serviço: Receita Federal | Federal | https://servicos.gov.br/api/v1/servicos/10416 | JSON | Pública (sem credencial) | confirmada (resposta JSON recebida) | 2026-10-10 |
| Inscrição no CPF (página gov.br) | Receita Federal do Brasil | Federal | https://www.gov.br/pt-br/servicos/inscrever-no-cpf | HTML | Não informado | confirmada | 2026-10-10 |
| Ficha da API do serviço "Inscrever Cidadão no Cadastro de Pessoas Físicas (CPF)" (ID 10420) | Ministério da Gestão e Inovação (Portal de Serviços gov.br) | Federal | https://servicos.gov.br/api/v1/servicos/10420 | JSON | Pública (sem credencial) | confirmada | 2026-10-10 |
| Alterar dados cadastrais no CPF (formulário, situação regular) | Receita Federal do Brasil | Federal | https://servicos.receita.fazenda.gov.br/Servicos/CPF/alterar/default.asp | HTML (formulário) | Formulário | não confirmada (URL citada em página oficial; não acessada) | — |
| Declarar imposto de renda (DIRPF), para status "Pendente de Regularização" | Receita Federal do Brasil | Federal | https://www.gov.br/pt-br/servicos/declarar-meu-imposto-de-renda | HTML | Não informado no conteúdo extraído | confirmada | 2026-10-10 |
| Título de eleitor (regularização do título, papel na regularização do CPF) | Tribunal Superior Eleitoral | Federal | https://www.tse.jus.br/ | Não informado | Não informado | não confirmada (página do TSE retornou 403 e falha de extração) | 2026-10-10 |
| API de Serviços — lista geral (autenticada) | Ministério da Gestão e Inovação | Federal | https://www.servicos.gov.br/api/v1/servicos-auth | JSON (não confirmado) | Token (HTTP 401 sem credencial) | confirmada (retorna 401) | 2026-10-10 |

Observação sobre o tipo de URL na tabela: a linha da DIRPF e a da inscrição referem-se a páginas do catálogo gov.br; a linha do TSE aponta para a raiz do portal, que também não foi acessada (ver seção de observações).

## Situação cadastral → providência oficial

| Situação cadastral (rótulo oficial) | Providência oficial | Fonte |
| --- | --- | --- |
| Regular | Nenhuma pendência; atualizar o cadastro se mudar nome ou endereço. Atualização online: https://servicos.receita.fazenda.gov.br/Servicos/CPF/alterar/Default.asp | https://www.gov.br/receitafederal/pt-br/assuntos/meu-cpf (acessada) |
| Suspenso (no gov.br: "Suspensa") | Corrigir as informações incorretas ou incompletas por meio da regularização. Formulário: https://servicos.receita.fazenda.gov.br/Servicos/CPF/regularizar/Default.asp. Página informa: "A solicitação de regularização de CPF só é permitida para situação cadastral suspensa." | https://www.gov.br/receitafederal/pt-br/assuntos/meu-cpf; https://servicos.receita.fazenda.gov.br/Servicos/CPF/regularizar/Default.asp; https://www.gov.br/pt-br/servicos/atualizar-cadastro-de-pessoas-fisicas |
| Pendente de Regularização | Enviar as declarações de imposto de renda (DIRPF) não entregues. Página: "Esta situação indica que alguma declaração de imposto de renda não foi enviada à Receita Federal." Link: https://www.gov.br/pt-br/servicos/declarar-meu-imposto-de-renda. No gov.br, o critério citado é DIRPF não entregue nos últimos cinco anos. | https://www.gov.br/receitafederal/pt-br/assuntos/meu-cpf; https://www.gov.br/pt-br/servicos/atualizar-cadastro-de-pessoas-fisicas |
| Cancelado | Não informado: a página diz apenas que o cadastro foi cancelado por duplicidade ou decisão de processo, sem providência. | https://www.gov.br/receitafederal/pt-br/assuntos/meu-cpf |
| Nulo | Não informado: a página diz apenas que o cadastro foi considerado nulo por fraude, sem providência. | https://www.gov.br/receitafederal/pt-br/assuntos/meu-cpf |
| Falecido (titular falecido) | Não informado: a página diz que o cadastro tem data de óbito registrada, sem providência indicada. A seção de documentos da página de atualização trata de pedidos relativos a pessoas falecidas (certidão de óbito e legitimidade do solicitante). | https://www.gov.br/receitafederal/pt-br/assuntos/meu-cpf; https://www.gov.br/pt-br/servicos/atualizar-cadastro-de-pessoas-fisicas |
| Papel do título de eleitor na regularização | Não confirmado em fonte oficial acessada. O formulário de regularização tem o campo "Título de Eleitor", mas a página não diz que a atualização do título é condição ou etapa. | https://servicos.receita.fazenda.gov.br/Servicos/CPF/regularizar/Default.asp (campo); TSE não confirmado |

## Serviços

### Consulta da situação cadastral do CPF

- Órgão: Receita Federal do Brasil. Esfera: federal.
- URL: https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp (confirmada).
- Uso no sistema: esclarecimento intermediário. O cidadão é encaminhado à consulta para descobrir a situação; o sistema não consulta dados pessoais.
- Campos do formulário (extraídos): "CPF:" e "Data de Nascimento:". Captcha não mencionado no conteúdo extraído; não verificado no navegador.
- Conteúdo aproveitável: o comprovante "não fornece informações sobre a situação econômica, financeira ou fiscal do titular do CPF, limita-se tão somente a comprovar a situação cadastral no CPF". Exige cookies habilitados.
- Data de atualização declarada: não informada.

Amostra (trecho real da página):

```
Campos: "CPF:" e "Data de Nascimento:"
"O comprovante gerado não fornece informações sobre a situação econômica,
financeira ou fiscal do titular do CPF, limita-se tão somente a comprovar
a situação cadastral no CPF."
"Observação: para que a consulta funcione corretamente, é necessário que
seu navegador esteja habilitado para a gravação de "_cookies_"."
```

- Lacunas/divergências: o conteúdo extraído não mostra o resultado da consulta nem o texto de erro; não foi testada com dados reais (e não deve ser, pelo escopo). Os rótulos de situação diferem entre páginas: "Suspensa" (gov.br) e "Suspenso" (Receita).

### Atualizar CPF e regularização (suspensa, pendente, etc.)

- Órgão: Receita Federal do Brasil. Esfera: federal.
- URL da página gov.br: https://www.gov.br/pt-br/servicos/atualizar-cadastro-de-pessoas-fisicas (confirmada). Ficha da API (ID 10416): https://servicos.gov.br/api/v1/servicos/10416 (confirmada).
- Canais documentados: online para alterar dados quando regular (https://servicos.receita.fazenda.gov.br/Servicos/CPF/alterar/default.asp, não confirmada), online para regularizar CPF suspenso (https://servicos.receita.fazenda.gov.br/Servicos/CPF/regularizar/Default.asp, confirmada), "Complementar Meu CPF" e "Alterar Meu Endereço no CPF" (links em cav.receita.fazenda.gov.br, não acessados), e-mail, presencial em unidades da Receita Federal e Pontos de Atendimento Virtual, e unidades conveniadas (Cartórios de Registro Civil, Banco do Brasil, Caixa e Correios), com tarifa de R$ 7,00. Residentes no exterior: consulado brasileiro.
- Requisitos: ser inscrito no CPF. Quem tem CIN deve alterar dados de identificação civil no Órgão de Identificação Civil; contato, endereço, cadastro externo e situação cadastral vão diretamente à Receita.
- Documentos: documento oficial com foto; certidão de nascimento ou casamento (ou equivalente para estrangeiros) se o documento não trouxer naturalidade, filiação e data de nascimento; foto segurando o documento quando enviado por e-mail; outros documentos a critério do atendente. Regras específicas: menores de 16 e de 16–17 anos, pessoas com deficiência de 18 anos ou mais, pessoas falecidas (certidão de óbito e comprovação de legitimidade).
- Custo: gratuito, exceto em unidades conveniadas (R$ 7,00).
- Prazo: cada etapa até 15 minutos; atendimento por e-mail em média 48 horas; "Atendimento imediato" para o total.
- Formato do formulário de regularização: campos pedidos incluem CPF, nome completo, data de nascimento, sexo, naturalidade e UF, título de eleitor, nome da mãe, CPF e nome de um responsável, um documento de identidade, endereço completo e telefone.
- Data de atualização declarada: 24/09/2026 (página gov.br de atualização; "Última Modificação: 24/09/2026"). A ficha da API não traz data de atualização.

Amostra (trecho real):

```
{"resposta":{"id":"https://servicos.gov.br/api/v1/servicos/10416","nome":"Atualizar CPF","sigla":"","descricao":"Solicite a
"hasErro":false,"mensagem":null
"Última Modificação: 24/09/2026"
Órgão competente: Secretaria Especial da Receita Federal do Brasil
Regularizar CPF: "A solicitação de regularização de CPF só é permitida para situação cadastral suspensa."
```

- Lacunas/divergências: (a) o nome do serviço varia entre "Atualizar CPF", "Alterar CPF" e "Regularizar CPF" na ficha da API; (b) o formulário de regularização pede título de eleitor, mas sem indicar se é obrigatório; (c) a regularização não cobre cancelado, nulo e falecido na página; (d) o trecho da API veio truncado pela ferramenta, sem campo de data de atualização; (e) a API marca `servicoDigital: false` (serviço não totalmente digital), o que deve ser considerado na orientação.

### Inscrição no CPF (primeira inscrição) e alteração de dados

- Órgão: Receita Federal do Brasil. Esfera: federal.
- URL da página gov.br: https://www.gov.br/pt-br/servicos/inscrever-no-cpf (confirmada). Ficha da API (ID 10420): https://servicos.gov.br/api/v1/servicos/10420 (confirmada).
- Requisitos: pessoas físicas brasileiras e estrangeiras, residentes ou não no Brasil. A busca indicou que cada pessoa se inscreve uma vez, mas essa afirmação não foi conferida na página oficial acessada.
- Documentos: documento de identificação oficial com foto; certidão de nascimento ou casamento se naturalidade, filiação e data de nascimento não constarem no documento; outros documentos a critério do atendente. Para e-mail, foto segurando o documento.
- Canais: online (residentes, exterior e estrangeiros), e-mail, presencial em unidades da Receita, PAV e unidades conveniadas (Cartórios, Banco do Brasil, Caixa, Correios). Residentes no exterior: consulado brasileiro.
- Custo: gratuito, exceto unidades conveniadas (R$ 7,00).
- Prazo: cerca de 15 minutos no total; espera presencial até 15 minutos; e-mail em média 48 horas; apresentação de documentos em média 2 dias úteis.
- Data de atualização declarada: 08/10/2026 ("Última Modificação: 08/10/2026").

Amostra (trecho real da ficha da API):

```
{"resposta":{"id":"https://servicos.gov.br/api/v1/servicos/10420","nome":"Inscrever Cidadão no Cadastro
```

- Lacunas/divergências: (a) na ficha da API, o campo `gratuito` vem como `"false"`, mas a descrição diz que é gratuito exceto em unidades conveniadas; (b) a inscrição online para jovens de 16 a 25 anos com título regular e a alternativa por e-mail vêm de busca e não foram conferidas na página acessada; (c) alteração de dados (alterar/default.asp) não foi acessada.

### Declaração do imposto de renda (DIRPF) para status "Pendente de Regularização"

- Órgão: Receita Federal do Brasil. Esfera: federal.
- URL: https://www.gov.br/pt-br/servicos/declarar-meu-imposto-de-renda (confirmada).
- Conteúdo: a página não menciona o status "Pendente de Regularização" nem o efeito no CPF. Informa: serviço gratuito; prazo da DIRPF 2026 "o último dia útil do mês de maio"; atraso pode gerar MAED; se a declaração estiver retida em malha, consultar pendências e, se necessário, enviar declaração retificadora.
- Data de atualização declarada: 12/08/2026 (página).
- Amostra: trecho com o custo, como citado na página: "Este serviço é gratuito para o cidadão."
- Lacunas/divergências: a providência de entregar declarações faltantes vem da página de situação cadastral da Receita (meu-cpf), não desta página. O período exato ("últimos cinco anos") vem da página de atualização do CPF e da busca, não da página da DIRPF.

### Título de eleitor (papel na regularização)

- Órgão: Tribunal Superior Eleitoral (TSE) e cartórios eleitorais. Esfera: federal (cartórios eleitorais, esfera da Justiça Eleitoral).
- URL: não confirmada. A raiz https://www.tse.jus.br/ não foi acessada com sucesso; a notícia do TSE de 2022 retornou 403 e a de 2025 falhou na extração.
- Conteúdo: não confirmado em fonte oficial acessada. Resultados de busca indicam que título cancelado pode fazer o CPF ficar "Pendente de Regularização" e que a regularização pode ser feita pelo autoatendimento do TSE ou no cartório eleitoral. Essas afirmações não foram verificadas em página oficial.
- Lacuna principal: não há confirmação de que a Receita exige a atualização do título para regularizar o CPF.

### API do catálogo de serviços (Portal de Serviços gov.br)

- Órgão: Ministério da Gestão e Inovação em Serviços e Informações do Brasil (MGI/SGD), no Portal de Serviços. Esfera: federal.
- Página de catálogo: https://www.gov.br/conecta/catalogo/apis/api-de-servicos (acessada). Nome da API: "Consulta de Serviços Públicos", versão 1.0.0, data da versão 13/07/2018.
- Base declarada na página: `https://www.servicos.gov.br/api/v1/`. Produção declarada: `https://api-servicos.estaleiro.serpro.gov.br/servicos-json` (não testada).
- Operações declaradas: `GET /api/v1/orgao/{codSiorg}`; `GET /api/v1/servicos/{servicoId}` (pública, sem credencial); `GET /api/v1/servicos/simples/{servicoId}` (pública); `GET /api/v1/servicos-auth` (requer token).
- Testes realizados em 2026-10-10:
  - `https://www.servicos.gov.br/api/v1/servicos/` : HTTP 404 (raiz sem recurso).
  - `https://www.servicos.gov.br/api/v1/docs` : HTTP 403 (documentação não obtida).
  - `https://www.servicos.gov.br/api/v1/servicos-auth` : HTTP 401 (confirma exigência de token).
  - `https://servicos.gov.br/api/v1/servicos/simples/atualizar-cadastro-de-pessoas-fisicas` : HTTP 400 (slug não aceito; o endpoint espera ID numérico).
  - `https://servicos.gov.br/api/v1/servicos/10416` e `.../10420` : respostas JSON com `"hasErro":false`. A ferramenta não mostrou o código HTTP, apenas o corpo.
- Formato: JSON confirmado pela resposta (campo `resposta`). Conecta gov.br descreve formatos sem afirmar explicitamente; a busca mencionou XML, não confirmado.
- Identificadores: 10416 (Atualizar CPF), 10418 (Consultar situação cadastral, apenas citado em resultado de busca, não acessado), 10420 (Inscrição no CPF).

Amostra (trecho real, truncado pela ferramenta):

```
{"resposta":{"id":"https://servicos.gov.br/api/v1/servicos/10416","nome":"Atualizar CPF","sigla":"","descricao":"Solicite a
"hasErro":false,"mensagem":null
```

- Lacunas/divergências: os IDs 10416 e 10420 foram confirmados pela resposta; o ID 10418 não. Não há data de atualização na ficha da API. A página de catálogo (2018) e o uso em 2026 divergem; o ano de 2018 é a versão da API, não a data do conteúdo. O endpoint `/api/v1/servicos/` (lista) não respondeu com dados.

## Observações para revisão

1. Estado das URLs: apenas as URLs marcadas como "confirmada" foram acessadas com WebFetch em 2026-10-10. A URL de alteração de dados (`alterar/default.asp`) aparece como link em página oficial, mas não foi acessada. A URL do TSE não foi confirmada.
2. Códigos HTTP: a ferramenta de extração não expôs o código de status em respostas bem-sucedidas; afirmações de "resposta JSON" baseiam-se no corpo recebido.
3. Divergência de rótulos: "Suspensa" (gov.br) e "Suspenso" (Receita). Padronizar no domínio antes de usar como chave.
4. Divergência de custo na ficha 10420: `gratuito: "false"` versus descrição "gratuita, exceto unidades conveniadas". Usar o texto da página, não o campo.
5. Título de eleitor: a relação com a regularização do CPF não está confirmada em fonte oficial. Resultados de busca mencionam uma instrução normativa da Receita (nº 2172, de 9 de janeiro de 2024) dispensando o título em algumas situações; isso não foi conferido em página oficial e não deve entrar no MVP sem verificação.
6. Cancelado, nulo e falecido: a Receita informa o significado, mas não a providência. Para o MVP, marcar como "não informado" e encaminhar ao atendimento.
7. Datas: data de consulta (2026-10-10), data de atualização declarada pela página de atualização (24/09/2026), pela página de inscrição (08/10/2026), pela página de DIRPF (12/08/2026). A página de situação cadastral da Receita não traz data.
8. Consulta de situação: usada apenas como esclarecimento intermediário; não foram consultados dados pessoais.
9. Lacunas de busca: a documentação da API (`/api/v1/docs`) retornou 403; não foi possível confirmar limites de uso nem formato de resposta completo.
