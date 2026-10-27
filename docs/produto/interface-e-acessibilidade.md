# Interface, experiência do usuário e acessibilidade

> Princípios de interação, telas previstas, estrutura do plano, direção visual, acessibilidade e briefing de prototipação.

## Experiência do usuário, interface e acessibilidade

### Princípios de interação

- Começar por uma situação reconhecível pelo cidadão.
- Fazer uma pergunta principal por tela.
- Apresentar somente distinções relevantes para o contexto.
- Oferecer “não sei” quando a ausência de informação for plausível.
- Permitir voltar e corrigir respostas.
- Mostrar progresso sem prometer uma quantidade fixa de perguntas em um fluxo adaptativo.
- Apresentar o plano resumido antes dos detalhes.
- Explicar o motivo de cada providência em linguagem simples.
- Manter fonte e encaminhamento oficial acessíveis.

### Linguagem simples

Consolidado (Fase 7, 25/10/2026): regras de redação para perguntas e opções, pensadas para públicos com idade, escolaridade e familiaridade com tecnologia variadas.

- Frases curtas.
- Opções na primeira pessoa, descrevendo o que aconteceu com o cidadão: "A empresa me mandou embora".
- Termo oficial entre parênteses, quando existir: "(dispensa sem justa causa)".
- A dica da pergunta é opcional e fica ligada ao fieldset por `aria-describedby`.
- O efeito de cada resposta aparece em texto, sem animação.
- "Saiu do seu plano" nunca é redigido como "você não tem direito". Não aplicável é avaliação orientativa sobre os fatos informados, não decisão oficial.

### Telas previstas no documento inicial

| Tela ou estado | Conteúdo principal |
| --- | --- |
| Home | “O que aconteceu?”, situações frequentes e acesso aos dois modos. |
| Seleção de situação | Categorias e acontecimentos compreensíveis. |
| Perguntas | Uma pergunta principal, opções, retorno e progresso. Depois da última, uma pergunta de preferência de atendimento (Fase 7) antes do primeiro plano. |
| Orientação intermediária | Próximo passo para descobrir uma informação desconhecida. |
| Seu plano | Providências ordenadas e resumo do contexto. |
| Detalhe da etapa | Motivo, requisitos, órgão, canal, custo, prazo, dependências e fonte. |
| Onde resolvo? | Busca direta e contexto mínimo do serviço. |
| Lista de situações | Documentos, trabalho, família, veículos e cadastros. |
| Divergência ou desatualização | Informação sobre o limite e encaminhamento para confirmação. |
| Visualização mobile | Adaptação das telas principais a smartphones. |

### Estrutura do plano

Cada etapa deve apresentar título, explicação curta, motivo de aplicabilidade, órgão, canais, requisitos, dependências e fonte. Custos e prazos aparecem quando disponíveis. A ordem deve tornar visíveis os pré-requisitos e as etapas independentes.

Histórico (Fase 7, 25/10/2026): o plano tinha as seções "Comece por aqui", "Resumo" e "O que separar antes" e uma dica de impressão. Essas seções saíram em 27/10/2026.

Consolidado (27/10/2026): o plano é uma lista única de etapas, agrupada por camada.

- Topo: resumo "N etapas. Comece pelo passo 1." (a segunda frase só aparece com mais de uma camada), aviso orientativo de uma linha e linha com a preferência de atendimento e o link "Mudar".
- A camada 1 traz "Comece aqui". Uma camada com várias etapas diz "Pode fazer em qualquer ordem". Plano de uma só camada não mostra número.
- Cada cartão mostra título, descrição, "Onde: órgão", "Depois de" com "(sugestão)" quando a ordem é só recomendada (RN08) e o esclarecimento de "Não sei".
- O botão principal é "Ir para o site oficial": o primeiro canal, na ordem de preferência, que tenha URL e não seja "pode valer". Sem canal com URL, o cartão tem o botão de contorno "Ver a página oficial do serviço", que leva à fonte citada.
- Motivos, requisitos, todos os canais, custo, prazo e fonte com datas ficam em "Ver detalhes" (`<details>`).
- Impressão: o CSS abre os `<details>` com `::details-content`, que só funciona no Chromium 131 ou superior (`shortcut:` registrado no CSS).

### Direção visual discutida

Interface clara, pouco carregada, com espaço em branco, tipografia legível, cards grandes, ícones simples e destaque para a ação principal. A aparência deve transmitir confiança, neutralidade e acolhimento, com atenção prioritária ao smartphone.

Histórico: a paleta de 24/10/2026 (verde-petróleo) e a de 26/10/2026 (inspirada nas fachadas e azulejos de São Luís) foram substituídas.

Consolidado (27/10/2026): identidade neutra, que não imita o gov.br ([ADR 0004](../arquitetura/decisoes/0004-frontend-e-acessibilidade.md)). Os valores e os contrastes estão no topo de `guidance/static/guidance/site.css`.

- A cor só aparece com papel: azul para ação, verde para prioridade ("Comece aqui", "entrou no plano"), âmbar para alerta e vermelho para erro.
- Fonte Atkinson Hyperlegible Next, servida localmente, com texto base de 18 px.
- Alvos principais de 56 px, nenhum abaixo de 48 px.
- Coluna única de 36 rem, com mobile primeiro.
- O indicador de etapas tem 3 segmentos (Perguntas, Atendimento, Plano) e não aparece no plano.
- O botão de Libras continua flutuante à direita, agora na vertical (44 px de largura). Em telas estreitas, a página ganha margem direita do tamanho do botão, que assim não cobre o conteúdo.

Não há sistema de componentes.

### Acessibilidade

Considerar contraste, redimensionamento de texto, alvos de interação adequados, navegação por teclado, rótulos compreensíveis, leitores de tela e informação que não dependa somente de cor ou ícone.

As WCAG 2.2 foram incorporadas como referência conceitual no referencial. Consolidado (24/10/2026): a meta é WCAG 2.2 nível AA, com verificação própria ([ADR 0004](../arquitetura/decisoes/0004-frontend-e-acessibilidade.md)). O resultado está no [registro de implementação](../implementacao/README.md). Não há certificação de acessibilidade, e o uso com leitor de tela real ainda não foi verificado.

Consolidado (26/10/2026): o botão "Libras" oferece a tradução do VLibras, do governo federal. O widget só é carregado quando o cidadão confirma, depois de ver o aviso de tamanho e de envio do texto. O botão não aparece em "Rever respostas" nem sem JavaScript ([ADR 0008](../arquitetura/decisoes/0008-vlibras.md)).

## Direção para prototipação visual

O primeiro Markdown foi produzido para gerar uma amostra em V0, Lovable, Base44 ou ferramenta semelhante. O objetivo era visualizar a experiência antes de aprofundar a implementação.

Uma instrução coerente com o recorte atual é:

> Criar uma aplicação web responsiva chamada O que Fazer?, voltada a cidadãos que precisam descobrir os próximos passos de situações cotidianas envolvendo serviços públicos. Priorizar perda de documentos, CPF irregular e desligamento do trabalho. Na Home, apresentar “O que aconteceu?”, situações frequentes e o acesso “Já sei o que procuro — Onde resolvo?”. Conduzir uma pergunta principal por tela, com respostas compreensíveis, opção “não sei” e possibilidade de corrigir respostas. Ao final, apresentar “Seu plano”, com procedimentos aplicáveis, ordem, dependências, motivo da inclusão, requisitos, órgão, canal e fonte oficial. Demonstrar um esclarecimento intermediário para CPF desconhecido. Adotar interface leve, acessível e adequada a smartphones. As informações de demonstração devem ser identificadas como exemplos quando não houver conteúdo oficial validado. A plataforma orienta e encaminha aos canais oficiais; não confirma direitos nem executa serviços públicos.

Uma demonstração visual não comprova a implementação do motor de decisão nem a validação das fontes. Esses componentes precisam ser construídos e documentados separadamente.
