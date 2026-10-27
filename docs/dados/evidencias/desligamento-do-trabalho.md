# Evidências — Desligamento do trabalho

Registro das fontes oficiais consultadas para a jornada "fui demitido" (recorte federal, Maranhão e São Luís), com URLs, formatos, autenticação, trechos reais e lacunas. Data da consulta: 2026-10-10. A data de atualização informada pela página não é a data da consulta.

## Tabela-resumo

| Serviço | Órgão | Esfera | URL | Formato | Autenticação | Estado da URL | Data da consulta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Solicitar o Seguro-Desemprego | Ministério do Trabalho e Emprego (MTE) | Federal | https://www.gov.br/pt-br/servicos/solicitar-o-seguro-desemprego (HTML); API: https://servicos.gov.br/api/v1/servicos/1045 | HTML (página); JSON (API) | Sim: conta gov.br nível Bronze, Prata ou Ouro (`temLoginGovBR: S`, `temNivelMinimoContaGovBR: B`) | Confirmada (página e API) | 2026-10-10 |
| Seguro-desemprego para empregado doméstico | MTE | Federal | https://www.gov.br/pt-br/servicos/solicitar-seguro-desemprego-empregado-domestico (HTML); API: https://servicos.gov.br/api/v1/servicos/9815 | HTML (página); JSON (API) | Sim: conta gov.br nível Bronze, Prata ou Ouro (mesma base da API) | Confirmada (página e API) | 2026-10-10 |
| Saque do FGTS por dispensa sem justa causa | Caixa Econômica Federal (operadora); órgão gestor não declarado no trecho consultado | Federal (inferida: CAIXA é empresa pública federal; a página não declara esfera) | https://www.fgts.gov.br/Paginas/subpaginas/saque-dispensa.aspx | HTML | Não informado (a página informativa foi lida sem login; o login do canal de solicitação não foi verificado) | Confirmada | 2026-10-10 |
| Saque-aniversário do FGTS (efeito na rescisão) | Caixa Econômica Federal | Federal (inferida) | https://www.caixa.gov.br/beneficios-trabalhador/fgts/saque-FGTS/Paginas/default.aspx | HTML | Não informado | Não confirmada (redirecionamento em loop, 50 redirecionamentos). Também não confirmada: https://www.fgts.gov.br/Paginas/subpaginas/saque-aniversario.aspx (HTTP 404) | 2026-10-10 |
| Carteira de Trabalho Digital (CTPS) e consulta de vínculos | MTE | Federal | https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho; FAQ: https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho/perguntas-frequentes-carteira-de-trabalho-digital | HTML | Sim: conta gov.br nível Bronze, Prata ou Ouro (página "obter a carteira") | Confirmadas (ambas); página própria de "consultar vínculos" não encontrada | 2026-10-10 |
| Solicitar Extrato de Vínculos Empregatícios do CAGED | MTE | Federal | https://www.gov.br/pt-br/servicos/solicitar-vinculos-empregaticios-do-caged (HTML); API: https://servicos.gov.br/api/v1/servicos/7839 | HTML (página); JSON (API) | Sim: conta gov.br nível Bronze (`temLoginGovBR: S`, `temNivelMinimoContaGovBR: B`) | Confirmada (página e API) | 2026-10-10 |
| Atendimento presencial SINE / SRTE (São Luís e Maranhão) | MTE (SRTE e SINE federal); Sine-MA (estadual, site trabalho.ma.gov.br) | Federal e estadual | https://www.gov.br/pt-br/servicos/buscar-emprego-no-sistema-nacional-de-emprego-sine (apenas resultado de busca); https://www.gov.br/trabalho-e-emprego/pt-br/canais_atendimento/unidades-de-atendimento/rede-de-atendimento-do-trabalho-no-ma (conteúdo restrito); https://trabalho.ma.gov.br/sine-para-empresarios (HTTP 404) | HTML | Não informado | Não confirmada (nenhuma página de endereços foi lida com conteúdo público) | 2026-10-10 |

Observação sobre a API do catálogo: ver a seção "Observações para revisão".

## Forma de término → serviços potencialmente aplicáveis

| Forma de término | Serviço(s) potencialmente aplicável(is) | Fonte (trecho ou referência) |
| --- | --- | --- |
| Dispensa sem justa causa (empregado formal) | Seguro-desemprego; saque do FGTS (saldo da conta); CTPS/CAGED para conferir vínculos | Seguro-desemprego, API 1045, campo `solicitantes`: "Trabalhadores formais que foram demitidos involuntariamente (sem justa causa)". FGTS, fgts.gov.br: "O trabalhador demitido sem justa causa pode realizar o saque do saldo da sua conta do FGTS." |
| Dispensa sem justa causa (empregado doméstico) | Seguro-desemprego doméstico; saque do FGTS (se houver FGTS) | API 9815, campo `solicitantes`: "Trabalhador doméstico dispensado sem justa causa que:" |
| Dispensa sem justa causa, optante pelo saque-aniversário | Saque da multa rescisória (FGTS) | fgts.gov.br: "Caso você seja optante pelo Saque-Aniversário na data em que ocorrer a rescisão, poderá sacar a multa rescisória." Demais regras do saldo: não informado (ver lacunas) |
| Pedido de demissão | Seguro-desemprego: não documentado como aplicável | Página do seguro-desemprego (gov.br e API 1045) só menciona dispensa sem justa causa; "A página não menciona essas hipóteses" (consulta à página via WebFetch) |
| Justa causa | Seguro-desemprego: não documentado como aplicável | Mesma fonte acima |
| Acordo (rescisão por mútuo acordo) e culpa recíproca | não informado | Nenhuma fonte oficial consultada trata dessas formas de término |
| Fim de contrato (ex.: contrato por prazo determinado) | não informado | Nenhuma fonte oficial consultada trata dessa forma de término |
| Qualquer forma de término | Consulta de vínculos (CTPS Digital, CAGED) | FAQ da CTPS: "O seu funcionário poderá ver o contrato de trabalho na Carteira de Trabalho Digital 48 horas após o envio da informação por você." Não restringe a forma de término |

## Serviços

### Seguro-desemprego (solicitação)

- **Órgão e esfera:** Ministério do Trabalho e Emprego (MTE), federal. A página informa: "Este é um serviço do(a) Ministério do Trabalho e Emprego". A esfera não é declarada explicitamente; a página cita a Lei nº 7.998/1990.
- **URL:** https://www.gov.br/pt-br/servicos/solicitar-o-seguro-desemprego (confirmada)
- **API:** https://servicos.gov.br/api/v1/servicos/1045 (confirmada, JSON, sem autenticação para leitura)
- **Formato e autenticação:** HTML e JSON. A página exige conta gov.br ("Utilize a sua conta GOV.BR para acessar este serviço", nível Bronze, Prata ou Ouro).
- **Critérios de elegibilidade:**
  - Forma de término: apenas "Trabalhadores formais que foram demitidos involuntariamente (sem justa causa)". Pedido de demissão, justa causa, acordo e culpa recíproca não são citados.
  - Renda: "não possuem renda própria que seja suficiente à sua manutenção e de sua família."
  - Carência por número de solicitação: 12 meses nos últimos 18 meses (primeira); 9 meses nos últimos 12 meses (segunda); cada um dos 6 meses imediatamente anteriores (demais).
  - Regras de requisito (fatia 7, pergunta `vezes-seguro-desemprego`): cada carência vira um requisito condicional, com o trecho literal da API 1045 como citação. `regra-carencia-primeira` (`primeira`): "pelo menos 12 meses nos últimos 18 meses imediatamente anteriores à data de dispensa, quando da primeira solicitação". `regra-carencia-segunda` (`segunda`): "pelo menos 9 meses nos últimos 12 meses imediatamente anteriores à data de dispensa, quando da segunda solicitação". `regra-carencia-demais` (`terceira-ou-mais`): "cada um dos 6 meses imediatamente anteriores à data de dispensa, quando das demais solicitações". Sem resposta ou "Não sei", os três aparecem marcados "Pode valer para você". A fonte não define o que conta como "solicitação"; a pergunta não explica isso.
  - Benefício previdenciário: "não recebem qualquer benefício previdenciário de prestação continuada, com exceção do auxílio-acidente, do auxílio suplementar e do abono de permanência em serviço."
- **Documentos:** "Documento do Requerimento do Seguro-Desemprego (você recebe do empregador este documento no momento que é dispensado sem justa causa)" e "Número do CPF".
- **Canais:** web (Portal de Serviços da Dataprev); aplicativo Carteira de Trabalho Digital (Android e iOS); presencial com agendamento pela Plataforma FACILITA; telefone 158.
- **Prazo:** o prazo para requerer não consta na página. Prazo estimado do atendimento: 31 a 60 dias corridos (campo `tempoTotalEstimado`, API 1045).
- **Custo:** "Este serviço é gratuito para o cidadão." (API: `gratuito: "true"`)
- **Data de atualização declarada:** "Última Modificação: 25/09/2026" (página, conferido por curl)

Amostra (API 1045, campo `solicitantes`, texto real):

```
"tipo": "Trabalhadores formais que foram demitidos involuntariamente (sem justa causa) e que:",
"requisitos": "a) não possuem renda própria que seja suficiente à sua manutenção e de sua família.
 b) receberam salários de pessoa jurídica ou de pessoa física a ela equiparada, relativos a:
 · pelo menos 12 meses nos últimos 18 meses imediatamente anteriores à data de dispensa, quando da primeira solicitação; ou
 · pelo menos 9 meses nos últimos 12 meses imediatamente anteriores à data de dispensa, quando da segunda solicitação; ou
 · cada um dos 6 meses imediatamente anteriores à data de dispensa, quando das demais solicitações
 c) não recebem qualquer benefício previdenciário de prestação continuada, ..."
```

- **Lacunas e divergências:**
  - Número máximo de solicitações: não informado. A página fala apenas em carência por ordem de solicitação.
  - Prazo para requerer: não informado na página oficial. Resultados de busca de terceiros citam "7 a 120 dias"; não foi confirmado em fonte oficial e não deve ser usado.
  - Pedido de demissão, justa causa, acordo e culpa recíproca: a página não os menciona, nem para afirmar que são aplicáveis nem que não são.

### Seguro-desemprego para empregado doméstico

- **Órgão e esfera:** MTE, federal (`orgao.nomeOrgao: "Ministério do Trabalho e Emprego (MTE)"`).
- **URL:** https://www.gov.br/pt-br/servicos/solicitar-seguro-desemprego-empregado-domestico (confirmada)
- **API:** https://servicos.gov.br/api/v1/servicos/9815 (confirmada, JSON)
- **Formato e autenticação:** HTML e JSON. Conta gov.br nível Bronze, Prata ou Ouro (`temLoginGovBR: S`, `temNivelMinimoContaGovBR: B`).
- **Critérios:**
  - Forma de término: "Trabalhador doméstico dispensado sem justa causa que:".
  - Renda: "não possua renda própria para seu sustento e de sua família".
  - Carência: "tenha trabalhado pelo menos 15 meses nos últimos 24 meses".
  - Benefício previdenciário: "não receba nenhum benefício previdenciário, com exceção do auxílio-acidente e de pensão por morte".
  - Prazo: "tenha solicitado o seguro-desemprego no prazo de 7 a 90 dias contados da data da demissão".
- **Parcelas:** até três parcelas de um salário mínimo, conforme a descrição da API.
- **Documentos (etapa atual):** "CPF do empregador", "Data de admissão" e "Data de demissão".
- **Canais:** Carteira de Trabalho Digital (Android e iOS); Plataforma Facilita (web); telefone 158; presencial em unidades do SINE e nas SRTEs (agendamento pela Plataforma FACILITA para as SRTEs).
- **Custo:** gratuito (`gratuito: "true"`).
- **Data de atualização declarada:** "Última Modificação: 23/09/2026" (página, conferido por curl).

Amostra (API 9815, campo `solicitantes`, texto real):

```
"tipo": "Trabalhador doméstico dispensado sem justa causa que:",
"requisitos": "a) não possua renda própria para seu sustento e de sua família;
 b) tenha trabalhado pelo menos 15 meses nos últimos 24 meses;
 c) não receba nenhum benefício previdenciário, com exceção do auxílio-acidente e de pensão por morte; e
 d) tenha solicitado o seguro-desemprego no prazo de 7 a 90 dias contados da data da demissão."
```

- **Lacunas e divergências:**
  - Documentos: a página atual lista apenas CPF do empregador, data de admissão e data de demissão. A página antiga do eSocial (https://www.gov.br/esocial/pt-br/empregador-domestico/orientacoes/seguro-desemprego, lida via WebFetch, "Atualizado em 25/06/2020") lista CTPS, termo de rescisão e declarações. Prevalece a página atual, mas a divergência merece revisão.
  - Prazo: a página atual e a API dizem 7 a 90 dias. Fontes de terceiros (Distrito Federal) citam 7 a 120 dias. Não usar o número de terceiros.
  - Não foi possível confirmar o número de solicitações além da carência descrita na API.

### Saque do FGTS por dispensa sem justa causa

- **Órgão e esfera:** Caixa Econômica Federal como operadora. A página fgts.gov.br não declara o órgão gestor no trecho consultado. Esfera federal (inferida).
- **URL:** https://www.fgts.gov.br/Paginas/subpaginas/saque-dispensa.aspx (confirmada)
- **Formato:** HTML. Autenticação: não informado (leitura feita sem login; o login do app e do canal de solicitação não foi verificado).
- **Regras:** o saldo da conta pode ser sacado por demissão sem justa causa; optantes pelo saque-aniversário podem sacar a multa rescisória.
- **Prazo do crédito:** "o dinheiro entrará na sua conta bancária em até 5 dias úteis após o débito da conta do FGTS." Vale quando o empregador informou a dispensa e há conta bancária cadastrada no app.
- **Canais:** app FGTS ("Solicite seu saque 100% digital"); agência da Caixa, quando a liberação não for automática; lotérica, se não houver conta bancária indicada. Telefones: Atendimento 0800 726 0207; SAC 0800 726 0101; Ouvidoria 0800 725 7474.
- **Documentos (agência):** documento de identificação; CPF ou PIS/PASEP/NIS; Carteira de Trabalho (rescisões a partir de 11/11/2017) ou TRCT/TQRCT/THRCT, conforme a data da rescisão.
- **Custo:** não informado.
- **Data de atualização declarada:** não informado.

Amostra (página fgts.gov.br, texto real):

```
Saque Dispensa Sem Justa Causa
O trabalhador demitido sem justa causa pode realizar o saque do saldo da sua conta do FGTS.
Caso você seja optante pelo Saque-Aniversário na data em que ocorrer a rescisão, poderá sacar a multa rescisória
```

- **Lacunas e divergências:**
  - Regras do saldo para optantes pelo saque-aniversário em demissão sem justa causa: não confirmadas. A página só fala da multa rescisória; o trecho completo estava truncado no resumo do WebFetch.
  - Um blog jurídico (resultado de busca, não oficial) afirma que, a partir de 2026, optantes poderiam sacar o saldo integral. Não foi encontrado em fonte oficial e conflita com a orientação da Caixa obtida. Não usar.
  - Liberação extraordinária pela MP 1.290/2025 (saldos retidos de optantes): citada em resultado de busca (Agência Gov); a página não foi lida e o fato não foi verificado diretamente. Não usar como regra vigente.

### Saque-aniversário do FGTS

- **Órgão e esfera:** Caixa Econômica Federal (federal, inferida).
- **URLs:** https://www.caixa.gov.br/beneficios-trabalhador/fgts/saque-FGTS/Paginas/default.aspx (não confirmada: redirecionamento em loop, 50 redirecionamentos); https://www.fgts.gov.br/Paginas/subpaginas/saque-aniversario.aspx (não confirmada: HTTP 404).
- **Formato e autenticação:** não informado.
- **Conteúdo aproveitável:** apenas o que está em fgts.gov.br sobre multa rescisória (ver seção anterior). Regras completas da modalidade: não informado.
- **Data de atualização declarada:** não informado.
- **Lacunas:** não há conteúdo oficial verificado sobre saque-aniversário além da multa rescisória. Esta é a principal lacuna da jornada.

### Carteira de Trabalho Digital e consulta de vínculos

- **Órgão e esfera:** MTE, federal.
- **URLs:**
  - https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho (confirmada)
  - FAQ: https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho/perguntas-frequentes-carteira-de-trabalho-digital (confirmada)
  - https://www.gov.br/pt-br/servicos/consultar-vinculos-empregaticios (não confirmada: HTTP 404)
  - https://www.gov.br/pt-br/servicos/consultar-vinculos-trabalhistas (não confirmada: HTTP 404)
- **Formato e autenticação:** HTML. Login gov.br nível Bronze, Prata ou Ouro ("Você precisa ter uma conta nível Bronze, Prata ou Ouro para acessar este serviço").
- **Conteúdo aproveitável (FAQ):**
  - Vínculos exibidos: "O aplicativo mostra apenas vínculos de 'empregado' e 'empregado doméstico'. Contribuintes individuais, por exemplo, não aparecem."
  - Dados no primeiro acesso: as três últimas ocorrências do último vínculo; detalhamento com salários e toda a vida laboral exige validação adicional.
  - Correção: "Para erros posteriores a setembro de 2019, o trabalhador deve informar o empregador, que envia a correção." Após o envio, o contrato fica visível em 48 horas.
- **Custo:** gratuito (página "obter a carteira").
- **Data de atualização declarada:** página "obter a carteira": "Última Modificação: 15/12/2025"; FAQ: "Atualizado em 30/08/2024 17h53" (publicado em 13/12/2023).

Amostra (FAQ da CTPS Digital, texto real):

```
Publicado em 13/12/2023 15h59 Atualizado em 30/08/2024 17h53
...
O seu funcionário poderá ver o contrato de trabalho na Carteira de Trabalho Digital 48 horas após o envio da informação por você.
```

- **Lacunas e divergências:**
  - Não há página oficial específica de "consultar vínculos" no catálogo (as duas URLs testadas retornaram 404). A consulta é feita pelo próprio app/portal da CTPS Digital.
  - Resultados de busca falam em "contrato" visível em outras abas; não foi confirmado em fonte oficial.

### Extrato de vínculos do CAGED

- **Órgão e esfera:** MTE, federal (confirmado na API 7839).
- **URLs:** https://www.gov.br/pt-br/servicos/solicitar-vinculos-empregaticios-do-caged (confirmada); API https://servicos.gov.br/api/v1/servicos/7839 (confirmada, JSON).
- **Formato e autenticação:** HTML e JSON. Login gov.br nível Bronze.
- **Conteúdo aproveitável:** serve para o trabalhador obter, com selo de autenticidade do MTE, o relatório de vínculos do CAGED. Canais: CTPS Digital (web), Portal Emprega Brasil (web), Central 158.
- **Prazo:** "Em média 30 dia(s) corrido(s) é o tempo estimado para a prestação deste serviço."
- **Custo:** gratuito.
- **Data de atualização declarada:** "Última Modificação: 25/08/2026".

Amostra (API 7839, campos extraídos do JSON bruto; valores exatos, sem reformatação de texto):

```
"nome": "Solicitar Extrato de Vínculos Empregatícios do CAGED"
"nomeOrgao": "Ministério do Trabalho e Emprego (MTE)"
"temLoginGovBR": "S"
"temNivelMinimoContaGovBR": "B"
"url": "https://www.gov.br/pt-br/servicos/solicitar-vinculos-empregaticios-do-caged"
```

- **Lacunas:** o alcance dos vínculos (empregado e doméstico) é o mesmo da CTPS Digital; não foi verificado se o extrato inclui outros tipos.

### Atendimento presencial no Maranhão e em São Luís (SINE / SRTE)

- **Órgão e esfera:** MTE (SRTE e SINE, federal); Sine-MA (estadual, trabalha.ma.gov.br).
- **URLs:**
  - https://www.gov.br/pt-br/servicos/buscar-emprego-no-sistema-nacional-de-emprego-sine: apenas resultado de busca, não lido (não confirmada)
  - https://www.gov.br/trabalho-e-emprego/pt-br/canais_atendimento/unidades-de-atendimento/rede-de-atendimento-do-trabalho-no-ma: acessada, mas o conteúdo retornou "É necessário autenticar para visualizar essa página" (não confirmada quanto ao conteúdo)
  - https://trabalho.ma.gov.br/sine-para-empresarios: HTTP 404 (não confirmada)
- **Formato e autenticação:** HTML. Autenticação para leitura do conteúdo: não informado (a página de rede no MA exigiu autenticação).
- **Endereço em São Luís:** não confirmado em fonte oficial. Resultados de busca (sites de terceiros) citam endereços diferentes, como "Avenida Jerônimo de Albuquerque, 619" e "Rua da Paz, 316, Centro", atribuído ao Sine-MA em página não acessível. Não usar sem confirmação.
- **Agendamento:** a API 9815 indica que o agendamento para as SRTEs é feito pela Plataforma FACILITA. A forma de atendimento no Sine de São Luís não foi confirmada.
- **Custo:** gratuito (serviço de intermediação do Sine-MA, segundo resultado de busca; não confirmado na página).
- **Data de atualização declarada:** não informado.

- **Lacunas:** não há página oficial confirmada com endereço, telefone e horário da unidade de São Luís. Esta é a principal lacuna do recorte presencial.

## Observações para revisão

1. **API do catálogo Gov.br.** O endpoint `https://servicos.gov.br/api/v1/servicos/{id}` respondeu com JSON via curl (HTTP 200, `application/json`) para os IDs 1045, 9815 e 7839, sem autenticação. A resposta tem a chave raiz `resposta` e inclui `nome`, `orgao`, `solicitantes` (critérios por forma de término), `etapas` (documentos, canais, custos), `temLoginGovBR`, `temNivelMinimoContaGovBR`, `url` e `legislacoes`. Não há campo de data de atualização na API; a data veio da página HTML ("Última Modificação").
   - Chamadas que falharam: slug em vez de ID (`/api/v1/servicos/solicitar-o-seguro-desemprego`) retornou HTTP 400; a listagem `/api/v1/servicos` retornou HTTP 404.
   - Não foi localizada documentação pública da API. Os IDs foram descobertos por busca. Não foi possível listar todos os serviços.
   - O endpoint `GET /api/v1/servicos-auth`, citado no registro histórico de `docs/dados/fontes-oficiais.md`, não foi testado nesta consulta.
2. **Método de leitura.** As amostras de páginas HTML foram extraídas por curl e conferidas por busca de texto (FGTS, FAQ da CTPS, datas de atualização). Os critérios de algumas páginas (seguro-desemprego, doméstico, Maranhão) foram lidos via WebFetch, que resume o conteúdo; por isso os trechos citados nessas partes devem ser recheckados no texto bruto antes de uso formal.
3. **Caixa.** Os endereços da Caixa testados entraram em redirecionamento em loop. É preciso encontrar outra URL oficial para as regras do saque-aniversário.
4. **Fontes de terceiros não usadas como evidência:** blogs e sites de busca com prazos (7 a 120 dias), endereços do Sine-MA e regras de saque-aniversário de 2026. Nenhum desses dados entrou como fato neste documento.
5. **Divergências a decidir:** prazo do seguro-desemprego doméstico (90 dias oficial versus 120 de terceiros); documentos do doméstico (página atual versus eSocial de 2020); regra do saque-aniversário em demissão sem justa causa (ainda não confirmada).
6. **Não verificado:** número máximo de solicitações do seguro-desemprego; custo e data de atualização do FGTS; forma de término "acordo" e "culpa recíproca" em qualquer serviço; endereços, telefones e horários do SINE em São Luís.
7. **Escopo.** Nenhum arquivo além deste foi alterado.
8. **Custo e prazo citados (27/10/2026).** "Este serviço é gratuito para o cidadão." (seguro, doméstico, CAGED) e "Quanto tempo leva?" (seguro 1045: entre 31 e 60 dias corridos; CTPS: atendimento imediato) entraram como detalhes, com trecho do "Trecho de custo e prazo" de cada amostra, tirado da versão de fonte coletada por `fetch_sources`. O tempo estimado do seguro 1045 não é o prazo para requerer, que segue não informado. O custo do FGTS segue não informado.
