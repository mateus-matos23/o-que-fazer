# Matriz de evidências — índice e revisão

> Consolidação revisada do levantamento de fontes das três jornadas prioritárias (consultas de 10/10/2026).

Arquivos por jornada: [perda de documentos](perda-de-documentos.md) · [CPF irregular](cpf-irregular.md) · [desligamento do trabalho](desligamento-do-trabalho.md).

## API de serviços do Gov.br

Verificado pelo revisor via `curl` em 10/10/2026:

| Endpoint | Resultado |
| --- | --- |
| `GET https://servicos.gov.br/api/v1/servicos/{id}` | **JSON público, sem credencial.** Conferido com 10416 (Atualizar CPF) e 1045 (Solicitar o Seguro-Desemprego). |
| `GET .../api/v1/servicos/` (listagem) | 404. |
| `GET .../api/v1/servicos/{slug}` | 400 (relato do levantamento). |
| `GET .../api/v1/servicos-auth` | 401: exige token. |
| `GET .../api/v1/docs` | 403. |

Campos úteis da ficha (`resposta`): `nome`, `orgao`, `descricao`, `solicitantes` (critérios de elegibilidade em texto), `etapas` (documentos e canais), `gratuito`, `tempoTotalEstimado`, `legislacoes`, `servicosRelacionados`, `temLoginGovBR`, `temNivelMinimoContaGovBR`, `url`.

Consequências para a modelagem:

- **Sem listagem pública**: a coleta parte de uma lista curada de IDs por jornada. Isso é viável no recorte de três jornadas.
- **Sem data de atualização na ficha**: a data declarada pelo órgão ("Última Modificação") só aparece na página HTML do serviço. Para cumprir a RN12, cada procedimento precisa das duas fontes: ficha JSON e página HTML.
- **Critérios em texto livre**: `solicitantes.requisitos` é prosa. As regras do motor são escritas por humanos a partir dela ([ADR 0002](../../arquitetura/decisoes/0002-motor-baseado-em-regras.md)), e não extraídas automaticamente.
- **Divergências dentro da própria fonte**, por exemplo `gratuito: false` × "gratuito, exceto unidades conveniadas" (ficha 10420), precisam ser registradas (RN13).

## Classificação das fontes

| Jornada | Fonte | Decisão |
| --- | --- | --- |
| CPF irregular | API 10416 (Atualizar CPF), API 10420 (Inscrever no CPF) | **Usar** (com a página HTML para a data) |
| CPF irregular | Receita, "Meu CPF" (6 situações cadastrais) | **Usar com revisão manual**: conferida pelo revisor; Falecido/Cancelado/Nulo não têm providência |
| CPF irregular | Consulta de situação cadastral; formulário de regularização; página DIRPF | **Usar com revisão manual** (canais de encaminhamento) |
| CPF irregular | TSE (título de eleitor na regularização) | **Pendente**: 403; o papel do título não é confirmado |
| Desligamento | API 1045 (Seguro-Desemprego), API 9815 (doméstico), API 7839 (vínculos CAGED) | **Usar**: 1045 conferida pelo revisor |
| Desligamento | FGTS, saque por dispensa sem justa causa; CTPS Digital e FAQ | **Usar com revisão manual** (HTML; FGTS sem data de atualização) |
| Desligamento | Saque-aniversário; SINE/SRTE São Luís | **Pendente**: 404, loop ou autenticação |
| Perda de documentos | API 10424 (Obter Cartão de CPF) + página HTML | **Usar**: conferida pelo revisor |
| Perda de documentos | Delegacia Online PC-MA | **Usar com revisão manual**: HTML, com data de publicação de 2018 e sem data de atualização |
| Perda de documentos | Gov.br, "identidade" (orientação por estado) | **Pendente**: `https://www.gov.br/identidade` redireciona para uma página com HTTP 404 (verificado pelo revisor em 10/10/2026) |
| Perda de documentos | 2ª via da CNH (DETRAN-MA), 2ª via da CIN no MA, título de eleitor (TSE/TRE-MA), versões digitais no MA | **Pendente**: sem fonte oficial acessível; só notícias ou terceiros |

| Perda de documentos | Gov.br, perguntas frequentes da CIN (emissão estadual, certidão atualizada, 2ª via em qualquer UF) | **Usar** (atualização de 24/10/2026; substitui `gov.br/identidade`, que segue 404) |
| Perda de documentos | SSP-MA, notícia da CIN no MA (Ident-MA, Viva/Procon, documentos) | **Usar com revisão manual**: notícia de 12/01/2024; trata da primeira via; 2ª via e taxa atuais não confirmadas |
| Perda de documentos | DETRAN-MA, 2ª via da CNH/PpD (`Pagina.xhtml?id=19297`) e tabela de taxas | **Usar com revisão manual** (24/10/2026): conteúdo acessível; sem data declarada |
| Perda de documentos | São Luís, 2ª via de certidão de nascimento (carta de serviços, id 11) | **Usar com revisão manual** (24/10/2026): custo e prazo "em estudo" na própria página |
| Candidatas | Ver [jornadas candidatas](jornadas-candidatas.md) | Levantamento preliminar de 24/10/2026 |

Amostras brutas (via `curl`, com hash e data de coleta) em [`../amostras/`](../amostras/README.md).

## Ressalvas de método

- Trechos obtidos por WebFetch são **extratos processados**, não cópias literais. Antes de citar no TCC ou de virar regra, a amostra deve ser recoletada em bruto (`curl`) e salva em `docs/dados/amostras/`.
- Sites que bloqueiam acesso automatizado (TSE, TRE-MA, partes do DETRAN-MA e do Governo do MA) exigem conferência manual no navegador.

## Riscos para as jornadas

- **Perda de documentos**: as fontes estaduais centrais (CNH, CIN, título) não foram confirmadas. **Decisão de 10/10/2026:** a jornada foi reduzida aos procedimentos com fonte acessível ([recorte](../../produto/jornadas.md#recorte-da-jornada-de-perda-de-documentos-no-protótipo)).
- **Desligamento** tem critérios oficiais apenas para dispensa sem justa causa. Outras formas de término (acordo, culpa recíproca, fim de contrato) aparecem como "não informado" e devem resultar em indeterminado ou encaminhamento, nunca em suposição (RN03, RN11).

## Atualização de 24/10/2026: descoberta por catálogo

Para reduzir buscas abertas, a descoberta partiu dos catálogos oficiais baixados uma vez e filtrados localmente:

| Esfera | Catálogo | Resultado |
| --- | --- | --- |
| Federal | `https://www.gov.br/pt-br/sitemap.xml.gz` (URLs `/pt-br/servicos/`) | 5.747 serviços. CIN, 2ª via da CNH, título de eleitor, transferência de veículo e certidão de nascimento **não** estão no catálogo federal: são estaduais, municipais, de cartório ou da Justiça Eleitoral. |
| Estadual (MA) | `https://www.ma.gov.br/todos-os-servicos` | Lista carregada por JavaScript; inacessível por `curl`. Fontes estaduais localizadas por WebSearch restrito a `ma.gov.br` e depois coletadas em bruto. |
| Municipal (São Luís) | `https://www.saoluis.ma.gov.br/portal/carta-servicos/{página}/0/0/0/cidadao/0` | 468 serviços ao cidadão, com páginas de detalhe `.../carta-servicos/{id}/` e data "Atualizado em". |

Dependências entre procedimentos sustentadas por trecho literal (primeiras do projeto):

| Dependência | Tipo proposto | Trecho e amostra |
| --- | --- | --- |
| Registrar ocorrência → 2ª via da CNH (MA) | Obrigatória | "DOCUMENTOS NECESSÁRIOS: • Boletim de Ocorrência;" ([amostra](../amostras/html-detran-2via-cnh.md)) |
| 2ª via da certidão de nascimento → CIN | Condicional (só se a certidão também foi perdida) | "é necessário levar a certidão de nascimento ou casamento atualizada" ([amostra](../amostras/html-govbr-cin-faq.md)) |
| Vistoria aprovada em ECV → transferência digital de veículo (MA) | Obrigatória | "O Procedimento inicia com agendamento da vistoria veicular em ECV do Maranhão; Após aprovação, o usuário seguirá para a plataforma online" ([amostra](../amostras/html-detran-transf-digital.md)) |

Ressalvas: a WebSearch devolveu valores (R$ 61,30 para a 2ª via da CNH; R$ 32,83 para a 2ª via do RG em 2019) que **não** aparecem nas amostras brutas. A tabela de taxas do DETRAN-MA traz R$ 90,00 de serviço e itens opcionais (total de R$ 199,27). Só os valores das amostras podem ser citados.
