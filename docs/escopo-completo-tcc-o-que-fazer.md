# Escopo consolidado do TCC — O que Fazer?

**Autor:** Mateus Matos de Oliveira  
**Curso:** Sistemas de Informação — UNDB  
**Orientador registrado na versão acadêmica consultada:** Prof. Me. Danilo José dos Santos Costa  
**Local e ano:** São Luís, 2026  
**Data desta consolidação:** 30 de setembro de 2026  
**Período histórico coberto:** início da concepção em 10 de agosto de 2026 até esta solicitação.

## Como utilizar este documento

Este arquivo reúne a concepção do produto, o escopo acadêmico, as propostas de arquitetura, as jornadas, a análise preliminar das fontes oficiais e as orientações de escrita discutidas ao longo do projeto. Serve como referência para continuar o TCC, apresentar a proposta e orientar a especificação e a implementação do protótipo.

É uma consolidação temática do histórico recuperado e dos documentos disponíveis, e não uma transcrição literal de todas as mensagens. Quando uma informação mais recente restringe uma proposta inicial, prevalece o recorte da versão acadêmica mais recente consultada. Detalhes não recuperados ficam registrados como pendências, em vez de serem preenchidos por suposição.

Os estados utilizados são:

| Estado | Significado |
| --- | --- |
| Consolidado | Consta na versão acadêmica mais recente consultada ou em uma escolha explícita do autor. |
| Proposto | Foi apresentado durante a elaboração, mas não há confirmação suficiente de adoção definitiva ou implementação. |
| Histórico | Representa uma formulação anterior ou uma etapa já discutida. |
| Futuro | Possibilidade de expansão além do protótipo delimitado. |
| Pendente | Depende de definição, confirmação, documentação ou avaliação. |

## 1. Identificação e evolução dos nomes

### 1.1 Nome do produto

**O que Fazer?** é o nome utilizado para a plataforma e para o protótipo. As expressões **“O que faço agora?”** e **“Onde resolvo?”** representam dois caminhos complementares de utilização.

### 1.2 Título acadêmico consolidado

**Título:** Orientação ao cidadão no acesso a serviços públicos  
**Subtítulo:** Desenvolvimento de uma plataforma baseada em situações cotidianas

Apresentação conjunta:

> **ORIENTAÇÃO AO CIDADÃO NO ACESSO A SERVIÇOS PÚBLICOS: Desenvolvimento de uma plataforma baseada em situações cotidianas**

Esse título aparece nas versões posteriores da introdução e no arquivo que integra introdução e referencial teórico.

### 1.3 Formulação anterior

Uma versão inicial utilizou:

> **O QUE FAZER: DESENVOLVIMENTO DE UM SISTEMA DE ORIENTAÇÃO BASEADO EM CONHECIMENTO PARA ACESSO A SERVIÇOS PÚBLICOS**

Essa formulação permanece como registro histórico. O nome do produto continua sendo O que Fazer?, embora o título acadêmico tenha passado a destacar a orientação ao cidadão.

### 1.4 Definição acadêmica do artefato

Um sistema de orientação baseado em conhecimento para descobrir e organizar procedimentos relacionados a serviços públicos a partir da situação vivenciada pelo cidadão.

A comparação com o Akinator foi aceita como recurso informal para explicar perguntas sucessivas e eliminação de alternativas. A definição formal do TCC se apoia em conhecimento explícito, regras de decisão, proveniência das informações e dependências entre procedimentos.

## 2. Origem da proposta e evolução do projeto

| Data ou etapa | Discussão e encaminhamento | Situação atual |
| --- | --- | --- |
| 10/08/2026 | Busca de um TCC prático para Sistemas de Informação que resolva um problema real de pessoas comuns. | Direção consolidada. |
| 10/08/2026 | Interesse pelas ideias “Onde Resolvo?” e “O que faço agora?”, relacionadas à descoberta de serviços e próximos passos. | Incorporadas ao conceito do produto. |
| 10–12/08/2026 | Explicação da ideia para um possível orientador e aproximação com a mecânica de perguntas do Akinator. | Perguntas progressivas e eliminação de alternativas mantidas. |
| 12/08/2026 | Discussão sobre estruturas de dados, algoritmos e geração da sequência de providências. | Separação entre aplicabilidade e ordenação consolidada; detalhes de implementação propostos. |
| 12/08/2026 | Produção de `o-que-fazer-projeto.md`, destinado a V0, Lovable, Base44 e ferramentas semelhantes. | Documento de visão inicial consultado nesta consolidação. |
| 12/08/2026 | Discussão da fundação de dados: REST, CSV, XML e outros formatos; SQL versus NoSQL. | PostgreSQL com JSONB foi proposto; stack final não confirmada. |
| 12/08/2026 | Solicitação de prova de viabilidade das fontes oficiais e análise de autenticação. | Há registro de análise preliminar positiva, com 15 serviços considerados. |
| 12/08/2026 | Registro resumido do projeto no Google Docs e atualização do tópico sobre viabilidade. | Etapa histórica de documentação. |
| 13/08/2026 | Explicação acadêmica ampliada para apresentação a possível orientador, incluindo dados, algoritmos e impacto social. | Conteúdo incorporado ao escopo. |
| Agosto de 2026 | Discussão e refinamento do título e subtítulo acadêmicos. | Prevalece “Orientação ao cidadão no acesso a serviços públicos”. |
| 29–30/08/2026 | Produção e revisão do trabalho até a introdução, conforme UNDB e materiais ABNT. | Introdução estruturada com problema, objetivos, justificativa, metodologia resumida e organização. |
| 27/09/2026 | Solicitação de referencial teórico a partir da versão mais recente da introdução. | Localizado documento com introdução e referencial teórico. |
| 27/09, avançando para 28/09 em UTC | Revisão de estilo: variedade, especificidade, redução de padrões repetitivos e preservação das ressalvas necessárias. | Diretriz editorial vigente. |
| 30/09/2026 | Solicitação de um Markdown com todo o escopo, desde a primeira até a última conversa. | Entrega deste documento. |

As datas acima correspondem aos registros recuperados. Algumas mensagens de fim de noite aparecem no dia seguinte quando registradas em UTC.

## 3. Visão geral e proposta de valor

O cidadão costuma reconhecer o acontecimento que precisa resolver antes de conhecer o nome oficial do serviço ou a instituição responsável. Pode dizer “perdi meus documentos” sem saber quais providências tomar, onde solicitar cada documento ou quais requisitos precisam ser atendidos primeiro.

O O que Fazer? começa por essa situação, faz perguntas relevantes e transforma as respostas em um plano organizado. O plano apresenta os procedimentos pertinentes, suas dependências, os requisitos conhecidos e os canais oficiais de atendimento.

O resultado esperado permite ao usuário compreender:

- O que precisa resolver.
- O que fazer primeiro.
- Quais ações podem ser realizadas depois ou em paralelo.
- Por que cada procedimento se aplica à sua situação.
- Qual órgão responde por cada etapa.
- Quais documentos ou condições precisa conferir.
- Onde encontrar o atendimento e a informação oficial.

O propósito inicial é social e cotidiano. O foco não é construir uma solução de gestão interna para empresas ou órgãos públicos.

## 4. Problema e questão de pesquisa

### 4.1 Problema prático

A informação sobre serviços públicos pode estar distribuída entre órgãos federais, estaduais e municipais, publicada em formatos distintos e organizada por estrutura administrativa. Mesmo quando a página oficial existe, o cidadão pode ter dificuldade para formular a busca, interpretar requisitos e reconhecer relações entre procedimentos.

Uma única situação pode exigir consultar diversas páginas, diferenciar casos semelhantes e descobrir que uma providência depende de outra. As dificuldades abordadas são de descoberta, compreensão e organização da informação.

### 4.2 Questão de pesquisa consolidada

> Como facilitar a descoberta e a compreensão de serviços públicos por cidadãos que conhecem o problema que precisam resolver, mas não necessariamente o nome do serviço ou o órgão responsável?

### 4.3 Proposição a avaliar

Organizar a orientação a partir de situações cotidianas, com perguntas progressivas e eliminação de alternativas incompatíveis, pode reduzir o esforço de descoberta e compreensão dos procedimentos em comparação à busca convencional por órgãos e serviços.

Essa proposição deverá ser examinada na avaliação. A documentação do conceito e a existência de fontes oficiais não demonstram, por si, que o protótipo será mais eficaz.

## 5. Objetivos

### 5.1 Objetivo geral consolidado

Desenvolver e avaliar uma plataforma web de orientação baseada em conhecimento que organize informações oficiais sobre serviços públicos a partir de situações cotidianas, conduzindo o cidadão por perguntas progressivas até a construção de uma jornada personalizada de resolução.

### 5.2 Objetivos específicos consolidados

1. Identificar dificuldades recorrentes na descoberta e compreensão de serviços públicos.
2. Analisar disponibilidade, confiabilidade e heterogeneidade das fontes oficiais selecionadas.
3. Definir um modelo de dados para situações, perguntas, respostas, procedimentos, requisitos, dependências e fontes.
4. Elaborar regras para eliminar alternativas e selecionar perguntas relevantes.
5. Ordenar os procedimentos conforme dependências e prioridades fundamentadas.
6. Implementar um protótipo web responsivo, acessível e orientado ao uso em dispositivos móveis.
7. Avaliar tempo de busca, taxa de conclusão, clareza das orientações, facilidade percebida e confiança nas informações.

## 6. Justificativa e contribuição esperada

### 6.1 Relevância social

A dificuldade para compreender procedimentos pode causar buscas repetidas, deslocamentos desnecessários, perda de tempo e atraso no acesso a serviços. A proposta procura apoiar pessoas com pouco conhecimento da organização administrativa e diferentes níveis de familiaridade digital.

O benefício esperado é tornar a informação oficial mais utilizável em situações concretas. Eventuais efeitos sobre acesso a direitos, inclusão digital ou redução de desigualdades precisam ser tratados com proporcionalidade às evidências obtidas.

### 6.2 Relevância acadêmica e tecnológica

O trabalho articula engenharia de requisitos, modelagem de dados, arquitetura de software, integração de fontes heterogêneas, experiência do usuário, acessibilidade, representação de conhecimento e algoritmos.

A contribuição do artefato está na combinação entre seleção contextual de procedimentos e ordenação das providências, mantendo vínculo verificável com as fontes oficiais. O TCC deverá documentar como essa combinação foi especificada, implementada e avaliada.

### 6.3 Relação com governo digital

A proposta dialoga com serviços centrados nas necessidades do cidadão, linguagem clara, facilidade de acesso e transparência. Sua atuação se concentra na orientação anterior ao atendimento ou à solicitação oficial.

## 7. Delimitação atual do TCC

### 7.1 Território

O recorte contempla informações de serviços federais e, quando aplicável, do Estado do Maranhão e do Município de São Luís. Isso não significa cobertura de todos os serviços dessas esferas.

### 7.2 Jornadas prioritárias na versão acadêmica

| Jornada | Razão de sua presença no protótipo |
| --- | --- |
| Perda de documentos | Demonstra múltiplos documentos, eliminação de procedimentos, canais e possíveis dependências. |
| Irregularidade do CPF | Demonstra ambiguidade, resposta “não sei” e necessidade de uma consulta intermediária. |
| Desligamento do trabalho | Demonstra diferenças de contexto e múltiplas providências, sem presumir elegibilidade. |

A versão acadêmica enfatiza poucas jornadas representativas, com qualidade e avaliação controladas. A quantidade final de ramificações e serviços associados permanece pendente.

### 7.3 Diferença em relação às estimativas iniciais

O documento de visão inicial sugeria aproximadamente **10 a 20 jornadas**. A análise preliminar de dados também apresentou uma possibilidade de **30 a 50 serviços**. Essas quantidades eram propostas exploratórias e não constituem obrigação do protótipo atual.

Uma jornada pode reunir vários serviços. Quantidade de jornadas e quantidade de serviços são medidas diferentes.

### 7.4 Limites institucionais e funcionais

O sistema tem caráter orientativo. A confirmação de requisitos, elegibilidade, atendimento e decisão administrativa permanece com os órgãos competentes.

Não há compromisso de executar solicitações governamentais, autenticar o cidadão nos portais oficiais, consultar bases pessoais restritas ou abranger toda a burocracia brasileira. A orientação deve indicar quando uma condição exige confirmação oficial.

## 8. Público-alvo

Pessoas que precisam utilizar serviços públicos sem conhecer previamente o nome técnico dos procedimentos ou a organização dos órgãos.

Entre os perfis discutidos estão jovens emitindo documentos, pessoas que perderam documentos, trabalhadores após desligamento, responsáveis por dependentes, idosos e familiares que os auxiliam, pessoas com pendências cadastrais e usuários com pouca familiaridade tecnológica.

O público conceitual é amplo. O perfil dos participantes da avaliação, a quantidade de pessoas e os critérios de recrutamento ainda serão definidos com o orientador.

## 9. Modos de utilização

### 9.1 O que faço agora?

Entrada por situação cotidiana. O usuário seleciona ou descreve um acontecimento, responde perguntas e recebe uma jornada personalizada.

Fluxo previsto:

1. Informar a situação.
2. Identificar procedimentos candidatos.
3. Responder perguntas que diferenciem os caminhos relevantes.
4. Confirmar, descartar ou manter indeterminados os procedimentos.
5. Organizar as providências aplicáveis.
6. Consultar o plano e os detalhes de cada etapa.
7. Acessar o canal oficial correspondente.

### 9.2 Onde resolvo?

Entrada por serviço já conhecido. O usuário busca, por exemplo, regularização do CPF ou emissão de identidade, fornece apenas o contexto necessário e consulta órgão, requisitos e canais.

Esse modo integra a visão do produto. Sua profundidade no protótipo deve ser compatível com as jornadas selecionadas e com o objetivo central da avaliação.

### 9.3 Entrada por texto livre

Foi discutida uma entrada como “descreva sua situação”. O mecanismo que transforma esse texto em uma situação conhecida ainda não foi definido. Não se deve assumir que o histórico estabeleceu obrigatoriamente o uso de um modelo de linguagem.

A seleção de situações frequentes permite demonstrar o núcleo decisório enquanto a interpretação do texto livre permanece uma escolha de implementação.

## 10. Jornadas previstas ao longo da concepção

### 10.1 Jornada demonstrativa: perda de documentos

**Entrada:** “Perdi minha carteira” ou “Perdi meus documentos”.

Perguntas discutidas:

- Foi perda, furto, roubo ou a pessoa não tem certeza?
- Quais documentos estavam envolvidos?
- Existe acesso a alguma versão digital ou a outro documento relevante?
- Qual localização importa para o atendimento?
- Há outro detalhe que realmente altere o procedimento?

O plano combina as providências correspondentes aos itens informados. Se a pessoa indicar apenas identidade e CNH, não deve receber etapas relativas a cartões ou outros documentos que não declarou ter perdido.

O registro de ocorrência ou extravio só deve aparecer quando aplicável e fundamentado. Os exemplos de fluxo são ilustrativos e não estabelecem uma exigência universal.

### 10.2 Jornada demonstrativa: CPF irregular

**Entrada:** “Meu CPF está irregular”.

O sistema pergunta se a pessoa conhece a situação exibida na consulta oficial. No protótipo inicial foram exemplificadas opções como suspenso, pendente de regularização, cancelado, outro e “não sei”. As opções definitivas e as orientações associadas dependem das fontes da jornada.

Quando a resposta for “não sei”, a plataforma orienta primeiro a descobrir a situação cadastral no canal oficial e permite continuar a jornada depois. Informação ausente não pode ser interpretada como uma condição específica.

### 10.3 Jornada demonstrativa: desligamento do trabalho

**Entrada:** “Fui demitido”.

Perguntas candidatas tratam da forma de término do contrato, do vínculo e da data, quando esses fatos alteram as orientações. O plano pode envolver consulta a procedimentos trabalhistas e benefícios, conforme o caso documentado.

A plataforma não presume que todo desligamento gera direito a seguro-desemprego, saque ou outro benefício. Os critérios devem estar representados em regras verificadas e a confirmação final é oficial.

### 10.4 Jornadas candidatas de expansão

O histórico também considerou:

1. Documentos roubados.
2. Primeira identidade.
3. Segunda via de documento.
4. Primeiro emprego.
5. Nascimento de filho.
6. Falecimento de familiar.
7. Compra de veículo usado.
8. Venda de veículo.
9. Mudança de endereço.
10. Pendência eleitoral.
11. Descoberta de onde solicitar um benefício.
12. Dificuldade de acesso à conta Gov.br.
13. Resolução de procedimentos para outra pessoa.
14. Localização de atendimento presencial.
15. Necessidade de resolver uma situação com urgência.

Essas situações compõem a visão de expansão. Não devem ser apresentadas como funcionalidades implementadas ou obrigatórias no recorte acadêmico atual.

### 10.5 Exemplos adicionais discutidos

**Nascimento de filho:** possíveis relações entre registro, documentos, saúde e benefícios, condicionadas ao contexto e às fontes.

**Falecimento de familiar:** possíveis providências imediatas e posteriores, como registro, benefícios e questões patrimoniais. A interface deve adotar tom sóbrio e perguntas progressivas.

**Compra ou venda de veículo:** distinção entre comprador e vendedor, UF de registro, situação documental e canais disponíveis. O exemplo inicial utilizou Maranhão.

## 11. Requisitos funcionais consolidados e previstos

Os requisitos abaixo organizam o conteúdo discutido. Eles precisam ser detalhados e rastreados na especificação; sua inclusão aqui não significa implementação concluída.

| ID | Requisito | Enquadramento |
| --- | --- | --- |
| RF01 | Permitir selecionar uma situação cotidiana entre as jornadas cobertas. | Núcleo do protótipo. |
| RF02 | Prever entrada por descrição de situação. | Visão do produto; interpretação pendente. |
| RF03 | Apresentar perguntas progressivas conforme o contexto. | Núcleo do protótipo. |
| RF04 | Permitir respostas únicas, múltiplas e “não sei”, conforme a pergunta. | Núcleo do protótipo. |
| RF05 | Evitar perguntas já respondidas ou irrelevantes para a orientação. | Núcleo do protótipo. |
| RF06 | Adaptar as perguntas às respostas anteriores. | Núcleo do protótipo. |
| RF07 | Eliminar procedimentos incompatíveis. | Núcleo do protótipo. |
| RF08 | Identificar procedimentos aplicáveis. | Núcleo do protótipo. |
| RF09 | Preservar situações indeterminadas e indicar informação faltante. | Núcleo do protótipo. |
| RF10 | Ordenar providências segundo dependências e prioridades fundamentadas. | Núcleo do protótipo. |
| RF11 | Apresentar um plano resumido e detalhes de cada etapa. | Núcleo do protótipo. |
| RF12 | Exibir requisitos e documentos quando disponíveis nas fontes. | Núcleo do protótipo. |
| RF13 | Exibir órgão responsável e canais online ou presenciais. | Núcleo do protótipo. |
| RF14 | Exibir custos e prazos quando documentados. | Condicionado à fonte. |
| RF15 | Exibir fonte oficial e data de verificação. | Núcleo do protótipo. |
| RF16 | Permitir revisar respostas e recalcular a jornada. | Núcleo do protótipo. |
| RF17 | Perguntar localização apenas quando ela alterar a orientação. | Núcleo do protótipo. |
| RF18 | Permitir busca direta por serviço no modo “Onde resolvo?”. | Visão do produto. |
| RF19 | Explicar por que uma etapa aparece e por que depende de outra. | Núcleo explicável. |
| RF20 | Tratar informação divergente, desatualizada ou não disponível. | Qualidade da orientação. |

## 12. Regras de negócio e de orientação

1. Toda orientação publicada deve ter fundamento rastreável em fonte oficial pertinente ao serviço e ao território.
2. Cada pergunta deve existir porque sua resposta pode alterar a aplicabilidade, a ordem ou o encaminhamento.
3. Fatos desconhecidos não devem ser convertidos automaticamente em respostas negativas.
4. Um procedimento pode ser aplicável, não aplicável ou indeterminado.
5. Uma situação pode gerar vários procedimentos, inclusive de órgãos diferentes.
6. Procedimentos comuns a vários caminhos devem ser reunidos sem duplicação desnecessária.
7. Dependências obrigatórias, condicionais e recomendadas precisam ser diferenciadas.
8. Uma prioridade de apresentação não deve criar um requisito administrativo inexistente.
9. Alterar uma resposta exige reavaliar as regras afetadas e a sequência resultante.
10. A orientação termina quando há informação suficiente para o plano ou quando o limite da informação disponível exige confirmação externa.
11. Custo, prazo e canal desconhecidos devem permanecer identificados como não informados; não cabe inventar valores.
12. A data da consulta da fonte deve ser diferenciada da data de atualização declarada pelo órgão.
13. Divergências relevantes precisam ser sinalizadas para revisão e registradas.
14. A preferência por atendimento presencial deve ser considerada quando houver alternativa documentada.
15. No uso básico, não será exigido cadastro e devem ser evitados dados pessoais desnecessários.

## 13. Experiência do usuário, interface e acessibilidade

### 13.1 Princípios de interação

- Começar por uma situação reconhecível pelo cidadão.
- Fazer uma pergunta principal por tela.
- Apresentar somente distinções relevantes para o contexto.
- Oferecer “não sei” quando a ausência de informação for plausível.
- Permitir voltar e corrigir respostas.
- Mostrar progresso sem prometer uma quantidade fixa de perguntas em um fluxo adaptativo.
- Apresentar o plano resumido antes dos detalhes.
- Explicar o motivo de cada providência em linguagem simples.
- Manter fonte e encaminhamento oficial acessíveis.

### 13.2 Telas previstas no documento inicial

| Tela ou estado | Conteúdo principal |
| --- | --- |
| Home | “O que aconteceu?”, situações frequentes e acesso aos dois modos. |
| Seleção de situação | Categorias e acontecimentos compreensíveis. |
| Perguntas | Uma pergunta principal, opções, retorno e progresso. |
| Orientação intermediária | Próximo passo para descobrir uma informação desconhecida. |
| Seu plano | Providências ordenadas e resumo do contexto. |
| Detalhe da etapa | Motivo, requisitos, órgão, canal, custo, prazo, dependências e fonte. |
| Onde resolvo? | Busca direta e contexto mínimo do serviço. |
| Lista de situações | Documentos, trabalho, família, veículos e cadastros. |
| Divergência ou desatualização | Informação sobre o limite e encaminhamento para confirmação. |
| Visualização mobile | Adaptação das telas principais a smartphones. |

### 13.3 Estrutura do plano

Cada etapa deve apresentar título, explicação curta, motivo de aplicabilidade, órgão, canais, requisitos, dependências e fonte. Custos e prazos aparecem quando disponíveis. A ordem deve tornar visíveis os pré-requisitos e as etapas independentes.

### 13.4 Direção visual discutida

Interface clara, pouco carregada, com espaço em branco, tipografia legível, cards grandes, ícones simples e destaque para a ação principal. A aparência deve transmitir confiança, neutralidade e acolhimento, com atenção prioritária ao smartphone.

Não foram confirmados uma identidade visual final, uma paleta específica ou um sistema de componentes para este TCC.

### 13.5 Acessibilidade

Considerar contraste, redimensionamento de texto, alvos de interação adequados, navegação por teclado, rótulos compreensíveis, leitores de tela e informação que não dependa somente de cor ou ícone.

As WCAG 2.2 foram incorporadas como referência conceitual no referencial. O nível de conformidade pretendido e os procedimentos de verificação ainda precisam ser definidos; não há certificação de acessibilidade registrada.

## 14. Casos de borda discutidos

| Caso | Comportamento esperado |
| --- | --- |
| Perda, furto ou roubo | Diferenciar quando a distinção altera procedimentos. |
| Vários documentos envolvidos | Combinar providências sem repetir etapas comuns. |
| Falta de um documento exigido | Identificar a obtenção do requisito e avaliar a dependência. |
| CPF irregular sem situação conhecida | Orientar consulta intermediária e permitir retorno. |
| Diferentes formas de desligamento | Perguntar o contexto relevante e não presumir benefício. |
| Compra versus venda de veículo | Usar papel do usuário e UF de registro pertinentes. |
| Localizações diferentes | Distinguir residência, local do fato, localização atual ou UF do registro, se necessário. |
| Falecimento de familiar | Perguntas graduais e organização de providências por momento e contexto. |
| Nascimento de filho | Combinar ações aplicáveis sem sobrecarregar a pessoa. |
| Dependências encadeadas | Ordenar os requisitos anteriores à etapa principal. |
| Falta de conta ou requisito de acesso Gov.br | Incluir preparação do acesso apenas quando documentada como necessária. |
| Preferência ou necessidade presencial | Exibir alternativa oficial disponível. |
| Procedimento para outra pessoa | Verificar titularidade, responsabilidade ou representação quando relevante. |
| Documento brasileiro ou migratório | Perguntar contexto quando ele mudar o caminho. |
| Urgência | Destacar canais e alternativas documentadas, sem prometer prazo. |
| Risco imediato ou emergência | Priorizar encaminhamento aos canais oficiais de emergência apropriados ao contexto. |
| Fontes contraditórias | Registrar conflito, verificar competência e informar o limite. |
| Informação possivelmente desatualizada | Exibir fonte e datas, com revisão do conteúdo. |
| Resposta “não sei” | Manter o fato desconhecido e oferecer alternativa de esclarecimento. |
| Resposta anterior corrigida | Recalcular aplicabilidade e ordem das providências. |
| Ciclo entre dependências | Tratar como inconsistência de modelagem ou conteúdo a revisar. |
| Situação fora da cobertura | Informar o limite e evitar construir uma orientação sem fundamento. |

Os dois últimos casos complementam a delimitação e o referencial. A cobertura de cada caso deve ser proporcional às jornadas efetivamente incluídas.

## 15. Fontes oficiais e prova preliminar de viabilidade

### 15.1 Pergunta que motivou a investigação

Antes de aprofundar a arquitetura, o autor questionou se as fontes oficiais realmente existiam e forneciam informação útil para a proposta. A preocupação era evitar construir um sistema cuja base informacional não pudesse ser obtida.

### 15.2 Resultado histórico recuperado

Em 12/08/2026 foi registrada uma análise preliminar de **15 serviços** das três esferas. O relato classificou oito com potencial alto, cinco com potencial médio ou médio-alto e dois com potencial baixo ou médio.

Essa classificação é um registro da análise anterior, não uma nova verificação realizada em 30/09/2026. A associação individual entre serviço e classificação não foi recuperada de forma suficiente para reproduzir uma pontuação por linha.

### 15.3 Serviços considerados naquela análise

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

### 15.4 Formatos e conteúdo relatados

- **Gov.br:** API e representações estruturadas mencionadas como XML, com informação sobre requisitos, documentos, etapas, custos e canais.
- **Maranhão:** páginas HTML com requisitos, documentos, locais e condições; o DETRAN-MA foi uma das fontes mencionadas.
- **São Luís:** JSON de catálogo de dados abertos, complementado por páginas HTML com detalhes dos serviços.

A conclusão histórica foi de viabilidade para um protótipo delimitado, com coleta por diferentes meios e revisão do conteúdo. A heterogeneidade foi reconhecida como parte do problema de integração.

### 15.5 Autenticação

| Acesso mencionado anteriormente | Registro histórico | Pendência para implementação |
| --- | --- | --- |
| `GET /api/v1/servicos-auth` | Relatado como endpoint que exige token. | Recuperar URL-base, documentação e condições de acesso. |
| Consultas Gov.br por serviço ou órgão | Relatadas como públicas. | Registrar rotas exatas, formatos, cobertura e testes. |
| JSON do catálogo de São Luís | Relatado como público. | Recuperar URL e documentar resposta e limites. |
| Páginas HTML do DETRAN-MA | Relatadas como públicas. | Registrar páginas específicas e critérios de coleta/revisão. |

No histórico, a autenticação de um catálogo foi considerada uma limitação contornável para o MVP, porque ele poderia trabalhar com informações públicas de serviços selecionados. Isso não garante acesso irrestrito a qualquer API governamental.

Consultar a descrição pública de um serviço é diferente de executar o serviço ou acessar informação pessoal. Essas operações podem ter requisitos próprios.

### 15.6 O que ainda falta documentar

As URLs exatas de todos os 15 serviços, a URL-base do endpoint autenticado, os exemplos de respostas e o método detalhado da classificação não estão integralmente disponíveis nesta consolidação.

A implementação e a metodologia deverão produzir uma matriz de evidências por jornada: órgão competente, serviço, URL, formato, conteúdo aproveitável, autenticação, data, amostra, lacunas e decisão de uso. Não se deve apresentar o levantamento preliminar como prova de que todos os dados já foram integrados ou de que todos os endpoints permanecem disponíveis.

## 16. Coleta, tratamento e governança da informação

### 16.1 Fontes consideradas

Foram discutidas APIs REST, arquivos CSV, XML e JSON, páginas institucionais e documentos, incluindo PDF quando pertinente. A presença desses formatos na arquitetura é uma previsão de adaptabilidade, não uma afirmação de que cada órgão oferece todos eles.

### 16.2 Pipeline proposto

1. Identificar a fonte oficial e sua competência territorial.
2. Registrar formato, endereço, condições de acesso e data de coleta.
3. Obter e preservar o conteúdo original quando pertinente.
4. Extrair a informação útil por um adaptador adequado.
5. Normalizar nomes, requisitos, canais, documentos e etapas.
6. Separar conteúdo confirmado, lacunas e divergências.
7. Revisar as condições que serão transformadas em regras.
8. Vincular cada orientação à fonte e à versão utilizada.
9. Publicar somente o conteúdo aprovado para a jornada.
10. Revisar quando a fonte ou a regra administrativa mudar.

### 16.3 Proveniência

Cada informação relevante precisa permitir identificar sua origem, a coleta que a produziu e a transformação realizada. Foram propostos endereço da fonte, órgão, data de consulta, versão, hash ou snapshot quando útil e registro da revisão.

Data de coleta não equivale a data de vigência. Se o órgão não informar atualização, isso deve ficar explícito.

### 16.4 Normalização e divergências

Os dados coletados devem ser transformados em entidades comuns sem apagar particularidades territoriais ou condições. Requisitos parecidos não podem ser unificados automaticamente quando representarem situações diferentes.

Em caso de divergência, registrar as fontes, verificar o órgão competente, revisar o contexto e documentar a decisão editorial. A frequência de revisão e os critérios operacionais permanecem pendentes.

### 16.5 Limite da automação

Extrair uma frase de uma página não comprova que ela foi interpretada corretamente como regra. A proposta prevê revisão do conhecimento usado no motor, especialmente quando o encaminhamento envolve condições administrativas.

## 17. Arquitetura e armazenamento discutidos

### 17.1 Direção técnica proposta

Foi sugerido **PostgreSQL como banco principal**, com entidades relacionais para o núcleo do domínio e uso controlado de **JSONB** para dados heterogêneos ou conteúdo bruto.

A proposta permite representar relações e preservar variações de origem sem exigir um segundo banco NoSQL no MVP. A adoção definitiva e a implementação desse desenho não estão confirmadas nos documentos consultados.

### 17.2 Separação das camadas de informação

| Camada proposta | Responsabilidade |
| --- | --- |
| Fontes | Identificar órgão, endereço, território, formato e acesso. |
| Importações | Registrar cada coleta, resultado, data e versão. |
| Conteúdo bruto | Preservar dados antes da transformação. |
| Domínio normalizado | Representar serviços, requisitos, canais e documentos. |
| Conhecimento e regras | Relacionar fatos, perguntas, condições e procedimentos. |
| Jornada e apresentação | Produzir sequência explicável para o usuário. |

Arquivos originais maiores podem ser preservados em filesystem ou armazenamento de objetos, com referências no banco. A escolha do provedor ou serviço não foi fechada.

### 17.3 Componentes lógicos

- Interface web responsiva.
- Lógica de sessão e coleta das respostas.
- Motor de avaliação das regras.
- Seleção da próxima pergunta.
- Construção e ordenação da jornada.
- Consulta de procedimentos e fontes.
- Adaptadores de ingestão e revisão de conteúdo.

Essas responsabilidades não exigem, por si, microserviços ou várias aplicações. A organização concreta do código ainda será definida.

### 17.4 Stack ainda não confirmada

O escopo acadêmico exige um protótipo web e descreve necessidades de armazenamento e decisão. Não há confirmação suficiente de framework de frontend, backend, ORM, hospedagem, autenticação administrativa ou versões de ferramentas.

Preferências e stacks discutidas em outros projetos do autor não são automaticamente decisões deste TCC.

## 18. Modelo conceitual de dados

Os nomes abaixo descrevem responsabilidades do domínio; não constituem um esquema físico de tabelas aprovado.

| Entidade ou relação | Finalidade |
| --- | --- |
| Situação | Acontecimento pelo qual o cidadão inicia a orientação. |
| Pergunta | Informação necessária para distinguir casos relevantes. |
| Opção de resposta | Valores permitidos, incluindo seleção múltipla ou desconhecimento. |
| Fato da sessão | Conhecimento declarado durante a interação. |
| Regra | Condição explícita que afeta um procedimento ou pergunta. |
| Procedimento/serviço | Providência que pode integrar o plano. |
| Requisito | Condição ou documento necessário ao procedimento. |
| Dependência | Relação de precedência, com tipo e contexto. |
| Órgão | Instituição responsável ou canal competente. |
| Canal de atendimento | Meio online ou presencial documentado. |
| Abrangência territorial | Contexto geográfico ao qual a orientação se aplica. |
| Fonte | Registro de origem oficial da informação. |
| Importação e versão | Histórico da coleta e das alterações. |
| Jornada calculada | Conjunto de providências e ordem resultantes do contexto. |

Relações centrais:

- Uma situação pode acionar várias perguntas e procedimentos candidatos.
- Uma pergunta pode ser reutilizada em mais de uma situação.
- Um procedimento pode integrar mais de uma jornada.
- Uma regra usa fatos e afeta a aplicabilidade ou a necessidade de esclarecimento.
- Um procedimento pode ter requisitos, canais e dependências.
- Fontes devem fundamentar também requisitos e relações relevantes, não apenas o nome do serviço.
- Alterações de conteúdo devem poder ser distinguidas das respostas particulares de uma sessão.

A persistência da sessão e seu prazo de retenção ainda precisam ser definidos. Não se presume a criação de uma conta para o cidadão.

## 19. Estruturas de dados e algoritmos

### 19.1 Dois problemas separados

| Problema | Entrada | Saída |
| --- | --- | --- |
| Descobrir o que se aplica | Situação, fatos, regras e respostas. | Procedimentos aplicáveis e questões ainda indeterminadas. |
| Organizar a ordem | Procedimentos selecionados e dependências pertinentes. | Plano que respeita pré-requisitos e distingue ações independentes. |

Essa separação é central no referencial e na introdução. Um grafo de dependências não decide sozinho a elegibilidade ou a aplicabilidade.

### 19.2 Estruturas propostas no histórico

| Estrutura | Uso proposto |
| --- | --- |
| Objeto ou `Map` | Manter fatos conhecidos da sessão. |
| `Set` | Manter candidatos sem duplicação. |
| Regras/predicados | Classificar aplicabilidade a partir dos fatos. |
| Grafo direcionado | Representar relações entre procedimentos. |
| DAG, quando válido | Representar dependências sem ciclos. |
| Máquina de estados | Organizar início, perguntas, esclarecimento e resultado da sessão. |

São alternativas de implementação discutidas, sem um código definitivo registrado.

### 19.3 Avaliação ternária

- **Aplicável:** há informação suficiente e compatível com a regra.
- **Não aplicável:** há informação que afasta o procedimento naquele contexto.
- **Indeterminado:** faltam fatos necessários ou há ambiguidade relevante.

“Não sei” mantém o fato desconhecido. Pode gerar outra pergunta ou uma providência intermediária para consultar o canal oficial.

### 19.4 Próxima pergunta

Foram discutidos critérios de prioridade e de ganho de informação: escolher perguntas capazes de diferenciar os candidatos remanescentes, evitando repetições e condições irrelevantes.

O trabalho de Quinlan sobre árvores de decisão foi incorporado como base conceitual. Isso não significa que o protótipo necessariamente adotará ID3, aprenderá regras administrativas automaticamente ou usará dados de treinamento.

A forma de calcular a utilidade da pergunta, os pesos, os desempates e a condição de parada permanecem pendentes. Um fluxo baseado em regras verificadas pode ser especificado antes de qualquer estratégia estatística.

### 19.5 Ordenação topológica

Após selecionar os procedimentos, as dependências obrigatórias pertinentes podem ser representadas em um grafo dirigido sem ciclos e ordenadas topologicamente. Kahn foi utilizado como referência conceitual no referencial.

Etapas sem relação de precedência podem ser apresentadas como independentes. Em caso de várias ordens válidas, a prioridade de exibição precisa ser fundamentada, sem criar obrigação inexistente.

Um ciclo indica que o modelo ou a interpretação das fontes exige revisão. O sistema não deve produzir uma sequência aparentemente válida ignorando essa inconsistência.

### 19.6 Explicabilidade e mudança de resposta

Cada etapa deve manter relação com fatos, regras e fontes que justificaram sua inclusão. Ao corrigir uma resposta, o motor reavalia candidatos e dependências e atualiza o plano.

## 20. Metodologia acadêmica prevista

### 20.1 Caracterização consolidada

- Pesquisa de natureza aplicada.
- Objetivos exploratórios e descritivos.
- Desenvolvimento e avaliação de um artefato computacional.
- Combinação de evidências qualitativas e quantitativas.

Não foi confirmado um protocolo completo de Design Science Research ou outro método formal específico. A caracterização não deve ser ampliada sem alinhamento com o orientador.

### 20.2 Etapas previstas

1. Revisão bibliográfica e documental.
2. Seleção das jornadas e delimitação territorial.
3. Prova de viabilidade e registro das fontes.
4. Especificação de requisitos e modelagem do conhecimento.
5. Modelagem de dados, regras e dependências.
6. Desenvolvimento do protótipo responsivo.
7. Verificação de conteúdo e funcionamento.
8. Avaliação comparativa com usuários.
9. Análise dos resultados, limitações e continuidade.

### 20.3 Aspectos ainda pendentes

Instrumentos, tamanho e perfil da amostra, recrutamento, tarefas, condições da comparação, critérios de análise e procedimentos éticos serão definidos com o orientador conforme as exigências institucionais aplicáveis.

Não há registro suficiente de testes com participantes ou de resultados quantitativos já obtidos.

## 21. Avaliação e critérios de sucesso

### 21.1 Comparação prevista

A proposta é comparar a jornada guiada com a busca convencional em portais e mecanismos de pesquisa, por meio de tarefas equivalentes. A avaliação observa a obtenção e a compreensão da orientação, e não apenas a realização final de um atendimento governamental.

### 21.2 Métricas discutidas

| Dimensão | Indicador previsto |
| --- | --- |
| Eficiência | Tempo para encontrar e compreender a orientação. |
| Eficácia | Conclusão correta da tarefa proposta. |
| Esforço de navegação | Quantidade de páginas, passos ou interações. |
| Precisão da orientação | Erros ou encaminhamentos incompatíveis com o caso. |
| Compreensão | Clareza percebida e entendimento dos próximos passos. |
| Usabilidade percebida | Facilidade de uso relatada. |
| Confiança | Percepção de confiança nas informações e fontes. |
| Fluxo de perguntas | Quantidade de perguntas necessárias ao resultado. |

Não foram fixados percentuais de melhoria, tempos máximos ou metas numéricas obrigatórias.

### 21.3 Critérios de qualidade do protótipo

- O usuário identifica os próximos passos sem reiniciar toda a pesquisa.
- A jornada respeita o contexto informado e as dependências documentadas.
- “Não sei” não produz falsa confirmação de um requisito.
- Uma correção de resposta modifica o resultado quando necessário.
- As fontes são localizáveis e as lacunas ficam explícitas.
- A interface é compreensível no recorte de usuários avaliado.

## 22. Fundamentação teórica construída

A versão localizada organiza o capítulo em seis subseções:

| Seção | Conteúdo | Relação com o protótipo |
| --- | --- | --- |
| 2.1 Governo digital e serviços centrados no cidadão | Diretrizes brasileiras e internacionais; jornada completa; confiança. | Fundamentar a entrada por necessidade cotidiana. |
| 2.2 Informação oficial, fontes heterogêneas e proveniência | Carta de Serviços, integração, metadados e origem da informação. | Sustentar coleta, revisão e rastreabilidade. |
| 2.3 Experiência do usuário, linguagem simples e acessibilidade | Heurísticas, comunicação clara, WCAG e uso móvel. | Sustentar perguntas progressivas e planos compreensíveis. |
| 2.4 Sistemas baseados em conhecimento e perguntas de decisão | Fatos, regras, candidatos, árvores e informação incompleta. | Fundamentar aplicabilidade e seleção de perguntas. |
| 2.5 Dependências entre procedimentos e ordenação da jornada | Grafos dirigidos, ordenação topológica e ciclos. | Fundamentar a sequência das providências. |
| 2.6 Síntese do referencial | Articulação dos conceitos e relação com a avaliação. | Conectar a teoria às escolhas do projeto sem antecipar eficácia. |

### 22.1 Fontes incorporadas na versão consultada

| Referência | Papel no texto |
| --- | --- |
| Lei nº 13.460/2017 | Informação ao usuário e Carta de Serviços. |
| Lei nº 14.129/2021 | Governo digital e simplificação da relação com o cidadão. |
| Decreto nº 12.069/2024 | Estratégia Nacional de Governo Digital 2024–2027. |
| Padrões de qualidade para serviços públicos digitais | Comunicação, facilidade de uso e acessibilidade. |
| TIC Domicílios 2024, publicada em 2025 | Contextualização das diferenças de uso associadas a escolaridade e conectividade. |
| OECD, 2022 | Desenho e entrega de serviços a partir das necessidades dos usuários. |
| Venkatesh et al., 2016 | Relações entre informação, transparência, confiança e uso em outro contexto institucional. |
| W3C DCAT 3 | Referência conceitual de metadados e descrição de fontes. |
| W3C PROV-O | Referência conceitual para proveniência. |
| Nielsen, 1994 | Heurísticas de usabilidade. |
| W3C WCAG 2.2 | Referência de acessibilidade web. |
| Habib et al., 2023 | Discussão internacional de peso de páginas e custo de acesso móvel. |
| Quinlan, 1986 | Árvores de decisão e distinção sucessiva de casos. |
| Kahn, 1962 | Ordenação topológica. |

O levantamento de artigos foi apoiado por ferramentas acadêmicas durante a elaboração. Há registro de uso de Consensus e de indisponibilidade do Elicit em uma etapa. Isso é histórico de trabalho, não uma exigência tecnológica do artefato.

### 22.2 Ressalvas que precisam permanecer

- Resultados de estudos internacionais não podem ser transferidos diretamente para a população brasileira.
- DCAT e PROV-O são referências conceituais; não se afirma que os órgãos adotam esses modelos ou que o protótipo os implementará integralmente.
- A referência a Quinlan não comprova treinamento automático de regras no sistema.
- Acessibilidade técnica e compreensão efetiva exigem verificação.
- As escolhas de projeto não demonstram previamente redução de desigualdade ou melhoria de desempenho.
- Competência administrativa e confirmação de elegibilidade continuam sendo oficiais.

## 23. Estrutura prevista da monografia e situação da escrita

### 23.1 Capítulos previstos

| Capítulo | Escopo |
| --- | --- |
| 1. Introdução | Contextualização e delimitação, problema, objetivos, justificativa, síntese metodológica e organização. |
| 2. Referencial teórico | Os seis eixos conceituais descritos neste documento. |
| 3. Metodologia | Seleção das jornadas, critérios documentais e plano de avaliação. |
| 4. Projeto da solução | Requisitos, arquitetura, dados, coleta, tratamento e algoritmos. |
| 5. Implementação | Construção e funcionamento do protótipo. |
| 6. Resultados e discussão | Evidências da avaliação e análise. |
| 7. Conclusões | Atendimento aos objetivos, limites e continuidade. |

Elementos pré-textuais, referências e possíveis apêndices e anexos seguem a apresentação exigida pela instituição na entrega final.

### 23.2 Estágio documentado

A etapa de agosto foi limitada à introdução. A solicitação posterior acrescentou o referencial teórico. O arquivo localizado `TCC_introducao_e_referencial_teorico.docx` contém esses dois capítulos e referências.

Também há registro de revisão posterior de estilo. A recuperação confirma a instrução e o relato da revisão, mas não permite certificar que todo o conteúdo daquela revisão esteja refletido em um arquivo mais recente do que o documento localizado.

Os demais capítulos são planejamento do trabalho. Sua presença neste escopo não implica que tenham sido redigidos ou que o sistema esteja implementado.

### 23.3 Separação de outros trabalhos acadêmicos

A solicitação recente de estrutura inicial de artigo com título em português e inglês, introdução e fundamentação teórica foi recuperada em uma conversa sobre PWA e Miniverso EdTech. Não foi incorporada como mudança de tema ou formato deste TCC.

Esta consolidação mantém o projeto de orientação ao cidadão e a estrutura de monografia registrada em seus documentos.

## 24. Normalização acadêmica e orientações de estilo

### 24.1 Materiais fornecidos e consultados

1. **MANUAL DE NORMALIZAÇÃO — REVISADO.pdf:** o conteúdo identifica um manual de normas e orientação para TCC, de São Luís, 2016.
2. **ABNT-NBR-6023-Referencias-Bibliograficas.pdf:** o conteúdo corresponde à NBR 6023:2018, versão corrigida 2, com errata de 2020.

O manual descreve uma introdução com delimitação, objetivos, justificativa, síntese metodológica e apresentação da organização do trabalho, conteúdo compatível com a introdução já construída.

Há uma diferença entre os materiais: o manual remete à NBR 6023:2002, enquanto o PDF específico de referências contém a edição de 2018. Esta consolidação registra as edições dos anexos, sem afirmar que sejam as normas mais recentes disponíveis em 2026. A edição exigida na entrega deve seguir as orientações institucionais aplicáveis.

Markdown organiza o conteúdo e não substitui a diagramação exigida para a versão final em Word ou PDF.

### 24.2 Diretriz editorial mais recente

Revisar o estilo para dar variedade e especificidade ao texto, **sem introduzir erros ou retirar ressalvas necessárias à precisão acadêmica**.

Pontos identificados para revisão:

- Ressalvas repetidas de maneira simétrica a cada referência.
- Uso recorrente de contrastes como “não equivale a”, “não determina por si só” e “sem presumir”.
- Fechamentos genéricos que sempre anunciam a contribuição do parágrafo.
- Parágrafos muito uniformes em tamanho e organização.

A revisão deve variar a construção dos argumentos, relacionar conceitos a exemplos específicos do projeto e concentrar ressalvas quando elas puderem ser reunidas sem perder precisão. A origem das evidências e seus limites devem continuar claros.

### 24.3 Integridade do texto acadêmico

Preservar a distinção entre intenção, implementação e resultado. Conferir se cada fonte sustenta a afirmação associada e se nomes, datas, números e referências estão corretos. Ajustes de estilo não autorizam inventar dados, fontes ou avaliações.

## 25. Riscos e limites já discutidos

| Risco ou limite | Encaminhamento previsto |
| --- | --- |
| Informação ausente ou pouco detalhada | Delimitar a jornada e registrar lacunas. |
| Fontes mudarem | Versionar e definir revisão. |
| Integração por formatos diferentes | Usar adaptadores e normalização. |
| API exigir autenticação | Avaliar acesso e alternativas públicas adequadas ao recorte. |
| Interpretação incorreta de requisitos | Revisar regras e manter vínculo com a fonte. |
| Encaminhamento como se fosse decisão oficial | Explicitar caráter orientativo e canal competente. |
| Falta de informação do cidadão | Estado indeterminado e esclarecimento intermediário. |
| Sobrecarga de perguntas ou resultado | Perguntas relevantes e plano resumido. |
| Cobertura excessiva para o prazo acadêmico | Priorizar poucas jornadas representativas. |
| Extrapolação de estudos externos | Preservar o contexto e os limites das referências. |
| Resultados insuficientes para afirmações amplas | Relacionar conclusões ao recorte e à amostra avaliados. |

## 26. Funcionalidades futuras discutidas

Além do protótipo, foram consideradas as seguintes possibilidades:

- Salvar jornadas.
- Marcar etapas concluídas.
- Lembrar prazos.
- Compartilhar um plano com familiares.
- Localizar postos de atendimento.
- Favoritos e histórico.
- Avaliar a orientação recebida.
- Sugerir correções ou atualizações.
- Ampliar para outros municípios e estados.
- Incluir novos conjuntos de serviços.
- Ampliar recursos de acessibilidade.
- Disponibilizar versão PWA ou aplicativo.

Essas ideias não pertencem automaticamente ao MVP. A menção histórica a PWA como expansão do O que Fazer? não transforma o TCC no artigo sobre a Miniverso.

## 27. Entregáveis e pendências

### 27.1 Entregáveis discutidos ou já produzidos

| Entregável | Estado documentado |
| --- | --- |
| Visão do produto em Markdown | Arquivo inicial localizado e consultado. |
| Explicação resumida para apresentação | Discussão histórica recuperada. |
| Registro consolidado no Google Docs | Produção e atualização relatadas no histórico. |
| Análise preliminar de viabilidade | Relato recuperado; evidências completas precisam ser reunidas. |
| Introdução acadêmica | Versões localizadas e consultadas. |
| Introdução e referencial teórico | Documento localizado e consultado. |
| Revisão de estilo com preservação de precisão | Instrução e relato recuperados. |
| Escopo consolidado em Markdown | Este arquivo. |
| Especificação detalhada e modelo físico de dados | Pendentes. |
| Protótipo funcional | Previsto; implementação não comprovada nesta consolidação. |
| Avaliação com usuários e resultados | Previstas; execução não comprovada. |
| Monografia completa | Prevista; capítulos posteriores ainda não comprovados. |

### 27.2 Decisões que ainda precisam ser fechadas

1. Ramificações e serviços finais das três jornadas prioritárias.
2. URLs, exemplos e evidências reproduzíveis da prova de viabilidade.
3. Critérios e frequência de atualização e resolução de divergências.
4. Modelo físico de dados e persistência das sessões.
5. Stack de frontend, backend, acesso a dados e hospedagem.
6. Estratégia de interpretação de texto livre.
7. Critério de seleção de perguntas, desempate e encerramento.
8. Representação concreta das regras e das dependências.
9. Forma de manutenção do conteúdo e necessidade de interface administrativa.
10. Procedimentos e nível pretendido de verificação de acessibilidade.
11. Amostra, instrumentos e protocolo da avaliação comparativa.
12. Cronograma com datas e critérios de conclusão de cada etapa.
13. Conferência final das referências e da normalização institucional.
14. Incorporação verificável da última revisão de estilo ao arquivo acadêmico.

Não há cronograma fechado ou resultados de avaliação suficientes para preencher essas pendências com números ou datas.

## 28. Direção para prototipação visual

O primeiro Markdown foi produzido para gerar uma amostra em V0, Lovable, Base44 ou ferramenta semelhante. O objetivo era visualizar a experiência antes de aprofundar a implementação.

Uma instrução coerente com o recorte atual é:

> Criar uma aplicação web responsiva chamada O que Fazer?, voltada a cidadãos que precisam descobrir os próximos passos de situações cotidianas envolvendo serviços públicos. Priorizar perda de documentos, CPF irregular e desligamento do trabalho. Na Home, apresentar “O que aconteceu?”, situações frequentes e o acesso “Já sei o que procuro — Onde resolvo?”. Conduzir uma pergunta principal por tela, com respostas compreensíveis, opção “não sei” e possibilidade de corrigir respostas. Ao final, apresentar “Seu plano”, com procedimentos aplicáveis, ordem, dependências, motivo da inclusão, requisitos, órgão, canal e fonte oficial. Demonstrar um esclarecimento intermediário para CPF desconhecido. Adotar interface leve, acessível e adequada a smartphones. As informações de demonstração devem ser identificadas como exemplos quando não houver conteúdo oficial validado. A plataforma orienta e encaminha aos canais oficiais; não confirma direitos nem executa serviços públicos.

Uma demonstração visual não comprova a implementação do motor de decisão nem a validação das fontes. Esses componentes precisam ser construídos e documentados separadamente.

## 29. Base documental desta consolidação

Foram considerados o histórico recuperado do projeto e os seguintes materiais:

- `o-que-fazer-projeto.md`, criado em 12/08/2026: visão inicial, jornadas, requisitos, casos de borda e direção para prototipação.
- `TCC_ate_a_introducao_revisado.docx`, criado em 30/08/2026: título revisado, problema, objetivos, delimitação, metodologia resumida e organização.
- `TCC_introducao_e_referencial_teorico.docx`, criado em 27/09/2026: introdução e seis subseções do referencial, com referências.
- Registros recuperados das conversas de 10–13/08, 29–30/08 e 27–28/09/2026.
- Os dois PDFs de normalização fornecidos nesta conversa.

O histórico também menciona `tcc_o_que_fazer_ate_introducao.docx`, `Introdução-1.1.docx` e `Introdução do TCC.docx` como etapas anteriores ou versões utilizadas durante as revisões. Os títulos e estados consolidados acima privilegiam os arquivos posteriores efetivamente consultados.

Este documento não contém uma auditoria nova de endpoints, legislação ou publicações. Referências e conclusões preliminares são registradas conforme a elaboração anterior, com as lacunas identificadas.

## Apêndice A. Referências identificadas na versão acadêmica

Esta lista facilita a continuidade da pesquisa. Reproduz a identificação das referências presentes no documento consultado, em formato de inventário, sem declarar nova conferência de metadados ou de disponibilidade dos links. Datas de acesso devem corresponder às consultas realmente realizadas.

| Autor/entidade e ano | Obra/documento | Identificador ou endereço registrado |
| --- | --- | --- |
| Brasil, 2017 | Lei nº 13.460, de 26 de junho de 2017. | <https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2017/lei/l13460.htm> |
| Brasil, 2021 | Lei nº 14.129, de 29 de março de 2021. | <https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14129.htm> |
| Brasil, 2024 | Decreto nº 12.069, de 21 de junho de 2024. | <https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/decreto/d12069.htm> |
| Brasil/Ministério da Gestão e da Inovação em Serviços Públicos, 2025 | Padrões de qualidade para serviços públicos digitais. | <https://www.gov.br/governodigital/pt-br/estrategias-e-governanca-digital/transformacao-digital/central-de-qualidade/padroes-de-qualidade> |
| Comitê Gestor da Internet no Brasil, 2025 | TIC Domicílios 2024. | <https://www.cetic.br/media/docs/publicacoes/2/pt-br/20251027170648/tic_domicilios_2024_livro_eletronico.pdf> |
| Habib, Rumaisa et al., 2023 | A first look at public service websites from the affordability lens. | DOI: <https://doi.org/10.1145/3543507.3583415> |
| Kahn, Arthur B., 1962 | Topological sorting of large networks. | DOI: <https://doi.org/10.1145/368996.369025> |
| Nielsen, Jakob, 1994 | 10 usability heuristics for user interface design. | <https://www.nngroup.com/articles/ten-usability-heuristics/> |
| OECD, 2022 | OECD good practice principles for public service design and delivery in the digital age. | DOI: <https://doi.org/10.1787/2ade500b-en> |
| Quinlan, J. R., 1986 | Induction of decision trees. | DOI: <https://doi.org/10.1007/BF00116251> |
| Venkatesh, Viswanath et al., 2016 | Managing citizens’ uncertainty in e-government services: the mediating and moderating roles of transparency and trust. | DOI: <https://doi.org/10.1287/isre.2015.0612> |
| W3C, 2013 | PROV-O: The PROV Ontology. | <https://www.w3.org/TR/prov-o/> |
| W3C, 2024a, conforme o documento consultado | Data Catalog Vocabulary (DCAT) — Version 3. | <https://www.w3.org/TR/vocab-dcat-3/> |
| W3C, 2024b, conforme o documento consultado | Web Content Accessibility Guidelines (WCAG) 2.2. | <https://www.w3.org/TR/WCAG22/> |

## Apêndice B. Resumo para retomada do projeto

**Produto:** O que Fazer?  
**Tema:** orientação ao cidadão no acesso a serviços públicos.  
**Entrada principal:** situação cotidiana.  
**Mecânica:** perguntas progressivas, fatos e regras verificáveis.  
**Resultado:** procedimentos aplicáveis e sequência fundamentada de próximos passos.  
**Recorte territorial:** federal, Maranhão e São Luís, conforme a jornada.  
**Jornadas prioritárias:** perda de documentos, CPF irregular e desligamento do trabalho.  
**Caráter:** orientativo, com encaminhamento para fontes e canais oficiais.  
**Dados:** fontes heterogêneas com normalização, revisão e proveniência.  
**Banco proposto:** PostgreSQL com JSONB, sem decisão final comprovada.  
**Algoritmos discutidos:** filtragem de candidatos, seleção de perguntas e ordenação topológica.  
**Interface:** responsiva, linguagem simples, uma pergunta por tela, “não sei”, revisão de respostas e plano resumido.  
**Uso básico:** sem cadastro obrigatório e com minimização de dados pessoais.  
**Avaliação prevista:** comparação com busca convencional, com indicadores de eficácia, esforço e percepção.  
**Estado acadêmico documentado:** introdução e referencial teórico, com revisão de estilo discutida.  
**Próximos marcos:** concluir especificação e fontes, implementar, avaliar e escrever os capítulos restantes.
