# Fontes oficiais e viabilidade

> Prova preliminar de viabilidade, serviços analisados, formatos, autenticação e evidências pendentes.

## Fontes oficiais e prova preliminar de viabilidade

### Pergunta que motivou a investigação

Antes de aprofundar a arquitetura, o autor questionou se as fontes oficiais realmente existiam e forneciam informação útil para a proposta. A preocupação era evitar construir um sistema cuja base informacional não pudesse ser obtida.

### Resultado histórico recuperado

Em 12/08/2026 foi registrada uma análise preliminar de **15 serviços** das três esferas. O relato classificou oito com potencial alto, cinco com potencial médio ou médio-alto e dois com potencial baixo ou médio.

Essa classificação é um registro da análise anterior, não uma nova verificação realizada em 30/09/2026. A associação individual entre serviço e classificação não foi recuperada de forma suficiente para reproduzir uma pontuação por linha.

### Serviços considerados naquela análise

| Esfera | Serviço registrado | Tipo de fonte mencionado no relato |
| --- | --- | --- |
| Federal | Inscrição no CPF | Catálogo Gov.br e informações oficiais. |
| Federal | Seguro-desemprego | Catálogo Gov.br e informações oficiais. |
| Federal | Passaporte | Catálogo Gov.br e informações oficiais. |
| Federal | Cadastro Único | Catálogo Gov.br e informações oficiais. |
| Federal | ID Jovem | Catálogo Gov.br e informações oficiais. |
| Maranhão | Renovação de CNH | Páginas oficiais, com HTML do DETRAN-MA na análise. |
| Maranhão | Segunda via de CNH/PPD | Páginas oficiais, com HTML do DETRAN-MA na análise. |
| Maranhão | CNH definitiva | Páginas oficiais, com HTML do DETRAN-MA na análise. |
| Maranhão | Transferência de CNH de outra UF | Páginas oficiais, com HTML do DETRAN-MA na análise. |
| Maranhão | Carteira de Identidade Nacional | Fonte estadual oficial mencionada na análise. |
| São Luís | BPC | Catálogo municipal e páginas de atendimento/orientação mencionados. |
| São Luís | Bolsa Família | Catálogo municipal e páginas de atendimento/orientação mencionados. |
| São Luís | Isenção de IPTU | Catálogo municipal e páginas oficiais mencionados. |
| São Luís | Centro-Dia | Catálogo municipal e páginas oficiais mencionados. |
| São Luís | Alvará de Construção Industrial | Catálogo municipal e páginas oficiais mencionados. |

“Esfera” identifica o agrupamento das fontes na análise histórica. A presença de benefícios em um catálogo municipal não transfere ao município a competência por toda a decisão ou concessão correspondente.

Esses 15 serviços constituem uma amostra exploratória de fontes, não a lista final de funcionalidades. Vários deles não pertencem às três jornadas priorizadas na introdução.

### Formatos e conteúdo relatados

- **Gov.br:** API e representações estruturadas mencionadas como XML, com informação sobre requisitos, documentos, etapas, custos e canais.
- **Maranhão:** páginas HTML com requisitos, documentos, locais e condições; o DETRAN-MA foi uma das fontes mencionadas.
- **São Luís:** JSON de catálogo de dados abertos, complementado por páginas HTML com detalhes dos serviços.

A conclusão histórica foi de viabilidade para um protótipo delimitado, com coleta por diferentes meios e revisão do conteúdo. A heterogeneidade foi reconhecida como parte do problema de integração.

### Autenticação

| Acesso mencionado anteriormente | Registro histórico | Pendência para implementação |
| --- | --- | --- |
| `GET /api/v1/servicos-auth` | Relatado como endpoint que exige token. | Recuperar URL-base, documentação e condições de acesso. |
| Consultas Gov.br por serviço ou órgão | Relatadas como públicas. | Registrar rotas exatas, formatos, cobertura e testes. |
| JSON do catálogo de São Luís | Relatado como público. | Recuperar URL e documentar resposta e limites. |
| Páginas HTML do DETRAN-MA | Relatadas como públicas. | Registrar páginas específicas e critérios de coleta/revisão. |

No histórico, a autenticação de um catálogo foi considerada uma limitação contornável para o MVP, porque ele poderia trabalhar com informações públicas de serviços selecionados. Isso não garante acesso irrestrito a qualquer API governamental.

Consultar a descrição pública de um serviço é diferente de executar o serviço ou acessar informação pessoal. Essas operações podem ter requisitos próprios.

### O que ainda falta documentar

As URLs exatas de todos os 15 serviços, a URL-base do endpoint autenticado, os exemplos de respostas e o método detalhado da classificação não estão integralmente disponíveis nesta consolidação.

A implementação e a metodologia deverão produzir uma matriz de evidências por jornada: órgão competente, serviço, URL, formato, conteúdo aproveitável, autenticação, data, amostra, lacunas e decisão de uso. Não se deve apresentar o levantamento preliminar como prova de que todos os dados já foram integrados ou de que todos os endpoints permanecem disponíveis.
