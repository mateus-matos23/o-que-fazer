# Evidências — Perda de documentos

Levantamento de fontes oficiais para a jornada "perdi minha carteira / meus documentos", no recorte federal, Estado do Maranhão e Município de São Luís. Data da consulta de todas as URLs: 2026-10-10. A data de consulta não é a data de atualização declarada pelo órgão; quando o órgão declara uma data, ela aparece separadamente.

## Tabela-resumo

| Serviço | Órgão | Esfera | URL | Formato | Autenticação | Estado da URL | Data da consulta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Segunda via da Carteira de Identidade Nacional (CIN) no MA | Governo do Maranhão / SSP-MA (emissão pelo Ident-MA; atendimento via Viva/Procon) | Estadual (MA) | https://www.ssp.ma.gov.br/governo-passa-a-emitir-nova-carteira-de-identidade-nacional-em-todo-o-maranhao/ | HTML | Não exige | Confirmada (notícia de 12/01/2024; trata da primeira emissão, não da segunda via) | 2026-10-10 |
| CIN — portal federal de orientação | Ministério da Gestão e da Inovação (Governo Digital) | Federal | https://www.gov.br/identidade | HTML | Não exige | Confirmada (página existe; remete ao estado: "Saiba onde fazer a sua no seu estado!") | 2026-10-10 |
| Segunda via da CNH / PpD no MA | DETRAN-MA | Estadual (MA) | http://www.detran.ma.gov.br/paginas/detalhe/19297 | não confirmado | não confirmado | Não confirmada (HTTP 404). Raiz do domínio confirmada, mas sem conteúdo de serviço | 2026-10-10 |
| Segunda via do CPF (comprovante de inscrição) | Receita Federal do Brasil | Federal | https://www.gov.br/pt-br/servicos/obter-cartao-de-cpf | HTML | Sim: conta gov.br nível prata ou ouro (canal gov.br); há canal "sem gov.br" | Confirmada (Última Modificação: 06/08/2026) | 2026-10-10 |
| Segunda via do título de eleitor | TSE / TRE-MA (Justiça Eleitoral) | Federal (Justiça Eleitoral) | https://www.tse.jus.br/comunicacao/noticias/2023/Outubro/perdeu-o-titulo-de-eleitor-veja-como-tirar-a-2o-via-do-documento | não confirmado | não confirmado | Não confirmada (HTTP 403). Também 403: TRE-MA FAQ e portarias. gov.br/pt-br/servicos/emitir-segunda-via-do-titulo-de-eleitor: HTTP 404 | 2026-10-10 |
| Registro de ocorrência de extravio/perda de documentos (Delegacia Online) | Polícia Civil do Maranhão / SSP-MA | Estadual (MA) | https://www.policiacivil.ma.gov.br/delegacia-online/ | HTML | Não exige (formulário público) | Confirmada (página com "Publicado em 1 de março de 2018"). Domínio delegaciaonline.ssp.ma.gov.br: não confirmado (falha de DNS) | 2026-10-10 |
| CNH digital / CIN digital (perda do app) | DETRAN-MA / Ident-MA | Estadual (MA) | não informada | não informado | não informado | Não confirmada: nenhuma fonte oficial do MA foi localizada | 2026-10-10 |

## Atualização de 24/10/2026

A tabela acima registra a consulta de 10/10/2026 e fica como **Histórico**. Nova coleta em bruto ([amostras](../amostras/README.md#coleta-de-24102026)):

| Serviço | Estado em 24/10/2026 | O que a amostra sustenta |
| --- | --- | --- |
| CIN (orientação federal) | **Confirmada**: [perguntas frequentes da CIN](../amostras/html-govbr-cin-faq-emissao.md), atualizada em 16/07/2026 | Emissão pelos órgãos de identificação civil dos estados; exige "certidão de nascimento ou casamento atualizada"; 2ª via em qualquer UF ([amostra](../amostras/html-govbr-cin-faq.md)); o órgão de identificação pode inscrever o CPF de menores. |
| CIN no MA | **Confirmada com ressalva**: [notícia SSP-MA](../amostras/html-ssp-cin-ma.md) de 12/01/2024 | Locais (Ident-MA na Rua da Palma; postos Viva/Procon) e documentos da primeira via. Custo da 2ª via e agendamento: **não informado** (Ident-MA sem resposta). |
| 2ª via da CNH/PpD no MA | **Confirmada**: [DETRAN-MA](../amostras/html-detran-2via-cnh.md), sem data declarada | Exige Boletim de Ocorrência e RG; atendimento nas unidades do DETRAN-MA; CNH de outra UF segue outro serviço. Taxas na [tabela](../amostras/html-detran-taxas.md). |
| 2ª via da certidão de nascimento (São Luís) | **Confirmada**: [carta de serviços](../amostras/html-sl-2via-certidao-nascimento.md), atualizada em 05/05/2026 | Requerimento eletrônico pelo SEI externo; custo e prazo "em estudo" (= não informado). Não cobre certidões de outros municípios. |
| Título de eleitor | **Pendente**: TSE e TRE-MA seguem com HTTP 403; a conferência manual de 25/10/2026 também não localizou a página | Continua fora da cobertura. |
| 2ª via da CIN no MA (requisitos e taxa) | **Pendente**: o Ident-MA só oferece formulário de agendamento (25/10/2026) | Se a 2ª via exige B.O. e quanto custa: não informado. |

Consequência para a jornada: a CIN e a CNH podem sair de `out_of_coverage`, e surge a primeira **dependência obrigatória** com fonte (ocorrência → 2ª via da CNH) e uma **condicional** (certidão → CIN, se a certidão também foi perdida). A mudança no conteúdo (`content/perda-de-documentos.toml`) fica para uma fatia própria.

## Catálogo Gov.br e API de serviços (verificação técnica)

Esta seção registra o que foi efetivamente testado. Ela não é um serviço de jornada, mas define o formato de coleta possível. Ver a subseção "API de serviços do Gov.br" abaixo.

### Carteira de Identidade Nacional (CIN) — segunda via no Maranhão

**Conteúdo aproveitável**
- Órgão: notícia oficial do Governo do Maranhão, publicada pela Secretaria de Segurança Pública (SSP-MA).
- Emissão na Grande Ilha: sede do Instituto de Identificação do Maranhão (Ident-MA), Rua da Palma, Centro de São Luís, e postos do Ident nas unidades do Viva/Procon.
- Demais municípios: unidades do Viva/Procon e postos conveniados com as prefeituras.
- Documentos: certidão de nascimento ou de casamento (original ou cópia) e RG atual (o RG é exigido apenas se a pessoa tiver um).
- Custo: "A primeira via da nova carteira e as renovações são gratuitas" (a notícia não trata do custo da segunda via).
- Canal online para solicitar a carteira: não informado pela notícia.
- Canal presencial: unidades listadas acima.
- Prazo: não informado.

**Amostra** (trecho retornado pela consulta à página; texto como extraído pelo WebFetch)
```
Publicação: "sexta-feira, 12 de janeiro de 2024", às 10:40
Órgão: "por meio da Secretaria de Segurança Pública", do Governo do Maranhão.
"pode ser solicitada na sede do Instituto de Identificação do Maranhão (Ident-MA), na Rua da Palma, Centro de São Luís"
"levar certidão de nascimento ou de casamento (original ou cópia) e o RG atual"
"A primeira via da nova carteira e as renovações são gratuitas"
```

**Lacunas e divergências**
- A notícia é de 2024 e não trata especificamente de "segunda via" por perda ou roubo.
- Não há data de atualização declarada além da publicação.
- Fontes de terceiros (não utilizadas como evidência, somente apontadas na busca): Imirante (set/2026) menciona agendamento pelo site do Procon-MA e pelo app VIVA PROCON, e pelo portal ma.gov.br; Exame e Olhar Digital tratam da emissão da CIN no MA. Não foram acessadas.
- Valor da segunda via divergente nas fontes de terceiros (R$ 45,00 em matéria antiga; R$ 44,19 em página da Prefeitura de Timon). Não confirmado em fonte oficial.
- Página federal gov.br/identidade (confirmada) não lista as regras estaduais; remete ao banner "Saiba onde fazer a sua no seu estado!".
- A notícia da Secom de fev/2026 sobre "2ª via da CIN após caso de perda" (https://www.gov.br/secom/pt-br/acompanhe-a-secom/noticias/2026/02/saiba-como-solicitar-a-2a-via-da-cin-apos-caso-de-perda) retornou "É necessário autenticar para visualizar essa página"; não foi possível ler seu conteúdo.

### CIN — portal federal de orientação

**Conteúdo aproveitável**
- Página de orientação federal: a segunda via é orientada por estado; a página não contém passo a passo de perda.

**Amostra**
```
Título: "Identificação do Cidadão e Carteira de Identidade Nacional"
"Saiba onde fazer a sua no seu estado!"
```

**Lacunas e divergências**
- Sem órgão, custo, canais ou data de atualização na página.

### Segunda via da CNH / PpD (DETRAN-MA)

**Conteúdo aproveitável (somente de fonte não oficial, não utilizável como evidência sem confirmação)**
- Documentos citados: boletim de ocorrência (para furto ou extravio), RG (original e cópia), CPF, comprovante de pagamento e foto 3x4 (fundo branco).
- Canal: agendamento online pelo site oficial e atendimento presencial em unidade do DETRAN-MA.
- Custo citado: R$ 61,30 ("2ª Via da PD/CNH – DETRAN").
- Data declarada na página: 22/11/2023.

**Amostra** (texto da página de terceiro, não oficial)
```
Título: "SEGUNDA VIA DE CNH/PpD DETRAN MA"
Rodapé: "Copyright © 2026 DETRAN MA - Simulado, Multas, IPVA..."
"o site do Detran MA (www.detran.ma.gov.br)"
```

**Lacunas e divergências**
- Página oficial detalhe/19297 retornou HTTP 404.
- A raiz http://www.detran.ma.gov.br/ redireciona para /inicio/, que retornou apenas o título "Detran-MA", sem links de serviço nem data.
- A página de terceiro cita valor (R$ 61,30) e documentos que não foram confirmados em fonte oficial.
- Busca genérica retornou página de terceiros (segundaviadetudo.com.br) que não foi acessada.
- Ainda não há fonte oficial de MA para documentos, custo, prazo ou canais.

### Segunda via do CPF (Receita Federal)

**Conteúdo aproveitável**
- Órgão: Secretaria Especial da Receita Federal do Brasil.
- Requisitos: CPF cadastrado; documento oficial de identificação com foto; para o canal gov.br, conta gov.br nível prata ou ouro.
- Canais: web "Emitir Meu Cartão de CPF (2ª via)"; web "sem gov.br" ("Emitir Meu Cartão de CPF (2ªvia) Sem Gov.br"); e-mail ("Atendimento por e-mail").
- Custo: "Este serviço é gratuito para o cidadão."
- Prazo: não informado.
- Observação de fonte de busca (não lida na página, não confirmada): o canal "sem gov.br" vale para quem não apresentou declaração de IR nos últimos dois anos.

**Amostra**
```
Título: "Obter Cartão de CPF"
Órgão: "Secretaria Especial da Receita Federal do Brasil"
"Você precisa ter uma conta nível Prata ou Ouro para acessar este serviço."
Web: "Emitir Meu Cartão de CPF (2ª via)"
Web, sem gov.br: "Emitir Meu Cartão de CPF (2ªvia) Sem Gov.br"
Custo: "Este serviço é gratuito para o cidadão."
Última Modificação: 06/08/2026
```

**Lacunas e divergências**
- A página de detalhe receitafederal/.../comprovante-de-inscricao-no-cpf retornou "Conteúdo Restrito" (exige autenticação); não foi possível confirmar seus requisitos.
- Nota de contexto: a Receita informa que o cartão físico do CPF não existe mais e que o comprovante impresso e a versão digital têm a mesma validade (fonte de busca, não lida na íntegra).
- Se a pessoa não souber o número do CPF, a orientação é contatar a Receita (sem canal detalhado lido).

### Segunda via do título de eleitor (TSE / TRE-MA)

**Conteúdo aproveitável (apenas de trechos de busca; nenhuma página foi lida)**
- Canal online: impressão em Autoatendimento Eleitoral no site do TSE, opção "Título Eleitoral"; aplicativo e-Título; PDF.
- Restrição: não é possível para inscrição "cancelado"; emissão impressa em cartório exige presença do eleitor (sem procuração).
- Presencial: cartório eleitoral em que o eleitor é inscrito, com documento oficial com foto e comprovante de residência (FAQ do TRE-MA, conforme trecho de busca).
- Documentos: Portaria 1/2026 TRE-MA/ZE-16 (conforme trecho de busca): documento oficial com foto. Portaria 647/2024: exigia também boletim de ocorrência.
- Custo e prazo: não informados.

**Amostra**
```
não confirmada: todas as URLs de TSE/TRE-MA retornaram HTTP 403 ao WebFetch.
```

**Lacunas e divergências**
- Divergência entre as portarias quanto à exigência de boletim de ocorrência; a vigente não foi confirmada.
- Não há página gov.br confirmada para o serviço (gov.br/pt-br/servicos/emitir-segunda-via-do-titulo-de-eleitor retornou 404; a URL foi um palpite, não um link encontrado).

### Registro de ocorrência de extravio ou perda de documentos (Polícia Civil / SSP-MA)

**Conteúdo aproveitável**
- Órgão: Polícia Civil do Maranhão (sistema desenvolvido pelo Núcleo de Desenvolvimento de Sistemas da SSP-MA, conforme a página).
- Serve para registrar "ocorrências de extravio de documentos", sem ida à delegacia.
- Opções do formulário: "questão de extravio de documentos e de furto simples".
- O boletim é enviado ao e-mail do solicitante, com número de protocolo.
- Custo: não informado (nenhum custo foi localizado).

**Amostra**
```
Título: "DELEGACIA ONLINE"
Órgão: Polícia Civil do Maranhão (rodapé)
"registrar ocorrências de extravio de documentos"
"questão de extravio de documentos e de furto simples"
"O boletim de Ocorrência será enviado ao e-mail do solicitante."
"Publicado em: quinta-feira, 1 de março de 2018"
```

**Lacunas e divergências**
- A única data da página é de publicação (01/03/2018); não há data de atualização declarada.
- Domínio delegaciaonline.ssp.ma.gov.br (citado em busca): falha de DNS no WebFetch; não confirmado.
- Buscas trouxeram fontes antigas (2010 a 2017) que descrevem validação por e-mail e restrições por tipo de crime; não foram usadas como evidência.
- Não há confirmação de que o registro online dispensa BO presencial para perda de CNH ou CIN na prática atual.

### CNH digital e CIN digital (perda do aplicativo)

- Nenhuma fonte oficial do Maranhão foi localizada sobre perda ou reemissão do aplicativo.
- Fontes de outros estados (busca): São Paulo informa que a CNH digital fica no app CNH do Brasil em até 24 horas após a expedição; Santa Catarina exige cadastro gov.br. Não usar como válido para o MA.
- Status: não informado para o MA.

### API de serviços do Gov.br (catálogo)

**Testes realizados (data 2026-10-10)**

| URL testada | Resultado |
| --- | --- |
| https://www.servicos.gov.br/api/v1/servicos/ | HTTP 404 |
| https://www.servicos.gov.br/api/v1/servicos/1 | HTTP 404 |
| https://www.servicos.gov.br/api/v1/servicos/simples/1 | Erro de certificado (hostname não corresponde ao certificado do SERPRO) |
| https://www.servicos.gov.br/api/v1/orgao/ | Erro de certificado (mesmo motivo) |
| https://www.servicos.gov.br/api/v1/docs | HTTP 403 |
| https://api-servicos.estaleiro.serpro.gov.br/servicos-json/api/v1/servicos/1 | HTTP 404 (caminho montado por mim a partir da URL-base; não é um caminho documentado) |
| https://www.gov.br/conecta/catalogo/apis/api-de-servicos | Confirmada: documentação oficial da API |
| https://servicosgovbr.github.io/ | Confirmada: portal de desenvolvedores |

**Conteúdo aproveitável da documentação (conecta/catalogo)**
- Versão 1.0.0, data declarada 13/07/2018; responsável MGI/SGD, CGATE.
- URL-base de produção declarada: https://api-servicos.estaleiro.serpro.gov.br/servicos-json
- Documentação de uso declarada: https://www.servicos.gov.br/api/v1/docs (retornou 403).
- Endpoints GET declarados: /api/v1/orgao/{codSiorg}; /api/v1/servicos/{servicoId}; /api/v1/servicos/simples/{servicoId}; /api/v1/servicos-auth (lista completa, com credencial).
- Autenticação: consulta de serviço específico sem credencial; lista completa exige credencial solicitada em https://gov.br/apiservicos.
- Formato: página não especifica de forma geral. O portal de desenvolvedores diz "XML e JSON".
- Limite de requisições e termos: não informados.

**Amostra** (texto da página do catálogo, como extraído)
```
Consulta de Serviços Públicos (API de Serviços do Portal gov.br)
Responsável: MGI/SGD, Coordenação-Geral de Automação e Atendimento (CGATE)
Versão e data de atualização: 1.0.0, 13/07/2018
URL base de produção: https://api-servicos.estaleiro.serpro.gov.br/servicos-json
Documentação de uso: https://www.servicos.gov.br/api/v1/docs
Consultas a um serviço específico não exigem credencial.
```

**Lacunas e divergências**
- A URL-base de produção (SERPRO) e os caminhos documentados (www.servicos.gov.br) não batem; a página não explica a relação.
- O endpoint /api/v1/servicos/{id} não foi testado com um id desta jornada (nenhum id de serviço de perda de documentos foi localizado). **Nota do revisor (2026-10-10):** o endpoint responde JSON público para outros ids (10416, 1045), conferido via curl; ver [índice das evidências](README.md).
- O portal de desenvolvedores (servicosgovbr.github.io) cita uma API de testes em www.servicos.nuvem.gov.br, não testada.
- A busca citou https://www.gov.br/api/v1/servicos (descrita como API fornecedora do Portal de Serviços); não foi testada.
- Slugs gov.br adivinhados (ex.: /pt-br/servicos/segunda-via-da-carteira-de-identidade, /pt-br/servicos/emitir-carteira-nacional-de-habilitacao-cnh-segunda-via) retornaram 404 ou erro; não representam páginas confirmadas.

## Observações para revisão

1. **Natureza das amostras.** O WebFetch devolve texto processado por modelo, não o HTML bruto. Os trechos acima são extratos da resposta, não cópias byte a byte. Antes de citar no TCC, o revisor deve abrir cada URL confirmada no navegador e copiar o texto literal.
2. **CNH (DETRAN-MA) sem fonte oficial.** O único conteúdo de CNH veio de site de terceiros (detran.ma com rodapé de "Simulado, Multas, IPVA"). Custo R$ 61,30 e documentos não podem ser usados como oficiais sem confirmação no domínio detran.ma.gov.br.
3. **Título de eleitor sem leitura.** TSE e TRE-MA responderam 403. Verificar manualmente a exigência de boletim de ocorrência (conflito entre Portaria 647/2024 e Portaria 1/2026).
4. **Segunda via da CIN no MA.** A notícia confirmada é de 2024 e trata da primeira emissão. Verificar no portal oficial (ma.gov.br, ou Procon-MA/Viva) se há agendamento online atual e o valor da segunda via.
5. **Delegacia Online.** Confirmar o domínio atual (delegaciaonline.ssp.ma.gov.br ou policiacivil.ma.gov.br) e se o registro online cobre perda de CNH e CIN, além de custos.
6. **CPF.** ~~Conferir se o canal "sem gov.br" exige não ter declarado IR nos dois últimos anos.~~ Resolvido em 24/10/2026: a página traz literalmente "Se você não apresentou declaração de imposto de renda nos últimos dois anos" antes do link "sem gov.br".
7. **Esfera e competência.** CIN, CNH e Delegacia Online são estaduais (MA). CPF e título de eleitor são federais. Nenhum serviço de jornada foi localizado como municipal de São Luís; o município aparece apenas indiretamente (postos conveniados).
8. **Catálogo Gov.br.** Não foi encontrada página confirmada no catálogo gov.br para segunda via de CIN, CNH ou título. A API de serviços não respondeu para os ids testados; o levantamento não confirma se a API cobre os serviços estaduais do MA.
9. **Data de consulta versus data de atualização.** Todas as consultas são de 2026-10-10. As datas declaradas pelos órgãos são: CPF, Última Modificação 06/08/2026; Delegacia Online, publicação 01/03/2018; notícia SSP-MA, 12/01/2024; API de serviços, versão 13/07/2018; página DETRAN-MA de terceiros, 22/11/2023.
